# Ìº± Smart Eco Tour ‚Äì Backend

Backend API for **Smart Eco Tour**, an AI-powered sustainable travel planner
focused on sustainability-first travel planning.

## Ì∫Ä Features
- AI-generated itineraries (OpenAI + fallback)
- Transparent sustainability scoring
- Carbon-aware transport & accommodation scoring
- Group matching for eco-conscious travelers
- FastAPI + auto Swagger docs

## Ì∑† Tech Stack
- FastAPI
- Python 3.10+
- OpenAI API (optional)
- In-memory data (hackathon MVP)

## ‚ñ∂Ô∏è Run Locally
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

