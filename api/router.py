from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
import logging
import json
import models
from typing import Annotated
from models.database import engine, SessionLocal
from datetime import timedelta, datetime,  timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decorators.security import signature_required
from config import settings
import models.database
from utils.whatsapp_bot import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)
from starlette import status
from services.auth import pwd_context,ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, create_access_token, create_refresh_token,authenticate_user, validate_refresh_token, RoleChecker
from models.healthcare_provider_model import HealthCareProvider as DBHealthCareProvider
from schema.healthcare_provider_schema import HealthCareProviderSchema, Token
from services.decryption_service import decrypt_and_process_data
models.database.Base.metadata.create_all(bind=engine)

refresh_tokens=[]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

async def handle_message(request: Request):
    try:
        body = await request.json()
        if not body:
            return {"status": "error", "message": "Empty request body"}

        entry = body.get("entry", [{}])[0]
        if "changes" in entry:
            changes = entry["changes"][0]
            logging.info(f"Processing changes: {changes}")
            # return {"status": "processed", "details": changes}
        else:
            logging.info("No 'changes' found in entry.")

        # Validate WhatsApp message structure
        if is_valid_whatsapp_message(body):
            await process_whatsapp_message(body)
            logging.info("Message has been processed successfully.")
            return {"status": "ok"}
        else:
            logging.warning("Invalid WhatsApp message structure.")
            return {"status": "error", "message": "No changes found in the request"}

    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {str(e)}")
        return {"status": "error", "message": "Invalid JSON format"}
    except Exception as e:
        logging.error(f"Unexpected error processing the request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing the message")
    

@router.get("/webhook")
async def webhook_get(mode: str = Query(default=None, alias="hub.mode"),token: str = Query(default=None, alias="hub.verify_token"),challenge: str = Query(default=None, alias="hub.challenge")):
    logging.debug(f"Received mode: {mode}, token: {token}, challenge: {challenge}")
    if mode and token:
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            logging.info("WEBHOOK_VERIFIED")
            return Response(content=challenge, media_type="text/plain") 
        else:
            logging.error("VERIFICATION_FAILED") 
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        logging.error("MISSING_PARAMETERS")
        raise HTTPException(status_code=400, detail="Missing parameters")

@router.post("/webhook")
async def webhook_post(request: Request, auth: bool = Depends(signature_required)):
    return await handle_message(request) 


@router.post("/create/healthcareprovider/", response_model=HealthCareProviderSchema, status_code=status.HTTP_201_CREATED)
async def create_healthcare_provider(provider: HealthCareProviderSchema, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(provider.hashed_password)
    db_provider = DBHealthCareProvider(
        username=provider.username,
        email=provider.email,
        role=provider.role,
        hashed_password=hashed_password,  # Make sure this is hashed!
        is_active=provider.is_active
    )
    try:
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        response_data = jsonable_encoder(db_provider)
        return response_data
    except IntegrityError:
        db.rollback()  # Rollback the session to a clean state
        raise HTTPException(status_code=400, detail="Username already exists. Please use a different username.")
    
    
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires)
    
    refresh_tokens.append(refresh_token)  # Ensure you handle the storage of refresh tokens securely
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(token_data: Annotated[tuple[DBHealthCareProvider, str], Depends(validate_refresh_token)]):
    
    user, token = token_data
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires)
    
    refresh_tokens.remove(token)
    refresh_tokens.append(refresh_token)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/data")
def get_data(_: bool = Depends(RoleChecker(allowed_roles=["admin"]))):
    decrypt_and_process_data('/Users/anishmore/Downloads/whatsapp_bot_api/encrypted_patients.json','decrypted_patients.csv')
    return {"data": "Csv file generated"}