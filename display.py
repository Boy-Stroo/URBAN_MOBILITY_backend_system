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

def display_search_results_table(items, display_key):
    """
    Displays a list of items in a table format and returns the selected item.

    :param items: List of dictionaries containing the items to display
    :param display_key: The key in each item dictionary that contains the display text
    :param headers: Optional list of column headers
    :return: The selected item or None if cancelled
    """
    print("Displaying search results")
    for index, item in enumerate(items):
        display_text = item.get(display_key, "N/A")
        print(f"    [{index + 1}] {display_text}")
    print("    [0] Cancel")

    choice = input("Select an item by number: ").strip()
    if choice.isdigit():
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(items):
            return items[choice_index]
        elif choice_index == -1:
            return None





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

        # print(tabulate(table_data, headers=headers, tablefmt=TABLE_STYLES["detailed"]))

        # Without tabulate for simplicity in this example
        print("=" * 174)
        print(f"| {'Time':<30} | {'User':<15} | {'Event':<20} | {'Description':<50} | {'Details':<30} | {'Suspicious':<10} |")
        print("=" * 174)
        for row in table_data:
            # for row 5 split the margin between in front and after the text
            print(f"| {row[0]:<30} | {row[1]:<15} | {row[2]:<20} | {row[3]:<50} | {row[4]:<30} | {row[5]:^10} |")


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

    # Example data for testing
    example_items = [
        {"id": 1, "name": "Item One", "value": 100},
        {"id": 2, "name": "Item Two", "value": 200},
        {"id": 3, "name": "Item Three", "value": 300}
    ]
    example_headers = ["id", "name", "value"]
    selected_item = display_search_results_table(example_items, "name", example_headers)
    if selected_item:
        print(f"Selected Item: {selected_item}")
    else:
        print("No item selected.")
    # Example logs for testing pagination
    example_logs = [
        {
            "timestamp": datetime.now() - timedelta(days=i),
            "username": f"user{i}",
            "event_type": "Event Type",
            "description": f"Description of event {i}",
            "additional_info": f"Details for event {i}",
            "is_suspicious": i % 2 == 0  # Even indexed logs are suspicious
        } for i in range(25)  # Create 25 log entries for testing
    ]
    display_system_logs_paginated(example_logs)
    print("--- End of Display Module Test ---")
    input("\nPress Enter to exit...")
