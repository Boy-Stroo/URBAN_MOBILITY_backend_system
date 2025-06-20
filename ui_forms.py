import sys

import services
import validators
from ui_utils import display_header, get_validated_input, get_input, get_password_input
import time
from datetime import datetime
import display
import data_access


def select_from_list(prompt, item_list, display_key):
    if not item_list:
        print("No items found.")
        return None


    print(f"\n{prompt}")
    for idx, item in enumerate(item_list):
        print(f"  [{idx + 1}] {item[display_key]}")

    while True:
        try:
            choice = get_input("Enter the number of your choice (or 0 to cancel)")
            choice_idx = int(choice)
            if choice_idx == 0:
                return None
            if 1 <= choice_idx <= len(item_list):
                return item_list[choice_idx - 1]
            else:
                print("Invalid number. Please try again.")
        except (ValueError, TypeError):
            print("Invalid input. Please enter a number.")


def _search_and_select_item(search_prompt, search_function, current_user, result_formatter, selection_prompt,
                            no_results_message):
    query = get_input(search_prompt)
    results = search_function(query, current_user)

    if not results:
        print(no_results_message.format(query=query))
        input("\nPress Enter to return...")
        return None

    display_list = [result_formatter(r) for r in results]

    import display
    selected = display.display_search_results_table(display_list, 'display')

    return selected


def ui_add_traveller(user):
    display_header("Add New Traveller")
    first_name = get_validated_input("First Name", validators.is_valid_name)
    last_name = get_validated_input("Last Name", validators.is_valid_name)
    birthday = get_validated_input("Birthday (YYYY-MM-DD)", validators.is_valid_birth_date)
    gender = get_validated_input("Gender (male/female)", validators.is_valid_gender)
    street_name = get_validated_input("Street Name", validators.is_valid_address_field)
    house_number = get_validated_input("House Number", validators.is_valid_house_number)
    zip_code = get_validated_input("Zip Code (e.g., 1234AB)", validators.is_valid_zip_code)
    city = get_validated_input("City", validators.is_valid_city)
    email_address = get_validated_input("Email Address", validators.is_valid_email)
    mobile_phone = get_validated_input("Mobile Phone (+31-6-XXXXXXXX)", validators.is_valid_mobile_phone,
                                       pre_prompt='+31-6-')
    driving_license_number = get_validated_input("Driving License", validators.is_valid_driving_license)
    traveller_data = {'first_name': first_name, 'last_name': last_name, 'birthday': birthday, 'gender': gender,
                      'street_name': street_name, 'house_number': house_number, 'zip_code': zip_code, 'city': city,
                      'email_address': email_address, 'mobile_phone': mobile_phone,
                      'driving_license_number': driving_license_number}
    print("\nAdding traveller to the system...")
    services.add_new_traveller(traveller_data, user)
    input("\nPress Enter to return to the menu...")


def ui_search_travellers(user):
    """UI flow for searching travellers and viewing details."""
    display_header("Search for Traveller")

    selected = _search_and_select_item(
        search_prompt="Enter a first name, surname or ID to search for",
        search_function=services.search_travellers_by_name_or_id,
        current_user=user,
        result_formatter=lambda r: {
            'display': f"{r['first_name']} {r['last_name']} (License: {r['driving_license_number']})",
            'id': r['customer_id']},
        selection_prompt="Select a traveller to view details:",
        no_results_message="\nNo travellers found matching '{query}'."
    )
    print("\nTraveller Search Results:")
    if selected:
        traveller_obj = services.get_traveller_details(selected['id'], user)
        if traveller_obj:
            display_header(f"Details for {traveller_obj.first_name} {traveller_obj.last_name}")
            print(f"  Customer ID: {traveller_obj.customer_id}")
            print(f"  Birthday: {traveller_obj.birthday}")
            print(f"  Gender: {traveller_obj.gender}")
            print(
                f"  Address: {traveller_obj.street_name} {traveller_obj.house_number}, {traveller_obj.zip_code} {traveller_obj.city}")
            print(f"  Email: {traveller_obj.email_address}")
            print(f"  Phone: {traveller_obj.mobile_phone}")
            print(f"  License #: {traveller_obj.driving_license_number}")
            print(f"  Registered: {traveller_obj.registration_date}")
            input("\nPress Enter to return to the menu...")


def ui_update_traveller(user):
    display_header("Update Traveller Record")

    selected = _search_and_select_item(
        search_prompt="Enter a name to search for the traveller to update",
        search_function=services.search_travellers_by_name_or_id,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['first_name']} {r['last_name']}", 'id': r['customer_id']},
        selection_prompt="Select a traveller to update:",
        no_results_message="\nNo travellers found matching '{query}'."
    )

    if not selected:
        return

    traveller_obj = services.get_traveller_details(selected['id'], user)
    if not traveller_obj:
        print("Could not retrieve traveller details.")
        input("\nPress Enter to return...")
        return

    while True:
        display_header(f"Updating: {traveller_obj.first_name} {traveller_obj.last_name}")

        update_menu = {
            "1": {"prompt": "First Name", "attr": "first_name", "value": traveller_obj.first_name,
                  "validator": validators.is_valid_name},
            "2": {"prompt": "Last Name", "attr": "last_name", "value": traveller_obj.last_name,
                  "validator": validators.is_valid_name},
            "3": {"prompt": "Birthday", "attr": "birthday", "value": traveller_obj.birthday,
                  "validator": validators.is_valid_birth_date},
            "4": {"prompt": "Gender (male/female)", "attr": "gender", "value": traveller_obj.gender, "validator": validators.is_valid_gender},
            "5": {"prompt": "Street Name", "attr": "street_name", "value": traveller_obj.street_name,
                  "validator": validators.is_valid_address_field},
            "6": {"prompt": "House Number", "attr": "house_number", "value": traveller_obj.house_number,
                  "validator": validators.is_valid_house_number},
            "7": {"prompt": "Zip Code", "attr": "zip_code", "value": traveller_obj.zip_code,
                  "validator": validators.is_valid_zip_code},
            "8": {"prompt": "City", "attr": "city", "value": traveller_obj.city, "validator": validators.is_valid_city},
            "9": {"prompt": "Email Address", "attr": "email_address", "value": traveller_obj.email_address,
                  "validator": validators.is_valid_email},
            "10": {"prompt": "Mobile Phone", "attr": "mobile_phone", "value": traveller_obj.mobile_phone,
                   "validator": validators.is_valid_mobile_phone},
            "11": {"prompt": "Driving License", "attr": "driving_license_number",
                   "value": traveller_obj.driving_license_number, "validator": validators.is_valid_driving_license},
        }

        for key, item in update_menu.items():
            print(f"  [{key}] {item['prompt']}: {item['value']}")

        print("-" * 40)
        print("Enter the number of the field to update. 'S' to Save, 'C' to Cancel.")
        choice = get_input("\nYour choice").upper()

        if choice == 'S':
            print("\nSaving changes...")
            if services.update_traveller_details(traveller_obj, user):
                print("Update successful.")
            else:
                print("Update failed.")
            input("\nPress Enter to return...")
            break
        elif choice == 'C':
            print("Update cancelled. No changes were saved.")
            input("\nPress Enter to return...")
            break
        elif choice in update_menu:
            field = update_menu[choice]
            prompt_text = f"New {field['prompt']}"
            if field['validator']:
                new_val = get_validated_input(prompt_text, field['validator'])
            else:
                new_val = get_input(prompt_text, required=False)
            setattr(traveller_obj, field['attr'], new_val)
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)


def ui_delete_traveller(user):
    display_header("Delete Traveller Record")

    selected = _search_and_select_item(
        search_prompt="Enter a name to search for the traveller to delete",
        search_function=services.search_travellers_by_name_or_id,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['first_name']} {r['last_name']}", 'id': r['customer_id']},
        selection_prompt="Select a traveller to DELETE:",
        no_results_message="\nNo travellers found matching '{query}'."
    )

    if not selected:
        return

    print("\n!! WARNING: This action is permanent and cannot be undone. !!")
    confirm = get_input(f"Type 'DELETE' to permanently remove traveller ID {selected['id']}: ")
    if confirm == 'DELETE':
        if services.delete_traveller_record(selected['id'], user):
            print("Traveller record has been deleted.")
        else:
            print("Failed to delete traveller record.")
    else:
        print("Deletion cancelled.")
    input("\nPress Enter to return...")

# --- User Management Forms (for any logged-in user) ---

def ui_update_own_profile(user):
    """UI flow for a user to update their own profile."""
    display_header("Update My Profile")
    profile_obj = services.get_service_engineer_details(user.user_id, user)
    if not profile_obj:
        print("Could not retrieve your profile.")
        input("\nPress Enter...")
        return

    print("Enter new information. Press Enter to keep current value.")
    new_first_name = get_validated_input(f"First Name [{profile_obj.first_name}]", validators.is_valid_name,
                                         required=False) or profile_obj.first_name
    new_last_name = get_validated_input(f"Last Name [{profile_obj.last_name}]", validators.is_valid_name,
                                        required=False) or profile_obj.last_name

    if services.update_own_profile(user.user_id, new_first_name, new_last_name, user):
        print("\nProfile updated successfully.")
    else:
        print("\nFailed to update profile.")
    input("Press Enter to return...")


def ui_change_own_password(user):
    """UI flow for a user to change their own password."""
    display_header("Change My Password")
    old_password = get_password_input("Enter your CURRENT password")
    if not old_password:
        print("\nOperation cancelled.")
        input("Press Enter...")
        return

    new_password = get_validated_input("Enter your NEW password", validators.is_valid_password, is_password=True)
    confirm_password = get_password_input("Confirm your NEW password")

    if new_password != confirm_password:
        print("\nNew passwords do not match. Operation cancelled.")
        input("Press Enter...")
        return

    success, message = services.change_own_password(current_user=user, old_password=old_password,
                                                    new_password=new_password)
    print(f"\n{message}")
    input("Press Enter to return...")

# --- Admin Forms for User Management ---

def ui_add_system_admin(user):
    """UI flow for a SuperAdmin to add a new System Administrator."""
    display_header("Add New System Administrator")
    username = get_validated_input("Enter username for new System Admin", validators.is_valid_username)
    password = get_validated_input("Enter temporary password", validators.is_valid_password, is_password=True)
    first_name = get_validated_input("First Name", validators.is_valid_name)
    last_name = get_validated_input("Last Name", validators.is_valid_name)
    print("\nCreating System Administrator account...")
    services.add_new_system_admin(username, password, first_name, last_name, user)
    input("\nPress Enter to return to the menu...")

def ui_search_system_admins(user):
    """UI flow for searching System Administrators and viewing details."""
    display_header("Search for System Administrator")

    selected = _search_and_select_item(
        search_prompt="Enter username or name to search for",
        search_function=services.find_system_admins,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a System Administrator to view details:",
        no_results_message="\nNo System Administrators found matching '{query}'."
    )

    if selected:
        admin_obj, username = services.get_system_admin_details(selected['id'], user)
        if admin_obj:
            display_header(f"Details for {admin_obj.first_name} {admin_obj.last_name}")
            print(f"  Username: {username}")
            print(f"  Registered on: {admin_obj.registration_date}")
    input("\nPress Enter to return...")

def ui_update_system_admin(user):
    """UI flow for finding and updating a System Administrator."""
    display_header("Update System Administrator Profile")

    selected = _search_and_select_item(
        search_prompt="Enter username or name of admin to search for",
        search_function=services.find_system_admins,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a System Administrator to UPDATE:",
        no_results_message="\nNo System Administrators found matching '{query}'."
    )

    if not selected:
        return

    profile_obj, username = services.get_system_admin_details(selected['id'], user)
    if not profile_obj:
        print("Could not retrieve profile details.")
        input("\nPress Enter to return...")
        return

    while True:
        display_header(f"Updating: {profile_obj.first_name} {profile_obj.last_name}")
        print("Current Profile Details:")
        print(f"  [1] First Name: {profile_obj.first_name}")
        print(f"  [2] Last Name: {profile_obj.last_name}")
        print("-" * 30)
        print("Enter the number of the field to update. 'S' to Save, 'C' to Cancel.")
        choice = get_input("\nYour choice").upper()

        if choice == 'S':
            print("\nSaving changes...")
            if services.update_system_admin_profile(profile_obj, user):
                print("Update successful.")
            else:
                print("Update failed.")
            input("\nPress Enter to return...")
            break
        elif choice == 'C':
            print("Update cancelled. No changes were saved.")
            input("\nPress Enter to return...")
            break
        elif choice == '1':
            new_val = get_validated_input(f"New First Name [{profile_obj.first_name}]", validators.is_valid_name,
                                          required=False)
            if new_val:
                profile_obj.first_name = new_val
        elif choice == '2':
            new_val = get_validated_input(f"New Last Name [{profile_obj.last_name}]", validators.is_valid_name,
                                          required=False)
            if new_val:
                profile_obj.last_name = new_val
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

def ui_add_service_engineer(user):
    """UI flow for adding a new Service Engineer."""
    display_header("Add New Service Engineer")
    username = get_validated_input("Enter username", validators.is_valid_username)
    password = get_validated_input("Enter password", validators.is_valid_password, is_password=True)
    first_name = get_validated_input("First Name", validators.is_valid_name)
    last_name = get_validated_input("Last Name", validators.is_valid_name)
    print("\nCreating Service Engineer account...")
    services.add_new_service_engineer(username, password, first_name, last_name, user)
    input("\nPress Enter to return to the menu...")

def ui_search_service_engineers(user):
    """UI flow for searching Service Engineers and viewing details."""
    display_header("Search for Service Engineer")

    selected = _search_and_select_item(
        search_prompt="Enter username or name to search for",
        search_function=services.find_service_engineers,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a Service Engineer to view details:",
        no_results_message="\nNo engineers found matching '{query}'."
    )

    if selected:
        profile_obj, username = services.get_service_engineer_details(selected['id'], user)
        if profile_obj:
            display_header(f"Details for {profile_obj.first_name} {profile_obj.last_name}")
            print(f"  Username: {username}")
            print(f"  Registered on: {profile_obj.registration_date}")
    input("\nPress Enter to return...")


def ui_update_service_engineer(user):
    """UI flow for finding and updating a Service Engineer."""
    display_header("Update Service Engineer Profile")

    selected = _search_and_select_item(
        search_prompt="Enter username or name of engineer to search for",
        search_function=services.find_service_engineers,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select an engineer to UPDATE:",
        no_results_message="\nNo engineers found matching '{query}'."
    )

    if not selected:
        return

    profile_obj = services.get_service_engineer_details(selected['id'], user)
    if not profile_obj:
        print("Could not retrieve profile details.")
        input("\nPress Enter to return...")
        return

    while True:
        display_header(f"Updating: {profile_obj.first_name} {profile_obj.last_name}")
        print("Current Profile Details:")
        print(f"  [1] First Name: {profile_obj.first_name}")
        print(f"  [2] Last Name: {profile_obj.last_name}")
        print("-" * 30)
        print("Enter the number of the field to update. 'S' to Save, 'C' to Cancel.")
        choice = get_input("\nYour choice").upper()

        if choice == 'S':
            print("\nSaving changes...")
            if services.update_service_engineer_profile(profile_obj, user):
                print("Update successful.")
            else:
                print("Update failed.")
            input("\nPress Enter to return...")
            break
        elif choice == 'C':
            print("Update cancelled. No changes were saved.")
            input("\nPress Enter to return...")
            break
        elif choice == '1':
            new_val = get_validated_input(f"New First Name [{profile_obj.first_name}]", validators.is_valid_name,
                                          required=False)
            if new_val:
                profile_obj.first_name = new_val
        elif choice == '2':
            new_val = get_validated_input(f"New Last Name [{profile_obj.last_name}]", validators.is_valid_name,
                                          required=False)
            if new_val:
                profile_obj.last_name = new_val
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)


def ui_delete_service_engineer(user):
    """UI flow for finding and deleting a Service Engineer."""
    display_header("Delete Service Engineer")

    selected = _search_and_select_item(
        search_prompt="Enter username or name of engineer to search for",
        search_function=services.find_service_engineers,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select an engineer to DELETE:",
        no_results_message="\nNo engineers found matching '{query}'."
    )

    if not selected:
        return

    print("\n!! WARNING: This will deactivate the user's account. !!")
    confirm = get_input(f"Type 'DELETE' to deactivate user {selected['display']}: ")
    if confirm == 'DELETE':
        if services.delete_service_engineer(selected['id'], user):
            print("Service Engineer has been deactivated.")
        else:
            print("Failed to deactivate account.")
    else:
        print("Deletion cancelled.")
    input("\nPress Enter to return...")

def ui_delete_system_admin(user):
    """UI flow for finding and deleting a System Administrator."""
    display_header("Delete System Administrator")

    selected = _search_and_select_item(
        search_prompt="Enter username or name of admin to search for",
        search_function=services.find_system_admins,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a System Administrator to DELETE:",
        no_results_message="\nNo System Administrators found matching '{query}'."
    )

    if not selected:
        return

    print("\n!! WARNING: This will permanently delete the user's account. !!")
    confirm = get_input(f"Type 'DELETE' to permanently remove admin {selected['display']}: ")
    if confirm == 'DELETE':
        if services.delete_system_admin(selected['id'], user):
            print("System Administrator has been deleted.")
        else:
            print("Failed to delete account.")
    else:
        print("Deletion cancelled.")
    input("\nPress Enter to return...")

def ui_reset_service_engineer_password(user):
    """UI flow for resetting a Service Engineer's password."""
    display_header("Reset Service Engineer Password")

    selected = _search_and_select_item(
        search_prompt="Enter username or name of engineer to search for",
        search_function=services.find_service_engineers,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select an engineer to reset password for:",
        no_results_message="\nNo engineers found matching '{query}'."
    )

    if not selected:
        return

    display_header(f"Resetting password for {selected['display']}")
    print("\n!! WARNING: This will immediately change the user's password. !!")

    new_password = get_validated_input("Enter the new temporary password", validators.is_valid_password,
                                       is_password=True)
    confirm_password = get_password_input("Confirm the new password")

    if new_password != confirm_password:
        print("\nNew passwords do not match. Password reset cancelled.")
        input("Press Enter to return...")
        return

    print(f"\nResetting password for user ID {selected['id']}...")
    if services.reset_service_engineer_password(selected['id'], new_password, user):
        print("Password has been successfully reset.")
    else:
        print("Failed to reset the password.")

    input("\nPress Enter to return...")


# --- Scooter UI Forms ---
def ui_add_scooter(user):
    """UI flow for adding a new scooter with robust type conversion."""
    display_header("Add New Scooter")

    scooter_str_data = {
        'brand': get_validated_input("Brand", validators.is_valid_name),
        'model': get_validated_input("Model", validators.is_valid_model),
        'serial_number': get_validated_input("Serial Number (10-17 chars)", validators.is_valid_scooter_serial),
        'top_speed_kmh': get_validated_input("Top Speed (km/h)", validators.is_valid_speed),
        'battery_capacity_wh': get_validated_input("Battery Capacity (Wh)", validators.is_valid_battery_capacity),
        'soc_percentage': get_validated_input("Current State of Charge (%)", validators.is_valid_soc),
        'target_soc_min': get_validated_input("Min Target SoC (%)", validators.is_valid_soc),
        'target_soc_max': get_validated_input("Max Target SoC (%)", validators.is_valid_soc),
        'location_latitude': get_validated_input("Latitude",
                                                 lambda v: validators.validate_rotterdam_coordinates(v, 'latitude')),
        'location_longitude': get_validated_input("Longitude",
                                                  lambda v: validators.validate_rotterdam_coordinates(v, 'longitude')),
        'out_of_service': get_validated_input("Out of service? (yes/no)", validators.is_valid_OoS).lower(),
        'mileage_km': get_validated_input("Current Mileage (km)", validators.is_valid_mileage),
        'last_maintenance_date': get_validated_input("Last Maintenance Date (YYYY-MM-DD)", validators.is_valid_date,
                                                     required=False)
    }

    try:
        scooter_data = {
            'scooter_id': None,
            'brand': scooter_str_data['brand'],
            'model': scooter_str_data['model'],
            'serial_number': scooter_str_data['serial_number'],
            'top_speed_kmh': int(scooter_str_data['top_speed_kmh']),
            'battery_capacity_wh': int(scooter_str_data['battery_capacity_wh']),
            'soc_percentage': float(scooter_str_data['soc_percentage']),
            'target_soc_min': float(scooter_str_data['target_soc_min']),
            'target_soc_max': float(scooter_str_data['target_soc_max']),
            'location_latitude': float(scooter_str_data['location_latitude']),
            'location_longitude': float(scooter_str_data['location_longitude']),
            'out_of_service': scooter_str_data['out_of_service'] == 'yes',
            'mileage_km': float(scooter_str_data['mileage_km']),
            'last_maintenance_date': scooter_str_data['last_maintenance_date'] or None,
            'in_service_date': datetime.now()
        }

        print("\nAdding scooter to the system...")
        services.add_new_scooter(scooter_data, user)

    except (ValueError, TypeError) as e:
        print(f"\nAn internal error occurred during data conversion: {e}")
        print("Could not add scooter. Please try again.")

    input("\nPress Enter to return to the menu...")


def ui_search_scooters(user):
    """UI flow for searching scooters and viewing details."""
    display_header("Search for Scooter")
    selected = _search_and_select_item(
        search_prompt="Enter brand, model, or serial number to search",
        search_function=services.search_scooters,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['brand']} {r['model']} (SN: {r['serial_number']})",
                                    'id': r['scooter_id']},
        selection_prompt="Select a scooter to view details:",
        no_results_message="\nNo scooters found matching '{query}'."
    )

    if selected:
        scooter_obj = services.get_scooter_details(selected['id'], user)
        if scooter_obj:
            display_header(f"Details for {scooter_obj.brand} {scooter_obj.model}")
            for attr, value in vars(scooter_obj).items():
                print(f"  {attr.replace('_', ' ').title()}: {value}")
    input("\nPress Enter to return...")


def ui_update_scooter(user, limited=False):
    """
    UI flow for finding and updating a scooter.
    Can be run in a limited mode for Service Engineers.
    """
    display_header("Update Scooter Record")
    selected = _search_and_select_item(
        search_prompt="Enter a brand, model, or serial to search for the scooter to update",
        search_function=services.search_scooters,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['brand']} {r['model']} (SN: {r['serial_number']})",
                                    'id': r['scooter_id']},
        selection_prompt="Select a scooter to update:",
        no_results_message="\nNo scooters found matching '{query}'."
    )

    if not selected:
        return

    scooter_obj = services.get_scooter_details(selected['id'], user)
    if not scooter_obj:
        print("Could not retrieve scooter details.")
        input("\nPress Enter to return...")
        return

    full_menu = {
        "1": {"prompt": "Brand", "attr": "brand", "value": scooter_obj.brand, "validator": validators.is_valid_name},
        "2": {"prompt": "Model", "attr": "model", "value": scooter_obj.model, "validator": validators.is_valid_model},
        "3": {"prompt": "Serial Number", "attr": "serial_number", "value": scooter_obj.serial_number,
              "validator": validators.is_valid_scooter_serial},
        "4": {"prompt": "Top Speed (km/h)", "attr": "top_speed_kmh", "value": scooter_obj.top_speed_kmh,
              "validator": validators.is_valid_speed},
        "5": {"prompt": "Battery Capacity (Wh)", "attr": "battery_capacity_wh",
              "value": scooter_obj.battery_capacity_wh, "validator": validators.is_valid_battery_capacity},
        "6": {"prompt": "SoC (%)", "attr": "soc_percentage", "value": scooter_obj.soc_percentage,
              "validator": validators.is_valid_soc},
        "7": {"prompt": "Min Target SoC (%)", "attr": "target_soc_min", "value": scooter_obj.target_soc_min,
              "validator": validators.is_valid_soc},
        "8": {"prompt": "Max Target SoC (%)", "attr": "target_soc_max", "value": scooter_obj.target_soc_max,
              "validator": validators.is_valid_soc},
        "9": {"prompt": "Latitude", "attr": "location_latitude", "value": scooter_obj.location_latitude,
              "validator": lambda v: validators.validate_rotterdam_coordinates(v, 'latitude')},
        "10": {"prompt": "Longitude", "attr": "location_longitude", "value": scooter_obj.location_longitude,
               "validator": lambda v: validators.validate_rotterdam_coordinates(v, 'longitude')},
        "11": {"prompt": "Out of Service", "attr": "out_of_service",
               "value": "Yes" if scooter_obj.out_of_service is True else "No", "validator": validators.is_valid_OoS},
        "12": {"prompt": "Mileage (km)", "attr": "mileage_km", "value": scooter_obj.mileage_km,
               "validator": validators.is_valid_mileage},
        "13": {"prompt": "Last Maintenance Date", "attr": "last_maintenance_date",
               "value": scooter_obj.last_maintenance_date, "validator": validators.is_valid_date},
    }

    limited_menu_keys = ["6", "7", "8", "9", "10", "11", "12", "13"]
    update_menu = {k: full_menu[k] for k in limited_menu_keys} if limited else full_menu

    while True:
        display_header(f"Updating: {scooter_obj.brand} {scooter_obj.model}")

        for key, item in update_menu.items():
            item['value'] = getattr(scooter_obj, item['attr'])
            display_value = "Yes" if item['attr'] == 'out_of_service' and item['value'] else "No" if item[
                                                                                                         'attr'] == 'out_of_service' and not \
                                                                                                     item['value'] else \
            item['value']
            print(f"  [{key}] {item['prompt']}: {display_value}")

        print("-" * 40)
        print("Enter the number of the field to update. 'S' to Save, 'C' to Cancel.")
        choice = get_input("\nYour choice").upper()

        if choice == 'S':
            print("\nSaving changes...")
            if services.update_scooter_details(scooter_obj, user, is_limited=limited):
                print("Update successful.")
            else:
                print("Update failed.")
            input("\nPress Enter to return...")
            break
        elif choice == 'C':
            print("Update cancelled. No changes were saved.")
            input("\nPress Enter to return...")
            break
        elif choice in update_menu:
            field = update_menu[choice]
            prompt_text = f"New {field['prompt']}"
            if field['validator']:
                new_val_str = get_validated_input(prompt_text, field['validator'])
            else:
                new_val_str = get_input(prompt_text)

            try:
                if field['attr'] == 'out_of_service':
                    setattr(scooter_obj, field['attr'], new_val_str.lower() == 'yes')
                elif isinstance(getattr(scooter_obj, field['attr']), float):
                    setattr(scooter_obj, field['attr'], float(new_val_str))
                elif isinstance(getattr(scooter_obj, field['attr']), int):
                    setattr(scooter_obj, field['attr'], int(new_val_str))
                else:
                    setattr(scooter_obj, field['attr'], new_val_str)
            except (ValueError, TypeError) as e:
                print(f"Invalid input type: {e}")
                time.sleep(2)
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)


def ui_delete_scooter(user):
    """UI flow for finding and deleting a scooter."""
    display_header("Delete Scooter Record")
    selected = _search_and_select_item(
        search_prompt="Enter brand, model, or serial number to search for the scooter to delete",
        search_function=services.search_scooters,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['brand']} {r['model']} (SN: {r['serial_number']})",
                                    'id': r['scooter_id']},
        selection_prompt="Select a scooter to DELETE:",
        no_results_message="\nNo scooters found matching '{query}'."
    )

    if not selected:
        return

    print("\n!! WARNING: This action is permanent and cannot be undone. !!")
    confirm = get_input(f"Type 'DELETE' to permanently remove scooter ID {selected['id']}: ")
    if confirm == 'DELETE':
        if services.delete_scooter_record(selected['id'], user):
            print("Scooter record has been deleted.")
        else:
            print("Failed to delete scooter record.")
    else:
        print("Deletion cancelled.")
    input("\nPress Enter to return...")


def ui_view_system_logs(user):
    """UI flow for displaying system logs using the display module."""
    logs = services.view_system_logs(user)
    display.display_system_logs_paginated(logs)


def ui_create_backup(user):
    """UI flow for creating a database backup."""
    display_header("Create Database Backup")
    print("This will create a secure, timestamped backup of the entire database.")
    confirm = get_input("Are you sure you want to proceed? (yes/no): ").lower()
    if confirm == 'yes':
        print("\nCreating backup...")
        services.create_backup(user)
    else:
        print("\nBackup cancelled.")
    input("Press Enter to return to the menu...")


def ui_restore_from_backup(user):
    """UI flow for restoring the database from a backup."""
    display_header("Restore Database from Backup")

    backup_file = None
    restore_code_obj = None

    if user.role == 'systemadmin':
        restore_code_value = get_input("Enter your one-time restore code")
        if not restore_code_value:
            print("Operation cancelled.")
            input("\nPress Enter...")
            return

        code_obj, message = services.validate_restore_code(restore_code_value, user)
        if not code_obj:
            print(f"Error: {message}")
            input("\nPress Enter...")
            return

        backup_file = code_obj.backup_filename
        restore_code_obj = code_obj
        print(f"\nRestore code accepted for backup file: {backup_file}")
        time.sleep(1)

    elif user.role == 'superadmin':
        backups = services.list_backups(user)
        if not backups:
            print("No backup files found.")
            input("\nPress Enter to return...")
            return

        display_list = [{'display': b, 'id': b} for b in backups]
        selected = select_from_list("Select a backup file to restore from:", display_list, 'display')

        if not selected:
            print("Restore cancelled.")
            input("\nPress Enter to return...")
            return
        backup_file = selected['id']

    print("\n" + "=" * 60)
    print("!!  CRITICAL WARNING  !!")
    print(f"You are about to restore the database from the file: {backup_file}")
    print("This action will OVERWRITE all current data and CANNOT be undone.")
    print("The application will shut down after the restore is complete.")
    print("=" * 60)

    confirm = get_input(f"\nType 'RESTORE' to confirm this operation: ").upper()
    if confirm == 'RESTORE':
        print("\nStarting restore process...")
        success, message = services.restore_from_backup(backup_file=backup_file, current_user=user,
                                                        restore_code_obj=restore_code_obj)

        print(f"\n{message}")
        if success:
            print("Please restart the application to use the restored database.")
            input("Press Enter to quit.")
            sys.exit(0)
        else:
            input("Press Enter to return...")
    else:
        print("\nConfirmation failed. Restore operation cancelled.")
        input("Press Enter to return...")


def ui_generate_restore_code(user):
    """UI flow for a SuperAdmin to generate a one-time restore code."""
    display_header("Generate Restore Code")

    backups = services.list_backups(user)
    if not backups:
        print("No backup files found. A backup must exist to generate a code.")
        input("\nPress Enter to return...")
        return

    backup_display_list = [{'display': b, 'id': b} for b in backups]
    selected_backup = select_from_list("Select a backup file for the restore code:", backup_display_list, 'display')

    if not selected_backup:
        print("Operation cancelled.")
        input("\nPress Enter...")
        return

    backup_file = selected_backup['id']

    selected_admin = _search_and_select_item(
        search_prompt="Enter username or name of System Admin to assign code to",
        search_function=services.find_system_admins,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a System Administrator:",
        no_results_message="\nNo System Admins found matching '{query}'."
    )

    if not selected_admin:
        print("Operation cancelled.")
        input("\nPress Enter...")
        return

    admin_id = selected_admin['id']

    print(f"\nGenerating a restore code for {selected_admin['display']} and backup {backup_file}...")
    code = services.generate_restore_code(system_admin_id=admin_id, backup_filename=backup_file, current_user=user)

    if code:
        print("\n" + "-" * 50)
        print("  SUCCESS! Restore code generated.")
        print("  Please securely transmit the following code to the System Administrator.")
        print(f"\n  Restore Code: {code}\n")
        print("  This code is valid for 24 hours and can only be used once.")
        print("-" * 50)
    else:
        print("\nFailed to generate restore code. Please check the logs.")

    input("\nPress Enter to return to the menu...")

def ui_remove_restore_code(user):
    """UI flow for a SuperAdmin to remove an existing restore code assigned to a specific system admin."""
    display_header("Remove Restore Code")

    selected_admin = _search_and_select_item(
        search_prompt="Enter username or name of System Admin to remove code from",
        search_function=services.find_system_admins,
        current_user=user,
        result_formatter=lambda r: {'display': f"{r['name']} ({r['username']})", 'id': r['id']},
        selection_prompt="Select a System Administrator:",
        no_results_message="\nNo System Admins found matching '{query}'."
    )

    if not selected_admin:
        print("Operation cancelled.")
        input("\nPress Enter...")
        return

    admin_id = selected_admin['id']

    print(f"\nRemoving restore code for {selected_admin['display']}...")
    result = services.remove_restore_code(system_admin_id=admin_id, current_user=user)
    if result is True:
        print("\nRestore code has been successfully removed.")
    elif result == "not_found":
        print("\nThere are no restore codes for that user.")
    else:
        print("\nFailed to remove restore code. Please check the logs.")

    input("\nPress Enter to return to the menu...")
