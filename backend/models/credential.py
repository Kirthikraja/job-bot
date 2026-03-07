#What happens with credential.py (and the credentials table)
# 1. We store username and password (per site)
# In the DB we store:
# • Username (login id / email — whatever that site uses)
# • Password (stored encrypted, e.g. with Fernet; the model column is password_encrypted)
# So “user id and password” = username and password in this model. Correct.
# 2. We only ask the user when the bot is about to log in and we don’t have credentials yet
# When the bot lands on a login page (LinkedIn, Workday, etc.):
# • We check: do we already have a row in credentials for this site (e.g. site = "linkedin" or "workday_acme")?
# • If no → we ask the user (only this first time for that site).
# • If yes → we use the stored username + decrypted password and don’t ask again.
# 3. Whenever the user gives credentials for a site, we save them here
# When the user submits username + password in the app (because we asked for that site), we:
# • Encrypt the password
# • Insert (or update) a row in the credentials table with site, username, password_encrypted
# So: any time the user provides credentials for a site, they get saved in this table (via credential.py’s model). Next time the bot needs to log in to that same site, we read from here and don’t ask again.

from sqlalchemy import Column, Integer, String #sqlalcmy conent yhton to the a database
from .database import Base


class Credential(Base): 
    __tablename__="credentials"#Sets the actual table name in the database to credentials
    id=Column(Integer,primary_key=True,index=True)
    site=Column(String,unique=True)#e.g. "workday", "greenhouse"
    username=Column(String)
    password_encrypted=Column(String)#encrypted with Fernet