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
