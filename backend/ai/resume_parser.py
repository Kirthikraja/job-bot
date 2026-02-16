# import fitz  # PyMuPDF
# from .gemini import ask_gemini_json
# import json
# import os

# def extract_text_from_pdf(pdf_path: str) -> str:
#     """Extract raw text from a PDF resume"""
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     doc.close()
#     return text.strip()

# def parse_resume(pdf_path: str) -> dict:
#     """
#     Extract structured data from resume PDF using Gemini.
#     Returns a dict with all key candidate information.
#     """
#     # Step 1 — Extract raw text from PDF
#     raw_text = extract_text_from_pdf(pdf_path)
    
#     if not raw_text:
#         raise ValueError("Could not extract text from resume PDF")

#     # Step 2 — Send to Gemini for structured extraction
#     prompt = f"""
#     You are a resume parser. Extract all relevant information from the resume text below.
    
#     Resume Text:
#     {raw_text}
    
#     Extract and return a JSON object with exactly these fields:
#     {{
#         "full_name": "candidate full name",
#         "email": "email address",
#         "phone": "phone number",
#         "location": "city, country",
#         "linkedin_url": "linkedin profile url or empty string",
#         "summary": "professional summary or objective in 2-3 sentences",
#         "skills": ["skill1", "skill2", "skill3"],
#         "languages": ["language1", "language2"],
#         "education": [
#             {{
#                 "degree": "degree name",
#                 "field": "field of study",
#                 "institution": "university or school name",
#                 "graduation_year": "year or expected year",
#                 "gpa": "gpa or empty string"
#             }}
#         ],
#         "experience": [
#             {{
#                 "title": "job title",
#                 "company": "company name",
#                 "duration": "start - end dates",
#                 "description": "brief description of responsibilities"
#             }}
#         ],
#         "projects": [
#             {{
#                 "name": "project name",
#                 "description": "what it does and tech used"
#             }}
#         ],
#         "certifications": ["certification1", "certification2"],
#         "job_preference": "internship or full-time or both",
#         "visa_required": false
#     }}
#     """
    
#     return ask_gemini_json(prompt)


# def save_parsed_resume(parsed_data: dict, save_path: str = "backend/uploads/parsed_resume.json"):
#     """Save parsed resume data as JSON for other components to use"""
#     os.makedirs(os.path.dirname(save_path), exist_ok=True)
#     with open(save_path, "w") as f:
#         json.dump(parsed_data, f, indent=2)
#     print(f"Resume parsed and saved to {save_path}")


# def load_parsed_resume(save_path: str = "backend/uploads/parsed_resume.json") -> dict:
#     """Load previously parsed resume data"""
#     if not os.path.exists(save_path):
#         raise FileNotFoundError("No parsed resume found. Please upload your resume first.")
#     with open(save_path, "r") as f:
#         return json.load(f)


import fitz  # PyMuPDF
from .gemini import ask_gemini_json
import json
import os

#step 1: extract the text from the pdf file(resume) using PyMuPDF

#pdf_path : is the path to pdf file , and the value is the string 
def extract_text_from_pdf(pdf_path:str) -> str:
    doc=fitz.open(pdf_path)
    text=""  #resume text stored in this
    for page in doc:
        text= text + page.get_text()  #get the text from get_text()
    doc.close()
    return text.strip() # removing the extra spaces and new lines


#step 2: parse the resume text using Gemini and return a json  object
def parse_resume (pdf_path :str)-> dict:

    raw_text=extract_text_from_pdf(pdf_path) #get the extracted resume text

    if not raw_text:
        raise ValueError("Could not extract text from your resume pdf") 

    prompt=f"""
You are a resume parser. The resume may have any structure or section names. Extract whatever is present.

Resume text:
{raw_text}

Return a JSON object with exactly these keys. Use empty string "" or empty list [] if not found.
- full_name (string)
- email (string)
- phone (string)
- location (string)
- linkedin_url (string)
- github_url (string)
- portfolio_url (string)
- other_urls (list of strings)
- summary (string)
- skills (list of strings)
- languages (list of strings)
- education (list of objects: degree, field, institution, graduation_year, gpa)
- experience (list of objects: title, company, duration, description)
- projects (list of objects: name, description)
- certifications (list of strings)
- job_preference (string: "internship" or "full-time" or "both")
- visa_required (boolean)
"""
    return ask_gemini_json(prompt) # its a function  is ai/gemini.py whichh takes a string(prompt above) sends that to gemii api and get geimini text reply and returns a dictionary





#step 3: validate the json object . make sure that the dictionary return form gemini has the shape and types your app expects , and if not fix it 
def validate_parsed_resume(data:dict)->dict:  #data: parameter name , dict: parameter type hint 
    #all expected keys exist and types are correct. Return a clean dict.


    #keys that must be string
    string_keys=["full_name", "email", "phone", "location", "linkedin_url", "summary",
        "job_preference", "github_url", "portfolio_url"]

    #keys that must  be list 
    list_keys=["skills", "languages", "other_urls"]
    # Keys that must be list of objects

    list_of_obj_keys=["education", "experience", "projects", "certifications"]
    
    # Keys that must be bool
    bool_keys=["visa_required"]

    out= dict(data)

    for k in string_keys:
        if k not in out or out[k] is None: # if the the key is missing (gemini didnt returnit ) or the key exist but the value is NONE
            out[k]="" #set it to empty string

        elif not isinstance(out[k], str): #the key exit and also not none but the vaue is not stirng 
            out[k]=str(out[k].strip()) #convert it to string and strip the extra spaces and new lines

    for k in list_keys: #skils ,"languages"  {list of eys ex: ["Python", "Java"]}
        if k not in out or out[k] is None: 
            out[k] = []
        elif isinstance(out[k], str): # the value return is a sring and not a list 
            out[k] = [s.strip() for s in out[k].split(",") if s.strip()]# out[k].spilt split the string by commas into parts 
            #s.strip() remove spacs around each part and skip empty parts
        elif not isinstance(out[k], list): # the value return is not a list
            out[k] = []

    for k in list_of_obj_keys: #list of objects ex: [{"degree": "B.Tech", "institution": "XYZ"}]
        if k not in out or out[k] is None:
            out[k] = []
        elif isinstance(out[k], dict):# if gimin return one object instead of list 

#"education": {"degree": "B.Tech", "institution": "XYZ"}.
# Put that single dict inside a list: [{"degree": "B.Tech", "institution": "XYZ"}].
            out[k] = [out[k]]
        elif not isinstance(out[k], list):
            out[k] = []

    for k in bool_keys:
        if k not in out or out[k] is None:
            out[k] = None #not statedd
        elif isinstance(out[k], str):
            s = out[k].strip().lower()
            out[k] = True if s in ("true", "yes", "1") else False
            
        else:
            out[k] = bool(out[k])

    return out


#step 4:save the parsed resume data as JSON file

def save_parsed_resume(parsed_data:dict, save_path:str="uploads/parsed_resume.json")-> None:
    """Save parsed resume data as JSON for other components to use it"""
    os.makedirs(os.path.driname(save_path), exist_ok=True) #creates the folder
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False) #dump the data into the file

    
#step 5: load the parsed resume data from the JSON file

def load_parsed_resume(save_path: str = "uploads/parsed_resume.json") -> dict:
    """
    Load the saved parsed resume from the JSON file.
    Returns the resume data as a dict. Raises FileNotFoundError if the file does not exist.
    """
    # Check if the file exists before trying to open it
    if not os.path.exists(save_path):
        raise FileNotFoundError("No parsed resume found. Please upload your resume first.")

    # Open the file for reading (UTF-8 so special characters are correct)
    with open(save_path, "r", encoding="utf-8") as f:
        # Parse the JSON and return the dict
        return json.load(f)