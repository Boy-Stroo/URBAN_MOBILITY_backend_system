import sqlite3
from contextlib import contextmanager
import database
import uuid
from models import Traveller, Scooter, UserProfile, RestoreCode # , User
from security import SecurityManager

class DataAccess:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataAccess, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if DataAccess._initialized:
            return

        self.security = SecurityManager()

        self.in_memory_data = {
            'users': [],
            'user_profiles': [],
            'travellers': [],
            'scooters': [],
            'restore_codes': [],
            'logs': []
        }

        self.load_all_data_to_memory()

        DataAccess._initialized = True

    @contextmanager
    def db_connection(self):
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
        if value is None:
            return None
        if isinstance(value, (int, float, bool)):
            return self.security.encrypt_data(str(value))
        return self.security.encrypt_data(value)

    def decrypt_value(self, value):
        if value is None:
            return None
        decrypted = self.security.decrypt_data(value)
        if decrypted is None:
            return None
        return decrypted

    def load_all_data_to_memory(self):

        self.in_memory_data = {
            'users': [],
            'user_profiles': [],
            'travellers': [],
            'scooters': [],
            'restore_codes': [],
            'logs': []
        }

        with self.db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Users")
            for row in cursor.fetchall():
                user_data = dict(row)
                user_data['username'] = self.decrypt_value(user_data['username'])
                user_data['password_hash'] = self.decrypt_value(user_data['password_hash'])
                user_data['role'] = self.decrypt_value(user_data['role'])
                user_data['is_active'] = self.decrypt_value(user_data['is_active'])
                self.in_memory_data['users'].append(user_data)

            cursor.execute("SELECT * FROM UserProfiles")
            for row in cursor.fetchall():
                profile_data = dict(row)
                profile_data['first_name'] = self.decrypt_value(profile_data['first_name'])
                profile_data['last_name'] = self.decrypt_value(profile_data['last_name'])
                profile_data['registration_date'] = self.decrypt_value(profile_data['registration_date'])
                self.in_memory_data['user_profiles'].append(profile_data)

            cursor.execute("SELECT * FROM Travellers")
            for row in cursor.fetchall():
                traveller_data = dict(row)
                for key in traveller_data:
                    if key not in ['customer_id']:
                        traveller_data[key] = self.decrypt_value(traveller_data[key])


                self.in_memory_data['travellers'].append(traveller_data)

            cursor.execute("SELECT * FROM Scooters")
            for row in cursor.fetchall():
                scooter_data = dict(row)
                for key in scooter_data:
                    if key != 'scooter_id':
                        scooter_data[key] = self.decrypt_value(scooter_data[key])
                self.in_memory_data['scooters'].append(scooter_data)

            cursor.execute("SELECT * FROM RestoreCodes")
            for row in cursor.fetchall():
                code_data = dict(row)
                for key in code_data:
                    if key not in ['code_id', 'system_admin_id']:
                        code_data[key] = self.decrypt_value(code_data[key])
                self.in_memory_data['restore_codes'].append(code_data)

            cursor.execute("SELECT * FROM Logs")
            for row in cursor.fetchall():
                log_data = dict(row)
                for key in log_data:
                    if key not in ['log_id', 'is_suspicious', 'is_read']:
                        log_data[key] = self.decrypt_value(log_data[key])
                self.in_memory_data['logs'].append(log_data)

        return self.in_memory_data

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
                self.load_all_data_to_memory()
                return user_id
        except sqlite3.IntegrityError:
            print("Error: This username may already be taken.")
            return None

    def find_user_by_username(self, username):
        username = username.lower()
        for user in self.in_memory_data['users']:
            if user['username'] and user['username'].lower() == username:
                if user['is_active'] == '1':
                    return (user['user_id'], user['password_hash'], user['role'])

        return None

    def get_user_hash_by_id(self, user_id):
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
        sql = "UPDATE Users SET password_hash = ? WHERE user_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (new_password_hash, user_id))
                self.load_all_data_to_memory()
                return True
        except Exception as e:
            print(f"An error occurred while updating the password: {e}")
            return False

    def add_user_profile(self, user_id, first_name, last_name, registration_date):
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
        username = ""
        print("My user_id:", user_id)
        for user in self.in_memory_data['users']:
            if user['user_id'] == user_id:
                username = user['username']
        for profile in self.in_memory_data['user_profiles']:
            print("Checking profile:", profile)
            if profile['user_id'] == user_id:
                return UserProfile(**profile), username

        return None

    def update_user_profile(self, user_id, first_name, last_name):
        sql = "UPDATE UserProfiles SET first_name = ?, last_name = ? WHERE user_id = ?"
        encrypted_first_name = self.security.encrypt_data(first_name)
        encrypted_last_name = self.security.encrypt_data(last_name)

        try:
            with self.db_connection() as conn:
                conn.execute(sql, (encrypted_first_name, encrypted_last_name, user_id))
                self.load_all_data_to_memory()
                return True
        except Exception as e:
            print(f"An error occurred while updating user profile: {e}")
            return False

    def get_all_users_by_role(self, role_to_find):
        users = []

        for user in self.in_memory_data['users']:
            if user['role'] == role_to_find and user['is_active'] == '1':
                user_profile = None
                for profile in self.in_memory_data['user_profiles']:
                    if profile['user_id'] == user['user_id']:
                        user_profile = profile
                        break

                if user_profile:
                    users.append({
                        'id': user['user_id'],
                        'username': user['username'],
                        'name': f"{user_profile['first_name']} {user_profile['last_name']}"
                    })

        return users

    def delete_user_by_id(self, user_id):
        sql = "UPDATE Users SET is_active = 0 WHERE user_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (user_id,))
                self.load_all_data_to_memory()
                return True
        except Exception as e:
            print(f"An error occurred while deleting a user: {e}")
            return False

    # --- Traveller Data Access ---
    def add_traveller(self, traveller: Traveller):
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
        results = []
        traveller_query = traveller_query.lower()  # Case-insensitive search

        for traveller in self.in_memory_data['travellers']:
            if (traveller_query in traveller['first_name'].lower() or
                    traveller_query in traveller['last_name'].lower() or
                    traveller_query in traveller['customer_id'].lower()
            ):
                results.append({
                    'customer_id': traveller['customer_id'],
                    'first_name': traveller['first_name'],
                    'last_name': traveller['last_name'],
                    'driving_license_number': traveller['driving_license_number']
                })

        return results

    def get_traveller_by_id(self, traveller_id):
        for traveller in self.in_memory_data['travellers']:
            if traveller_id in traveller['customer_id']:
                return Traveller(**traveller)
        return None

    def update_traveller(self, traveller: Traveller):
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
        results = []
        query = query.lower()

        for scooter in self.in_memory_data['scooters']:
            if (query in str(scooter['brand']).lower() or
                    query in str(scooter['model']).lower() or
                    query in str(scooter['serial_number']).lower()):
                results.append({
                    'scooter_id': scooter['scooter_id'],
                    'brand': scooter['brand'],
                    'model': scooter['model'],
                    'serial_number': scooter['serial_number'],
                    'out_of_service': scooter['out_of_service']
                })

        return results

    def get_scooter_by_id(self, scooter_id):
        for scooter in self.in_memory_data['scooters']:
            if scooter['scooter_id'] == scooter_id:
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
        sql = """UPDATE Scooters SET
                    brand = ?, model = ?, serial_number = ?, top_speed_kmh = ?,
                    battery_capacity_wh = ?, soc_percentage = ?, target_soc_min = ?,
                    target_soc_max = ?, location_latitude = ?, location_longitude = ?,
                    out_of_service = ?, mileage_km = ?, last_maintenance_date = ?
                 WHERE scooter_id = ?"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()

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
        from datetime import datetime
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

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
        sorted_logs = sorted(self.in_memory_data['logs'], key=lambda x: x['timestamp'], reverse=True)
        return sorted_logs

    def get_unread_suspicious_logs_count(self):
        count = 0
        for log in self.in_memory_data['logs']:
            if log['is_suspicious'] == '1' and log['is_read'] == '0':
                count += 1

        return count

    def mark_all_logs_as_read(self):
        sql = "UPDATE Logs SET is_read = ? WHERE is_read = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                encrypted_read = self.encrypt_value(1)
                encrypted_unread = self.encrypt_value(0)
                cursor.execute(sql, (encrypted_read, encrypted_unread))

                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()

                return True
        except Exception as e:
            print(f"An error occurred while marking logs as read: {e}")
            return False

    def add_restore_code(self, code: RestoreCode):
        code_id = str(uuid.uuid4())
        sql = """INSERT INTO RestoreCodes (code_id, restore_code, backup_filename, system_admin_id, status, generated_at, expires_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()

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
        for code in self.in_memory_data['restore_codes']:
            if code['restore_code'] == code_value:
                return RestoreCode(**code)

        return None

    def delete_restore_codes_by_system_admin(self, system_admin_id):
        try:
            query = "DELETE FROM RestoreCodes WHERE system_admin_id = ?"
            params = (system_admin_id,)
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred while deleting restore codes: {e}")
            return False

    def get_restore_codes_by_system_admin(self, system_admin_id):
        restore_codes = []
        for code in self.in_memory_data['restore_codes']:
            if code['system_admin_id'] == system_admin_id:
                restore_codes.append(RestoreCode(**code))
        return restore_codes

    def update_restore_code_status(self, code_id, new_status):
        sql = "UPDATE RestoreCodes SET status = ? WHERE code_id = ?"
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                encrypted_status = self.encrypt_value(new_status)
                cursor.execute(sql, (encrypted_status, code_id))

                if cursor.rowcount > 0:
                    self.load_all_data_to_memory()

                return cursor.rowcount > 0
        except Exception as e:
            print(f"An error occurred updating the restore code status: {e}")
            return False

    def delete_restore_code(self, code_id):
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
    print("Testing data access functions...")

    data_access = DataAccess()
    user_id = data_access.add_user("testuser", "securepassword", "ServiceEngineer")
