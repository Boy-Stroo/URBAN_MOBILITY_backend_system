import data_access
import database
from datetime import datetime
import services  # Import services to use the audited function


def setup_initial_accounts():
    """
    A one-time script to create the initial SuperAdmin account.
    This should be run only once when setting up the system for the first time.
    """
    print("--- Urban Mobility System Initial Setup ---")

    # 1. Initialize the database to ensure all tables exist
    print("\n[Step 1/2] Initializing database...")
    database.initialize_database()
    print("Database initialization complete.")

    # 2. Check if a SuperAdmin already exists
    print("\n[Step 2/2] Checking for existing Super Administrators...")

    # We use a dummy User object because the service layer expects one for auditing.
    # The username '(setup_script)' will appear in the logs.
    setup_user = services.User(user_id=0, username='(setup_script)', role='System')

    existing_user = data_access.find_user_by_username("super_admin")
    if existing_user:
        print("\n!! A 'super_admin' user already exists in the database. !!")
        print("Setup aborted.")
        return

    # 3. Create the Super Administrator account
    print("\nCreating the initial Super Administrator account...")
    print("Username: super_admin")
    print("Password: Admin_123?")

    # Use the audited service function to create the user
    user_id = services.add_new_super_admin(
        username="super_admin",
        password="Admin_123?",
        first_name="Default",
        last_name="SuperAdmin",
        current_user=setup_user  # Pass the dummy user for logging
    )

    if user_id:
        print("\n--- Success! ---")
        print("Initial Super Administrator 'superadmin' has been created successfully.")
        print("You can now run the main application using 'python app.py'.")
    else:
        print("\n--- Error! ---")
        print("Failed to create the Super Administrator user.")
        print("Please check the logs or database file for errors.")


if __name__ == "__main__":
    setup_initial_accounts()
