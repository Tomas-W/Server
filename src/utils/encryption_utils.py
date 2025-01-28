import json
import os

from cryptography.fernet import Fernet

from config.settings import Environ


def get_key() -> bytes:
    """Load the encryption key from an environment variable."""
    key = os.environ.get("ENCRYPTION_KEY")
    if key is None:
        raise ValueError("Encryption key not found in environment variables.")
    return key.encode()  # Ensure it's in bytes


def encrypt_data(data: bytes) -> bytes:
    """Encrypt the given data using the key from environment variables."""
    key = get_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data


def decrypt_data(encrypted_data: bytes) -> bytes:
    """Decrypt the given data using the key from environment variables."""
    key = get_key()
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data


def encrypt_json_file(file_path: str) -> None:
    """Encrypts the JSON data in the specified file."""
    # Load the encryption key from environment variables

    # Read the existing JSON data
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return

    # Encrypt the data
    encrypted_data = encrypt_data(json.dumps(data).encode())

    # Write the encrypted data back to the file
    with open(file_path, "wb") as json_file:  # Open in binary mode
        json_file.write(encrypted_data)

    print(f"Successfully encrypted the JSON data in {file_path}")
