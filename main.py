"""WorldWise API (FastAPI).

This file only contains the web layer: routes, request validation and error handling.
All real work is delegated to the classes in services.py (dataset, photos, AI), which keeps the routes short
and makes each part replaceable.

Run:  uvicorn main:app --reload     then open http://127.0.0.1:8000
"""
from functools import lru_cache

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services import BASE, AnthropicLLM, BriefingService, DatasetRepository, WikimediaImages

app = FastAPI(title="WorldWise")

# Serve the front-end files (css/ and js/) under /static.
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

# --- Wiring (dependency injection) -------------------------------------------------------------
# The service receives its collaborators from outside. To use another AI provider, write a new LLM
# subclass in services.py and pass it here; nothing else changes.
dataset = DatasetRepository(BASE / "dataset.json")
images = WikimediaImages()
service = BriefingService(AnthropicLLM(), dataset)


@lru_cache(maxsize=256)
def _photos(q: str, n: int) -> tuple:
    """Cache photo searches in memory so repeated searches are instant and we are polite to Wikimedia."""
    return tuple(images.search(q, n))


# --- Request models (validated automatically by Pydantic) ---------------------------------------
class Msg(BaseModel):
    role: str      # "user" or "assistant"
    content: str


class AskBody(BaseModel):
    place: str     # name of the place being discussed
    briefing: dict # the briefing JSON the user is looking at (context for the AI)
    history: list[Msg]


# --- Routes -------------------------------------------------------------------------------------
@app.get("/api/briefing")
def briefing(q: str = Query(min_length=2, max_length=80)):
    """AI briefing (safety, laws, pros/cons, practical info) for a country or city."""
    try:
        return service.briefing(q)
    except ValueError as e:  # the model did not return valid JSON
        raise HTTPException(502, str(e))
    except Exception:  # network error, missing/invalid API key, rate limit...
        raise HTTPException(500, "The language model request failed. Check ANTHROPIC_API_KEY.")


@app.get("/api/images")
def photos(q: str = Query(min_length=2, max_length=120), n: int = Query(3, ge=1, le=8)):
    """Real photos from Wikimedia Commons. Returns an empty list (not an error) if Wikimedia is unreachable."""
    try:
        return list(_photos(q, n))
    except httpx.HTTPError:
        return []


@app.post("/api/ask")
def ask(body: AskBody):
    """Follow-up question about the place. The conversation must end with a user message."""
    hist = [m.model_dump() for m in body.history]
    if not hist or hist[-1]["role"] != "user":
        raise HTTPException(400, "History must end with a user message")
    try:
        return {"answer": service.answer(body.place, body.briefing, hist)}
    except Exception:
        raise HTTPException(500, "The language model request failed.")


@app.get("/api/dataset")
def get_dataset():
    """The curated dataset, used by the browse grid and the CSV export on the page."""
    return dataset.items


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")
