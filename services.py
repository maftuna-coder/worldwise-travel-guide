"""WorldWise service layer. Four small parts, each with one job:

  DatasetRepository  reads the curated dataset (dataset.json)           -> pattern: Repository
  ImageProvider      finds real photos; WikimediaImages is one provider  -> patterns: Strategy / Adapter
  LLM                talks to a language model; AnthropicLLM is one      -> pattern: Adapter
  BriefingService    builds the prompts and grounds them in the dataset  -> the "RAG" step

main.py wires them together and exposes them as web routes.
"""
from __future__ import annotations

import html
import json
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

BASE = Path(__file__).parent


# ---------- Repository: the curated dataset ----------
class DatasetRepository:
    def __init__(self, path: Path):
        self.items: list[dict] = json.loads(path.read_text(encoding="utf-8"))

# find(): exact match on name or capital first, then partial match on the name.
# Returns None for very short input so random letters do not match.
    def find(self, text: str) -> dict | None:
        t = text.lower().strip()
        if len(t) < 3:
            return None
        for d in self.items:
            if t in (d["n"].lower(), d["cap"].lower()):
                return d
        return next((d for d in self.items if t in d["n"].lower()), None)


# ---------- Strategy / Adapter: image providers ----------
class ImageProvider(ABC):
    @abstractmethod
    def search(self, query: str, n: int) -> list[dict]: ...


# Adapter for the Wikimedia Commons API: translates our simple search(query, n) into the real API call
# and converts the answer into {url, page, title, credit}. Photos are freely licensed; credit and license are returned
# because the licenses require attribution.
class WikimediaImages(ImageProvider):
    """Real, freely licensed photos from Wikimedia Commons, returned with credit and license."""

    API = "https://commons.wikimedia.org/w/api.php"
    HEADERS = {"User-Agent": "WorldWise/1.0 (university project; replace with your email)"}
    BAD = re.compile(r"\b(map|flag|logo|coat of arms|diagram|locator|seal|stamp|poster)\b", re.I)

    def search(self, query: str, n: int = 3) -> list[dict]:
# Ask Commons for image files (namespace 6) matching the query, with a 1000px-wide thumbnail and license metadata.
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 25,
            "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1000,
        }
        r = httpx.get(self.API, params=params, headers=self.HEADERS, timeout=15)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        out: list[dict] = []
# Keep only real, large JPEG photos and skip maps, flags, logos and diagrams, which are common in Commons results.
        for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
            info = (p.get("imageinfo") or [None])[0]
            if not info or info.get("mime") != "image/jpeg" or info.get("width", 0) < 900:
                continue
            title = re.sub(r"^File:|\.\w+$", "", p["title"])
            if self.BAD.search(title):
                continue
            meta = info.get("extmetadata", {})
            artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "Unknown"))
            lic = meta.get("LicenseShortName", {}).get("value", "")
            out.append({
                "url": info["thumburl"],
                "page": info["descriptionurl"],
                "title": title[:70],
                "credit": f"{html.unescape(artist).strip()[:40]} / {lic}".strip(" /"),
            })
            if len(out) >= n:
                break
        return out


# ---------- Adapter: LLM providers ----------
class LLM(ABC):
    @abstractmethod
    def complete(self, system: str, messages: list[dict], max_tokens: int = 1800) -> str: ...


# Adapter for the Anthropic API. The key is read from the ANTHROPIC_API_KEY environment variable (never stored in code).
# Set WORLDWISE_MODEL to change the model.
class AnthropicLLM(LLM):
    def __init__(self) -> None:
        import anthropic  # reads ANTHROPIC_API_KEY from the environment

        self.client = anthropic.Anthropic()
        self.model = os.getenv("WORLDWISE_MODEL", "claude-sonnet-5-5")

    def complete(self, system, messages, max_tokens=1800):
        msg = self.client.messages.create(
            model=self.model, max_tokens=max_tokens, system=system, messages=messages
        )
        return "".join(b.text for b in msg.content if b.type == "text")


# ---------- Service: prompts + grounding ----------
# The JSON shape we ask the model to return. The front-end draws the page from exactly these fields.
SCHEMA = (
    '{"name":string,"type":"country"|"city","country":string,"flag":"one flag emoji","summary":"2 sentences",'
    '"safety":{"score":integer 1-5 (5 = very safe),"overview":"2-3 sentences","risks":[3-5 short strings],"tips":[3-5 short strings]},'
    '"laws":[5-7 short strings: laws and customs visitors must know],"advantages":[4-6 short strings],"disadvantages":[4-6 short strings],'
    '"practical":{"currency":string,"language":string,"bestTime":string,"visa":string}}'
)


# Models sometimes wrap JSON in ```json fences or add a sentence around it; this extracts the JSON object safely.
def parse_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("The model did not return JSON")
    return json.loads(text[start : end + 1])


class BriefingService:
    def __init__(self, llm: LLM, dataset: DatasetRepository):
        self.llm, self.dataset = llm, dataset

    def briefing(self, place: str) -> dict:
        rec = self.dataset.find(place)
        system = "You are a careful travel-information analyst. Be balanced and accurate. Reply with JSON only."
        prompt = (
            f'Write a briefing about "{place}" (a country or city). Return ONLY JSON with this shape:\n{SCHEMA}\n'
            'Each practical value must be under 14 words. Plain text only, no markdown or asterisks. '
            'If the input is not a real place return {"error":"short reason"}. Flag uncertainty where laws change often.'
        )
# Retrieval-augmented generation (RAG): if the place is in our dataset, the record is added to the prompt
# so the model stays consistent with curated data. Otherwise the model answers from its own knowledge.
        if rec:
            prompt += "\nReference record from the WorldWise dataset (treat as ground truth where consistent): " + json.dumps(rec, ensure_ascii=False)
        return parse_json(self.llm.complete(system, [{"role": "user", "content": prompt}]))

# Follow-up chat. The briefing and dataset record go into the system prompt; the conversation goes in messages.
    def answer(self, place: str, briefing: dict, history: list[dict]) -> str:
        rec = self.dataset.find(place)
        system = (
            f"You are WorldWise, a careful travel-safety assistant. Answer only about {place} for travellers. "
            "Be concrete, under 120 words, and say when laws or conditions may have changed. "
            "You may use short bullet lists with **bold** labels.\nBriefing: " + json.dumps(briefing, ensure_ascii=False)
        )
        if rec:
            system += "\nDataset record: " + json.dumps(rec, ensure_ascii=False)
        return self.llm.complete(system, history, 700)
