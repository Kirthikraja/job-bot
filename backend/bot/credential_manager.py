# credential_manager.py – helpers for storing and reading site credentials.
# Detector / application engine use this to get LinkedIn (and later Workday, etc.) logins
# from the database in a safe, consistent way.

#We want the bot to log into LinkedIn (and other sites) in a safe, low-friction way:
#
# 1. Preferred: use a saved SESSION (cookies)
#    - First time: we log in once (manually or via the bot), then save the session
#      to something like session.json (or a DB row).
#    - Next runs: we load that session into the browser (Browserbase/Playwright),
#      so we are already logged in and do NOT need to type the password again.
#    - This is less suspicious to LinkedIn than logging in with username/password
#      on every run.
#
# 2. Fallback: use stored USERNAME + PASSWORD
#    - If we do not have a valid session (no session saved, or LinkedIn says we are
#      logged out), then we fall back to credentials stored in the credentials table.
#    - credential_manager will provide helpers like get_linkedin_credentials(db)
#      that:
#         - Look up the row where site == "linkedin" in the Credential model.
#         - If no row → return None (the bot must ask the user for creds).
#         - If row exists → return (username, password) so the bot can log in and
#           then save a new session.
#
# In short:
# - credential_manager is the single place where agents ask for "do we have
#   LinkedIn login info?".
# - Most of the time we will rely on sessions; the username/password path is
#   only used when we cannot log in through the saved session.


from sqlalchemy.orm import Session
from models.credential import Credential


def get_linkedin_credentials(db: Session):
    

        """
    Look up LinkedIn credentials in the credentials table.
    Returns:
        (username, password) tuple if we have a row for site == "linkedin",
        or None if no such credential exists yet.
    For now we just return the stored password_encrypted as-is.
    Later we will decrypt it with Fernet before returning.
    """
        #find the credential row where th site is
        cred=db.query(Credential).filter(Credential.site=="linkedin").first()

        if cred is None:
            # We have never saved LinkedIn credentials in the DB.
        # The detector should treat this as "missing_linkedin_credentials"
        # and ask the user (via the chat/UI) to provide them.
            return None

        username=cred.username
        password=cred.password_encrypted
        return username, password


    