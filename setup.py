import database
import data_access
import sqlite3
from datetime import datetime


def create_super_admin_if_not_exists(data_access=None):
    print("Checking if super admin exists...")

    user_info = data_access.find_user_by_username("super_admin")

    if user_info:
        print("Super admin already exists.")
        return

    print("Creating super admin user...")
    user_id = data_access.add_user("super_admin", "Admin_123?", "SuperAdmin")
    if user_id:
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_created = data_access.add_user_profile(user_id, "Super", "Admin", registration_date)
        if profile_created:
            print("Super admin created successfully with the following credentials:")
            print("Username: super_admin")
            print("Password: Admin_123?")

    print("Creating easy login superadmin user...")
    user_id_easy = data_access.add_user("sa", "sa", "SuperAdmin")
    if user_id_easy:
        registration_date_easy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_created_easy = data_access.add_user_profile(user_id_easy, "Super", "Admin", registration_date_easy)
        if profile_created_easy:
            print("Easy login super admin created successfully with the following credentials:")
            print("Username: sa")
            print("Password: sa")

    print("Creating easy login sysadmin user...")
    user_id_sysadmin = data_access.add_user("sysad", "sysad", "SystemAdmin")
    if user_id_sysadmin:
        registration_date_sysadmin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_created_sysadmin = data_access.add_user_profile(user_id_sysadmin, "System", "Admin", registration_date_sysadmin)
        if profile_created_sysadmin:
            print("Easy login sys admin created successfully with the following credentials:")
            print("Username: sysad")
            print("Password: sysad")

    if user_id:
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_created = data_access.add_user_profile(user_id, "Super", "Admin", registration_date)

        if profile_created:
            print("Super admin created successfully with the following credentials:")
            print("Username: super_admin")
            print("Password: Admin_123?")
        else:
            print("Error: Super admin user was created, but profile creation failed.")
    else:
        print("Error: Failed to create super admin user.")

if __name__ == '__main__':
    print("Initializing database...")
    database.initialize_database()
    data_access = data_access.DataAccess()

    create_super_admin_if_not_exists(data_access)

    print("Setup completed.")
