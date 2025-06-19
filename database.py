import sqlite3
from sqlite3 import Error
import uuid

# Define the name of the database file
DATABASE_NAME = "urban_mobility.db"


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
        user_id TEXT PRIMARY KEY,
        username BLOB NOT NULL UNIQUE,
        password_hash BLOB NOT NULL,
        role BLOB NOT NULL,
        is_active BLOB NOT NULL DEFAULT 1
    );"""

    sql_create_user_profiles_table = """
    CREATE TABLE IF NOT EXISTS UserProfiles (
        profile_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL UNIQUE,
        first_name BLOB,
        last_name BLOB,
        registration_date BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
    );"""

    sql_create_travellers_table = """
    CREATE TABLE IF NOT EXISTS Travellers (
        customer_id TEXT PRIMARY KEY,
        first_name BLOB NOT NULL,
        last_name BLOB NOT NULL,
        birthday BLOB NOT NULL,
        gender BLOB,
        street_name BLOB,
        house_number BLOB,
        zip_code BLOB,
        city BLOB,
        email_address BLOB UNIQUE,
        mobile_phone BLOB,
        driving_license_number BLOB NOT NULL,
        registration_date BLOB NOT NULL
    );"""

    sql_create_scooters_table = """
    CREATE TABLE IF NOT EXISTS Scooters (
        scooter_id TEXT PRIMARY KEY,
        brand BLOB NOT NULL,
        model BLOB NOT NULL,
        serial_number BLOB NOT NULL UNIQUE,
        top_speed_kmh BLOB,
        battery_capacity_wh BLOB,
        soc_percentage BLOB,
        target_soc_min BLOB,
        target_soc_max BLOB,
        location_latitude BLOB,
        location_longitude BLOB,
        out_of_service BLOB NOT NULL DEFAULT 0,
        mileage_km BLOB NOT NULL DEFAULT 0,
        last_maintenance_date BLOB,
        in_service_date BLOB NOT NULL
    );"""

    sql_create_restore_codes_table = """
    CREATE TABLE IF NOT EXISTS RestoreCodes (
        code_id TEXT PRIMARY KEY,
        restore_code BLOB NOT NULL UNIQUE,
        backup_filename BLOB NOT NULL,
        system_admin_id TEXT NOT NULL,
        status BLOB NOT NULL,
        generated_at BLOB NOT NULL,
        expires_at BLOB NOT NULL,
        FOREIGN KEY (system_admin_id) REFERENCES Users (user_id) ON DELETE CASCADE
    );"""

    sql_create_logs_table = """
    CREATE TABLE IF NOT EXISTS Logs (
        log_id TEXT PRIMARY KEY,
        timestamp BLOB NOT NULL,
        username BLOB NOT NULL,
        event_type BLOB NOT NULL,
        description BLOB NOT NULL,
        additional_info BLOB,
        is_suspicious BLOB NOT NULL DEFAULT 0,
        is_read BLOB NOT NULL DEFAULT 0 -- 0 for unread, 1 for read
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
