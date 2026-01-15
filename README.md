# 🌿 Smart Eco Tour – Backend

Backend API for **Smart Eco Tour**, an AI-powered sustainable travel planner
focused on sustainability-first travel planning.

## 🌟 Features
- AI-generated itineraries (OpenAI + fallback)
- Transparent sustainability scoring
- Carbon-aware transport & accommodation scoring
- Group matching for eco-conscious travelers
- FastAPI + auto Swagger docs

## 🛠️ Tech Stack
- FastAPI
- Python 3.10+
- OpenAI API (optional)
- In-memory data (hackathon MVP)

## ▶️ Run Locally
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## 🔗 Frontend Integration

The backend is designed to work with the React frontend located in `../ecotour`.

### CORS Configuration
CORS is pre-configured to accept requests from any origin for development. 

### Running with Frontend

**Terminal 1 (Backend):**
```bash
cd smart-eco-tour-backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd ecotour
npm install
npm run dev
```

The frontend will automatically connect to the backend at `http://localhost:8000`.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate-itinerary` | POST | Generate sustainable itineraries |
| `/api/itinerary/{id}` | GET | Get itinerary details |
| `/api/traveler-profile` | POST | Create traveler profile |
| `/api/find-group` | POST | Find matching travelers |
| `/api/travelers` | GET | List all travelers |
| `/api/sustainability-tips` | GET | Get eco-travel tips |
| `/api/health` | GET | Health check |

