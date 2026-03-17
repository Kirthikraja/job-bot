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

# ensure_linkedin_seesion = ensure we have a saved LinkedIn session we can use later.
    # If the session file exists and is still valid (we land on the feed, not the login page)
    #   -> we already have a saved session; return {"status": "session_ok"}.
    # If the file is missing or the session is invalid
    #   -> log in with username/password, save the new session to linkedin_session.json, return {"status": "logged_in"}.
    # So after it runs, we always have a valid saved session: either we reused the existing one or we just created and saved one.


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






#step:It uses the saved LinkedIn session to open LinkedIn, go to Notifications, then switch to the Jobs tab so we’re on the “Jobs notifications” list (the one with cards like “32m”, “4h”, etc.).

# Step by step:

# Start a browser (Playwright, headless).
# Load the saved session from linkedin_session.json into a new context so we’re already logged in.
# Open one tab in that context.
# Go to https://www.linkedin.com/notifications/.
# Click the “Jobs” tab on that page (so we’re on the Jobs sub-tab, not “All” or “My posts”).
# Wait a bit for the list of job notification cards to load.
# Return a status (e.g. {"status": "ok", "url": ...}) and close the browser.


def open_linkedin_notifications():
    """
    Load saved session, go to Notifications, click the Jobs tab.
    Returns {"status": "ok", "url": ...} on success, or {"status": "error", "message": ...} on failure.
    """

    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context_option={}
        if os.path.exists(SESSION_STATE_PATH):
            context_option["storage_state"]=SESSION_STATE_PATH
        context=browser.new_context(**context_option)
        page=context.new_page()

        try:
            page.goto("https://www.linkedin.com/notifications/", wait_until="domcontentloaded",timeout=30000)
            time.sleep(2)
            ## Click the Jobs tab (notifications sub-tab). Adjust selector if LinkedIn's DOM differs.
            page.get_by_role("tab",name="Jobs").click()
            time.sleep(3)
            url=page.url
            browser.close()
            return{"status": "ok", "url": url}
        except Exception as e:
            browser.close()
            return{"status": "error", "message": str(e)}





             























        

















