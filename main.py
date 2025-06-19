import time
import data_access
import services
import ui_forms
from security import SecurityManager
from models import User
from ui_utils import display_header, get_input, get_password_input, clear_screen
from auditing import audit_activity


# --- Core Application Logic / Services ---

class AuthenticationService:
    """Handles the business logic for user authentication."""

    # Track failed login attempts by username
    failed_attempts = {}

    da = data_access.DataAccess()

    def __init__(self):
        self.security = SecurityManager()

    def _check_for_sql_injection(self, input_str):
        """Check for potential SQL injection patterns in input"""
        sql_patterns = [
            "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION", 
            "OR 1=1", "' OR '", "\" OR \"", "--", "/*", "*/", ";"
        ]

        for pattern in sql_patterns:
            if pattern.upper() in input_str.upper():
                return True
        return False

    def _check_for_null_bytes(self, input_str):
        """Check for null bytes in input string"""
        return '\0' in input_str

    def _track_failed_attempt(self, username):
        """Track failed login attempts for a username"""
        if username in self.failed_attempts:
            self.failed_attempts[username] += 1
        else:
            self.failed_attempts[username] = 1
        return self.failed_attempts[username]

    def _reset_failed_attempts(self, username):
        """Reset failed attempts counter after successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

    @audit_activity("LOGIN", "User '{username}' logged in successfully.",
                   "Failed login attempt for username: '{username}'.", suspicious_on_fail=True)
    def login(self, username, password):
        """
        Attempts to log a user in. The 'username' kwarg is used by the decorator.
        """
        # Check for SQL injection and null bytes
        if self._check_for_sql_injection(username) or self._check_for_sql_injection(password):
            print("Error: Invalid input detected.")
            self.da.add_log_entry(
                username=username,
                event_type="LOGIN_SECURITY_ALERT",
                description=f"Potential SQL injection attempt for username: '{username}'",
                is_suspicious=1
            )
            return None

        if self._check_for_null_bytes(username) or self._check_for_null_bytes(password):
            print("Error: Invalid input detected.")
            self.da.add_log_entry(
                username=username,
                event_type="LOGIN_SECURITY_ALERT",
                description=f"Null byte detected in login attempt for username: '{username}'",
                is_suspicious=1
            )
            return None

        user_data = self.da.find_user_by_username(username)
        if user_data:
            user_id, hashed_password, role = user_data
            if self.security.check_password(password, hashed_password):
                print("Login successful.")
                self._reset_failed_attempts(username)
                return User(user_id=user_id, username=username, role=role)

        # Track and handle failed login attempts
        attempts = self._track_failed_attempt(username)
        if attempts >= 3:
            self.da.add_log_entry(
                username=username,
                event_type="LOGIN_MULTIPLE_FAILURES",
                description=f"Multiple failed login attempts ({attempts}) for username: '{username}'",
                is_suspicious=1
            )

        print("Error: Invalid username or password.")
        return None


# --- The UI and Main Application Class ---

class ConsoleMenu:
    """A class to represent and manage a single console menu."""

    def __init__(self, title, subtitle="Please choose an option:"):
        self.title = title
        self.subtitle = subtitle
        self.menu_options = {}

    def add_option(self, key, description, function):
        """Adds a menu option."""
        self.menu_options[key.upper()] = {'desc': description, 'func': function}
        print(f"Added option [{key.upper()}]: {description}")

    def display(self):
        """Displays the menu, prompts for user selection, and handles menu flow."""
        while True:
            display_header(self.title)
            print(self.subtitle)
            print("-" * len(self.subtitle))
            for key, option in self.menu_options.items():
                print(f"  [{key}] {option['desc']}")
            print("-" * len(self.subtitle))

            choice = input("Your choice: ").strip().upper()
            if choice in self.menu_options:
                func = self.menu_options[choice]['func']
                if func is None:
                    return
                result = func()
                if result in ['EXIT_MENU', 'EXIT_APP']:
                    return result  # Pass the signal up the call stack
            else:
                print("Invalid option. Please try again.")
                time.sleep(1)


class UrbanMobilityApp:
    """The main application controller."""
    da = data_access.DataAccess()

    def __init__(self):
        self.current_user = None
        self.is_running = True
        self.auth_service = AuthenticationService()

    def main_menu(self):
        """Displays the main menu based on the user's role."""
        if not self.current_user:
            self.show_login_screen()
            return

        menu_title = f"{self.current_user.role} Menu (User: {self.current_user.username})"
        main_menu = ConsoleMenu(menu_title)
        result = None
        match self.current_user.role:
            case 'superadmin' | 'SuperAdmin':
                main_menu.add_option('1', "Manage System Administrator Accounts", self.system_admin_management_menu)
                main_menu.add_option('2', "View System Logs", lambda: ui_forms.ui_view_system_logs(self.current_user))
                main_menu.add_option('3', "Manage Backups", self.backup_management_menu)
                main_menu.add_option('4', "Manage Traveller Accounts", self.traveller_management_menu)
                main_menu.add_option('5', "Manage Service Engineer Accounts", self.service_engineer_management_menu)
                main_menu.add_option('6', "Manage Scooter Fleet", self.scooter_management_menu)
            case 'systemadmin' | 'SystemAdmin':
                main_menu.add_option('1', "Manage Traveller Accounts", self.traveller_management_menu)
                main_menu.add_option('2', "Manage Service Engineer Accounts", self.service_engineer_management_menu)
                main_menu.add_option('3', "Manage Scooter Fleet", self.scooter_management_menu)
                main_menu.add_option('4', "View System Logs", lambda: ui_forms.ui_view_system_logs(self.current_user))
                main_menu.add_option('5', "Manage Backups", self.backup_management_menu)
            case 'serviceengineer' | 'ServiceEngineer':
                main_menu.add_option('1', "Update Scooter Status", self.scooter_update_menu_limited)
                main_menu.add_option('2', "Manage My Account", self.account_management_menu)
        main_menu.add_option('L', "Logout", self.logout)
        main_menu.add_option('Q', "Quit Application", self.quit)
        result = main_menu.display()

        if result == 'EXIT_APP':
            self.quit()

    def show_login_screen(self):
        """Handles the user login process."""
        display_header("Login")
        username = get_input("Username")
        password = get_password_input("Password")

        user = self.auth_service.login(username=username, password=password)
        if user:
            self.current_user = user

            if user.role in ['systemadmin', 'superadmin']:
                suspicious_count = services.check_for_suspicious_activity(user)
                if suspicious_count > 0:
                    print("\n" + "!" * 60)
                    print(f"!!  WARNING: {suspicious_count} new suspicious activity alert(s) recorded. !!")
                    print("!!  Please review the system logs for details.          !!")
                    print("!" * 60)
                    input("\nPress Enter to continue to the main menu...")

            time.sleep(1.5)
        else:
            time.sleep(1.5)

    def logout(self):
        """Logs the current user out and returns a signal to exit the current menu."""
        if self.current_user:
            self.da.add_log_entry(self.current_user.username, "LOGOUT", "User logged out.")
            print(f"Logging out {self.current_user.username}...")
            self.current_user = None
            time.sleep(1)
        print("You have been successfully logged out.")
        time.sleep(1.5)
        return 'EXIT_MENU'

    def quit(self):
        """Sets the application to stop running and returns a signal to exit the current menu."""
        print("Shutting down the system. Goodbye!")
        self.is_running = False
        self.current_user = None
        return 'EXIT_MENU'

    def run(self):
        """The main loop of the application."""
        while self.is_running:
            if self.current_user:
                self.main_menu()
            else:
                if self.is_running:
                    self.show_login_screen()

    # --- Management Sub-Menus ---
    def system_admin_management_menu(self):
        menu = ConsoleMenu("System Administrator Management")
        menu.add_option('1', "Add New System Administrator", lambda: ui_forms.ui_add_system_admin(self.current_user))
        menu.add_option('2', "Search & View System Administrator", lambda: ui_forms.ui_search_system_admins(self.current_user))
        menu.add_option('3', "Update System Administrator Profile", lambda: ui_forms.ui_update_system_admin(self.current_user))
        menu.add_option('4', "Delete System Administrator", lambda: ui_forms.ui_delete_system_admin(self.current_user))
        menu.add_option('B', "Back to Main Menu", None)
        menu.display()

    def traveller_management_menu(self):
        menu = ConsoleMenu("Traveller Management")
        menu.add_option('1', "Add New Traveller", lambda: ui_forms.ui_add_traveller(self.current_user))
        menu.add_option('2', "Search & View Traveller", lambda: ui_forms.ui_search_travellers(self.current_user))
        menu.add_option('3', "Update Traveller Record", lambda: ui_forms.ui_update_traveller(self.current_user))
        menu.add_option('4', "Delete Traveller Record", lambda: ui_forms.ui_delete_traveller(self.current_user))
        menu.add_option('B', "Back to Main Menu", None)
        menu.display()

    def service_engineer_management_menu(self):
        menu = ConsoleMenu("Service Engineer Management")
        menu.add_option('1', "Add New Service Engineer", lambda: ui_forms.ui_add_service_engineer(self.current_user))
        menu.add_option('2', "Update Service Engineer Profile",
                        lambda: ui_forms.ui_update_service_engineer(self.current_user))
        menu.add_option('3', "Delete Service Engineer", lambda: ui_forms.ui_delete_service_engineer(self.current_user))
        menu.add_option('4', "Reset Service Engineer Password",
                        lambda: ui_forms.ui_reset_service_engineer_password(self.current_user))
        menu.add_option('B', "Back to Main Menu", None)
        menu.display()

    def scooter_management_menu(self):
        menu = ConsoleMenu("Scooter Fleet Management")
        menu.add_option('1', "Add New Scooter", lambda: ui_forms.ui_add_scooter(self.current_user))
        menu.add_option('2', "Search & View Scooter", lambda: ui_forms.ui_search_scooters(self.current_user))
        menu.add_option('3', "Update Scooter Record", lambda: ui_forms.ui_update_scooter(self.current_user))
        menu.add_option('4', "Delete Scooter Record", lambda: ui_forms.ui_delete_scooter(self.current_user))
        menu.add_option('B', "Back to Main Menu", None)
        menu.display()

    def backup_management_menu(self):
        menu = ConsoleMenu("Backup Management")
        if self.current_user.role == 'superadmin':
            menu.add_option('1', "Create Database Backup", lambda: ui_forms.ui_create_backup(self.current_user))
            menu.add_option('2', "Restore from Backup (Direct)",
                            lambda: ui_forms.ui_restore_from_backup(self.current_user))
            menu.add_option('3', "Generate Restore Code for System Admin",
                            lambda: ui_forms.ui_generate_restore_code(self.current_user))
            menu.add_option('4', "Remove Restore Code from System Admin",
                            lambda: ui_forms.ui_remove_restore_code(self.current_user))
        elif self.current_user.role == 'systemadmin':
            menu.add_option('1', "Create Database Backup", lambda: ui_forms.ui_create_backup(self.current_user))
            menu.add_option('2', "Restore from Backup (with Code)",
                            lambda: ui_forms.ui_restore_from_backup(self.current_user))

        menu.add_option('B', "Back to Main Menu", None)

        result = menu.display()
        if result == 'EXIT_APP':
            # This is a special signal from the restore function to force a shutdown.
            self.quit()

    def account_management_menu(self):
        menu = ConsoleMenu("My Account")
        menu.add_option('1', "Update My Profile", lambda: ui_forms.ui_update_own_profile(self.current_user))
        menu.add_option('2', "Change My Password", lambda: ui_forms.ui_change_own_password(self.current_user))
        menu.add_option('B', "Back to Main Menu", None)
        menu.display()

    def scooter_update_menu_limited(self):
        ui_forms.ui_update_scooter(self.current_user, limited=True)


# --- Entry Point ---
if __name__ == "__main__":
    import database

    database.initialize_database()

    app = UrbanMobilityApp()
    app.run()
