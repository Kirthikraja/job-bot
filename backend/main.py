from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import init_db
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Job Bot API")

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