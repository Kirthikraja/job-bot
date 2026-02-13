from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    role = Column(String)
    apply_url = Column(String, unique=True)
    ats_type = Column(String)
    status = Column(String, default="pending")
    is_internship = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=func.now())