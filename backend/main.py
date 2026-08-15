"""
EcoBot — FastAPI backend for Render deployment.

This file wraps the existing query_engine.py RAG pipeline behind a REST API.
The RAG logic, ChromaDB, embeddings, and Groq integration are UNCHANGED.

Architecture:
    POST /api/chat  →  query_engine.query_rag()  →  ChromaDB + Groq  →  JSON response
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup: backend/main.py is in a subdirectory, but query_engine.py and
# vector_db/ live at the project root. Add the root to sys.path so imports work
# whether the server is started from project root or from backend/.
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load .env from project root for local development.
# On Render this is a no-op — env vars are injected by the platform.
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# ---------------------------------------------------------------------------
# Import the EXISTING RAG engine — zero changes to query_engine.py required.
# ---------------------------------------------------------------------------
try:
    import query_engine
    _engine_error = None
except RuntimeError as e:
    query_engine = None
    _engine_error = str(e)
except Exception as e:
    query_engine = None
    _engine_error = f"Failed to load RAG engine: {e}"


# ---------------------------------------------------------------------------
# CORS — frontend URL is injected via FRONTEND_URL env var on Render.
# Falls back to localhost for local development.
# ---------------------------------------------------------------------------
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
_allowed_origins = [
    _frontend_url,
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# ---------------------------------------------------------------------------
# App startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Log startup status without revealing secrets."""
    if _engine_error:
        print(f"[EcoBot] WARNING: RAG engine failed to load — {_engine_error}")
    else:
        print("[EcoBot] RAG engine loaded successfully.")
        print(f"[EcoBot] GROQ_API_KEY configured: {'yes' if os.getenv('GROQ_API_KEY') else 'NO — set this in Render Variables'}")
        print(f"[EcoBot] FRONTEND_URL: {_frontend_url}")
    yield


app = FastAPI(
    title="EcoBot API",
    description="Energy RAG Chatbot — FastAPI backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


# ---------------------------------------------------------------------------
# Health check — lets Render confirm the service is up
# ---------------------------------------------------------------------------
@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "EcoBot API",
        "rag_engine": "loaded" if query_engine else f"error: {_engine_error}",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Main chat endpoint — calls the EXISTING query_engine.query_rag() unchanged
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Guard: engine must have loaded successfully
    if query_engine is None:
        raise HTTPException(
            status_code=503,
            detail=f"RAG engine unavailable: {_engine_error}",
        )

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Call the EXISTING RAG function — signature and logic are untouched
    answer = query_engine.query_rag(question)

    # Retrieve source metadata for the same question to return to the frontend.
    # This is an additive read-only call; it does not change query_engine.py.
    sources: list[str] = []
    try:
        results = query_engine.vector_db.similarity_search(question, k=2)
        sources = list({
            doc.metadata.get("source", "")
            for doc in results
            if doc.metadata.get("source")
        })
    except Exception:
        pass  # Sources are informational — never fail the main response

    return ChatResponse(answer=answer, sources=sources)
