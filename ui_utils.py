import os
import data_access
import getpass
import time

da = data_access.DataAccess()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_header(title):
    clear_screen()
    header = "Urban Mobility Backend System - " + title
    print("=============================================================================")
    print(f"{header:^77}")
    print("=============================================================================")
    print()


def get_input(prompt, required=True):
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value
        if required:
            print("Error: This field is required.")
        else:
            return ""


def get_password_input(prompt):
    return getpass.getpass(f"{prompt}: ")


def get_validated_input(prompt, validator_func, is_password=False, required=True, pre_prompt=""):
    while True:
        if is_password:
            value = get_password_input(prompt)
        else:
            user_input = input(f"{prompt} {pre_prompt}").strip()
            value = pre_prompt + user_input if pre_prompt else user_input

        if not (value if is_password else user_input):
            if required:
                print("Error: This field is required.")
                continue
            else:
                return ""

        is_valid, message = validator_func(value)
        if is_valid:
            return value
        else:
            print(f"Error: {message}")
