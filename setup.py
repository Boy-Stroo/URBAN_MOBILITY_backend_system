import database
import data_access
import sqlite3
from datetime import datetime


def create_super_admin_if_not_exists(data_access=None):
    """
    Creates a super admin user with the specified credentials if it doesn't exist.

    Credentials:
    - username: super_admin
    - password: Admin_123?
    """
    print("Checking if super admin exists...")

    # Check if super_admin already exists
    user_info = data_access.find_user_by_username("super_admin")

    if user_info:
        print("Super admin already exists.")
        return

    # Create super admin user
    print("Creating super admin user...")
    user_id = data_access.add_user("super_admin", "Admin_123?", "SuperAdmin")

    # TODO: Remove this
    print("Creating easy login superadmin user...")
    user_id_easy = data_access.add_user("sa", "sa", "SuperAdmin")

    # TODO: Remove this
    print("Creating easy login sysadmin user...")
    user_id_sysadmin = data_access.add_user("sysad", "sysad", "SystemAdmin")

    if user_id:
        # Add user profile for super admin
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
    # Initialize the database
    print("Initializing database...")
    database.initialize_database()
    data_access = data_access.DataAccess()

    # Create super admin if it doesn't exist
    create_super_admin_if_not_exists(data_access)

    print("Setup completed.")