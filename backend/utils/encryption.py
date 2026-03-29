from cryptography.fernet import Fernet
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# Generate a proper Fernet key if not provided
if not ENCRYPTION_KEY or len(ENCRYPTION_KEY) < 32:
    # For development, generate a key
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️  Warning: Using generated encryption key. Set ENCRYPTION_KEY in .env for production.")
else:
    # Ensure the key is properly formatted for Fernet
    try:
        # Try to use it directly
        if len(ENCRYPTION_KEY) == 44 and ENCRYPTION_KEY.endswith('='):
            # Already a valid Fernet key
            pass
        else:
            # Pad to 32 bytes and base64 encode
            key_bytes = ENCRYPTION_KEY.encode().ljust(32)[:32]
            ENCRYPTION_KEY = base64.urlsafe_b64encode(key_bytes).decode()
    except Exception as e:
        ENCRYPTION_KEY = Fernet.generate_key().decode()
        print(f"⚠️  Warning: Invalid encryption key, using generated one: {e}")

cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return data
    encrypted = cipher_suite.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return encrypted_data
    try:
        decrypted = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return "***ENCRYPTED***"

def mask_account_number(account_number: str) -> str:
    """Mask account number for display (show only last 4 digits)"""
    if len(account_number) <= 4:
        return "*" * len(account_number)
    return "*" * (len(account_number) - 4) + account_number[-4:]