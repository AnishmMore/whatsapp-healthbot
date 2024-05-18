from pydantic import BaseModel, EmailStr

class HealthCareProviderSchema(BaseModel):
    username: str
    email: EmailStr # Using EmailStr for better validation
    role: str
    is_active: bool = False  # Defaulting to False is common for user models
    hashed_password: str 

class Token(BaseModel):
    access_token: str 
    refresh_token: str
