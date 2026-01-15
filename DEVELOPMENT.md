# Smart Eco Tour - Development Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)              │
│                  - Trip Input Form                          │
│                  - Sustainability Sliders                   │
│                  - Itinerary Results Cards                  │
│                  - Group Matching UI                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌─────────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
├─────────────────────────────────────────────────────────────┤
│                      Routes Layer                            │
│  ├─ POST /api/generate-itinerary                           │
│  ├─ POST /api/traveler-profile                             │
│  ├─ POST /api/find-group                                   │
│  └─ GET  /api/sustainability-tips                          │
├─────────────────────────────────────────────────────────────┤
│                   Services Layer                             │
│  ├─ Matching Service (itinerary generation)                │
│  ├─ Scoring Service (sustainability calculation)           │
│  ├─ LLM Service (OpenAI integration)                        │
│  └─ Similarity Service (vector matching)                    │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                │
│  ├─ Carbon Data (emissions factors)                         │
│  ├─ Activity Database (destinations)                        │
│  └─ Mock Travelers (in-memory)                              │
└─────────────────────────────────────────────────────────────┘
```

## Service Details

### 1. **Matching Service** (`services/matching.py`)
- Generates itineraries from origin to destination
- Selects activities based on user interests
- Creates multi-day plans
- Returns 3-5 options ranked by sustainability score

**Key Functions:**
- `generate_itinerary()` - Single itinerary generation
- `generate_multiple_itineraries()` - Multiple options
- `select_activities()` - Filter activities by interests
- `generate_day_plan()` - Daily schedule creation

### 2. **Scoring Service** (`services/scoring.py`)
- Calculates sustainability metrics across 5 dimensions
- Computes carbon footprint (kg CO2)
- Generates human-readable explanations
- Returns weighted total score (0-100)

**Dimensions:**
1. Transport (30%)
2. Accommodation (20%)
3. Activities (20%)
4. Local Engagement (20%)
5. Overtourism Mitigation (10%)

### 3. **LLM Service** (`services/llm.py`)
- Integrates with OpenAI GPT API
- Generates context-aware prompts
- Falls back to hardcoded templates
- Supports multiple itinerary styles

**Features:**
- Template-based prompts
- Fallback to 4 template styles (eco, adventure, culture, relaxation)
- Per-destination sample schedules

### 4. **Similarity Service** (`utils/similarity.py`)
- Computes cosine similarity between traveler profiles
- Normalizes vectors to unit length
- Recommends group sizes based on compatibility
- Implements Euclidean distance for alternatives

## Data Models

### Schemas (`models/schemas.py`)

```
TripInput
├─ origin: str
├─ destination: str
├─ days: int
├─ transport_preference: TransportMode
├─ interests: List[ActivityType]
└─ sustainability_weights: Dict[str, float]

Itinerary
├─ id: int
├─ title: str
├─ days: List[DayPlan]
└─ sustainability: ItinerarySustainability
    ├─ total_score: float (0-100)
    ├─ breakdown: ScoreBreakdown
    ├─ total_carbon_kg: float
    └─ explanation: str
```

## Development Workflow

### Setting up for Development

1. **Clone and setup:**
   ```bash
   cd smart-eco-tour
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure OpenAI (optional):**
   ```bash
   # Edit app/.env
   OPENAI_API_KEY=sk-...
   ```

3. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Check API:**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Running Tests

```bash
# Create mock travelers
curl -X POST http://localhost:8000/api/mock-traveler-data

# Generate itineraries
curl -X POST http://localhost:8000/api/generate-itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "New York",
    "destination": "Paris",
    "days": 5,
    "transport_preference": "train",
    "interests": ["culture", "food"]
  }'

# Find matches
curl -X POST "http://localhost:8000/api/find-group?traveler_id=traveler_001"
```

## Adding Features

### Add a New Destination

1. **Add activities to `services/matching.py`:**
   ```python
   ACTIVITY_DATABASE = {
       "NewCity": {
           ActivityType.CULTURE: [
               {"name": "Museum Visit", "duration": 2.0, ...},
               ...
           ],
           ...
       }
   }
   ```

2. **Add overtourism index to `data/carbon.py`:**
   ```python
   OVERTOURISM_INDEX = {
       "NewCity": 6.5,  # 1-10 scale
   }
   ```

3. **Add city distances in `data/carbon.py`:**
   ```python
   CITY_DISTANCES = {
       ("NewCity", "AnotherCity"): 500,  # km
   }
   ```

### Add a New Scoring Dimension

1. **Add calculation function in `services/scoring.py`:**
   ```python
   def calculate_custom_score(itinerary_data) -> float:
       # Your logic
       return score
   ```

2. **Update `ScoreBreakdown` in `models/schemas.py`:**
   ```python
   class ScoreBreakdown(BaseModel):
       # ... existing fields
       custom_score: float = Field(0.0, ge=0, le=100)
   ```

3. **Update weights in calculation:**
   ```python
   weights = {
       # ... existing
       "custom": 0.10,
   }
   ```

### Add a New API Endpoint

1. **Create route in `api/routes.py`:**
   ```python
   @router.post("/new-endpoint")
   async def new_endpoint(data: YourModel) -> dict:
       # Your logic
       return result
   ```

2. **Update root endpoint** to include new route

3. **Add tests and documentation**

## Performance Optimization

### Caching
- In-memory itinerary cache (last 1000 results)
- Profile vector pre-computation
- Activity database in memory

### Lazy Loading
- Activities loaded on demand
- Destination data loaded when needed

### Async Operations
- All FastAPI endpoints are async-ready
- Can be extended with background tasks

## Debugging

### Enable Detailed Logging
```bash
# Set in app/.env
LOG_LEVEL=debug
```

### Use Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Print Debugging
```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable}")
```

## Deployment Considerations

### Production Setup
```bash
# Use production ASGI server
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables
- `OPENAI_API_KEY` - For LLM features
- `ENVIRONMENT` - Set to "production"
- `LOG_LEVEL` - Set to "warning"
- `DATABASE_URL` - For future DB integration

### Database Migration (Future)
```bash
# Once PostgreSQL/MongoDB is integrated:
alembic upgrade head
```

## Monitoring & Logging

All requests are logged with:
- Timestamp
- Method and endpoint
- Request duration
- Response status
- Errors (if any)

Logs are written to:
- Console (for development)
- `eco_tour.log` (file, for production)

## Next Steps

1. **Frontend Integration:**
   - Connect React form to `/api/generate-itinerary`
   - Implement itinerary display UI
   - Add group matching UI

2. **Database Integration:**
   - Migrate from in-memory to PostgreSQL
   - Add user authentication
   - Implement persistent storage

3. **Advanced Features:**
   - Real-time collaborative planning
   - Integration with booking APIs
   - Mobile app support
   - Gamification

4. **Testing:**
   - Unit tests for each service
   - Integration tests for API flows
   - Performance testing

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Vector Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-15
