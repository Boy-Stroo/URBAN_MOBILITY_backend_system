from tabulate import tabulate
import time
from datetime import datetime, timedelta

# --- Centralized Table Styles ---
# We can define different styles here and reuse them across the application.
# Common tablefmt options: 'grid', 'fancy_grid', 'pipe', 'orgtbl', 'rst', 'psql', 'simple', 'html'
TABLE_STYLES = {
    "default": "grid",
    "compact": "pipe",
    "detailed": "fancy_grid"
}


def display_system_logs_paginated(logs):
    """
    Displays system logs in a paginated, tabulated format.

    :param logs: A list of log entry dictionaries.
    """
    if not logs:
        print("No logs found.")
        input("\nPress Enter to return...")
        return

    page_size = 10
    page = 0
    total_pages = (len(logs) - 1) // page_size + 1

    while True:
        from ui_utils import display_header, get_input  # Local import to avoid circular dependency
        display_header(f"System Logs (Page {page + 1}/{total_pages})")

        start_index = page * page_size
        end_index = start_index + page_size

        page_logs = logs[start_index:end_index]

        # Prepare data for tabulate
        headers = ["Time", "User", "Event", "Description", "Details", "Suspicious"]
        table_data = []
        for log in page_logs:
            suspicious_flag = "[!]" if log['is_suspicious'] else ""
            table_data.append([
                log['timestamp'],
                log['username'],
                log['event_type'],
                log['description'],
                log['additional_info'] or "N/A",
                suspicious_flag
            ])

        print(tabulate(table_data, headers=headers, tablefmt=TABLE_STYLES["detailed"]))

        print("\n[N] Next Page | [P] Previous Page | [Q] Quit to Menu")
        choice = get_input("Your choice").upper()

        if choice == 'N':
            if page < total_pages - 1:
                page += 1
            else:
                print("Already on the last page.")
                time.sleep(1)
        elif choice == 'P':
            if page > 0:
                page -= 1
            else:
                print("Already on the first page.")
                time.sleep(1)
        elif choice == 'Q':
            break
        else:
            print("Invalid option.")
            time.sleep(1)


# --- Main block for testing display functions ---
if __name__ == '__main__':
    # This block will only run when you execute `python display.py` directly.
    # It's useful for testing the look and feel of tables.

    print("--- Testing Display Module ---")

    # 1. Create some fake log data
    now = datetime.now()
    fake_logs = [
        {
            'timestamp': (now - timedelta(minutes=15)).isoformat(sep=' ', timespec='seconds'),
            'username': 'sysadmin1',
            'event_type': 'LOGIN_SUCCESS',
            'description': 'User logged in successfully.',
            'additional_info': 'Source IP: 192.168.1.100',
            'is_suspicious': 0
        },
        {
            'timestamp': (now - timedelta(minutes=10)).isoformat(sep=' ', timespec='seconds'),
            'username': 'service_eng',
            'event_type': 'UPDATE_SCOOTER',
            'description': 'Updated scooter status.',
            'additional_info': 'Scooter ID: 102, SoC: 85%',
            'is_suspicious': 0
        },
        {
            'timestamp': (now - timedelta(minutes=5)).isoformat(sep=' ', timespec='seconds'),
            'username': '(anonymous)',
            'event_type': 'LOGIN_FAILURE',
            'description': 'Failed login attempt.',
            'additional_info': 'Attempt for user: admin',
            'is_suspicious': 1
        },
        {
            'timestamp': (now - timedelta(minutes=2)).isoformat(sep=' ', timespec='seconds'),
            'username': 'sysadmin1',
            'event_type': 'ADD_TRAVELLER',
            'description': 'New traveller added.',
            'additional_info': 'Traveller ID: 5821',
            'is_suspicious': 0
        },
    ]

    # 2. Demonstrate the centralized table styles
    print("\n--- Demonstrating Different Table Styles ---")

    headers = ["Timestamp", "Username", "Event", "Description", "Suspicious"]
    table_data = [[log['timestamp'], log['username'], log['event_type'], log['description'],
                   "[!]" if log['is_suspicious'] else ""] for log in fake_logs]

    for style_name, table_format in TABLE_STYLES.items():
        print(f"\n--- Style: '{style_name}' (tablefmt='{table_format}') ---")
        print(tabulate(table_data, headers=headers, tablefmt=table_format))

    print("\n--- Log Pagination Test (run with more data to see pages) ---")
    # To test pagination, you can generate more fake data:
    # fake_logs.extend([fake_logs[0]] * 10)
    display_system_logs_paginated(fake_logs)

    print("\n--- End of Test ---")

