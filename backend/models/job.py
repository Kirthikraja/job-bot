# job.py: Defines the Job model (SQLAlchemy). This is the schema for the "jobs" table
# where we store each job the detector finds (company, role, apply_url, status, etc.).
# The table is created in the DB when the app starts (init_db in models/__init__.py).
# Used by: detector/queue (to save jobs), resolver and rest of pipeline (to read/update them).

#SQLAlchemy is a Python library for talking to databases
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base  # calaling database.py to get the Base class



#step: job class and collumn

#table designing 

class Job(Base):
    __tablename__ = "jobs"  # name of the table in the database

    id=Column(Integer, primary_key=True,index=True)
    role= Column(String )
    source_url=Column(String,nullable=False)
    apply_url=Column(String,unique=True,nullable=True)
    ats_type=Column(String)
    status=Column(String,default="pending")
    is_internship=Column(String)
    location=Column(String)
    company=Column(String)
    description=Column(String)
    created_at=Column(DateTime,default=func.now())





  # this file define the schema/ shape of the jobs table . it does not store or read   



