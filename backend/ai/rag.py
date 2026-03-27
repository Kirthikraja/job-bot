# What we are doing in rag.py
# ---------------------------
# We will create a small RAG engine that:
# 1) Reads our knowledge data (start with parsed resume; later add job descriptions).
# 2) Breaks that data into chunks.
# 3) Converts chunks into embeddings and stores them in a retrievable index.
# 4) For each user query, retrieves top relevant chunks.
# 5) Calls the LLM with only those chunks plus the query.
# 6) Returns an answer with sources used.
#
# Instead of asking the model to answer from generic memory, we force it to reason
# from our project data.
#
# Why we are using RAG in this app
# --------------------------------
# App decisions must be based on our resume and specific jobs, not generic model knowledge.
# - Resume and job descriptions are dynamic and user-specific.
# - The model is not trained on our resume by default.
# - KB storage alone is not enough; retrieval must happen per query.
#
# RAG gives us:
# - Grounding (lower hallucination risk),
# - Explainability (source chunks),
# - Freshness (new docs are usable immediately),
# - Better matching quality.
#
# Pipeline view
# -------------
# Resume upload -> parsed JSON -> KB
# Job fetch -> JD text -> KB
# Matcher/assistant query -> RAG retrieves relevant chunks -> LLM answers with evidence
#
# So, rag.py is the bridge between the KB and LLM calls, making outputs more trustworthy.

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI



load_dotenv() # Load environment variables from .env so Gemini API key and config are available at runtime.
#load_dotenv() is a function from python-dotenv.
#Its job is simple: read .env file and put values into environment variables (os.environ) so code can read them (like GEMINI_API_KEY, DATABASE_URL, etc.).

BASE_DIR = os.path.dirname(os.path.abspath(__file__))# Absolute folder path of this rag.py file.
PERSISTS_DIR=os.path.join(BASE_DIR, "persists") # Local folder where Chroma will persist vectors on disk.
COLLECTION_NAME="jobbot_kb"  ## Collection name used inside Chroma to group this project's embeddings.