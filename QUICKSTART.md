# Smart Eco Tour Backend - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
cd c:\Users\User\OneDrive\Desktop\fastapi\smart-eco-tour
pip install -r requirements.txt
```

### 2. Configure Environment (Optional - LLM)
```bash
# Edit app/.env
OPENAI_API_KEY=sk-your-key-here  # Optional, fallback templates work without it
```

### 3. Start the Server
```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4. Verify It's Running
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Smart Eco Tour Backend API",
  "version": "1.0.0",
  "cached_itineraries": 0,
  "registered_travelers": 0
}
```

---

## 📚 Core Features

### Feature 1: Generate Sustainable Itineraries
```bash
curl -X POST http://localhost:8000/api/generate-itinerary \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Response:**
- 3-5 itinerary options
- Sustainability score (0-100)
- Carbon footprint in kg CO2
- Day-by-day breakdown with times & activities

### Feature 2: Create Traveler Profiles
```bash
curl -X POST http://localhost:8000/api/traveler-profile \
  -H "Content-Type: application/json" \
  -d '{
    "id": "alice_123",
    "name": "Alice Johnson",
    "destination": "Paris",
    "trip_days": 5,
    "sustainability_score_min": 85,
    "interests": ["culture", "food"],
    "transport_preference": "train",
    "max_group_size": 4
  }'
```

### Feature 3: Find Compatible Travelers
```bash
# First, create mock travelers
curl -X POST http://localhost:8000/api/mock-traveler-data

# Then find matches
curl -X POST "http://localhost:8000/api/find-group?traveler_id=traveler_001"
```

**Response:**
- Top matching travelers
- Similarity scores
- Group recommendations
- Common interests

### Feature 4: Compare Itineraries
```bash
curl -X POST http://localhost:8000/api/compare-itineraries \
  -H "Content-Type: application/json" \
  -d '{
    "itinerary_ids": [123, 124, 125]
  }'
```

### Feature 5: Get Sustainability Tips
```bash
curl "http://localhost:8000/api/sustainability-tips?destination=Paris"
```

---

## 🧪 Run the Test Suite

```bash
# Make sure the server is running, then:
python test_api.py
```

This will run 9 comprehensive tests:
1. ✅ Health Check
2. ✅ Create Mock Travelers
3. ✅ Generate Itineraries
4. ✅ Get Itinerary Details
5. ✅ Create Traveler Profile
6. ✅ List Travelers
7. ✅ Find Group Matches
8. ✅ Compare Itineraries
9. ✅ Sustainability Tips

---

## 📖 Interactive API Documentation

Open in your browser:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

---

## 💡 Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate itineraries
response = requests.post(
    f"{BASE_URL}/api/generate-itinerary",
    json={
        "origin": "New York",
        "destination": "Tokyo",
        "days": 7,
        "transport_preference": "train",
        "interests": ["culture", "adventure"]
    }
)

itineraries = response.json()["itineraries"]

for i, itinerary in enumerate(itineraries, 1):
    score = itinerary["sustainability"]["total_score"]
    carbon = itinerary["sustainability"]["total_carbon_kg"]
    print(f"Option {i}: Score {score:.1f}/100, Carbon {carbon:.1f} kg")
```

---

## 🌍 Supported Destinations

Currently included in activity database:
- **Paris** - Culture, Food, Walking tours
- **Tokyo** - Culture, Adventure, Local experiences
- **Barcelona** - Gaudi architecture, Beach, Tapas
- **Bangkok** - Temples, Cooking, Night markets

Add more destinations in `services/matching.py` (see DEVELOPMENT.md)

---

## 🎯 Key Scoring Dimensions

| Dimension | Weight | Factors |
|-----------|--------|---------|
| **Transport** | 30% | Mode (walk/train/bus/car/flight), Distance |
| **Accommodation** | 20% | Type (eco-hotel/hostel/resort), Duration |
| **Activities** | 20% | Local engagement, Tourist spots |
| **Local Engagement** | 20% | Community interaction, Local guides |
| **Overtourism** | 10% | Destination popularity, Crowd avoidance |

---

## 🔧 Configuration

Edit `app/config.py` to customize:

```python
# Default sustainability weights
DEFAULT_SUSTAINABILITY_WEIGHTS = {
    "carbon": 0.4,
    "local": 0.3,
    "culture": 0.2,
    "overtourism": 0.1,
}

# Scoring dimension weights
SCORING_WEIGHTS = {
    "transport": 0.30,
    "accommodation": 0.20,
    "activity": 0.20,
    "local_engagement": 0.20,
    "overtourism": 0.10,
}
```

---

## 📊 Response Examples

### Itinerary Response
```json
{
  "id": 12345,
  "title": "Sustainable 5-Day Paris Adventure",
  "description": "Eco-conscious itinerary from New York to Paris",
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "time": "09:00",
          "activity": "Seine River Walk",
          "location": "Along Seine",
          "transport": "walk",
          "duration_hours": 2.0,
          "carbon_emission_kg": 0.0
        }
      ],
      "accommodation": "eco_hotel",
      "accommodation_carbon_kg": 8.5,
      "total_carbon_kg": 8.5
    }
  ],
  "sustainability": {
    "total_score": 82.5,
    "breakdown": {
      "transport_score": 85.0,
      "accommodation_score": 90.0,
      "activity_score": 80.0,
      "local_engagement_score": 75.0,
      "overtourism_score": 80.0
    },
    "total_carbon_kg": 145.2,
    "explanation": "🌱 Good Sustainable Travel\n\nThis itinerary balances travel experience with environmental responsibility..."
  }
}
```

### Matching Response
```json
{
  "status": "success",
  "matches_found": 3,
  "top_matches": [
    {
      "traveler_id": "bob_456",
      "name": "Bob Smith",
      "destination": "Paris",
      "similarity_score": 0.92,
      "common_interests": ["culture", "food"]
    }
  ],
  "group_recommendations": [
    {
      "traveler_ids": ["alice_123", "bob_456"],
      "similarity_score": 0.92,
      "recommended_group_size": 2,
      "common_interests": ["culture", "food"]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### "Connection refused" error
```bash
# Make sure the server is running:
uvicorn app.main:app --reload
```

### "ModuleNotFoundError: No module named 'app'"
```bash
# Install in development mode:
pip install -e .
```

### OpenAI API not working
The system automatically falls back to hardcoded templates. No action needed!

### High carbon scores
Try adjusting:
1. Transport mode (prefer train/bus over flight)
2. Accommodation (choose eco_hotel/camping over resort)
3. Duration (longer stays have lower daily impact)

---

## 📈 Next Steps

1. **Connect to Frontend:**
   - React form → POST `/api/generate-itinerary`
   - Display results with sustainability cards
   - Implement group matching UI

2. **Enhance Features:**
   - Add more destinations
   - Integrate real booking APIs
   - Add user authentication
   - Save favorite itineraries

3. **Deployment:**
   - Set up PostgreSQL database
   - Deploy to Heroku, AWS, or GCP
   - Add CI/CD pipeline

---

## 📚 More Documentation

- **Full README**: See `README.md` for comprehensive API docs
- **Development Guide**: See `DEVELOPMENT.md` for architecture details
- **API Endpoints**: See all endpoints in `/docs`

---

## 🤝 Support

For issues or questions:
1. Check the README.md and DEVELOPMENT.md
2. Review test_api.py for usage examples
3. Check the Swagger UI at /docs for endpoint details

---

## ✅ You're All Set!

Your sustainable travel backend is now running. Test it:

```bash
# Quick test
curl http://localhost:8000/api/health

# Full test suite
python test_api.py

# Interactive docs
# Open http://localhost:8000/docs in your browser
```

**Happy sustainable traveling! 🌍♻️**
