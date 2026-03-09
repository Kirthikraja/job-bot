from fastapi import FastAPI  # core FastAPI app class
from fastapi.middleware.cors import CORSMiddleware  # allow frontend to call this API
from models import init_db  # create DB tables on startup
from api.routes.resume import router as resume_router  # all resume routes (upload, get JSON, get PDF)
from dotenv import load_dotenv  # load .env variables (e.g. GEMINI_API_KEY)
from api.routes.credentials import router as credentials_router
import os  # for os.getenv()

load_dotenv()  # load variables from .env into environment

app = FastAPI(title="Job Bot API")  # create the single app instance

# Mount the resume routes so /resume, /resume/upload, /resume/file work
app.include_router(resume_router)  # attach resume router so those URLs are live
app.include_router(credentials_router)## mount credentials routes so POST /credentials and GET /credentials/{site} work

app.add_middleware(
    CORSMiddleware,  # middleware that adds CORS headers to responses
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],  # which origins can call this API
    allow_credentials=True,  # allow cookies/auth headers
    allow_methods=["*"],  # allow GET, POST, etc.
    allow_headers=["*"],  # allow any request headers
)

@app.on_event("startup")  # run this function once when the server starts
def startup():
    init_db()  # create  tables (Job, Application, Credential, etc.)
    print("Database initialized")

@app.get("/health")  # GET /health → quick check if server is up
def health():
    return {"status": "running"}  # response body