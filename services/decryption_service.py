import json
from services.encryption_service import decrypt_data
import csv

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def decrypt_and_process_data(input_file_path, output_file_path):
    encrypted_data = load_data_from_json(input_file_path)
    decrypted_data = []

    for item in encrypted_data:
        decrypted_record = {}
        for key, value in item.items():
            try:
                decrypted_record[key] = decrypt_data(value)
            except Exception as e:
                print(f"Failed to decrypt {key}: {e}")
                decrypted_record[key] = None  # or use the original encrypted value if preferred
        decrypted_data.append(decrypted_record)

    keys = decrypted_data[0].keys()  # Extract column headers from the first item
    with open(output_file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(decrypted_data)

    return decrypted_data


#decrypted_patients = decrypt_and_process_data('/Users/anishmore/Downloads/whatsapp_bot_api/encrypted_patients.json','decrypted_patients.csv')
