from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

Base = declarative_base()

# Define a Patient model
class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    full_name = Column(String)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    address = Column(String)
    medical_history = Column(String)
    current_medications = Column(String)

# Setup the database connection and sessionmaker
engine = create_engine('sqlite:///./test.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)  # Create tables

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
