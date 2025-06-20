import services
import database
from datetime import datetime
from models import User


def seed_database():
    print("--- Starting Database Seeding ---")

    seeder_user = User(user_id=1, username='super_admin', role='superadmin')

    print("\n[1/2] Seeding Scooters...")
    scooters_to_add = [
        {
            'scooter_id': None, 'brand': 'Segway', 'model': 'Ninebot G30', 'serial_number': 'SNX987654321',
            'top_speed_kmh': 25, 'battery_capacity_wh': 551, 'soc_percentage': 88.5,
            'target_soc_min': 20.0, 'target_soc_max': 95.0, 'location_latitude': 51.9178, 'location_longitude': 4.5608,
            'out_of_service': False, 'mileage_km': 1204.5, 'last_maintenance_date': '2025-05-20',
            'in_service_date': datetime.now()
        },
        {
            'scooter_id': None, 'brand': 'NIU', 'model': 'KQi3 Max', 'serial_number': 'NIU123456789',
            'top_speed_kmh': 25, 'battery_capacity_wh': 608, 'soc_percentage': 99.0,
            'target_soc_min': 20.0, 'target_soc_max': 95.0, 'location_latitude': 51.9225, 'location_longitude': 4.47917,
            'out_of_service': False, 'mileage_km': 850.2, 'last_maintenance_date': '2025-04-15',
            'in_service_date': datetime.now()
        },
        {
            'scooter_id': None, 'brand': 'Tier', 'model': 'Six', 'serial_number': 'TIER998877665',
            'top_speed_kmh': 20, 'battery_capacity_wh': 500, 'soc_percentage': 15.0,
            'target_soc_min': 20.0, 'target_soc_max': 95.0, 'location_latitude': 51.9149, 'location_longitude': 4.4734,
            'out_of_service': True, 'mileage_km': 2530.0, 'last_maintenance_date': '2025-01-10',
            'in_service_date': datetime.now()
        },
    ]

    for scooter_data in scooters_to_add:
        print(f"  -> Adding Scooter: {scooter_data['brand']} {scooter_data['model']}...")
        services.add_new_scooter(scooter_data, seeder_user)

    print("Scooter seeding complete.")

    print("\n[2/2] Seeding Travellers...")
    travellers_to_add = [
        {
            'first_name': 'Lotte', 'last_name': 'de Vries', 'birthday': '1998-08-12', 'gender': 'Female',
            'street_name': 'Hoofdstraat', 'house_number': '24A', 'zip_code': '3111AA', 'city': 'Schiedam',
            'email_address': 'lotte.devries@example.com', 'mobile_phone': '+31-6-12345678',
            'driving_license_number': 'DE12345678'
        },
        {
            'first_name': 'Daan', 'last_name': 'Jansen', 'birthday': '2001-03-21', 'gender': 'Male',
            'street_name': 'Nieuwe Binnenweg', 'house_number': '182', 'zip_code': '3015BE', 'city': 'Rotterdam',
            'email_address': 'daan.jansen@example.com', 'mobile_phone': '+31-6-87654321',
            'driving_license_number': 'JA8765432'
        },
        {
            'first_name': 'Fleur', 'last_name': 'van Dijk', 'birthday': '1995-01-11', 'gender': 'Female',
            'street_name': 'Lange Haven', 'house_number': '55', 'zip_code': '3111CB', 'city': 'Schiedam',
            'email_address': 'fleur.vandijk@example.com', 'mobile_phone': '+31-6-11223344',
            'driving_license_number': 'VD1122334'
        },
    ]

    for traveller_data in travellers_to_add:
        print(f"  -> Adding Traveller: {traveller_data['first_name']} {traveller_data['last_name']}...")
        services.add_new_traveller(traveller_data, seeder_user)

    print("Traveller seeding complete.")

    print("\n--- Database Seeding Finished ---")


if __name__ == '__main__':
    print("Initializing database...")
    database.initialize_database()

    seed_database()
