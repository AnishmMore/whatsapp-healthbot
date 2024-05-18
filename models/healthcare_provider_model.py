from sqlalchemy import Column, Integer, String, Boolean
from models.database import Base

class HealthCareProvider(Base):
    __tablename__ = 'healthcareproviders'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    # address = Column(String, nullable=True)
    # phone_number = Column(String, nullable=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)  # Added for authentication
    role = Column(String, nullable=False)  # Added for role-based access control
    is_active = Column(Boolean, default=False)




