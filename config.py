import sys
import os
from dotenv import load_dotenv
import logging
from pydantic import BaseSettings

# Load the environment variables from the .env file
load_dotenv()

class Settings(BaseSettings):
    ACCESS_TOKEN: str
    APP_ID: str
    APP_SECRET: str
    RECIPIENT_WAID: str
    VERSION: str
    PHONE_NUMBER_ID: str
    VERIFY_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"

settings = Settings()

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )