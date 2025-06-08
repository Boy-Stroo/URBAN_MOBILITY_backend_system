import sqlite3
from contextlib import contextmanager
import database
from models import User, Traveller, Scooter, UserProfile, RestoreCode
from security import SecurityManager

# Instantiate the security manager to use its encryption/hashing methods
security = SecurityManager()

@contextmanager
def db_connection():
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

# --- User and Profile Data Access ---
def add_user(username, password, role):
    """Adds a new user to the database with an encrypted username and hashed password."""
    encrypted_username = security.encrypt_data(username.lower())
    hashed_password = security.hash_password(password)
    sql = "INSERT INTO Users(username, password_hash, role) VALUES (?, ?, ?)"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (encrypted_username, hashed_password.decode('utf-8'), role))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Error: This username may already be taken.")
        return None

def find_user_by_username(username):
    """Finds a user by their plaintext username by fetching, decrypting, and comparing."""
    sql = "SELECT user_id, username, password_hash, role FROM Users WHERE is_active = 1"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            all_users = cursor.fetchall()
            for user_id, enc_username, password_hash, role in all_users:
                decrypted_username = security.decrypt_data(enc_username)
                if decrypted_username and decrypted_username == username.lower():
                    return (user_id, password_hash, role)
            return None
    except Exception as e:
        print(f"An error occurred while finding a user: {e}")
        return None

def get_user_hash_by_id(user_id):
    """Fetches just the password hash for a given user ID."""
    sql = "SELECT password_hash FROM Users WHERE user_id = ? AND is_active = 1"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"An error occurred fetching user hash: {e}")
        return None

def update_user_password(user_id, new_password_hash):
    """Updates the password hash for a specific user."""
    sql = "UPDATE Users SET password_hash = ? WHERE user_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (new_password_hash, user_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred while updating the password: {e}")
        return False

def add_user_profile(user_id, first_name, last_name, registration_date):
    """Adds a profile for a given user."""
    sql = "INSERT INTO UserProfiles(user_id, first_name, last_name, registration_date) VALUES (?, ?, ?, ?)"
    try:
        with db_connection() as conn:
            conn.execute(sql, (user_id, first_name, last_name, registration_date))
            return True
    except Exception as e:
        print(f"An error occurred while adding a user profile: {e}")
        return False

def get_user_profile_by_user_id(user_id):
    """Fetches a UserProfile object by the user's ID."""
    sql = "SELECT * FROM UserProfiles WHERE user_id = ?"
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            if row:
                return UserProfile(**dict(row))
            return None
    except Exception as e:
        print(f"An error occurred fetching user profile by ID: {e}")
        return None

def update_user_profile(user_id, first_name, last_name):
    """Updates an existing user's profile."""
    sql = "UPDATE UserProfiles SET first_name = ?, last_name = ? WHERE user_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (first_name, last_name, user_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred while updating user profile: {e}")
        return False

def get_all_users_by_role(role_to_find):
    """Fetches all active users of a specific role."""
    sql = "SELECT u.user_id, u.username, up.first_name, up.last_name FROM Users u JOIN UserProfiles up ON u.user_id = up.user_id WHERE u.is_active = 1 AND u.role = ?"
    users = []
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (role_to_find,))
            all_users = cursor.fetchall()
            for user_id, enc_username, first_name, last_name in all_users:
                dec_username = security.decrypt_data(enc_username)
                if dec_username:
                    users.append({'id': user_id, 'username': dec_username, 'name': f"{first_name} {last_name}"})
        return users
    except Exception as e:
        print(f"An error occurred while fetching users: {e}")
        return []

def delete_user_by_id(user_id):
    """Deletes a user by setting their is_active flag to 0. (Soft delete)"""
    sql = "UPDATE Users SET is_active = 0 WHERE user_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred while deleting a user: {e}")
        return False

# --- Traveller Data Access ---
def add_traveller(traveller: Traveller):
    """Adds a new traveller to the database, encrypting sensitive fields."""
    sql = """INSERT INTO Travellers(first_name, last_name, birthday, gender, street_name, house_number, zip_code, city, email_address, mobile_phone, driving_license_number, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            encrypted_data = { 'street': security.encrypt_data(traveller.street_name), 'house': security.encrypt_data(traveller.house_number), 'zip': security.encrypt_data(traveller.zip_code), 'city': security.encrypt_data(traveller.city), 'email': security.encrypt_data(traveller.email_address), 'phone': security.encrypt_data(traveller.mobile_phone) }
            params = ( traveller.first_name, traveller.last_name, str(traveller.birthday), traveller.gender, encrypted_data['street'], encrypted_data['house'], encrypted_data['zip'], encrypted_data['city'], encrypted_data['email'], encrypted_data['phone'], traveller.driving_license_number, str(traveller.registration_date) )
            cursor.execute(sql, params)
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Error: A traveller with this email address may already exist.")
        return None

def search_travellers_by_name(name_query):
    """Searches for travellers by first or last name using a partial match."""
    sql = "SELECT customer_id, first_name, last_name, driving_license_number FROM Travellers WHERE first_name LIKE ? OR last_name LIKE ?"
    results = []
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (f'%{name_query}%', f'%{name_query}%'))
            rows = cursor.fetchall()
            for row in rows:
                results.append(dict(row))
        return results
    except Exception as e:
        print(f"An error occurred during traveller search: {e}")
        return []

def get_traveller_by_id(traveller_id):
    """Fetches a single, fully-decrypted traveller record by their ID."""
    sql = "SELECT * FROM Travellers WHERE customer_id = ?"
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (traveller_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['street_name'] = security.decrypt_data(data['street_name'])
                data['house_number'] = security.decrypt_data(data['house_number'])
                data['zip_code'] = security.decrypt_data(data['zip_code'])
                data['city'] = security.decrypt_data(data['city'])
                data['email_address'] = security.decrypt_data(data['email_address'])
                data['mobile_phone'] = security.decrypt_data(data['mobile_phone'])
                return Traveller(**data)
            return None
    except Exception as e:
        print(f"An error occurred fetching traveller by ID: {e}")
        return None

def update_traveller(traveller: Traveller):
    """Updates an existing traveller record in the database."""
    sql = """UPDATE Travellers SET
                first_name = ?, last_name = ?, birthday = ?, gender = ?,
                street_name = ?, house_number = ?, zip_code = ?, city = ?,
                email_address = ?, mobile_phone = ?, driving_license_number = ?
             WHERE customer_id = ?"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            encrypted_data = { 'street': security.encrypt_data(traveller.street_name), 'house': security.encrypt_data(traveller.house_number), 'zip': security.encrypt_data(traveller.zip_code), 'city': security.encrypt_data(traveller.city), 'email': security.encrypt_data(traveller.email_address), 'phone': security.encrypt_data(traveller.mobile_phone) }
            params = ( traveller.first_name, traveller.last_name, str(traveller.birthday), traveller.gender, encrypted_data['street'], encrypted_data['house'], encrypted_data['zip'], encrypted_data['city'], encrypted_data['email'], encrypted_data['phone'], traveller.driving_license_number, traveller.customer_id )
            cursor.execute(sql, params)
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        print("Error: Update failed. The email address may already be in use by another traveller.")
        return False

def delete_traveller_by_id(traveller_id):
    """Permanently deletes a traveller from the database."""
    sql = "DELETE FROM Travellers WHERE customer_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (traveller_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred deleting traveller: {e}")
        return False


# --- Scooter Data Access ---
def add_scooter(scooter: Scooter):
    """Adds a new scooter to the database."""
    sql = """INSERT INTO Scooters(brand, model, serial_number, top_speed_kmh, battery_capacity_wh, soc_percentage, target_soc_min, target_soc_max, location_latitude, location_longitude, out_of_service, mileage_km, last_maintenance_date, in_service_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            params = (scooter.brand, scooter.model, scooter.serial_number, scooter.top_speed_kmh, scooter.battery_capacity_wh, scooter.soc_percentage, scooter.target_soc_min, scooter.target_soc_max, scooter.location_latitude, scooter.location_longitude, scooter.out_of_service, scooter.mileage_km, str(scooter.last_maintenance_date), str(scooter.in_service_date))
            cursor.execute(sql, params)
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Error: A scooter with this serial number may already exist.")
        return None

def search_scooters(query):
    """Searches for scooters by brand, model, or serial number."""
    sql = "SELECT scooter_id, brand, model, serial_number, out_of_service FROM Scooters WHERE brand LIKE ? OR model LIKE ? OR serial_number LIKE ?"
    results = []
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (f'%{query}%', f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            for row in rows:
                results.append(dict(row))
        return results
    except Exception as e:
        print(f"An error occurred during scooter search: {e}")
        return []

def get_scooter_by_id(scooter_id):
    """Fetches a single scooter record by its ID."""
    sql = "SELECT * FROM Scooters WHERE scooter_id = ?"
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (scooter_id,))
            row = cursor.fetchone()
            if row:
                return Scooter(**dict(row))
            return None
    except Exception as e:
        print(f"An error occurred fetching scooter by ID: {e}")
        return None

def update_scooter(scooter: Scooter):
    """Updates an existing scooter record in the database."""
    sql = """UPDATE Scooters SET
                brand = ?, model = ?, serial_number = ?, top_speed_kmh = ?,
                battery_capacity_wh = ?, soc_percentage = ?, target_soc_min = ?,
                target_soc_max = ?, location_latitude = ?, location_longitude = ?,
                out_of_service = ?, mileage_km = ?, last_maintenance_date = ?
             WHERE scooter_id = ?"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            params = (scooter.brand, scooter.model, scooter.serial_number, scooter.top_speed_kmh, scooter.battery_capacity_wh, scooter.soc_percentage, scooter.target_soc_min, scooter.target_soc_max, scooter.location_latitude, scooter.location_longitude, scooter.out_of_service, scooter.mileage_km, str(scooter.last_maintenance_date), scooter.scooter_id)
            cursor.execute(sql, params)
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        print("Error: Update failed. The serial number may already be in use by another scooter.")
        return False

def delete_scooter_by_id(scooter_id):
    """Permanently deletes a scooter from the database."""
    sql = "DELETE FROM Scooters WHERE scooter_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (scooter_id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred deleting scooter: {e}")
        return False


# --- Log Data Access ---
def add_log_entry(username, event_type, description, additional_info="", is_suspicious=0):
    """Adds a new, encrypted entry to the Logs table."""
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    enc_description = security.encrypt_data(description)
    enc_additional_info = security.encrypt_data(additional_info) if additional_info else None
    sql = """INSERT INTO Logs(timestamp, username, event_type, description, additional_info, is_suspicious, is_read) VALUES (?, ?, ?, ?, ?, ?, 0)"""
    try:
        with db_connection() as conn:
            conn.execute(sql, (timestamp, username, event_type, enc_description, enc_additional_info, is_suspicious))
            return True
    except Exception as e:
        print(f"An error occurred while adding a log entry: {e}")
        return False

def get_all_logs():
    """Retrieves and decrypts all logs, ordered by most recent first."""
    sql = "SELECT * FROM Logs ORDER BY timestamp DESC"
    logs = []
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                log_entry = dict(row)
                log_entry['description'] = security.decrypt_data(log_entry['description'])
                if log_entry['additional_info']:
                    log_entry['additional_info'] = security.decrypt_data(log_entry['additional_info'])
                logs.append(log_entry)
        return logs
    except Exception as e:
        print(f"An error occurred while fetching logs: {e}")
        return []

def get_unread_suspicious_logs_count():
    """Counts the number of unread suspicious logs."""
    sql = "SELECT COUNT(*) FROM Logs WHERE is_suspicious = 1 AND is_read = 0"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print(f"An error occurred while counting suspicious logs: {e}")
        return 0

def mark_all_logs_as_read():
    """Marks all log entries as read."""
    sql = "UPDATE Logs SET is_read = 1 WHERE is_read = 0"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return True
    except Exception as e:
        print(f"An error occurred while marking logs as read: {e}")
        return False

# --- Restore Code Data Access ---
def add_restore_code(code: RestoreCode):
    """Saves a new restore code to the database."""
    sql = """INSERT INTO RestoreCodes (restore_code, backup_filename, system_admin_id, status, generated_at, expires_at)
             VALUES (?, ?, ?, ?, ?, ?)"""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            params = (code.restore_code, code.backup_filename, code.system_admin_id, code.status, str(code.generated_at), str(code.expires_at))
            cursor.execute(sql, params)
            return cursor.lastrowid
    except Exception as e:
        print(f"An error occurred saving the restore code: {e}")
        return None

def get_restore_code(code_value):
    """Retrieves a restore code from the database by its value."""
    sql = "SELECT * FROM RestoreCodes WHERE restore_code = ?"
    try:
        with db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (code_value,))
            row = cursor.fetchone()
            if row:
                return RestoreCode(**dict(row))
            return None
    except Exception as e:
        print(f"An error occurred fetching the restore code: {e}")
        return None

def update_restore_code_status(code_id, new_status):
    """Updates the status of a restore code (e.g., to 'used')."""
    sql = "UPDATE RestoreCodes SET status = ? WHERE code_id = ?"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (new_status, code_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"An error occurred updating the restore code status: {e}")
        return False
