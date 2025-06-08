import sqlite3
from sqlite3 import Error

# Define the name of the database file
DATABASE_NAME = "urban_mobility_2.db"


def connect_db():
    """
    Creates a connection to the SQLite database specified by DATABASE_NAME.
    If the database file does not exist, it will be created.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = 1;")
        # print(f"Successfully connected to SQLite database: {DATABASE_NAME}")
        # print(f"SQLite version: {sqlite3.version}")
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_table(conn, create_table_sql):
    """
    Creates a table from the create_table_sql statement.
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Error creating table: {e}")


def initialize_database():
    """
    Connects to the database and creates all necessary tables if they don't exist.
    This is the main function to set up the database schema.
    """
    # SQL statements for creating tables
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username BLOB NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('SuperAdmin', 'SystemAdmin', 'ServiceEngineer')),
        is_active INTEGER NOT NULL DEFAULT 1
    );"""

    sql_create_user_profiles_table = """
    CREATE TABLE IF NOT EXISTS UserProfiles (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
    );"""

    sql_create_travellers_table = """
    CREATE TABLE IF NOT EXISTS Travellers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthday TEXT NOT NULL,
        gender TEXT,
        street_name BLOB,
        house_number BLOB,
        zip_code BLOB,
        city BLOB,
        email_address BLOB UNIQUE,
        mobile_phone BLOB,
        driving_license_number TEXT NOT NULL,
        registration_date TEXT NOT NULL
    );"""

    sql_create_scooters_table = """
    CREATE TABLE IF NOT EXISTS Scooters (
        scooter_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        serial_number TEXT NOT NULL UNIQUE,
        top_speed_kmh INTEGER,
        battery_capacity_wh INTEGER,
        soc_percentage REAL,
        target_soc_min REAL,
        target_soc_max REAL,
        location_latitude REAL,
        location_longitude REAL,
        out_of_service INTEGER NOT NULL DEFAULT 0,
        mileage_km REAL NOT NULL DEFAULT 0,
        last_maintenance_date TEXT,
        in_service_date TEXT NOT NULL
    );"""

    sql_create_restore_codes_table = """
    CREATE TABLE IF NOT EXISTS RestoreCodes (
        code_id INTEGER PRIMARY KEY AUTOINCREMENT,
        restore_code TEXT NOT NULL UNIQUE,
        backup_filename TEXT NOT NULL,
        system_admin_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('active', 'used', 'revoked')),
        generated_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY (system_admin_id) REFERENCES Users (user_id) ON DELETE CASCADE
    );"""

    sql_create_logs_table = """
    CREATE TABLE IF NOT EXISTS Logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description BLOB NOT NULL, -- Encrypted
        additional_info BLOB, -- Encrypted
        is_suspicious INTEGER NOT NULL DEFAULT 0,
        is_read INTEGER NOT NULL DEFAULT 0 -- 0 for unread, 1 for read
    );"""

    # create a database connection
    conn = connect_db()

    # create tables
    if conn is not None:
        print("Creating tables...")
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_user_profiles_table)
        create_table(conn, sql_create_travellers_table)
        create_table(conn, sql_create_scooters_table)
        create_table(conn, sql_create_restore_codes_table)
        create_table(conn, sql_create_logs_table)
        print("Tables created successfully (if they didn't already exist).")
        conn.close()
    else:
        print("Error! cannot create the database connection.")


# This block allows you to run this script directly to set up the database.
if __name__ == '__main__':
    initialize_database()

