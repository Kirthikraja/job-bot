from sqlalchemy import Column, Integer, String
from .database import Base

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String, unique=True)   # e.g. "workday", "greenhouse"
    username = Column(String)
    password_encrypted = Column(String)  # encrypted with Fernet