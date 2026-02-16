from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import init_db
#from api.routes.resume import router as resume_router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Job Bot API")

# Mount the resume routes so /resume and /resume/upload work
#app.include_router(resume_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    print("Database initialized")

@app.get("/health")
def health():
    return {"status": "running"}