# detector.py – LinkedIn job detector.
# This module will contain the agent that:
# - Gets LinkedIn credentials (via credential_manager).
# - Ensures a logged-in LinkedIn session.
# - Navigates to Notifications → Jobs.
# - Reads job notification cards and enqueues jobs.



#step 
from sqlalchemy.orm import Session   # to interact with the database
from .credential_manager import get_linkedin_credentials
from .import queue


#step 
def detect_jobs_from_linkedin(db: Session):
    """
    High-level entrypoint for the detector agent.
    Current responsibility:
      1. Try to get LinkedIn credentials.
      2. If missing → tell the caller so the LLM/chat can ask the user.
      3. If present → tell the caller that we can proceed to login/navigation next.
    """

    #step1: try to get linkedin credentials
    creds=get_linkedin_Credentials(db)
    if creds is None:
        # We don't have LinkedIn creds yet.
        # The caller (LLM/chat) should see this and ask the user to provide them,
        # then save via the credentials API.
        return{"status": "missing_linkedin_credentials"}

    username, password=creds
    # TODO: next steps will use username/password to open a browser session,
    # log into LinkedIn, navigate to notifications, and extract jobs.
    # For now we just return a stub so we can wire the credentials flow first.

    return {
        "status": "logged_in_linkedin",
        "username": username,
        #Note: nevr return the password here
    }


