from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)
    company = Column(String)
    role = Column(String)
    ats_type = Column(String)
    apply_url = Column(String)
    status = Column(String)        # applied / failed / action_needed
    result = Column(String)
    ai_extracted_skills = Column(String)
    screenshot_path = Column(String)
    applied_at = Column(DateTime, default=func.now())