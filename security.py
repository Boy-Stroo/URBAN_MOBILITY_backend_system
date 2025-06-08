import os
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

# The name of the file where the encryption key is stored.
# IMPORTANT: This file must be kept secret and should NOT be committed to version control.
KEY_FILE = "secret.key"

class SecurityManager:
    """
    Handles all security-related operations like encryption, decryption,
    and password hashing.
    """
    def __init__(self, key_file=KEY_FILE):
        """
        Initializes the SecurityManager. It ensures an encryption key exists,
        loading it or creating a new one if necessary.
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        """
        Loads the encryption key from the key file. If the file doesn't exist,
        it generates a new key and saves it to the file.
        """
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
            print("Security key loaded.")
        else:
            print("No security key found. Generating a new one...")
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            print(f"New security key generated and saved to {self.key_file}.")
        return key

    def encrypt_data(self, data):
        """
        Encrypts a piece of data.

        Args:
            data (str): The plaintext string data to encrypt.

        Returns:
            bytes: The encrypted data as bytes. Returns None if input is invalid.
        """
        if not isinstance(data, str) or not data:
            return None
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt_data(self, encrypted_data):
        """
        Decrypts a piece of data.

        Args:
            encrypted_data (bytes): The encrypted data in bytes.

        Returns:
            str: The decrypted plaintext string. Returns None if decryption fails.
        """
        if not isinstance(encrypted_data, bytes):
            return None
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            # This error occurs if the token is invalid or has been tampered with.
            print("Error: Decryption failed. The data may be corrupt or tampered with.")
            return None

    def hash_password(self, password):
        """
        Hashes a password using bcrypt.

        Args:
            password (str): The plaintext password.

        Returns:
            bytes: The hashed password as bytes, ready for database storage.
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password

    def check_password(self, password, hashed_password):
        """
        Verifies a plaintext password against a stored bcrypt hash.

        Args:
            password (str): The plaintext password to check.
            hashed_password (bytes): The stored hash from the database.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        password_bytes = password.encode('utf-8')
        try:
            # Ensure hashed_password is in bytes format
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_password)
        except (ValueError, TypeError):
            # Handles cases where the hashed_password format is incorrect.
            return False

