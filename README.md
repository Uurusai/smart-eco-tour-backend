# Smart Eco Tour Backend API

An AI-powered sustainable travel itinerary generator with group matching capabilities, built with FastAPI, LLM integration, and sustainability scoring.

## Features

### 🌍 Core Capabilities

1. **Itinerary Generation**
   - AI-powered itinerary generation using OpenAI GPT (with hardcoded template fallback)
   - Multi-option generation (compare 3-5 different itineraries)
   - Activity selection based on user interests and sustainability preferences
   - Day-by-day scheduling with specific times and locations

2. **Sustainability Scoring Engine**
   - Comprehensive scoring across 5 dimensions:
     - Transport emissions (walk, train, bus, car, flight)
     - Accommodation carbon footprint
     - Activity impact (local vs. mainstream tourist spots)
     - Local community engagement
     - Overtourism mitigation
   - Real carbon footprint calculations in kg CO2
   - Weighted scoring system (customizable)

3. **Carbon Tracking**
   - Transport carbon factors (kg CO2/km)
   - Accommodation carbon data (kg CO2/night)
   - Activity-specific emissions
   - Distance-based calculations between major cities

4. **Group Matching**
   - Vector similarity using cosine similarity and Euclidean distance
   - Traveler profile creation with interests and sustainability scores
   - Compatible group recommendations
   - Group size optimization based on profile compatibility

5. **Destination Intelligence**
   - Overtourism index for major cities
   - Activity database for multiple destinations (Paris, Tokyo, Barcelona, Bangkok)
   - Sustainability tips per destination
   - Local engagement opportunities

## Project Structure

```
app/
├── main.py                 # FastAPI application & startup
├── api/
│   └── routes.py          # API endpoints
├── models/
│   └── schemas.py         # Pydantic data models
├── services/
│   ├── llm.py             # LLM integration (OpenAI GPT)
│   ├── scoring.py         # Sustainability scoring engine
│   └── matching.py        # Itinerary generation & selection
├── data/
│   └── carbon.py          # Carbon factors & environmental data
├── utils/
│   └── similarity.py       # Vector similarity algorithms
└── .env                   # Environment configuration
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key (optional - fallback templates included)

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd c:\Users\User\OneDrive\Desktop\fastapi\smart-eco-tour
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Edit app/.env
   OPENAI_API_KEY=your_api_key_here  # Optional
   ENVIRONMENT=development
   LOG_LEVEL=info
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

Server will be available at `http://localhost:8000`

## API Endpoints

### 1. Generate Itineraries
**POST** `/api/generate-itinerary`

Generate multiple sustainable itinerary options.

**Request Body:**
```json
{
  "origin": "New York",
  "destination": "Paris",
  "days": 5,
  "transport_preference": "train",
  "interests": ["culture", "food"],
  "sustainability_weights": {
    "carbon": 0.4,
    "local": 0.3,
    "culture": 0.2,
    "overtourism": 0.1
  }
}
```

**Response:**
```json
{
  "status": "success",
  "itineraries": [
    {
      "id": 12345,
      "title": "Sustainable 5-Day Paris Adventure",
      "days": [...],
      "sustainability": {
        "total_score": 82.5,
        "total_carbon_kg": 145.2,
        "explanation": "🌱 Good Sustainable Travel..."
      }
    }
  ]
}
```

### 2. Get Itinerary Details
**GET** `/api/itinerary/{itinerary_id}`

Get detailed view of a specific itinerary with day-by-day breakdown.

### 3. Create Traveler Profile
**POST** `/api/traveler-profile`

Create a profile for a traveler to enable group matching.

**Request Body:**
```json
{
  "id": "user_123",
  "name": "Alice Johnson",
  "destination": "Paris",
  "trip_days": 5,
  "sustainability_score_min": 85,
  "interests": ["culture", "food"],
  "max_group_size": 4,
  "transport_preference": "train"
}
```

### 4. Find Group Matches
**POST** `/api/find-group`

Find compatible travelers for group travel.

**Query Parameters:**
- `traveler_id`: ID of the reference traveler
- `destination` (optional): Filter by destination
- `min_similarity` (default: 0.7): Minimum similarity threshold (0.0-1.0)

**Response:**
```json
{
  "status": "success",
  "matches_found": 3,
  "top_matches": [
    {
      "traveler_id": "user_456",
      "name": "Bob Smith",
      "similarity_score": 0.92,
      "common_interests": ["culture", "food"]
    }
  ],
  "group_recommendations": [
    {
      "traveler_ids": ["user_123", "user_456"],
      "similarity_score": 0.92,
      "recommended_group_size": 2
    }
  ]
}
```

### 5. Compare Itineraries
**POST** `/api/compare-itineraries`

Compare multiple itineraries side-by-side.

**Request Body:**
```json
{
  "itinerary_ids": [12345, 12346, 12347]
}
```

### 6. Get Sustainability Tips
**GET** `/api/sustainability-tips?destination=Paris`

Get destination-specific sustainability tips.

### 7. Create Mock Traveler Data
**POST** `/api/mock-traveler-data`

Generate sample traveler profiles for testing group matching.

### 8. Health Check
**GET** `/api/health`

Check API status and cache information.

## Sustainability Scoring Details

### Scoring Dimensions

1. **Transport Score (30% weight)**
   - Walk: 100/100
   - Train: 85/100
   - Bus: 80/100
   - Car: 40/100
   - Flight: 20/100
   - Distance penalty for long trips

2. **Accommodation Score (20% weight)**
   - Eco Hotel: 90/100
   - Camping: 95/100
   - Hostel: 80/100
   - Airbnb: 75/100
   - Hotel: 60/100
   - Resort: 30/100
   - Bonus for longer stays (≥7 days)

3. **Activity Score (20% weight)**
   - Local engagement opportunities
   - Overtourism index consideration
   - Cultural vs. mainstream tourist activities

4. **Local Engagement Score (20% weight)**
   - Cooking classes, homestays, markets
   - Cultural workshops
   - Local guided tours

5. **Overtourism Mitigation (10% weight)**
   - Destination overtourism level
   - Off-season travel bonus
   - Alternative activity selection

### Carbon Emissions Data

All carbon factors based on real-world averages:

**Transport (kg CO2/km):**
- Flight: 0.12
- Car: 0.15
- Bus: 0.028
- Train: 0.021
- Walk: 0.0

**Accommodation (kg CO2/night):**
- Eco Hotel: 8.5
- Camping: 2.0
- Hostel: 5.5
- Airbnb: 12.0
- Hotel: 15.0
- Resort: 25.0
- Lodge: 10.0

## Vector Similarity for Group Matching

Uses cosine similarity with profile vectors encoding:
- Sustainability preferences (0-1 normalized)
- Trip duration
- Budget
- Interest categories (one-hot encoding)
- Transport preferences

### Algorithm:
```
similarity = dot_product(v1, v2) / (magnitude(v1) * magnitude(v2))
```

Group compatibility calculated as average pairwise similarity.

## LLM Integration

### OpenAI GPT Integration
- Model: GPT-3.5 Turbo
- Context-aware prompts for destination-specific recommendations
- Fallback to hardcoded templates if API unavailable

### Fallback Strategy
If OpenAI API is not configured or fails:
1. Returns hardcoded template itineraries
2. 4 template styles: eco_focused, adventure_focused, culture_focused, relaxation_focused
3. Per-destination sample schedules (Paris, Tokyo, Barcelona, Bangkok)

## Sample Usage

### Python Client
```python
import requests

BASE_URL = "http://localhost:8000"

# Generate itineraries
response = requests.post(
    f"{BASE_URL}/api/generate-itinerary",
    json={
        "origin": "New York",
        "destination": "Paris",
        "days": 5,
        "transport_preference": "train",
        "interests": ["culture", "food"]
    }
)

itineraries = response.json()["itineraries"]
print(f"Generated {len(itineraries)} itineraries")
print(f"Best option score: {itineraries[0]['sustainability']['total_score']}")

# Create mock travelers
response = requests.post(f"{BASE_URL}/api/mock-traveler-data")
print(response.json())

# Find group matches
response = requests.post(
    f"{BASE_URL}/api/find-group",
    params={"traveler_id": "traveler_001"}
)

matches = response.json()["top_matches"]
print(f"Found {len(matches)} compatible travelers")
```

### React Integration (Frontend)
```javascript
// Generate itinerary
const response = await fetch('/api/generate-itinerary', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    origin: 'New York',
    destination: 'Paris',
    days: 5,
    transport_preference: 'train',
    interests: ['culture', 'food']
  })
});

const data = await response.json();
const bestItinerary = data.itineraries[0];
console.log(`Score: ${bestItinerary.sustainability.total_score}`);
console.log(`Carbon: ${bestItinerary.sustainability.total_carbon_kg}kg`);
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-...           # OpenAI API key (optional)
ENVIRONMENT=development         # development, staging, production
LOG_LEVEL=info                 # debug, info, warning, error
```

### Customization

**Modify sustainability weights in request:**
```json
{
  "sustainability_weights": {
    "carbon": 0.5,       // Prioritize carbon reduction
    "local": 0.2,        // Local engagement
    "culture": 0.2,      // Cultural experience
    "overtourism": 0.1   // Overtourism mitigation
  }
}
```

## Testing

### Run with Mock Data
```bash
# Get health check
curl http://localhost:8000/api/health

# Create mock travelers
curl -X POST http://localhost:8000/api/mock-traveler-data

# Generate itinerary
curl -X POST http://localhost:8000/api/generate-itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "New York",
    "destination": "Paris",
    "days": 5,
    "transport_preference": "train"
  }'

# Find group matches
curl -X POST "http://localhost:8000/api/find-group?traveler_id=traveler_001"
```

### Interactive API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Performance Features

- **Caching**: In-memory itinerary caching
- **Lazy Loading**: Activities loaded on demand
- **Vector Optimization**: Pre-computed profile vectors
- **Batch Operations**: Multiple itinerary comparison

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time collaborative itinerary planning
- [ ] Advanced ML-based itinerary personalization
- [ ] Integration with real booking APIs
- [ ] Real-time carbon tracking during trips
- [ ] Gamification: sustainability challenges
- [ ] Mobile app support
- [ ] Multi-language support

## Error Handling

All endpoints return standardized error responses:

```json
{
  "status": "error",
  "detail": "Descriptive error message",
  "error_code": "ITINERARY_NOT_FOUND"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad request
- 404: Not found
- 500: Server error

## Development Notes

### Adding New Destinations
1. Add activities to `ACTIVITY_DATABASE` in `services/matching.py`
2. Add overtourism index to `OVERTOURISM_INDEX` in `data/carbon.py`
3. Add city distances to `CITY_DISTANCES` in `data/carbon.py`

### Customizing Scoring
Edit weights in `services/scoring.py`:
```python
weights = {
    "transport": 0.30,
    "accommodation": 0.20,
    "activity": 0.20,
    "local_engagement": 0.20,
    "overtourism": 0.10,
}
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-15  
**Status**: Production Ready ✅
