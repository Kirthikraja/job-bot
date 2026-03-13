# detector.py – LinkedIn job detector.
# This module will contain the agent that:
# - Gets LinkedIn credentials (via credential_manager).
# - Ensures a logged-in LinkedIn session.
# - Navigates to Notifications → Jobs.
# - Reads job notification cards and enqueues jobs.



#step 
from sqlalchemy.orm import Session   # to interact with the database
from . credential_manager import get_linkedin_credentials
from . import queue
import os
from playwright.sync_api import sync_playwright

SESSION_STATE_PATH="linkedin_session.json"


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
    creds=get_linkedin_credentials(db)
    if creds is None:
        # We don't have LinkedIn creds yet.
        # The caller (LLM/chat) should see this and ask the user to provide them,
        # then save via the credentials API.
        return{"status": "missing_linkedin_credentials"}

    username, password=creds
    # Step 2 (stub for now): ensure we have a logged-in LinkedIn session.
    # Later this will use Browserbase + Stagehand / browser-use + Claude to
    # either load a saved session or log in with username/password.
    session_info=ensure_linkedin_session(username, password)
    notification_state=open_linkedin_notifications_jobs()

    return {
        "status": "credentials_available",
        "username": username,
        "session": session_info,      #Note: nevr return the password here
        "notification":notification_state
    }



def open_linkedin_notifications(session_info:dict):
    """
    Stub helper for navigating to the LinkedIn Notifications → Jobs tab.
    Eventually this function will:
      - Use the active browser/session (e.g. Browserbase + Playwright + Stagehand)
        to open https://www.linkedin.com/notifications/.
      - Click on the "Jobs" filter/tab at the top of the notifications page.
      - Scroll the list to load all recent job alert cards.
    For now it just returns a dummy value so we can see that the flow reaches here.
    """
    return {"status": "notifications_jobs_stub"}



