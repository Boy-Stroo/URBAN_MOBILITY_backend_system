import sqlite3
from contextlib import contextmanager
import database
import uuid
from models import Traveller, Scooter, UserProfile, RestoreCode # , User
from security import SecurityManager


class DataAccess:
    """
    Data access layer with encrypted database storage and in-memory decrypted data cache.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern: return the same instance if it already exists."""
        if cls._instance is None:
            cls._instance = super(DataAccess, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the DataAccess instance with security manager and load data to memory."""
        # Only initialize once
        if DataAccess._initialized:
            return

        # Instantiate the security manager to use its encryption/hashing methods
        self.security = SecurityManager()

        # In-memory database for decrypted data
        self.in_memory_data = {
            'users': [],
            'user_profiles': [],
            'travellers': [],
            'scooters': [],
            'restore_codes': [],
            'logs': []
        }

        # Load all data to memory upon instantiation
        self.load_all_data_to_memory()

        # Mark as initialized
        DataAccess._initialized = True

    @contextmanager
    def db_connection(self):
        """A context manager to simplify database connection and transactions."""
        conn = database.connect_db()
        if conn is None:
            raise ConnectionError("Failed to connect to the database.")
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def encrypt_value(self, value):
        """Encrypts a value, handling different data types."""
        if value is None:
            return None
        if isinstance(value, (int, float, bool)):
            return self.security.encrypt_data(str(value))
        return self.security.encrypt_data(value)

    def decrypt_value(self, value):
        """Decrypts a value, handling different data types."""
        if value is None:
            return None
        decrypted = self.security.decrypt_data(value)
        if decrypted is None:
            return None
        return decrypted

    def load_all_data_to_memory(self):
        """Loads all data from the database, decrypts it, and stores it in memory."""
        # Clear existing in-memory data
        self.in_memory_data = {
            'users': [],
            'user_profiles': [],
            'travellers': [],
            'scooters': [],
            'restore_codes': [],
            'logs': []
        }

        # Load and decrypt users
        with self.db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Load Users
            cursor.execute("SELECT * FROM Users")
            for row in cursor.fetchall():
                user_data = dict(row)
                user_data['username'] = self.decrypt_value(user_data['username'])
                user_data['password_hash'] = self.decrypt_value(user_data['password_hash'])
                user_data['role'] = self.decrypt_value(user_data['role'])
                user_data['is_active'] = self.decrypt_value(user_data['is_active'])
                self.in_memory_data['users'].append(user_data)

            # Load UserProfiles
            cursor.execute("SELECT * FROM UserProfiles")
            for row in cursor.fetchall():
                profile_data = dict(row)
                profile_data['first_name'] = self.decrypt_value(profile_data['first_name'])
                profile_data['last_name'] = self.decrypt_value(profile_data['last_name'])
                profile_data['registration_date'] = self.decrypt_value(profile_data['registration_date'])
                self.in_memory_data['user_profiles'].append(profile_data)

            # Load Travellers
            cursor.execute("SELECT * FROM Travellers")
            for row in cursor.fetchall():
                traveller_data = dict(row)
                for key in traveller_data:
                    if key not in ['customer_id']:
                        traveller_data[key] = self.decrypt_value(traveller_data[key])


                self.in_memory_data['travellers'].append(traveller_data)

            # Load Scooters
            cursor.execute("SELECT * FROM Scooters")
            for row in cursor.fetchall():
                scooter_data = dict(row)
                for key in scooter_data:
                    if key != 'scooter_id':
                        scooter_data[key] = self.decrypt_value(scooter_data[key])
                self.in_memory_data['scooters'].append(scooter_data)

            # Load RestoreCodes
            cursor.execute("SELECT * FROM RestoreCodes")
            for row in cursor.fetchall():
                code_data = dict(row)
                for key in code_data:
                    if key not in ['code_id', 'system_admin_id']:
                        code_data[key] = self.decrypt_value(code_data[key])
                self.in_memory_data['restore_codes'].append(code_data)

            # Load Logs
            cursor.execute("SELECT * FROM Logs")
            for row in cursor.fetchall():
                log_data = dict(row)
                for key in log_data:
                    if key not in ['log_id', 'is_suspicious', 'is_read']:
                        log_data[key] = self.decrypt_value(log_data[key])
                self.in_memory_data['logs'].append(log_data)

        return self.in_memory_data

    # --- User and Profile Data Access ---
    def add_user(self, username, password, role):
        """Adds a new user to the database with an encrypted username and hashed password."""
        user_id = str(uuid.uuid4())
        encrypted_username = self.security.encrypt_data(username.lower())
        hashed_password = self.security.hash_password(password)
        encrypted_password = self.security.encrypt_data(hashed_password.decode('utf-8'))
        encrypted_role = self.security.encrypt_data(role.lower())
        encrypted_is_active = self.security.encrypt_data('1')  # Active by default

        sql = "INSERT INTO Users(user_id, username, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?)"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id, encrypted_username, encrypted_password, encrypted_role, encrypted_is_active))
                # Refresh in-memory data after successful insert
                self.load_all_data_to_memory()
                return user_id
        except sqlite3.IntegrityError:
            print("Error: This username may already be taken.")
            return None

    def find_user_by_username(self, username):
        """Finds a user by their plaintext username using in-memory decrypted data."""

        # Search for the user in the in-memory data
        username = username.lower()  # Case-insensitive search
        for user in self.in_memory_data['users']:
            if user['username'] and user['username'].lower() == username:
                if user['is_active'] == '1':  # Check if user is active
                    return (user['user_id'], user['password_hash'], user['role'])

        return None

    def get_user_hash_by_id(self, user_id):
        """Fetches just the password hash for a given user ID."""
        sql = "SELECT password_hash FROM Users WHERE user_id = ? AND is_active = 1"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"An error occurred fetching user hash: {e}")
            return None

    def update_user_password(self, user_id, new_password_hash):
        """Updates the password hash for a specific user."""
        sql = "UPDATE Users SET password_hash = ? WHERE user_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (new_password_hash, user_id))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred while updating the password: {e}")
            return False

    def add_user_profile(self, user_id, first_name, last_name, registration_date):
        """Adds a profile for a given user."""
        profile_id = str(uuid.uuid4())
        sql = "INSERT INTO UserProfiles(profile_id, user_id, first_name, last_name, registration_date) VALUES (?, ?, ?, ?, ?)"
        encrypted_first_name = self.security.encrypt_data(first_name)
        encrypted_last_name = self.security.encrypt_data(last_name)
        try:
            with self.db_connection() as conn:
                conn.execute(sql, (profile_id, user_id, encrypted_first_name, encrypted_last_name, registration_date))
                self.load_all_data_to_memory()
                return profile_id
        except Exception as e:
            print(f"An error occurred while adding a user profile: {e}")
            return None

    def get_user_profile_by_user_id(self, user_id):
        """Fetches a UserProfile object by the user's ID using in-memory decrypted data."""
        # Search for the user profile in the in-memory data
        username = ""
        for user in self.in_memory_data['users']:
            if user['user_id'] == user_id:
                username = user['username']
        for profile in self.in_memory_data['user_profiles']:
            if profile['user_id'] == user_id:
                return UserProfile(**profile), username



        return None

    def update_user_profile(self, user_id, first_name, last_name):
        """Updates an existing user's profile."""
        sql = "UPDATE UserProfiles SET first_name = ?, last_name = ? WHERE user_id = ?"
        encrypted_first_name = self.security.encrypt_data(first_name)
        encrypted_last_name = self.security.encrypt_data(last_name)
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                conn.execute(sql, (encrypted_first_name, encrypted_last_name, user_id))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred while updating user profile: {e}")
            return False

    def get_all_users_by_role(self, role_to_find):
        """Fetches all active users of a specific role using in-memory decrypted data."""
        users = []

        # Search for users with the specified role in the in-memory data
        for user in self.in_memory_data['users']:
            if user['role'] == role_to_find and user['is_active'] == '1':
                # Find the corresponding user profile
                user_profile = None
                for profile in self.in_memory_data['user_profiles']:
                    if profile['user_id'] == user['user_id']:
                        user_profile = profile
                        break

                # Add the user to the results
                if user_profile:
                    users.append({
                        'id': user['user_id'],
                        'username': user['username'],
                        'name': f"{user_profile['first_name']} {user_profile['last_name']}"
                    })

        return users

    def delete_user_by_id(self, user_id):
        """Deletes a user by setting their is_active flag to 0. (Soft delete)"""
        sql = "UPDATE Users SET is_active = 0 WHERE user_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred while deleting a user: {e}")
            return False

    # --- Traveller Data Access ---
    def add_traveller(self, traveller: Traveller):
        """Adds a new traveller to the database, encrypting sensitive fields."""
        customer_id = str(uuid.uuid4())
        sql = """INSERT INTO Travellers(customer_id, first_name, last_name, birthday, gender, street_name, house_number, zip_code, city, email_address, mobile_phone, driving_license_number, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                encrypted_data = {
                    'first_name': self.security.encrypt_data(traveller.first_name),
                    'last_name': self.security.encrypt_data(traveller.last_name),
                    'birthday': self.security.encrypt_data(str(traveller.birthday)),
                    'gender': self.security.encrypt_data(traveller.gender),
                    'street': self.security.encrypt_data(traveller.street_name),
                    'house': self.security.encrypt_data(traveller.house_number),
                    'zip': self.security.encrypt_data(traveller.zip_code),
                    'city': self.security.encrypt_data(traveller.city),
                    'email': self.security.encrypt_data(traveller.email_address),
                    'phone': self.security.encrypt_data(traveller.mobile_phone),
                    'driving_license_number': self.security.encrypt_data(traveller.driving_license_number)
                }
                params = (customer_id, encrypted_data['first_name'], encrypted_data['last_name'],
                          encrypted_data['birthday'], encrypted_data['gender'],
                          encrypted_data['street'], encrypted_data['house'], encrypted_data['zip'],
                          encrypted_data['city'],
                          encrypted_data['email'], encrypted_data['phone'], encrypted_data['driving_license_number'],
                          str(traveller.registration_date))
                cursor.execute(sql, params)
                self.load_all_data_to_memory()
                return customer_id
        except sqlite3.IntegrityError:
            print("Error: A traveller with this email address may already exist.")
            return None

    def search_travellers_by_name_or_id(self, traveller_query):
        """Searches for travellers by first or last name using in-memory decrypted data."""
        results = []
        traveller_query = traveller_query.lower()  # Case-insensitive search


        # Search in the in-memory decrypted data
        for traveller in self.in_memory_data['travellers']:
            # Check if the query matches any of the name fields
            if (traveller_query in traveller['first_name'].lower() or
                    traveller_query in traveller['last_name'].lower() or
                    traveller_query in traveller['customer_id'].lower()
            ):
                # Add only the required fields to the results
                results.append({
                    'customer_id': traveller['customer_id'],
                    'first_name': traveller['first_name'],
                    'last_name': traveller['last_name'],
                    'driving_license_number': traveller['driving_license_number']
                })

        return results

    def get_traveller_by_id(self, traveller_id):
        """Fetches a single, fully-decrypted traveller record by their ID using in-memory data."""
        # Search for the traveller in the in-memory data
        for traveller in self.in_memory_data['travellers']:
            if traveller_id in traveller['customer_id']:
                return Traveller(**traveller)
        return None

    def update_traveller(self, traveller: Traveller):
        """Updates an existing traveller record in the database, encrypting sensitive fields."""
        sql = """UPDATE Travellers SET
                    first_name = ?, last_name = ?, birthday = ?, gender = ?,
                    street_name = ?, house_number = ?, zip_code = ?, city = ?,
                    email_address = ?, mobile_phone = ?, driving_license_number = ?
                 WHERE customer_id = ?"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                encrypted_data = {
                    'first_name': self.security.encrypt_data(traveller.first_name),
                    'last_name': self.security.encrypt_data(traveller.last_name),
                    'birthday': self.security.encrypt_data(str(traveller.birthday)),
                    'gender': self.security.encrypt_data(traveller.gender),
                    'street': self.security.encrypt_data(traveller.street_name),
                    'house': self.security.encrypt_data(traveller.house_number),
                    'zip': self.security.encrypt_data(traveller.zip_code),
                    'city': self.security.encrypt_data(traveller.city),
                    'email': self.security.encrypt_data(traveller.email_address),
                    'phone': self.security.encrypt_data(traveller.mobile_phone),
                    'driving_license_number': self.security.encrypt_data(traveller.driving_license_number)
                }
                params = (
                    encrypted_data['first_name'], encrypted_data['last_name'], encrypted_data['birthday'],
                    encrypted_data['gender'],
                    encrypted_data['street'], encrypted_data['house'], encrypted_data['zip'], encrypted_data['city'],
                    encrypted_data['email'], encrypted_data['phone'], encrypted_data['driving_license_number'],
                    traveller.customer_id
                )
                cursor.execute(sql, params)
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("Error: Update failed. The email address may already be in use by another traveller.")
            return False

    def delete_traveller_by_id(self, traveller_id):
        """Permanently deletes a traveller from the database."""
        sql = "DELETE FROM Travellers WHERE customer_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (traveller_id,))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred deleting traveller: {e}")
            return False

    # --- Scooter Data Access ---
    def add_scooter(self, scooter: Scooter):
        """Adds a new scooter to the database, encrypting all fields."""
        scooter_id = str(uuid.uuid4())
        sql = """INSERT INTO Scooters(scooter_id, brand, model, serial_number, top_speed_kmh, battery_capacity_wh, soc_percentage, target_soc_min, target_soc_max, location_latitude, location_longitude, out_of_service, mileage_km, last_maintenance_date, in_service_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                # Encrypt all fields
                encrypted_data = {
                    'brand': self.encrypt_value(scooter.brand),
                    'model': self.encrypt_value(scooter.model),
                    'serial_number': self.encrypt_value(scooter.serial_number),
                    'top_speed_kmh': self.encrypt_value(scooter.top_speed_kmh),
                    'battery_capacity_wh': self.encrypt_value(scooter.battery_capacity_wh),
                    'soc_percentage': self.encrypt_value(scooter.soc_percentage),
                    'target_soc_min': self.encrypt_value(scooter.target_soc_min),
                    'target_soc_max': self.encrypt_value(scooter.target_soc_max),
                    'location_latitude': self.encrypt_value(scooter.location_latitude),
                    'location_longitude': self.encrypt_value(scooter.location_longitude),
                    'out_of_service': self.encrypt_value(1 if scooter.out_of_service else 0),
                    'mileage_km': self.encrypt_value(scooter.mileage_km),
                    'last_maintenance_date': self.encrypt_value(str(scooter.last_maintenance_date)),
                    'in_service_date': self.encrypt_value(str(scooter.in_service_date))
                }

                params = (
                    scooter_id,
                    encrypted_data['brand'],
                    encrypted_data['model'],
                    encrypted_data['serial_number'],
                    encrypted_data['top_speed_kmh'],
                    encrypted_data['battery_capacity_wh'],
                    encrypted_data['soc_percentage'],
                    encrypted_data['target_soc_min'],
                    encrypted_data['target_soc_max'],
                    encrypted_data['location_latitude'],
                    encrypted_data['location_longitude'],
                    encrypted_data['out_of_service'],
                    encrypted_data['mileage_km'],
                    encrypted_data['last_maintenance_date'],
                    encrypted_data['in_service_date']
                )

                cursor.execute(sql, params)
                self.load_all_data_to_memory()
                return scooter_id
        except sqlite3.IntegrityError:
            print("Error: A scooter with this serial number may already exist.")
            return None

    def search_scooters(self, query):
        """Searches for scooters by brand, model, or serial number using in-memory decrypted data."""
        results = []
        query = query.lower()  # Case-insensitive search

        # Search in the in-memory decrypted data
        for scooter in self.in_memory_data['scooters']:
            # Check if the query matches any of the search fields
            if (query in str(scooter['brand']).lower() or
                    query in str(scooter['model']).lower() or
                    query in str(scooter['serial_number']).lower()):
                # Add only the required fields to the results
                results.append({
                    'scooter_id': scooter['scooter_id'],
                    'brand': scooter['brand'],
                    'model': scooter['model'],
                    'serial_number': scooter['serial_number'],
                    'out_of_service': scooter['out_of_service']
                })

        return results

    def get_scooter_by_id(self, scooter_id):
        """Fetches a single scooter record by its ID using in-memory decrypted data."""
        # Search for the scooter in the in-memory data
        for scooter in self.in_memory_data['scooters']:
            if scooter['scooter_id'] == scooter_id:
                # Convert numeric string values to appropriate types for the Scooter model
                try:
                    scooter_data = {
                        'scooter_id': scooter['scooter_id'],
                        'brand': scooter['brand'],
                        'model': scooter['model'],
                        'serial_number': scooter['serial_number'],
                        'top_speed_kmh': int(scooter['top_speed_kmh']) if scooter['top_speed_kmh'] else None,
                        'battery_capacity_wh': int(scooter['battery_capacity_wh']) if scooter[
                            'battery_capacity_wh'] else None,
                        'soc_percentage': float(scooter['soc_percentage']) if scooter['soc_percentage'] else None,
                        'target_soc_min': float(scooter['target_soc_min']) if scooter['target_soc_min'] else None,
                        'target_soc_max': float(scooter['target_soc_max']) if scooter['target_soc_max'] else None,
                        'location_latitude': float(scooter['location_latitude']) if scooter[
                            'location_latitude'] else None,
                        'location_longitude': float(scooter['location_longitude']) if scooter[
                            'location_longitude'] else None,
                        'out_of_service': bool(int(scooter['out_of_service'])) if scooter['out_of_service'] else False,
                        'mileage_km': float(scooter['mileage_km']) if scooter['mileage_km'] else 0,
                        'last_maintenance_date': scooter['last_maintenance_date'],
                        'in_service_date': scooter['in_service_date']
                    }
                    return Scooter(**scooter_data)
                except (ValueError, TypeError) as e:
                    print(f"Error converting scooter data types: {e}")
                    return None

        return None

    def update_scooter(self, scooter: Scooter):
        """Updates an existing scooter record in the database, encrypting all fields."""
        sql = """UPDATE Scooters SET
                    brand = ?, model = ?, serial_number = ?, top_speed_kmh = ?,
                    battery_capacity_wh = ?, soc_percentage = ?, target_soc_min = ?,
                    target_soc_max = ?, location_latitude = ?, location_longitude = ?,
                    out_of_service = ?, mileage_km = ?, last_maintenance_date = ?
                 WHERE scooter_id = ?"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()

                # Encrypt all fields
                encrypted_data = {
                    'brand': self.encrypt_value(scooter.brand),
                    'model': self.encrypt_value(scooter.model),
                    'serial_number': self.encrypt_value(scooter.serial_number),
                    'top_speed_kmh': self.encrypt_value(scooter.top_speed_kmh),
                    'battery_capacity_wh': self.encrypt_value(scooter.battery_capacity_wh),
                    'soc_percentage': self.encrypt_value(scooter.soc_percentage),
                    'target_soc_min': self.encrypt_value(scooter.target_soc_min),
                    'target_soc_max': self.encrypt_value(scooter.target_soc_max),
                    'location_latitude': self.encrypt_value(scooter.location_latitude),
                    'location_longitude': self.encrypt_value(scooter.location_longitude),
                    'out_of_service': self.encrypt_value(1 if scooter.out_of_service else 0),
                    'mileage_km': self.encrypt_value(scooter.mileage_km),
                    'last_maintenance_date': self.encrypt_value(str(scooter.last_maintenance_date))
                }

                params = (
                    encrypted_data['brand'],
                    encrypted_data['model'],
                    encrypted_data['serial_number'],
                    encrypted_data['top_speed_kmh'],
                    encrypted_data['battery_capacity_wh'],
                    encrypted_data['soc_percentage'],
                    encrypted_data['target_soc_min'],
                    encrypted_data['target_soc_max'],
                    encrypted_data['location_latitude'],
                    encrypted_data['location_longitude'],
                    encrypted_data['out_of_service'],
                    encrypted_data['mileage_km'],
                    encrypted_data['last_maintenance_date'],
                    scooter.scooter_id
                )

                cursor.execute(sql, params)
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("Error: Update failed. The serial number may already be in use by another scooter.")
            return False

    def delete_scooter_by_id(self, scooter_id):
        """Permanently deletes a scooter from the database."""
        sql = "DELETE FROM Scooters WHERE scooter_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (scooter_id,))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred deleting scooter: {e}")
            return False

    # --- Log Data Access ---
    def add_log_entry(self, username, event_type, description, additional_info="", is_suspicious=0):
        """Adds a new, encrypted entry to the Logs table."""
        from datetime import datetime
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Encrypt all fields
        encrypted_data = {
            'timestamp': self.encrypt_value(timestamp),
            'username': self.encrypt_value(username),
            'event_type': self.encrypt_value(event_type),
            'description': self.encrypt_value(description),
            'additional_info': self.encrypt_value(additional_info) if additional_info else None,
            'is_suspicious': is_suspicious,
            'is_read': 0
        }

        sql = """INSERT INTO Logs(log_id, timestamp, username, event_type, description, additional_info, is_suspicious, is_read) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db_connection() as conn:
                conn.execute(sql,
                             (log_id,
                              encrypted_data['timestamp'],
                              encrypted_data['username'],
                              encrypted_data['event_type'],
                              encrypted_data['description'],
                              encrypted_data['additional_info'],
                              encrypted_data['is_suspicious'],
                              encrypted_data['is_read']))
                self.load_all_data_to_memory()
                return log_id
        except Exception as e:
            print(f"An error occurred while adding a log entry: {e}")
            return None

    def get_all_logs(self):
        """Retrieves all logs using in-memory decrypted data, ordered by most recent first."""
        # Sort logs by timestamp in descending order (most recent first)
        sorted_logs = sorted(self.in_memory_data['logs'], key=lambda x: x['timestamp'], reverse=True)
        return sorted_logs

    def get_unread_suspicious_logs_count(self):
        """Counts the number of unread suspicious logs using in-memory decrypted data."""
        # Count suspicious and unread logs in memory
        count = 0
        for log in self.in_memory_data['logs']:
            if log['is_suspicious'] == '1' and log['is_read'] == '0':
                count += 1

        return count

    def mark_all_logs_as_read(self):
        """Marks all log entries as read."""
        sql = "UPDATE Logs SET is_read = ? WHERE is_read = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                # Encrypt the values for is_read
                encrypted_read = self.encrypt_value(1)
                encrypted_unread = self.encrypt_value(0)
                cursor.execute(sql, (encrypted_read, encrypted_unread))

                # Refresh in-memory data
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()

                return True
        except Exception as e:
            print(f"An error occurred while marking logs as read: {e}")
            return False

    # --- Restore Code Data Access ---
    def add_restore_code(self, code: RestoreCode):
        """Saves a new restore code to the database, encrypting all fields."""
        code_id = str(uuid.uuid4())
        sql = """INSERT INTO RestoreCodes (code_id, restore_code, backup_filename, system_admin_id, status, generated_at, expires_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()

                # Encrypt all fields
                encrypted_data = {
                    'restore_code': self.encrypt_value(code.restore_code),
                    'backup_filename': self.encrypt_value(code.backup_filename),
                    'status': self.encrypt_value(code.status),
                    'generated_at': self.encrypt_value(str(code.generated_at)),
                    'expires_at': self.encrypt_value(str(code.expires_at))
                }

                params = (
                    code_id,
                    encrypted_data['restore_code'],
                    encrypted_data['backup_filename'],
                    code.system_admin_id,
                    encrypted_data['status'],
                    encrypted_data['generated_at'],
                    encrypted_data['expires_at']
                )

                cursor.execute(sql, params)
                self.load_all_data_to_memory()
                return code_id
        except Exception as e:
            print(f"An error occurred saving the restore code: {e}")
            return None

    def get_restore_code(self, code_value):
        """Retrieves a restore code from the database by its value using in-memory decrypted data."""
        # Search for the restore code in the in-memory data
        for code in self.in_memory_data['restore_codes']:
            if code['restore_code'] == code_value:
                return RestoreCode(**code)

        return None

    def get_restore_codes_by_system_admin(self, system_admin_id):
        """Retrieves all restore codes for a specific system administrator using in-memory decrypted data."""
        codes = []

        # Search for restore codes in the in-memory data
        for code in self.in_memory_data['restore_codes']:
            if code['system_admin_id'] == system_admin_id:
                id_to_remove = code['code_id']
                codes.append(RestoreCode(**code))

        return codes

    def update_restore_code_status(self, code_id, new_status):
        """Updates the status of a restore code (e.g., to 'used')."""
        sql = "UPDATE RestoreCodes SET status = ? WHERE code_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                # Encrypt the new status
                encrypted_status = self.encrypt_value(new_status)
                cursor.execute(sql, (encrypted_status, code_id))

                # Refresh in-memory data
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()

                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred updating the restore code status: {e}")
            return False

    def delete_restore_code(self, code_id):
        """Deletes a restore code from the database."""
        sql = "DELETE FROM RestoreCodes WHERE code_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (code_id,))
                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred deleting the restore code: {e}")
            return False

if __name__ == "__main__":
    # This block is for testing the data access functions directly.
    # You can run this script to see if the database operations work as expected.
    print("Testing data access functions...")

    # Example: Create a DataAccess instance and add a user
    data_access = DataAccess()
    user_id = data_access.add_user("testuser", "securepassword", "ServiceEngineer")
    # if user_id:
    #     print(f"User added with ID: {user_id}")
