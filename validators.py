import re
from datetime import datetime

# --- Regular Expression Patterns ---
RE_ZIP_CODE = re.compile(r'^\d{4}[A-Z]{2}$')
RE_MOBILE_PHONE = re.compile(r'^\+31-6-\d{8}$')
RE_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
# Driving license regex is now handled within the function for more complex logic.
RE_PASSWORD_COMPLEXITY = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_#-])[A-Za-z\d@$!%*?&_#-]{12,30}$'
)
RE_SCOOTER_SERIAL = re.compile(r'^[A-Za-z0-9]{10,17}$')
RE_ALPHA_ONLY = re.compile(r'^[a-zA-Z\s.-]+$') # Allows letters, spaces, hyphens, dots
RE_ALPHA_NUMERIC_ONLY = re.compile(r'^[a-zA-Z0-9\s.,#-]+$') # Allows more characters for addresses
RE_HOUSE_NUMBER = re.compile(r'^\d{1,5}(\s*-?\s*[a-zA-Z0-9-]+)?$') # For Dutch house numbers e.g., 123, 123A, 123-A

# --- Validation Functions ---
# Each function now returns a tuple: (is_valid: bool, message: str or None)

def is_valid_name(name):
    """Validates that a name contains only alphabetic characters, spaces, or hyphens."""
    if RE_ALPHA_ONLY.match(name):
        return True, None
    return False, "Input must only contain letters, spaces, dots, or hyphens."

def is_valid_address_field(field):
    """Validates that a street name contains reasonable characters."""
    if RE_ALPHA_NUMERIC_ONLY.match(field):
        return True, None
    return False, "Input contains invalid characters for a street name."

def is_valid_house_number(number):
    """Validates a Dutch house number format (e.g., 123, 123A, 123-A)."""
    if RE_HOUSE_NUMBER.match(number):
        return True, None
    return False, "Invalid house number format. It should be a number with an optional suffix (e.g., 24 B)."

def is_valid_date(date_string, date_format='%Y-%m-%d'):
    """Validates if a string is a valid date, is in the correct format, and is not in the future."""
    try:
        b_date = datetime.strptime(date_string, date_format).date()
        _120_YEARS_AGO = datetime.now().date().replace(year=datetime.now().year - 120)
        if b_date < _120_YEARS_AGO:
            return False, "Date cannot be more than 120 years ago."
        if b_date > datetime.now().date():
            return False, "Date cannot be in the future."
        return True, None
    except ValueError:
        return False, f"Invalid date format. Please use {date_format}."

def is_valid_zip_code(zip_code):
    """Validates Dutch zip code format (DDDDXX)."""
    if RE_ZIP_CODE.match(zip_code):
        return True, None
    return False, "Invalid Zip Code format. Must be DDDDXX (e.g., 1234AB)."

def is_valid_mobile_phone(phone):
    """Validates Dutch mobile phone format (+31-6-DDDDDDDD)."""
    if RE_MOBILE_PHONE.match(phone):
        return True, None
    return False, "Invalid mobile phone format. Must be +31-6-DDDDDDDD."

def is_valid_email(email):
    """Validates email format."""
    if RE_EMAIL.match(email):
        return True, None
    return False, "Invalid email address format."

def is_valid_driving_license(license_number):
    """Validates Dutch driving license format (1 letter + 8 digits OR 2 letters + 7 digits)."""
    # General format check: must start with 1 or 2 letters, followed by only digits.
    if not re.match(r'^[A-Z]{1,2}\d+$', license_number):
        return False, "Invalid format. Must start with 1 or 2 uppercase letters followed by digits."

    # Specific length check based on the number of leading letters.
    if license_number[1].isdigit(): # First character is a letter, second is a digit.
        if len(license_number) == 9: # 1 letter + 8 digits = 9 total
            return True, None
        else:
            return False, "A license starting with one letter must be followed by 8 digits."
    else: # First two characters are letters.
        if len(license_number) == 9: # 2 letters + 7 digits = 9 total
            return True, None
        else:
            return False, "A license starting with two letters must be followed by 7 digits."

def is_valid_password(password):
    """Validates password complexity."""
    if RE_PASSWORD_COMPLEXITY.match(password):
        return True, None
    return False, "Password must be 12-30 chars with an uppercase, lowercase, digit, and special character."

def is_valid_username(username):
    """Validates username length."""
    if 8 <= len(username) <= 20:
        return True, None
    return False, "Username must be between 8 and 20 characters long."

def is_valid_scooter_serial(serial):
    """Validates scooter serial number format."""
    if RE_SCOOTER_SERIAL.match(serial):
        return True, None
    return False, "Serial number must be 10-17 alphanumeric characters."

def is_valid_soc(soc_string):
    """Validates State of Charge (SoC) is between 0 and 100."""
    try:
        soc = float(soc_string)
        if 0 <= soc <= 100:
            return True, None
        return False, "SoC must be a number between 0 and 100."
    except (ValueError, TypeError):
        return False, "SoC must be a valid number."

def is_valid_gps_coordinate(coord_string, coord_type):
    """Validates latitude or longitude format and range."""
    try:
        coord = float(coord_string)
        if coord_type == 'latitude':
            if -90 <= coord <= 90:
                return True, None
            return False, "Latitude must be between -90 and 90."
        if coord_type == 'longitude':
            if -180 <= coord <= 180:
                return True, None
            return False, "Longitude must be between -180 and 180."
        return False, "Invalid coordinate type specified."
    except (ValueError, TypeError):
        return False, "GPS coordinate must be a valid number."

def is_valid_integer(value):
    """Checks if a string represents a valid integer."""
    if value.isdigit():
        return True, None
    return False, "Input must be a whole number."

def is_valid_float(value):
    """Checks if a string represents a valid float."""
    try:
        float(value)
        return True, None
    except ValueError:
        return False, "Input must be a valid number (e.g., 50 or 25.5)."
