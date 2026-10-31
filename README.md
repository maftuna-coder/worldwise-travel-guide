# WorldWise: AI country and city guide

Real photos (Wikimedia Commons, with credits), an AI briefing grounded in a curated dataset, and a follow-up question chat.
Full explanation (process, architecture, where AI is used, patterns): `docs/EXPLANATION.md`

## Run
```
python -m venv .venv
.venv\Scripts\activate          (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
set ANTHROPIC_API_KEY=your_key  (Mac/Linux: export ANTHROPIC_API_KEY=your_key)
uvicorn main:app --reload
```
Open http://127.0.0.1:8000

## Structure
```
main.py            routes (web layer)
services.py        dataset repository, photo provider, LLM adapter, briefing service
dataset.json/.csv  curated dataset (23 destinations)
static/index.html  page structure
static/css/        style.css
static/js/         utils, globe, dataset, gallery, chat, ui, app
docs/              EXPLANATION.md
```
