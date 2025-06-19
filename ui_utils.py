import os
import data_access
import getpass
import time

da = data_access.DataAccess()

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_header(title):
    """Displays a consistent header for each screen."""
    clear_screen()
    print("===================================================")
    print(f"      Urban Mobility Backend System - {title}")
    print("===================================================")
    print()


def get_input(prompt, required=True):
    """
    Prompts the user for standard, non-validated input.
    Handles empty input if not required.
    """
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value
        if required:
            print("Error: This field is required.")
        else:
            return ""


def get_password_input(prompt):
    """Gets password input securely without echoing to the console."""
    return getpass.getpass(f"{prompt}: ")


def get_validated_input(prompt, validator_func, is_password=False, required=True, pre_prompt=""):
    """
    A robust helper function to loop until valid input is received.
    It uses a validator function that returns a (bool, str) tuple for specific error messages.

    :param prompt: The text to display to the user.
    :param validator_func: A function that takes the input string and returns (is_valid, error_message).
    :param is_password: A boolean flag to hide input for passwords.
    :param required: A boolean flag indicating if empty input is allowed.
    :param pre_prompt: A string to prepend to the user's input before validation.
    :return: The validated user input string.
    """
    while True:
        if is_password:
            # pre_prompt doesn't make sense for passwords, so it's ignored.
            value = get_password_input(prompt)
        else:
            # Display the pre_prompt to the user, but only add it once to the input.
            user_input = input(f"{prompt} {pre_prompt}").strip()
            value = pre_prompt + user_input if pre_prompt else user_input

        # Check if user actually typed something (ignoring the pre-prompt)
        if not (value if is_password else user_input):
            if required:
                print("Error: This field is required.")
                continue
            else:
                return ""  # Return empty if not required and user entered nothing

        # Validate the combined value
        is_valid, message = validator_func(value)
        if is_valid:
            return value
        else:
            # Print the specific error message from the validator
            print(f"Error: {message}")
