from fastapi import HTTPException
import logging
import httpx
import json
import re
from typing import Dict
from pydantic import BaseModel, validator
from datetime import datetime
from config import settings
from services.encryption_service import encrypt_and_save_patient_data

patient_info = {}

class PatientInput(BaseModel):
    user_id: str
    input_data: str

    @validator('input_data', pre=True, always=True)
    def validate_data(cls, v, values, **kwargs):
        return v

async def collect_patient_data(input: PatientInput):
    user_id = input.user_id
    input_data = input.input_data.strip().lower() 
    stages = ["welcome", "full_name", "date_of_birth", "gender", "address", "medical_history", "current_medications", "confirm", "completed"]
    options = ", ".join([s.replace('_', ' ') for s in stages[1:-2]])

    if user_id not in patient_info or patient_info[user_id]["stage"] == "completed":
        if input_data == "restart":
            patient_info[user_id] = {"stage": "welcome", "data": {}, "updating_info": False}
            return await send_message(user_id, "Welcome back! Would you like to share your information again? (yes/no)")
        return await send_message(user_id, "Thank you for your previous participation. Type 'restart' to begin again.")

    current_stage = patient_info[user_id]["stage"]
    
    if current_stage == 'date_of_birth':
        try:
            datetime.strptime(input_data, '%Y-%m-%d')
        except ValueError:
            return await send_message(user_id, "Date of Birth must be in YYYY-MM-DD format. Please try again.")
    
    if current_stage == 'gender':
        if input_data not in ['male', 'female', 'other']:
            return await send_message(user_id, "Gender must be 'male', 'female', or 'other'. Please try again.")

    # If user is at the welcome stage
    if current_stage == "welcome":
        if input_data == "yes":
            patient_info[user_id]["stage"] = stages[1]  # Move to the next stage
            return await prompt_for_next_stage(user_id, stages[1])
        else:
            patient_info[user_id]["stage"] = "completed"
            return await send_message(user_id, "Thank you for your interest. Feel free to contact us anytime.")

    # Handle data input for stages and transition through stages
    if current_stage in stages[1:-2]:
        patient_info[user_id]["data"][current_stage] = input_data
        if patient_info[user_id]["updating_info"]:  # If updating, redirect back to confirm
            patient_info[user_id]["stage"] = "confirm"
            return await prompt_for_next_stage(user_id, "confirm")
        else:
            next_stage_index = stages.index(current_stage) + 1
            patient_info[user_id]["stage"] = stages[next_stage_index]
            return await prompt_for_next_stage(user_id, stages[next_stage_index])

    # Handle the confirmation stage
    if current_stage == "confirm":
        if input_data == "no":
            patient_info[user_id]["stage"] = "completed"
            logging.info(f"Patient data before saving: {patient_info[user_id]['data']}")
            encrypt_and_save_patient_data(patient_info[user_id]["data"])
            return await send_message(user_id, "Thank you for providing your information. We will be in touch soon!")
        elif input_data == "yes":
            return await send_message(user_id, f"Which information would you like to change? (Options: {options})")

    if input_data in [s.replace('_', ' ') for s in stages[1:-2]]: 
        specific_stage = input_data.replace(' ', '_')
        patient_info[user_id]["stage"] = specific_stage
        patient_info[user_id]["updating_info"] = True
        return await send_message(user_id, f"Please enter your new {input_data}:")
        
    error_response = f"I didn't understand that. Please try again."
    if current_stage == "confirm":
        error_response += f"To change details, specify the section: {options}."

    return await send_message(user_id,error_response)

async def prompt_for_next_stage(user_id, stage):
    
    existing_data = patient_info[user_id]["data"].get(stage, "")

    if stage == "completed":
        return await send_message(user_id, "Thank you for your interest. Feel free to contact us anytime.")

    if stage == "confirm":
        user_data = patient_info[user_id]["data"]
        user_data_formatted = "\n".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in user_data.items())
        confirmation_prompt = f"Please review your information:\n{user_data_formatted}\nWould you like to change anything? (yes/no)"
        return await send_message(user_id, confirmation_prompt)
    
    question_prompts = {
        "full_name": "Please enter your full name.",
        "date_of_birth": "Please enter your date of birth (YYYY-MM-DD).",
        "gender": "Please specify your gender (male, female, or other).",
        "address": "Please enter your address.",
        "medical_history": "Please list any medical history, such as allergies or previous surgeries.",
        "current_medications": "Please list your current medications.",
    }
    response = question_prompts.get(stage)
    if not response:  # Handle unexpected stage or missing prompt
        logging.warning(f"Unexpected stage '{stage}' for user {user_id}.")
        return await send_message(user_id, "I didn't understand that. Could you please repeat?")
    
    return await send_message(user_id, response)


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    })

def generate_response(response):
    return response.upper()

async def send_message(recipient: str, text: str):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
    }
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"body": text}
    })

    url = f"https://graph.facebook.com/{settings.VERSION}/{settings.PHONE_NUMBER_ID}/messages"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
def process_text_for_whatsapp(text):
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    whatsapp_style_text = re.sub(pattern, replacement, text)
    return whatsapp_style_text

async def process_whatsapp_message(body):
    try:
        if not is_valid_whatsapp_message(body):
            raise HTTPException(status_code=400, detail="Invalid WhatsApp message structure")

        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        #name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        if wa_id in patient_info:
            await collect_patient_data(PatientInput(user_id=wa_id, input_data=message_body))
        else:
            patient_info[wa_id] = {"stage": "welcome", "data": {}, "updating_info": False}
            return await send_message(wa_id, "Welcome to Turmerik. I'll be taking your clinical information today. You can edit your answers at the end by simply re-entering the option name (e.g full name, date of birth, gender, address, medical history, current medications). Would you like to share your information? (yes/no)")
        
    except Exception as e:
        logging.error(f"Failed to process WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

def is_valid_whatsapp_message(body):
    if body.get("object") != "whatsapp_business_account":
        return False
    if not body.get("entry"):
        return False
    
    for entry in body["entry"]:
        for change in entry.get("changes", []):
            if change.get("field") == "messages" and change.get("value", {}).get("messages"):
                return True
    return False
