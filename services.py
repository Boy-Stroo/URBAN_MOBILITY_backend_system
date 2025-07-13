import data_access as da
from models import Traveller, Scooter, User, RestoreCode
from datetime import datetime, timedelta
from security import SecurityManager
from auditing import audit_activity
from database import DATABASE_NAME
import authorization
import zipfile
import os
import shutil
import secrets

security = SecurityManager()
da = da.DataAccess()


@audit_activity("ADD_TRAVELLER", "Added new traveller account", "Failed to add new traveller")
def add_new_traveller(data, current_user):
    if authorization.has_permission(current_user.role, 'add_traveller') is True:
        try:
            traveller_obj = Traveller(customer_id=None, first_name=data['first_name'], last_name=data['last_name'],
                                      birthday=data['birthday'], gender=data['gender'], street_name=data['street_name'],
                                      house_number=data['house_number'], zip_code=data['zip_code'], city=data['city'],
                                      email_address=data['email_address'], mobile_phone=data['mobile_phone'],
                                      driving_license_number=data['driving_license_number'])
            print(f"Adding new traveller: {traveller_obj.first_name} {traveller_obj.last_name}")
            traveller_id = da.add_traveller(traveller_obj)
            if traveller_id:
                print(f"Successfully added traveller. New Traveller ID: {traveller_id}")
                return traveller_id
            else:
                print("Failed to add traveller.")
                return None
        except Exception as e:
            print(f"An error occurred in the service layer: {e}")
            return None

    print("Error: Permission denied.")
    return None


def search_travellers_by_name_or_id(traveller_query, current_user):
    if authorization.has_permission(current_user.role, 'search_travellers') is True:
        da.add_log_entry(current_user.username, "SEARCH_TRAVELLER", f"Searched for: '{traveller_query}'")
        return da.search_travellers_by_name_or_id(traveller_query)

    print("Error: Permission denied.")
    return []


def get_traveller_details(traveller_id, current_user):
    if authorization.has_permission(current_user.role, 'view_traveller_details') is True:
        da.add_log_entry(current_user.username, "VIEW_TRAVELLER", f"Viewed details for traveller ID: {traveller_id}")
        return da.get_traveller_by_id(traveller_id)

    print("Error: Permission denied.")
    return None


@audit_activity("UPDATE_TRAVELLER", "Updated traveller account details", "Failed to update traveller details")
def update_traveller_details(traveller_obj, current_user):
    if authorization.has_permission(current_user.role, 'update_traveller') is True:
        return da.update_traveller(traveller_obj)

    print("Error: Permission denied.")
    return False


@audit_activity("DELETE_TRAVELLER", "Deleted traveller account", "Failed to delete traveller account", suspicious_on_fail=True)
def delete_traveller_record(traveller_id, current_user):
    if authorization.has_permission(current_user.role, 'delete_traveller') is True:
        return da.delete_traveller_by_id(traveller_id)

    print("Error: Permission denied.")
    return False

@audit_activity("ADD_USER", "Created new Service Engineer: '{username}'", "Failed to create Service Engineer: '{username}'")
def add_new_service_engineer(username, password, first_name, last_name, current_user):
    if authorization.has_permission(current_user.role, 'add_service_engineer') is True:
        try:
            user_id = da.add_user(username, password, 'serviceengineer')
            if user_id:
                reg_date = datetime.now().isoformat()
                profile_created = da.add_user_profile(user_id, first_name, last_name, reg_date)
                if profile_created:
                    print(f"Successfully created Service Engineer '{username}'.")
                    return user_id
                else:
                    print("Error: User was created, but profile failed. Please contact support.")
                    da.add_log_entry(current_user.username, "ADD_USER_PROFILE_FAIL",
                                     f"User '{username}' created, but profile creation failed.", is_suspicious=1)
                    return None
            else:
                print("Failed to create Service Engineer.")
                return None
        except Exception as e:
            print(f"An error occurred while creating a service engineer: {e}")
            return None

    print("Error: Permission denied.")
    return None


@audit_activity("ADD_SYSTEM_ADMIN", "New System Administrator: {username}",
                "Failed to create System Administrator: {username}", suspicious_on_fail=True)
def add_new_system_admin(username, password, first_name, last_name, current_user):
    if authorization.has_permission(current_user.role, 'add_system_admin') is True:
        try:
            user_id = da.add_user(username, password, 'systemadmin')
            if user_id:
                reg_date = datetime.now().isoformat()
                profile_created = da.add_user_profile(user_id, first_name, last_name, reg_date)
                if profile_created:
                    print(f"Successfully created System Administrator '{username}'.")
                    return user_id
                else:
                    print("Error: User was created, but profile failed. Please contact support.")
                    da.add_log_entry(current_user.username, "ADD_USER_PROFILE_FAIL",
                                     f"System Admin User '{username}' created, but profile creation failed.",
                                     is_suspicious=1)
                    return None
            else:
                print("Failed to create System Administrator.")
                return None
        except Exception as e:
            print(f"An error occurred while creating a System Administrator: {e}")
            return None

    print("Error: Permission denied. Only a Super Administrator can perform this action.")
    da.add_log_entry(current_user.username, "ADD_SYSTEM_ADMIN_FAIL",
                     "Unauthorized attempt to create a System Admin.", is_suspicious=1)
    return None


def find_system_admins(query, current_user):
    if authorization.has_permission(current_user.role, 'search_system_admins') is True:
        all_admins = da.get_all_users_by_role('systemadmin')
        if not query:
            return all_admins

        query = query.lower()
        filtered_list = [
            admin for admin in all_admins
            if query in admin['username'].lower() or query in admin['name'].lower()
        ]
        return filtered_list

    print("Error: Permission denied.")
    return []


def find_service_engineers(query, current_user):
    if authorization.has_permission(current_user.role, 'search_service_engineers') is True:
        da.add_log_entry(current_user.username, "SEARCH_USER", f"Searched for Service Engineers with query: '{query}'")
        all_engineers = da.get_all_users_by_role('serviceengineer')
        if not query:
            return all_engineers

        query = query.lower()
        filtered_list = [
            eng for eng in all_engineers
            if query in eng['username'].lower() or query in eng['name'].lower()
        ]
        return filtered_list

    print("Error: Permission denied.")
    return []


def get_service_engineer_details(user_id, current_user):
    return da.get_user_profile_by_user_id(user_id)


def get_system_admin_details(user_id, current_user):
    return da.get_user_profile_by_user_id(user_id, add_username=True)


@audit_activity("UPDATE_OWN_PROFILE", "User updated their own profile", "User failed to update their own profile")
def update_own_profile(user_id, first_name, last_name, current_user):
    if authorization.has_permission(current_user.role, 'update_own_profile') is True:
        return da.update_user_profile(user_id, first_name, last_name)

    print("Error: Permission denied.")
    return False


@audit_activity("CHANGE_OWN_PASSWORD", "User changed their own password", "Password change failed", suspicious_on_fail=True)
def change_own_password(current_user, old_password, new_password):
    if authorization.has_permission(current_user.role, 'change_own_password') is True:
        user_data = da.find_user_by_username(current_user.username)
        if not user_data:
            return False, "User not found."

        _, hashed_password, _ = user_data


        if not security.check_password(old_password, hashed_password):
            return False, "Incorrect old password."

        new_hashed_password = security.hash_password(new_password)
        encrypted_hashed_password = security.encrypt_data(new_hashed_password.decode('utf-8'))
        success = da.update_user_password(current_user.user_id, encrypted_hashed_password)
        return success, "Password updated successfully." if success else "Failed to update password."

    print("Error: Permission denied.")
    return False, "Permission Denied"


@audit_activity("UPDATE_USER_PROFILE", "Successfully updated user profile", "Failed to update user profile")
def update_service_engineer_profile(profile_obj, current_user):
    if authorization.has_permission(current_user.role, 'update_service_engineer_profile') is True:
        return da.update_user_profile(profile_obj.user_id, profile_obj.first_name, profile_obj.last_name)

    print("Error: Permission denied.")
    return False


@audit_activity("UPDATE_SYSTEM_ADMIN_PROFILE", "Successfully updated system admin profile", "Failed to update system admin profile")
def update_system_admin_profile(profile_obj, current_user):
    if authorization.has_permission(current_user.role, 'update_system_admin_profile') is True:
        return da.update_user_profile(profile_obj.user_id, profile_obj.first_name, profile_obj.last_name)

    print("Error: Permission denied.")
    return False


@audit_activity("DELETE_USER", "Deactivated Service Engineer account", "Failed to deactivate Service Engineer account", suspicious_on_fail=True)
def delete_service_engineer(user_id, current_user):
    if authorization.has_permission(current_user.role, 'delete_service_engineer') is True:
        return da.delete_user_by_id(user_id)

    print("Error: Permission denied.")
    return False


@audit_activity("DELETE_SYSTEM_ADMIN", "Successfully deactivated system admin", "Failed to deactivate system admin", suspicious_on_fail=True)
def delete_system_admin(user_id, current_user):
    if authorization.has_permission(current_user.role, 'delete_system_admin') is True:
        return da.delete_user_by_id(user_id)

    print("Error: Permission denied.")
    return False


@audit_activity("PASSWORD_RESET", "Reset password for Service Engineer", "Failed to reset password for Service Engineer", suspicious_on_fail=True)
def reset_service_engineer_password(user_id, new_password, current_user):
    if authorization.has_permission(current_user.role, 'reset_service_engineer_password') is True:
        hashed_password = security.hash_password(new_password)
        encrypted_password = security.encrypt_data(hashed_password.decode('utf-8'))
        return da.update_user_password(user_id, encrypted_password)

    print("Error: Permission denied.")
    return False


@audit_activity("ADD_SCOOTER", "Added new scooter to fleet", "Failed to add new scooter")
def add_new_scooter(data, current_user):
    if authorization.has_permission(current_user.role, 'add_scooter') is True:
        try:
            scooter_obj = Scooter(**data)
            scooter_id = da.add_scooter(scooter_obj)
            if scooter_id:
                print(f"Successfully added scooter. New Scooter ID: {scooter_id}")
                return scooter_id
            else:
                print("Failed to add scooter.")
                return None
        except Exception as e:
            print(f"An error occurred in the service layer: {e}")
            return None

    print("Error: Permission denied.")
    return None


def search_scooters(query, current_user):
    if authorization.has_permission(current_user.role, 'search_scooters') is True:
        da.add_log_entry(current_user.username, "SEARCH_SCOOTER", f"Searched for scooters with query: '{query}'")
        return da.search_scooters(query)

    print("Error: Permission denied.")
    return []


def get_scooter_details(scooter_id, current_user):
    if authorization.has_permission(current_user.role, 'view_scooter_details') is True:
        da.add_log_entry(current_user.username, "VIEW_SCOOTER", f"Viewed details for scooter ID: {scooter_id}")
        return da.get_scooter_by_id(scooter_id)

    print("Error: Permission denied.")
    return None


@audit_activity("UPDATE_SCOOTER", "Successfully updated scooter", "Failed to update scooter")
def update_scooter_details(scooter_obj, current_user, is_limited=False):
    required_permission = 'update_scooter_limited' if is_limited else 'update_scooter_full'
    if authorization.has_permission(current_user.role, required_permission) is True:
        return da.update_scooter(scooter_obj)

    print("Error: Permission denied.")
    return False


@audit_activity("DELETE_SCOOTER", "Successfully deleted scooter", "Failed to delete scooter", suspicious_on_fail=True)
def delete_scooter_record(scooter_id, current_user):
    if authorization.has_permission(current_user.role, 'delete_scooter') is True:
        return da.delete_scooter_by_id(scooter_id)

    print("Error: Permission denied.")
    return False


def view_system_logs(current_user):
    if authorization.has_permission(current_user.role, 'view_system_logs') is True:
        da.add_log_entry(current_user.username, "VIEW_LOGS", "System logs were viewed.")
        logs = da.get_all_logs()
        da.mark_all_logs_as_read()
        return logs

    print("Error: Permission denied.")
    return []


def check_for_suspicious_activity(current_user):
    if authorization.has_permission(current_user.role, 'view_system_logs') is True:
        count = da.get_unread_suspicious_logs_count()
        if count > 0:
            return count

    return 0


@audit_activity("CREATE_BACKUP", "Backup created: {result}", "Backup creation failed.")
def create_backup(current_user):
    if authorization.has_permission(current_user.role, 'create_backup') is True:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        db_file = DATABASE_NAME
        if not os.path.exists(db_file):
            print(f"Error: Database file '{db_file}' not found.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = os.path.join(backup_dir, f"backup_{timestamp}.zip")

        try:
            with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(db_file, os.path.basename(db_file))
            print(f"Successfully created backup: {backup_filename}")
            return backup_filename
        except Exception as e:
            print(f"An error occurred during backup creation: {e}")
            return None

    print("Error: Permission denied.")
    return None


def list_backups(current_user):
    if authorization.has_permission(current_user.role, 'restore_backup') is True:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            return []

        backups = [f for f in os.listdir(backup_dir) if f.endswith('.zip') and f.startswith('backup_')]
        return sorted(backups, reverse=True)

    print("Error: Permission denied.")
    return []


@audit_activity("RESTORE_BACKUP", "Database restored from: {backup_file}", "Failed to restore database.",
                suspicious_on_fail=True)
def restore_from_backup(backup_file, current_user, restore_code_obj=None):
    if authorization.has_permission(current_user.role, 'restore_backup') is True:

        backup_dir = "backups"
        backup_path = os.path.join(backup_dir, backup_file)
        db_file = DATABASE_NAME

        if not os.path.exists(backup_path):
            return False, f"Backup file '{backup_path}' not found."

        temp_backup_db = db_file + ".temp_restore_bak"
        try:
            if os.path.exists(db_file):
                shutil.copy2(db_file, temp_backup_db)

            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extract(os.path.basename(db_file), path=".")

            if os.path.exists(temp_backup_db):
                os.remove(temp_backup_db)

            if restore_code_obj:
                da.update_restore_code_status(restore_code_obj.code_id, 'used')

            return True, f"Database successfully restored from {backup_file}."

        except Exception as e:
            if os.path.exists(temp_backup_db):
                shutil.move(temp_backup_db, db_file)
            return False, f"A critical error occurred during restore: {e}"

    return False, "Permission denied."


@audit_activity("GENERATE_RESTORE_CODE", "Generated restore code for System Admin ID: {system_admin_id}",
                "Failed to generate restore code.")
def generate_restore_code(system_admin_id, backup_filename, current_user):
    if authorization.has_permission(current_user.role, 'generate_restore_code') is True:
        code_value = secrets.token_hex(16)
        now = datetime.now()
        expires = now + timedelta(hours=24)

        code_obj = RestoreCode(
            code_id=None,
            restore_code=code_value,
            backup_filename=backup_filename,
            system_admin_id=system_admin_id,
            status='active',
            generated_at=now,
            expires_at=expires
        )

        if da.add_restore_code(code_obj):
            return code_value
        else:
            return None

    print("Error: Permission denied.")
    return None


@audit_activity("GET_RESTORE_CODES", "Got all restore codes for System Admin ID: {system_admin_id}",
                "Failed to get restore codes.")
def remove_restore_code(system_admin_id, current_user):
    if authorization.has_permission(current_user.role, 'generate_restore_code'):
        existing_codes = da.get_restore_codes_by_system_admin(system_admin_id)
        if not existing_codes:
            return "not_found"
        return da.delete_restore_codes_by_system_admin(system_admin_id)
    print("Error: Permission denied.")
    return False


@audit_activity("VALIDATE_RESTORE_CODE", "Restore code validated for user {current_user.username}",
                "Restore code validation failed for user {current_user.username}", suspicious_on_fail=True)
def validate_restore_code(restore_code_value, current_user):
    code_obj = da.get_restore_code(restore_code_value)
    if not code_obj:
        return None, "Invalid restore code."
    if code_obj.system_admin_id != current_user.user_id:
        return None, "This restore code is not assigned to you."
    if code_obj.status != 'active':
        return None, f"This restore code has already been '{code_obj.status}'."
    if datetime.now() > datetime.fromisoformat(code_obj.expires_at):
        da.update_restore_code_status(code_obj.code_id, 'expired')
        return None, "This restore code has expired."

    return code_obj, "Restore code is valid."


if __name__ == "__main__":
    print("This module is not meant to be run directly. Use the main application to access these services.")
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'birthday': '01-01-1990',
        'gender': 'male',
        'zip_code': '12345',
        'city': 'Test City',
        'street_name': 'Test Street',
        'house_number': '1A',
        'mobile_phone': '+31-6-12345678',
        'email_address': 'john.doe@example.com',
        'driving_license_number': 'TEST123456'
    }
    user = User(user_id='admin', username='admin', role='systemadmin')
    add_new_traveller(test_data, user)
