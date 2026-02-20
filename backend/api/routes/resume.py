# from fastapi import APIRouter, UploadFile, File, HTTPException
# from ai.resume_parser import parse_resume, save_parsed_resume, load_parsed_resume
# import shutil
# import os

# router = APIRouter()

# UPLOAD_PATH = "uploads/resume.pdf"

# @router.post("/resume/upload")
# async def upload_resume(file: UploadFile = File(...)):
#     """Upload resume PDF and parse it with Gemini"""
    
#     # Validate file type
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
#     # Save uploaded PDF
#     os.makedirs("uploads", exist_ok=True)
#     with open(UPLOAD_PATH, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
    
#     # Parse with Gemini
#     try:
#         parsed = parse_resume(UPLOAD_PATH)
#         save_parsed_resume(parsed)
#         return {
#             "message": "Resume uploaded and parsed successfully",
#             "data": parsed
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


# @router.get("/resume")
# def get_resume():
#     """Get the currently parsed resume data"""
#     try:
#         data = load_parsed_resume()
#         return {"data": data}
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="No resume uploaded yet")

# FastAPI: router = group of routes; UploadFile = type for uploaded file; File = mark param as file; HTTPException = return 4xx/5xx + message
from fastapi import APIRouter, UploadFile, File, HTTPException

from ai.resume_parser import (
    parse_resume,
    validate_parsed_resume,
    save_parsed_resume,
    load_parsed_resume,
)
import os   
import shutil   # copyfileobj; to save uploaded file bytes to disk

# Group of resume routes; mount in main.py. Path where we save the uploaded PDF and pass to parse_resume.
router = APIRouter()
UPLOAD_PATH = "uploads/resume.pdf"

#step :setting up the router
#post endpoint
@router.post("/resume/upload") #server  running, a request to http://localhost:8000/resume/upload is handled by the function under @router.post("/resume/upload")
# upload_resume = function name (runs on POST /resume/upload). file = param FastAPI fills from request. UploadFile = its type. File(...) = "put request body file in file"
async def upload_resume(file:UploadFile=File(...)):  # async = handler can pause on I/O so server can handle other requests
    """Upload resume PDF and parse it with Gemini"""

    #reject non-pdf so we dont save or parse worng file
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400 , detail="Only PDF files are accepted")
        #400 = bad request
    
    #if uplad folder exist 
    #ensure uploads folder exists so we can save the file
    os.makedirs("uploads",exist_ok=True)

    with open(UPLOAD_PATH,"wb") as buffer: #write binary
        shutil.copyfileobj(file.file,buffer)


    #parse pdf -> validate dict -save to json . failre: return 500 error
    try:
        raw=parse_resume(UPLOAD_PATH)
        validated=validate_parsed_resume(raw) #fuction iside the resume_parse.py
        save_parsed_resume(validated)   
        return {
            "message":"Resume uploaded and parsed successfully",
            "data":validated ,}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
