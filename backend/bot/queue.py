# queue.py – Job queue for the pipeline.
#
# What this file does:
#   • add_job(db, ...) – Inserts a new job into the jobs table. Called by the detector when it sees
#     a job (e.g. on LinkedIn); we store role, source_url, apply_url, company, etc. with status "pending".
#   • list_pending_jobs(db) – Returns all jobs where status is "pending", ordered by created_at.
#     Called by the resolver or application engine when they need the next jobs to process.
#
# Jobs are stored in the database (jobs table defined in models/job.py). The caller must pass a
# DB session (e.g. from get_db() or SessionLocal()). We do not run on our own; detector/pipeline call us.


from models.job import Job
from typing import Optional
from sqlalchemy.orm import Session

# Job is the model from job.py (id, role, source_url, apply_url, status, company, etc.).
# We use it here to build new rows (job = Job(...)) and in queries (db.query(Job).filter(...)).

def add_job(
    db:Session,
    role:str,
    source_url:str,
    apply_url:Optional[str]=None,
    ats_type:Optional[str]=None,
    status:str="pending",
    is_internship:Optional[str]=None,
    company:Optional[str]=None,
    description:Optional[str]=None,

):

    """Insert a new job into the jobs table.""" 
    job=Job(
        role=role,
        source_url=source_url,
        apply_url=apply_url,
        ats_type=ats_type,
        status=status,
        is_internship=is_internship,
        company=company,
        description=description,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_pending_jobs(db:Session):
    """Return all jobs where status is "pending", ordered by created_at."""
    return db.query(Job).filter(Job.status=="pending").order_by(Job.created_at.desc()).all()
    