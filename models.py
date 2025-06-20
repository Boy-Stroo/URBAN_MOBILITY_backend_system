import datetime

class Traveller:
    def __init__(self, customer_id, first_name, last_name, birthday, gender,
                 street_name, house_number, zip_code, city, email_address,
                 mobile_phone, driving_license_number, registration_date=None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday if isinstance(birthday, datetime.date) else datetime.datetime.strptime(birthday, '%Y-%m-%d').date()
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email_address = email_address
        self.mobile_phone = mobile_phone
        self.driving_license_number = driving_license_number
        self.registration_date = registration_date or datetime.datetime.now().date().strftime('%Y-%m-%d')

    def __str__(self):
        return (f"Traveller ID: {self.customer_id}\n"
                f"Name: {self.first_name} {self.last_name}\n"
                f"Email: {self.email_address}\n"
                f"License: {self.driving_license_number}")

class Scooter:
    def __init__(self, scooter_id, brand, model, serial_number, top_speed_kmh,
                 battery_capacity_wh, soc_percentage, target_soc_min, target_soc_max,
                 location_latitude, location_longitude, out_of_service,
                 mileage_km, last_maintenance_date, in_service_date=None):
        self.scooter_id = scooter_id
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.top_speed_kmh = top_speed_kmh
        self.battery_capacity_wh = battery_capacity_wh
        self.soc_percentage = soc_percentage
        self.target_soc_min = target_soc_min
        self.target_soc_max = target_soc_max
        self.location_latitude = location_latitude
        self.location_longitude = location_longitude
        self.out_of_service = out_of_service
        self.mileage_km = mileage_km
        self.last_maintenance_date = last_maintenance_date
        self.in_service_date = in_service_date or datetime.datetime.now()

    def __str__(self):
        status = "Out of Service" if self.out_of_service else "In Service"
        return (f"Scooter ID: {self.scooter_id} ({self.brand} {self.model})\n"
                f"Serial: {self.serial_number}\n"
                f"Status: {status}\n"
                f"SoC: {self.soc_percentage}%\n"
                f"Location: ({self.location_latitude}, {self.location_longitude})")

class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def __str__(self):
        return (f"User ID: {self.user_id}\n"
                f"Username: {self.username}\n"
                f"Role: {self.role}")

class UserProfile:
    def __init__(self, profile_id, user_id, first_name, last_name, registration_date = None):
        self.profile_id = profile_id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.registration_date = registration_date or datetime.datetime.now().date().strftime('%Y-%m-%d')

    def __str__(self):
        return (f"Profile for User ID: {self.user_id}\n"
                f"Name: {self.first_name} {self.last_name}\n"
                f"Registered on: {self.registration_date}")

class RestoreCode:
    def __init__(self, code_id, restore_code, backup_filename, system_admin_id,
                 status, generated_at, expires_at):
        self.code_id = code_id
        self.restore_code = restore_code
        self.backup_filename = backup_filename
        self.system_admin_id = system_admin_id
        self.status = status
        self.generated_at = generated_at
        self.expires_at = expires_at

    def __str__(self):
        return (f"Restore Code ID: {self.code_id}\n"
                f"For User ID: {self.system_admin_id}\n"
                f"Backup File: {self.backup_filename}\n"
                f"Status: {self.status}\n"
                f"Expires: {self.expires_at}")
