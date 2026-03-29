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
from datetime import datetime #it lets you create/read timestamps like “2026-03-04T18:22:10 . we used it cause to stamp metadata when chunks are indexed, e.g. created_at, indexed_at, updated_at
from typing import List, Dict, Any, Optional  #typing means telling Python what kind of data a variable or function should use.

from typing import Literal
from dotenv import load_dotenv

from langchain_core.documents import Document  # Standard LangChain document object: text chunk + metadata
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Splits long text into overlapping chunks for RAG
from langchain_chroma import Chroma  # Vector database wrapper (persistent embeddings + similarity search)
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI  # Gemini embeddings + Gemini chat LLM



load_dotenv() # Load environment variables from .env so Gemini API key and config are available at runtime.
#load_dotenv() is a function from python-dotenv.
#Its job is simple: read .env file and put values into environment variables (os.environ) so code can read them (like GEMINI_API_KEY, DATABASE_URL, etc.).

BASE_DIR = os.path.dirname(os.path.abspath(__file__))# Absolute folder path of this rag.py file.
PERSISTS_DIR=os.path.join(BASE_DIR, "persists") # Local folder where Chroma will persist vectors on disk.
COLLECTION_NAME="jobbot_kb"  ## Collection name used inside Chroma to group this project's embeddings.


PARSED_RESUMES_DIR="uploads/parsed_resumes"

# resume_id comes from the upload route (resume.py), not from this file — we only build the path.

def parsed_resume_json_path(resume_id:str)->str:# Function takes resume_id string; returns string path to that resume's JSON file.
    safe="".join(c for c in resume_id if c.isalnum() or c in "-_") # Keep only letters, digits, hyphen, underscore; drop anything else (e.g. ../).
    if safe!= resume_id or not safe:# If anything was stripped, or result is empty, the id was invalid or unsafe.
        raise ValueError("resume_id must be non empty alphanumeric and underscores only")# Stop instead of building a bad path.
    return os.path.join(PARSED_RESUMES_DIR,f"{safe}.json")# Build path: folder constant + filename "<safe>.json".


def _resume_doc_id(resume_id:str)->str: # Helper: one stable label per resume for Chroma metadata (not the file path).
    return f"resume :{resume_id}" # Prefix + id so doc_id is unique per version and easy to filter (e.g. resume:abc123).





#step: build the embedding client
# Build the Google embedding client used by Chroma: reads GEMINI_API_KEY, returns a
# GoogleGenerativeAIEmbeddings object (hosted model text-embedding-004). It does not
# embed text by itself—Chroma calls this client when indexing chunks or searching.
def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set")
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=key,)



# Create or open the persistent Chroma vector store for this project.
# - collection_name: logical KB namespace inside Chroma (e.g., jobbot_kb)
# - embedding_function: converts text/query to vectors using _get_embeddings()
# - persist_directory: on-disk folder where vectors + metadata are stored
# Returns a ready Chroma handle used by ingestion and retrieval code.
def get_vector_store() -> Chroma:
    os.makedirs(PERSISTS_DIR,exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=PERSISTS_DIR,
    )


def ingest_resume(resume_id: str) -> Dict[str, Any]:  # Ingest one resume version into Chroma; returns a small status dict.
    from .resume_parser import load_parsed_resume  # Import here so importing ai.rag does not always load resume_parser.

    try:  # Validate resume_id and build JSON path (may raise ValueError).
        path = parsed_resume_json_path(resume_id)  # e.g. uploads/parsed_resumes/<id>.json — must match save_parsed_resume path.
    except ValueError as e:  # Bad characters or empty id after sanitization.
        return {"status": "error", "message": str(e), "resume_id": resume_id}  # Tell caller the id was rejected.

    try:  # Load parsed dict from disk. #load_parsed_resume opens the JSON file, runs json.load, and returns a dict (the parsed resume). If the file is missing, it raises FileNotFoundError instead.
        data = load_parsed_resume(save_path=path)  # Same path resume.py should have used when saving after upload.
    except FileNotFoundError:  # JSON not there yet or wrong path / id mismatch.
        return {  # Do not crash — skip indexing.
            "status": "skipped",  # Not a hard failure of the whole app.
            "reason": "no_parsed_resume",  # Machine-readable reason.
            "resume_id": resume_id,  # Echo which id was requested.
            "path": path,  # Where we looked — helps debugging.
        }

    try:  # Main path: stringify, chunk, embed via Chroma, upsert.
        text = json.dumps(data, ensure_ascii=False, indent=2)  # One string of the whole resume dict for splitting.
        if not text.strip():  # Guard: nothing meaningful to index.
            return {"status": "skipped", "message": "Empty resume data", "resume_id": resume_id}  # Skip Chroma work.

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)  # Tool that cuts text into overlapping pieces.
        chunks = splitter.split_text(text)  # List of chunk strings.

        indexed_at = datetime.utcnow().isoformat() + "Z"  # Timestamp string stored on every chunk’s metadata.
        doc_id = _resume_doc_id(resume_id)  # Same doc_id on all chunks of this resume — used for delete/filter.

        docs: List[Document] = []  # Will hold one LangChain Document per chunk.
        for i, chunk in enumerate(chunks):  # i = chunk order; chunk = text of that piece.
            docs.append(  # Add one document to the list.
                Document(  # LangChain wrapper: text + metadata for Chroma.
                    page_content=chunk,  # The actual text Chroma embeds and searches.
                    metadata={  # Filterable fields stored with the vector.
                        "source_type": "resume",  # So you can tell resume chunks from future JD chunks, etc.
                        "doc_id": doc_id,  # Groups all chunks for this resume version for delete/replace.
                        "resume_id": resume_id,  # Redundant with doc_id if doc_id is resume:<id> — handy for debugging/filters.
                        "chunk_index": str(i),  # Position in the split order for this ingest run.
                        "indexed_at": indexed_at,  # When this batch was written.
                    },
                )
            )

        store = get_vector_store()  # Open Chroma with embedder + persist dir — once per ingest, not per chunk.

        try:  # Remove previous vectors for this doc_id so re-ingest does not duplicate stale chunks.
            old = store.get(where={"doc_id": doc_id})  # Fetch existing row ids for this logical resume.
            old_ids = old.get("ids") if old else None  # Chroma returns dict with "ids" list (or missing).
            if old_ids:  # Only delete if something was indexed before for this doc_id.
                store.delete(ids=old_ids)  # Drop old chunk vectors for this resume version only.
        except Exception:  # First run or API quirk — safe to continue and add fresh docs.
            pass  # Intentionally ignore errors here.

        if docs:  # Only call API if there is at least one chunk.
            store.add_documents(docs)  # Chroma embeds each chunk and persists.

        return {"status": "ok", "chunks_indexed": len(docs), "resume_id": resume_id}  # Success summary for API/logs.
    except Exception as e:  # Embedding failure, Chroma error, etc.
        return {"status": "error", "message": str(e), "resume_id": resume_id}  # Surface error without crashing caller.