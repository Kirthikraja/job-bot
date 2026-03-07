# Credentials API (routes/credentials.py)
#
# This file defines the HTTP endpoints for saving and reading login credentials
# (site, username, password) that the bot uses when it hits a login page.
#
# - POST: Save or update credentials for a site.
#   The client sends site, username, and password. We encrypt the password,
#   then insert or update a row in the credentials table.
#   Used when the user submits their login (e.g. first time the bot needs that site).
#
# - GET: Check if we have credentials for a site, or list all saved sites.
#   With a site (e.g. query param): return that credential (for the bot to log in).
#   Without: return a list of saved sites (e.g. for the UI to show "you have logins for: ...").
#
# Data is stored in the credentials table (Credential model). Encryption/decryption
# of the password is done before save and when the bot needs to use it.
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.credential import Credential
from models.database import get_db

router=APIRouter(prefix="/credentials",tags=["credentials"])



class CredentialRequest(BaseModel):
    site:str;
    username:str;
    password:str;


# POST /credentials: User submits site, username, password (e.g. when bot needs login for that site).
# We look up if we already have a row for this site. If yes, we update username and password; if no,
# we create a new Credential row. Password is stored in DB (TODO: encrypt with Fernet later).
# Returns a short message and the site name.
@router.post("",status_code=201)
def save_credential(body:CredentialRequest,db:Session=Depends(get_db)):
    """Save a new credential or update an existing one"""
    existing=db.query(Credential).filter(Credential.site==body.site).first()
    password_stored = body.password  # TODO: encrypt with Fernet before storing 
    if existing:
        existing.username=body.username
        existing.password_encrypted=password_stored
        db.commit()
        return{"message":"Credential saved successfully","site":body.site}
    cred=Credential(site=body.site,username=body.username,password_encrypted=password_stored)
    db.add(cred)
    db.commit()
    return{"message":"Credential saved successfully","site":body.site}