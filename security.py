import os
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = "secret.key"

class SecurityManager:
    def __init__(self, key_file=KEY_FILE):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
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
        if not isinstance(data, str) or not data:
            return None
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt_data(self, encrypted_data):
        if not isinstance(encrypted_data, bytes):
            return None
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            print("Error: Decryption failed. The data may be corrupt or tampered with.")
            return None

    def hash_password(self, password):
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password

    def check_password(self, password, hashed_password):
        password_bytes = password.encode('utf-8')
        try:
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_password)
        except (ValueError, TypeError):
            return False
