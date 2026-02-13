from fastapi import APIRouter, UploadFile, File, HTTPException
from ai.resume_parser import parse_resume, save_parsed_resume, load_parsed_resume
import shutil
import os

router = APIRouter()

UPLOAD_PATH = "uploads/resume.pdf"

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume PDF and parse it with Gemini"""
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Save uploaded PDF
    os.makedirs("uploads", exist_ok=True)
    with open(UPLOAD_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse with Gemini
    try:
        parsed = parse_resume(UPLOAD_PATH)
        save_parsed_resume(parsed)
        return {
            "message": "Resume uploaded and parsed successfully",
            "data": parsed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.get("/resume")
def get_resume():
    """Get the currently parsed resume data"""
    try:
        data = load_parsed_resume()
        return {"data": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")