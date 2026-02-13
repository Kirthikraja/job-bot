import fitz  # PyMuPDF
from .gemini import ask_gemini_json
import json
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF resume"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def parse_resume(pdf_path: str) -> dict:
    """
    Extract structured data from resume PDF using Gemini.
    Returns a dict with all key candidate information.
    """
    # Step 1 — Extract raw text from PDF
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        raise ValueError("Could not extract text from resume PDF")

    # Step 2 — Send to Gemini for structured extraction
    prompt = f"""
    You are a resume parser. Extract all relevant information from the resume text below.
    
    Resume Text:
    {raw_text}
    
    Extract and return a JSON object with exactly these fields:
    {{
        "full_name": "candidate full name",
        "email": "email address",
        "phone": "phone number",
        "location": "city, country",
        "linkedin_url": "linkedin profile url or empty string",
        "summary": "professional summary or objective in 2-3 sentences",
        "skills": ["skill1", "skill2", "skill3"],
        "languages": ["language1", "language2"],
        "education": [
            {{
                "degree": "degree name",
                "field": "field of study",
                "institution": "university or school name",
                "graduation_year": "year or expected year",
                "gpa": "gpa or empty string"
            }}
        ],
        "experience": [
            {{
                "title": "job title",
                "company": "company name",
                "duration": "start - end dates",
                "description": "brief description of responsibilities"
            }}
        ],
        "projects": [
            {{
                "name": "project name",
                "description": "what it does and tech used"
            }}
        ],
        "certifications": ["certification1", "certification2"],
        "job_preference": "internship or full-time or both",
        "visa_required": false
    }}
    """
    
    return ask_gemini_json(prompt)


def save_parsed_resume(parsed_data: dict, save_path: str = "backend/uploads/parsed_resume.json"):
    """Save parsed resume data as JSON for other components to use"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as f:
        json.dump(parsed_data, f, indent=2)
    print(f"Resume parsed and saved to {save_path}")


def load_parsed_resume(save_path: str = "backend/uploads/parsed_resume.json") -> dict:
    """Load previously parsed resume data"""
    if not os.path.exists(save_path):
        raise FileNotFoundError("No parsed resume found. Please upload your resume first.")
    with open(save_path, "r") as f:
        return json.load(f)