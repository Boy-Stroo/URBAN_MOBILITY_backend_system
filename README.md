# Urban Mobility Backend System
## 1. Introduction
This document provides a technical overview of the Urban Mobility Backend System. The system is a console-based application designed to manage travellers, electric scooters, and administrative users with a strong focus on security and data integrity. It is built using Python and follows a layered architecture to ensure a clear separation of concerns, making the codebase clean, maintainable, and secure.

## 2. Core Concepts & Architecture
The application is built upon a Layered Architecture. This design pattern separates the application into distinct layers, where each layer has a specific responsibility and only communicates with the layers immediately above or below it.

The flow of a user request is as follows:

**UI Layer -> Service Layer -> Data Access Layer -> Database**

### UI Layer (app.py, ui_forms.py, ui_utils.py, display.py)

Responsibility: Handles all user interaction, including displaying menus, gathering input, and presenting data.
Interaction: It calls the Service Layer to perform business operations. It never interacts directly with the database.

### Service Layer (services.py)

Responsibility: Contains the core business logic of the application. It acts as the intermediary between the UI and the data layers.
Interaction: It orchestrates operations by calling the Authorization, Auditing, and Data Access layers. For example, before deleting a record, it first checks if the user has permission (authorization.py), then calls the function to delete the data (data_access.py), and finally ensures the action is logged (auditing.py).

### Data Access Layer (data_access.py)

Responsibility: This is the only layer that directly communicates with the database. It is responsible for all CRUD (Create, Read, Update, Delete) operations.
Interaction: It uses parameterized SQL queries to prevent SQL injection and communicates with the security.py module to encrypt and decrypt data before writing to or reading from the database.

### Database (database.py, urban_mobility.db)

Responsibility: The SQLite database is the final persistence layer for all application data. The database.py script handles the initial schema creation.

## 3. Directory & File Structure
The project is organized into modules with distinct responsibilities:

```
├── backups/                  # Directory for created database backups
├── main.py                   # Main application entry point, handles top-level menus and app state
├── setup.py                  # One-time script to initialize the DB and create the superadmin
├── seeder.py                 # Optional script to populate the DB with test data
├── database.py               # Handles DB connection and table schema creation
├── models.py                 # Defines the data structures (e.g., User, Traveller classes)
├── services.py               # Core business logic layer
├── data_access.py            # Handles all direct database CRUD operations
├── security.py               # Manages encryption/decryption and password hashing
├── authorization.py          # Defines and checks user permissions (RBAC)
├── auditing.py               # Contains the audit decorator for logging activities
├── ui_forms.py               # Contains the UI logic for specific forms (e.g., add traveller)
├── ui_utils.py               # Utility functions for the UI (e.g., clear screen, get input)
├── display.py                # Handles formatted data presentation (e.g., using tabulate)
└── secret.key                # Stores the secret key for data encryption (auto-generated)
```

## 4. Security Implementation Details
Security is a primary concern and is implemented through several dedicated mechanisms.

### 4.1. Authentication
User passwords are never stored in plaintext. They are securely hashed using the bcrypt library.

The security.py module contains the hash_password() and check_password() functions that manage this process.

The initial superadmin user is created by the setup.py script, with all other users being managed through the application's role-based hierarchy.

### 4.2. Authorization (RBAC)
A Role-Based Access Control (RBAC) system is implemented in authorization.py.

This file contains a PERMISSIONS dictionary that maps roles (SuperAdmin, SystemAdmin, ServiceEngineer) to a set of allowed actions (e.g., 'delete_scooter', 'generate_restore_code').

The has_permission() function acts as a centralized gatekeeper. It is called by the Service Layer before any sensitive operation is executed to ensure the current user has the required privileges.

### 4.3. Data Encryption
Sensitive user and traveller data is encrypted at rest in the database.

Encryption is handled by the cryptography library's Fernet implementation (symmetric encryption).

The encryption key is stored in the secret.key file, which is automatically generated on first run and must not be shared or committed to version control.

The security.py module centralizes all encrypt_data() and decrypt_data() operations. The Data Access Layer calls these functions immediately before writing to or after reading from the database.

### 4.4. Auditing
(Could be improved)
A auditing system logs all significant actions. This is implemented using a Decorator Pattern in auditing.py. (Needs improvement)

The @audit_activity decorator wraps functions in the Service Layer. It automatically:

Executes the wrapped function.

Determines if the action was a success or failure.

Finds the user performing the action from the function's arguments.

Sanitizes the function's arguments to prevent logging sensitive data like passwords.

Records a new entry in the Logs table with all relevant context.

This approach keeps the business logic in services.py clean of repetitive logging code.

## 5. Database Schema
The SQLite database (urban_mobility.db) consists of the following key tables:
```
Users: 
    Stores core authentication info for all administrative users (user_id, username (encrypted), password_hash, role).
UserProfiles: 
    Stores profile information (first_name, last_name) linked to the Users table via user_id.
Travellers: 
    Stores all customer data. Sensitive fields like address and contact information are stored as BLOBs (encrypted).
Scooters: 
    Stores all data related to the scooter fleet.
Logs: 
    Contains the audit trail for all significant system events. Descriptions are encrypted. 
RestoreCodes: 
    Stores the one-time use codes generated by a SuperAdmin for a SystemAdmin to perform a database restore.
```

## 6. Setup & Running the Application
Follow these steps to set up and run the system:

### 1. Install Dependencies:
The project requires a few external libraries. Install them using pip:
```bash
pip install cryptography bcrypt tabulate
```

### 2. Run the Initial Setup:
This script will create the database file, set up the tables, and create the initial superadmin account.
```bash
python setup.py
```

Note: Run this script only once. If you need to restart from scratch, delete the urban_mobility.db and secret.key files before running it again.

### 3. (Optional) Seed the Database:
To populate the database with sample travellers and scooters for testing, run the seeder script:
```bash
python seeder.py
```

### 4. Run the Main Application:
Start the application by running the app.py file.
```bash
python app.py
```

You can then log in with the superadmin credentials (superadmin / superadmin) to begin using the system.