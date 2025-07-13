import re
from datetime import datetime

RE_ZIP_CODE = re.compile(r'^[1-9][0-9]{3}[A-Za-z]{2}$')
RE_MOBILE_PHONE = re.compile(r'^\+31-6-\d{8}$')
RE_EMAIL = re.compile(r'^(?=.{1,254}$)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
RE_PASSWORD_COMPLEXITY = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_#-])[A-Za-z\d@$!%*?&_#-]{12,30}$')

RE_MODEL = re.compile(r"^[A-Za-z0-9\s\-'.]{0,50}$")
RE_speed = re.compile(r'^(100|[1-9][0-9]?)$')
RE_battery_capacity = re.compile(r'^([1-9][0-9]{0,3})$')
RE_SCOOTER_SERIAL = re.compile(r'^[A-Za-z0-9]{10,17}$')
RE_ALPHA_ONLY = re.compile(r"^(?=.*[A-Za-z])[A-Za-z\s\-'.]{1,100}$")
RE_ALPHA_NUMERIC_ONLY = re.compile(r'^[a-zA-Z0-9\s.,#-]+$')
RE_HOUSE_NUMBER = re.compile(r'^[1-9][0-9]{0,3}[- ]?[A-Za-z]?$')
RE_FIVE_DECIMAL = re.compile(r'^\d{1,5}(\.\d{5})?$')
RE_SoC = re.compile(r'^(?:100(?:\.0{1,2})?|[0-9]{1,2}(?:\.[0-9]{1,2})?)$')
RE_MILEAGE = re.compile(r'^(?:0|[1-9][0-9]{0,9})(?:\.[0-9]{1,2})?$')

def is_valid_name(name):
    if RE_ALPHA_ONLY.match(name):
        return True, None
    return False, "Input must only contain letters, spaces, apostrophes, dots or hyphens (no numbers) and must be shorter than 100 characters."

def is_valid_gender(gender):
    if gender.lower() in ['male', 'female']:
        return True, None
    return False, "Gender must be either 'male' or 'female'."

def is_valid_address_field(field):
    if RE_ALPHA_ONLY.match(field):
        return True, None
    return False, "Street name must only contain letters, spaces, apostrophes, dots or hyphens (no numbers) and must be shorter than 100 characters."

def is_valid_house_number(number):
    if RE_HOUSE_NUMBER.match(number):
        return True, None
    return False, "Invalid house number format. It should be a number with an optional suffix (e.g., 24 B)."

def is_valid_date(date_string, date_format='%Y-%m-%d', is_birth_date=False):
    try:
        b_date = datetime.strptime(date_string, date_format).date()
        _120_YEARS_AGO = datetime.now().date().replace(year=datetime.now().year - 120)
        if b_date < _120_YEARS_AGO:
            return False, "Date cannot be more than 120 years ago."
        elif is_birth_date:
            _16_YEARS_AGO = datetime.now().date().replace(year=datetime.now().year - 16)
            if b_date > _16_YEARS_AGO:
                return False, "You must be at least 16 years old."
        elif b_date > datetime.now().date():
            return False, "Date cannot be in the future."
        return True, None
    except ValueError:
        return False, f"Invalid date format. Please use {date_format}."

def is_valid_birth_date(date_string):
    return is_valid_date(date_string, is_birth_date=True)

def is_valid_zip_code(zip_code):
    if RE_ZIP_CODE.match(zip_code):
        return True, None
    return False, "Invalid Zip Code format. Must be DDDDXX (e.g., 1234AB or 1234ab)."

def is_valid_city(city):
    _cities = ['Rotterdam', 'Schiedam', 'Delft', 'The Hague', 'Amsterdam', 'Spijkenisse', 'Barendrecht', 'Brielle', 'Hellevoetsluis', 'Vlaardingen']
    if city in _cities:
        return True, None
    return False, "Invalid city. Must be one of the predefined cities: {}".format(", ".join(_cities))

def is_valid_mobile_phone(phone):
    if RE_MOBILE_PHONE.match(phone):
        return True, None
    return False, "Invalid mobile phone format. Must be +31-6-DDDDDDDD."

def is_valid_email(email):
    if RE_EMAIL.match(email):
        return True, None
    return False, "Invalid email address format."

def is_valid_driving_license(license_number):
    license_number = license_number.upper()

    if not re.match(r'^[A-Z]{1,2}\d+$', license_number):
        return False, "Invalid format. Must start with 1 or 2 letters followed by digits."

    if license_number[1].isdigit():
        if len(license_number) == 9:
            return True, None
        else:
            return False, "A license starting with one letter must be followed by 8 digits."
    else:
        if len(license_number) == 9:
            return True, None
        else:
            return False, "A license starting with two letters must be followed by 7 digits."

def is_valid_password(password):
    if RE_PASSWORD_COMPLEXITY.match(password):
        return True, None
    return False, "Password must be 12-30 chars with an uppercase, lowercase, digit, and special character."

def is_valid_username(username):
    if not (8 <= len(username) <= 10):
        return False, "Username must be between 8 and 10 characters long."

    if not re.match(r'^[a-zA-Z0-9_.\']+$', username):
        return False, "Username can only contain letters (a-z), numbers (0-9), underscores (_), apostrophes ('), and periods (.)."

    return True, None

def is_valid_scooter_serial(serial):
    if RE_SCOOTER_SERIAL.match(serial):
        return True, None
    return False, "Serial number must be 10-17 alphanumeric characters."

def is_valid_soc(soc_string):
    if RE_SoC.match(soc_string):
        return True, None
    return False, "SoC must be a valid number between 0 and 100."

def is_valid_gps_coordinate(coord_string, coord_type):
    try:
        _coord = float(coord_string)
        if coord_type == 'latitude':
            if -90 <= _coord <= 90:
                return True, None
            return False, "Latitude must be between -90 and 90."
        if coord_type == 'longitude':
            if -180 <= _coord <= 180:
                return True, None
            return False, "Longitude must be between -180 and 180."
        return False, "Invalid coordinate type specified."
    except (ValueError, TypeError):
        return False, "GPS coordinate must be a valid number."

def is_valid_integer(value):
    if value.isdigit() and value <= 9999999999:
        return True, None
    return False, "Input must be a whole number."

def is_valid_speed(value):
    if RE_speed.match(value):
        return True, None
    return False, "Speed must be a number between 1 and 100."

def is_valid_mileage(value):
    if RE_MILEAGE.match(value):
        return True, None
    return False, "Mileage must be a number between 0 and 9999999999.99"

def is_valid_battery_capacity(value):
    if RE_battery_capacity.match(value):
        return True, None
    return False, "Battery capacity must be a number between 1 and 9999."

def is_valid_float(value):
    try:
        float(value)
        return True, None
    except ValueError:
        return False, "Input must be a valid number (e.g., 50 or 25.5)."

def is_valid_OoS(value):
    if value.lower() in ['yes', 'no']:
        return True, None
    return False, "Input must be 'yes' or 'no'."

def is_valid_model(value):
    if RE_MODEL.match(value):
        return True, None
    return False, "Input must be a string shorter than 100 characters."

def validate_rotterdam_coordinates(coords, directions):
    rotterdam_bounds = {
        'latitude': {'min': 51.89000, 'max': 51.94000},
        'longitude':{'min': 4.40000, 'max': 4.55000}
    }

    if not RE_FIVE_DECIMAL.match(coords):
        return False, "Coordinate must be a number with 5 decimal places. For example, 51.92250."

    try:
        float_coord = float(coords)
    except ValueError:
        return False, "Coordinate must be a valid number."

    _success = rotterdam_bounds[directions]['min'] <= float_coord <= rotterdam_bounds[directions]['max']
    if _success:
        return True, f"{directions.capitalize()} coordinate {coords} is valid for Rotterdam."
    else:
        return False, f"{directions.capitalize()} coordinate {coords} is out of bounds for Rotterdam. " \
                      f"Must be between {rotterdam_bounds[directions]['min']} and {rotterdam_bounds[directions]['max']}."

if __name__ == "__main__":
    coord = "51.92250"
    direction = "latitude"
    is_valid, message = validate_rotterdam_coordinates(coord, direction)

    print(message)
