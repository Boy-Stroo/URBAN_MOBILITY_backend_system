import time
from datetime import datetime, timedelta

def display_search_results_table(items, display_key):
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
    if not logs:
        print("No logs found.")
        input("\nPress Enter to return...")
        return

    page_size = 10
    page = 0
    total_pages = (len(logs) - 1) // page_size + 1

    while True:
        # Import moved inside to avoid circular dependency issues
        from ui_utils import display_header, get_input
        display_header(f"System Logs (Page {page + 1}/{total_pages})")

        start_index = page * page_size
        end_index = start_index + page_size
        page_logs = logs[start_index:end_index]

        # Define headers and column widths
        headers = ["Time", "User", "Event", "Description", "Details", "Suspicious"]
        widths = {'Time': 26, 'User': 15, 'Event': 28, 'Description': 55, 'Details': 60, 'Suspicious': 10}
        total_width = sum(widths.values()) + len(widths) * 3 + 1

        # --- Print Table Header ---
        print("=" * total_width)
        header_line = "| "
        for h in headers:
            header_line += f"{h:<{widths[h]}} | "
        print(header_line)
        print("=" * total_width)

        # --- Print Table Rows ---
        for log in page_logs:
            suspicious_flag = "[!]" if log.get('is_suspicious') else ""

            # Format timestamp to be shorter and cleaner
            try:
                ts = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                ts = log.get('timestamp', 'N/A')

            # Truncate long values to fit in columns
            def truncate(text, length):
                if text is None:
                    return "N/A"
                text = str(text)
                return (text[:length - 3] + '...') if len(text) > length else text

            row_data = {
                'Time': ts,
                'User': truncate(log.get('username'), widths['User']),
                'Event': truncate(log.get('event_type'), widths['Event']),
                'Description': truncate(log.get('description'), widths['Description']),
                'Details': truncate(log.get('additional_info'), widths['Details']),
                'Suspicious': suspicious_flag
            }

            row_line = "| "
            for h in headers:
                align = "^" if h == 'Suspicious' else "<"
                row_line += f"{row_data[h]:{align}{widths[h]}} | "
            print(row_line)
        print("-" * total_width)

        # --- Pagination Controls ---
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

if __name__ == '__main__':

    print("--- Testing Display Module ---")

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
    example_logs = [
        {
            "timestamp": datetime.now() - timedelta(days=i),
            "username": f"user{i}",
            "event_type": "Event Type",
            "description": f"Description of event {i}",
            "additional_info": f"Details for event {i}",
            "is_suspicious": i % 2 == 0
        } for i in range(25)
    ]
    display_system_logs_paginated(example_logs)
    print("--- End of Display Module Test ---")
    input("\nPress Enter to exit...")
