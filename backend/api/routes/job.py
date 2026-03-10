# job.py – HTTP API for the job queue.
#
# This file exposes the job queue over HTTP so that:
#   • GET /jobs/pending – Returns all jobs with status "pending" (uses list_pending_jobs from bot.queue).
#   • POST /jobs – Creates a new job in the DB (uses add_job from bot.queue).
#
# Used by: frontend (to list or add jobs), detector (to add jobs via API), pipeline (to fetch pending jobs).
# The actual add/list logic lives in bot/queue.py; this file is only the HTTP layer.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional


from models .database import get_db# get_db: FastAPI dependency that opens a DB session per request and closes it after the response
from bot.queue import add_job,list_pending_jobs


#step: setting up the router

router =APIRouter()

#step: define the model for the job

# Same fields as add_job in queue.py: API body (JobCreate) is passed through to add_job so one row is inserted.
class JobCreate(BaseModel):
    role:str;
    source_url:str;
    apply_url:Optional[str]=None;
    ats_type:Optional[str]=None;
    status:str="pending";
    is_internship:Optional[str]=None;
    company:Optional[str]=None;
    description:Optional[str]=None;


#step: define the route for the pending jobs
router.get("/jobs/pending") # GET /jobs/pending: Returns all jobs with status "pending" (uses list_pending_jobs from bot.queue).
def get_pending_jobs(db:Session=Depends(get_db)):
    """Return all jobs where status is "pending", ordered by created_at."""
    jobs=list_pending_jobs(db)
    return [#list of jobs in the format of the API response
        {
            "id":j.id,
            "role":j.role,
            "source_url":j.source_url,
            "apply_url":j.apply_url,
            "ats_type":j.ats_type,
            "status":j.status,
            "is_internship":j.is_internship,
            "company":j.company,
            "description":j.description,
            "created_at":j.created_at.isoformat() if j.created_at else None,

        }
        for j in jobs
    ]


#step: define the route for the new job
@router.post("/jobs") # #When someone sends a POST request to the path /jobs, run the function POST /jobs: Creates a new job in the DB (uses add_job from bot.queue).
def create_job(job:JobCreate,db:Session=Depends(get_db)):
    """Create a new job in the queu(eg form fetector or frontend)."""
    try:
        job=add_job(
            db,
            role=job.role,
            source_url=job.source_url,
            apply_url=job.apply_url,
            ats_type=job.ats_type,
            status=job.status,
            is_internship=job.is_internship,
            company=job.company,
            description=job.description,
        )	
        return {
            "id":job.id,
            "role":job.role,
            "source_url":job.source_url,
            "apply_url":job.apply_url,
            "ats_type":job.ats_type,
            "status":job.status,
            "is_internship":job.is_internship,
            "company":job.company,
            "description":job.description,
            "created_at":job.created_at.isoformat() if job.created_at else None,
        }

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to create job: {str(e)}")