import json
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv,set_key
import base64

load_dotenv()
# key = Fernet.generate_key()
# f = Fernet(key)
# cipher_suite = f
# with open('encryptionkey.key', 'wb') as file:
#    file.write(key)

with open('/Users/anishmore/Downloads/whatsapp_bot_api/services/encryptionkey.key', 'rb') as f:
   key = f.read()
   
f = Fernet(key)
cipher_suite = f

def encrypt_data(plain_text: str) -> str:
    """Encrypt data."""
    try:
        encrypted_text = cipher_suite.encrypt(plain_text.encode())
        return encrypted_text.decode()
    except Exception as e:
        print(f"Encryption failed: {e}")
        return None  

def decrypt_data(encrypted_text: str) -> str:
    """Decrypt data."""
    decrypted_text = cipher_suite.decrypt(encrypted_text.encode())
    return decrypted_text.decode()

# Function to save data to JSON
def save_data_to_json(file_path, new_data):
    try:
        # Check if the file already exists and has data
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    data.append(new_data)
                else:
                    data = [data, new_data]
        else:
            data = [new_data]

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}")

    except Exception as e:
        print(f"Failed to save data to {file_path}: {e}")


def encrypt_and_save_patient_data(patient_info, file_path='encrypted_patients.json'):
    print(f"Received patient info for encryption: {patient_info}")
    if patient_info:
        encrypted_data = {key: encrypt_data(str(value)) for key, value in patient_info.items()}
        save_data_to_json(file_path, encrypted_data)
    else:
        print("No patient info available to encrypt and save.")
