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


def ingest_resume() -> Dict[str,Any]:
    from.resume_parser import load_parsed_resume

    try:
        data=load_parsed_resume()

    except FileNotFoundError:
        return {"status": "error", "message": "No parsed resume found"}

    try:
        text=json.dumps(data,ensure_ascii=False,indent=2)
        if not text.strip():
            return{"status":"skipped","message":"Empty resume data"}

        splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150,)

        chunks=splitter.split_text(text)

        docs:List[Document]=[]
        indexed_at=datetime.utnow().isoformat()+"Z"


        for i, chunk in enumerate(chunks):
            docs.append(Document(page_content=chunk,metadata={"source_type":"resume","doc_id":"resume","chunk_index":str(i),"indexed_at": indexed_at,},))
            store=get_vector_store()

        #remove old resume chunks so re-index does not duplicate

        try:
            old = store.get(where={"doc_id":"resume"})
            old_ids=old.get("ids") if old else None
            if old_ids:
                store.delete(ids=old_ids)

        except Exception:
            pass

        if docs:
            store.add_documents(docs)

        return {"status": "ok", "chunks_indexed": len(docs)}

    except Exception as e:
        return {"status": "error", "message": str(e)}


