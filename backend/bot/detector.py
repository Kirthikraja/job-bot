# detector.py – LinkedIn job detector.
# This module will contain the agent that:
# - Gets LinkedIn credentials (via credential_manager).
# - Ensures a logged-in LinkedIn session.
# - Navigates to Notifications → Jobs.
# - Reads job notification cards and enqueues jobs.



#step 
from sqlalchemy.orm import Session   # to interact with the database
from .credential_manager import get_linkedin_credentials
from . import queue
import os
import time
from playwright.sync_api import sync_playwright

SESSION_STATE_PATH="linkedin_session.json"


def ensure_linkedin_seesion(username:str, password:str)-> dict:
  
    """
    Ensure we have a valid LinkedIn session (fallback: Playwright).
    - If linkedin_session.json exists and we land on feed (not login), return {"status": "session_ok"}.
    - Else: login with username/password, save storage state, return {"status": "logged_in"}.
    """
    #with is python cleanup it says run syn_playwirgth  , run evrything insdie it and then while levaing the bloack close the file and stop playwirght
    with sync_playwright() as p: # with sync_playwright()  it is async verison . when we call it pyhton waits until the navigatio is done before runing  the next line 
        # Start a Chromium browser (no window). p = Playwright instance. We need a real browser to talk to LinkedIn.
        browser=p.chromium.launch(headless=True)
        # Empty dict to hold options we'll pass to new_context(). We add to it only when session file exists.
        context_option={}
        # Only load saved session if the file exists (e.g. we logged in on a previous run).
        if os.path.exists(SESSION_STATE_PATH):
            # One option: storage_state = path to session file. Tells Playwright "load cookies from this file" when creating context.
            context_option["storage_state"]=SESSION_STATE_PATH
        # Create a context (profile with its own cookies). With storage_state, it starts already logged in. We need a context so we have a place to load the session; pages opened in it will use these cookies.
        context=browser.new_context(**context_option)
        # Open one tab in this context. That tab uses the context's cookies (logged in). We need a page to goto/click; we keep `page` so the rest of the script can control this tab.
        page=context.new_page()

        try:
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded",timeout=30000)
            time.sleep(10)
            url=page.url
            if "/login" not in url and "linkedin.com" in url:
                browser.close()
                return {"status": "session_ok"}
        except Exception :
            pass

        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded",timeout=30000)
        time.sleep(1.5)
        page.get_by_label("Email or phone").fill(username)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Sign in").click()
        page.wait_for_url("**/feed**",timeout=20000)
        context.storage_state(path=SESSION_STATE_PATH)
        browser.close()
        return {"status": "logged_in"}
             























        















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



