# Urban Mobility Backend System

# Setup & Running the Application
Follow these steps to set up and run the system:

## 1. Install Dependencies:
The project requires a few external libraries. Install them using pip:
```bash
pip install cryptography bcrypt
```

## 2. Run the Initial Setup:
This script will create the database file, set up the tables, and create the initial superadmin account.
```bash
python setup.py
```

Note: Run this script only once. If you need to restart from scratch, delete the urban_mobility.db and secret.key files before running it again.

## 3. (Optional) Seed the Database:
To populate the database with sample travellers and scooters for testing, run the seeder script:
```bash
python seeder.py
```

## 4. Run the Main Application:
Start the application by running the app.py file.
```bash
python app.py
```
