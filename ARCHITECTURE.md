# System Architecture & Data Flow

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Trip Input Form │  │ Sustainability   │  │ Group Matching   │ │
│  │  - Origin        │  │ Sliders          │  │ - Browse matches │ │
│  │  - Destination   │  │ - Carbon weight  │  │ - View profiles  │ │
│  │  - Duration      │  │ - Local weight   │  │ - Join groups    │ │
│  │  - Interests     │  │ - Culture weight │  │                  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└────────────┬─────────────────────────────────────────────────────┬┘
             │ HTTP/REST (JSON)                                    │
             └────────────────┬─────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                    FASTAPI BACKEND (Port 8000)                   │
├──────────────────────────────────────────────────────────────────┤
│                        API Routes Layer                          │
│  POST   /api/generate-itinerary         (IDs: 1000-9999)        │
│  GET    /api/itinerary/{id}                                     │
│  POST   /api/traveler-profile           (IDs: traveler_*)       │
│  POST   /api/find-group                 (Vector similarity)     │
│  POST   /api/compare-itineraries                                │
│  GET    /api/sustainability-tips                                │
│  GET    /api/health                                             │
│  POST   /api/mock-traveler-data                                 │
├──────────────────────────────────────────────────────────────────┤
│                      Services Layer                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Matching Service (services/matching.py)                  │  │
│  │ - generate_itinerary()                                   │  │
│  │ - generate_multiple_itineraries()                        │  │
│  │ - select_activities() - Based on interests              │  │
│  │ - generate_day_plan() - Schedule activities             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │ Scoring Service (services/scoring.py)                   │  │
│  │ - calculate_transport_score()    [30% weight]           │  │
│  │ - calculate_accommodation_score() [20% weight]          │  │
│  │ - calculate_activity_score()      [20% weight]          │  │
│  │ - calculate_local_engagement_score() [20% weight]       │  │
│  │ - calculate_overtourism_mitigation_score() [10% weight] │  │
│  │ - calculate_carbon_footprint()                          │  │
│  │ - generate_explanation()  → Human-readable text         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │ LLM Service (services/llm.py)                           │  │
│  │ - generate_prompt_for_itinerary()                       │  │
│  │ - call_openai_gpt() [OpenAI GPT-3.5]                   │  │
│  │ - parse_llm_itinerary()                                 │  │
│  │ - get_template_itinerary() [Fallback templates]         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │ Similarity Service (utils/similarity.py)                │  │
│  │ - create_profile_vector()      [Normalize to [0,1]]     │  │
│  │ - cosine_similarity()          [Vector similarity]      │  │
│  │ - euclidean_distance()         [Alternative metric]     │  │
│  │ - find_similar_travelers()     [Top K matching]         │  │
│  │ - calculate_group_compatibility()                       │  │
│  │ - recommend_group_size()                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                      Data Layer                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Models (models/schemas.py) - Pydantic                    │  │
│  │ - TripInput                 │ User input                 │  │
│  │ - Itinerary                 │ Complete itinerary         │  │
│  │ - DayPlan                   │ Single day                 │  │
│  │ - DayActivity               │ Single activity            │  │
│  │ - ItinerarySustainability   │ Scores & metrics           │  │
│  │ - ScoreBreakdown            │ 5-dimension breakdown      │  │
│  │ - TravelerProfile           │ User profile               │  │
│  │ - GroupMatch                │ Group recommendation       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │ Carbon Data (data/carbon.py)                            │  │
│  │ CARBON_FACTORS = {                                       │  │
│  │   "flight": 0.12,        # kg CO2/km                    │  │
│  │   "train": 0.021,                                        │  │
│  │   "bus": 0.028,                                          │  │
│  │   "car": 0.15,                                           │  │
│  │   "walk": 0.0                                            │  │
│  │ }                                                         │  │
│  │                                                           │  │
│  │ ACCOMMODATION_CARBON = {                                 │  │
│  │   "eco_hotel": 8.5,      # kg CO2/night                 │  │
│  │   "hotel": 15.0,                                         │  │
│  │   "resort": 25.0,                                        │  │
│  │   "camping": 2.0, ...                                    │  │
│  │ }                                                         │  │
│  │                                                           │  │
│  │ OVERTOURISM_INDEX = {                                    │  │
│  │   "Venice": 9.5,         # 1-10 scale                   │  │
│  │   "Paris": 7.5, ...                                      │  │
│  │ }                                                         │  │
│  │                                                           │  │
│  │ ACTIVITY_DATABASE = {                                    │  │
│  │   "Paris": {...},        # Activities per destination    │  │
│  │   "Tokyo": {...},                                        │  │
│  │   "Barcelona": {...}, ...                                │  │
│  │ }                                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │ In-Memory Storage (Caching)                             │  │
│  │ ITINERARY_CACHE        → {key: [itineraries]}           │  │
│  │ TRAVELER_DATABASE      → {id: TravelerProfile}          │  │
│  │ (Can be replaced with PostgreSQL/MongoDB)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Flow 1: Generate Itinerary

```
User Input (TripInput)
    │
    ├─ origin: "New York"
    ├─ destination: "Paris"
    ├─ days: 5
    ├─ transport_preference: "train"
    ├─ interests: ["culture", "food"]
    └─ sustainability_weights: {...}
    │
    ▼
[Matching Service]
    │
    ├─ estimate_distance("New York", "Paris") → 5800 km
    │
    ├─ select_activities(destination, days, interests)
    │  │
    │  ├─ Look up ACTIVITY_DATABASE["Paris"]
    │  ├─ Filter by interests → ["culture", "food"]
    │  └─ Return: [activity1, activity2, ...]
    │
    └─ generate_day_plan(day, destination, activities)
       │
       ├─ Create time-based schedule (9:00 AM - 6:00 PM)
       ├─ Assign transport per activity
       └─ Calculate carbon per activity
    │
    ▼
[Scoring Service]
    │
    ├─ calculate_transport_score()
    │  │
    │  ├─ Check transport modes [walk, train, bus, car, flight]
    │  ├─ Look up TRANSPORT_SCORES
    │  ├─ Penalize long distance with high-carbon transport
    │  └─ Return: 0-100
    │
    ├─ calculate_accommodation_score()
    │  │
    │  ├─ Check accommodation type [eco_hotel, hotel, resort, ...]
    │  ├─ Look up accommodation_scores
    │  ├─ Bonus for longer stays (≥7 days)
    │  └─ Return: 0-100
    │
    ├─ calculate_activity_score()
    │  │
    │  ├─ Check overtourism index for destination
    │  ├─ Score activities based on local engagement
    │  ├─ Adjust based on overtourism level
    │  └─ Return: 0-100
    │
    ├─ calculate_local_engagement_score()
    │  │
    │  ├─ Count local-focused activities
    │  ├─ Calculate percentage
    │  └─ Return: 0-100
    │
    ├─ calculate_overtourism_mitigation_score()
    │  │
    │  ├─ Check OVERTOURISM_INDEX[destination]
    │  ├─ Apply off-season bonus
    │  ├─ Check for alternative activities
    │  └─ Return: 0-100
    │
    ├─ calculate_carbon_footprint()
    │  │
    │  ├─ Transport carbon: distance × CARBON_FACTORS[mode]
    │  ├─ Accommodation carbon: duration × ACCOMMODATION_CARBON[type]
    │  ├─ Activity carbon: activity × ACTIVITY_CARBON[type]
    │  └─ Return: total kg CO2
    │
    └─ Weighted average using SCORING_WEIGHTS
       total_score = (transport×0.30 + accommodation×0.20
                    + activity×0.20 + local×0.20 + overtourism×0.10)
    │
    ▼
Output: Itinerary
    ├─ id: 12345
    ├─ title: "Sustainable 5-Day Paris Adventure"
    ├─ days: [DayPlan1, DayPlan2, ...]
    └─ sustainability: ItinerarySustainability
       ├─ total_score: 82.5 (0-100)
       ├─ breakdown: ScoreBreakdown (5 dimensions)
       ├─ total_carbon_kg: 145.2
       └─ explanation: "🌱 Good Sustainable Travel..."
```

### Flow 2: Find Group Matches

```
Traveler Profile (TravelerProfile)
    │
    ├─ id: "alice_123"
    ├─ name: "Alice Johnson"
    ├─ destination: "Paris"
    ├─ trip_days: 5
    ├─ sustainability_score_min: 85
    ├─ interests: ["culture", "food"]
    ├─ transport_preference: "train"
    └─ max_group_size: 4
    │
    ▼
[Similarity Service - create_profile_vector]
    │
    ├─ Normalize sustainability: 85/100 = 0.85
    ├─ Normalize days: 5/30 = 0.167
    ├─ Normalize budget: 8500/10000 = 0.85
    │
    ├─ Encode interests (one-hot):
    │  ["adventure": 0, "culture": 1, "nature": 0, "food": 1, ...]
    │
    ├─ Combine: [0.85, 0.167, 0.85, 0, 1, 0, 1, ...]
    │
    └─ Normalize: vector / ||vector||
       Result: profile_vector (unit length)
    │
    ▼
[Similarity Service - find_similar_travelers]
    │
    ├─ Get all travelers from TRAVELER_DATABASE
    ├─ For each other traveler:
    │  │
    │  ├─ similarity = cosine_similarity(alice_vector, other_vector)
    │  │              = dot_product(v1, v2) / (||v1|| × ||v2||)
    │  │
    │  ├─ If similarity ≥ 0.7:
    │  │  └─ Add to matches
    │  │
    │  └─ Sort by similarity (descending)
    │
    ├─ Return top_matches = [(id, profile, score), ...]
    │
    └─ Create group recommendations:
       ├─ Best pair (top 1 match)
       ├─ Calculate group compatibility from top matches
       └─ Recommend group size based on avg similarity
    │
    ▼
Output: GroupMatch
    ├─ traveler_ids: ["alice_123", "bob_456", ...]
    ├─ similarity_score: 0.92
    ├─ recommended_group_size: 2-3
    └─ common_interests: ["culture", "food"]
```

### Flow 3: Compare Itineraries

```
Multiple Itinerary IDs [id1, id2, id3]
    │
    ▼
[Search through ITINERARY_CACHE]
    │
    ├─ For each ID:
    │  ├─ Find matching itinerary
    │  └─ Collect all found
    │
    ▼
[Compare in two ways]
    │
    ├─ By Sustainability Score (descending)
    │  │ id1: 82.5 (Best)
    │  │ id2: 78.0
    │  └─ id3: 72.5
    │
    └─ By Carbon Footprint (ascending)
       │ id3: 120 kg (Lowest)
       │ id2: 145 kg
       └─ id1: 155 kg
    │
    ▼
Output: Comparison
    ├─ comparison.by_score: [sorted by score]
    └─ comparison.by_carbon: [sorted by carbon]
```

## Vector Representation

### Traveler Profile Vector Format

```
[sustainability_norm, days_norm, budget_norm, interest_vector...]

Example (Alice):
[0.85, 0.167, 0.85, 0, 1, 0, 0, 1, 0, 0, 0, 0]
                      ├─ adventure  ├─ culture   ├─ food
                      ├─ nature     ├─ local     └─ relaxation
                      ├─ luxury     
                      └─ budget

Length: 12 dimensions (3 numeric + 8 interest categories + margin for extension)
Normalized: ||vector|| = 1.0
```

### Similarity Calculation

```
For two travelers A and B:
similarity(A, B) = (A · B) / (||A|| × ||B||)

Where:
- A · B = sum of element-wise multiplication
- ||A|| = sqrt(sum of squares)
- Result: 0.0 (completely different) to 1.0 (identical)

Threshold: 0.7 typically means "good match"
```

## Scoring Algorithm

### Complete Scoring Calculation

```
For each Itinerary:

1. Transport Score (30% weight)
   ├─ Base scores: walk=100, train=85, bus=80, car=40, flight=20
   ├─ Average across all transport modes
   ├─ Penalize long-distance high-carbon combinations
   └─ Result: 0-100

2. Accommodation Score (20% weight)
   ├─ Base scores: eco_hotel=90, camping=95, hostel=80, ...
   ├─ Bonus for stays ≥7 days (+5%)
   ├─ Penalty for short stays ≤2 days (-5%)
   └─ Result: 0-100

3. Activity Score (20% weight)
   ├─ Factor in local engagement scores
   ├─ Adjust based on overtourism index
   ├─ Prefer cultural/local activities in high-tourism areas
   └─ Result: 0-100

4. Local Engagement Score (20% weight)
   ├─ Count activities with keywords: ["local", "cooking", "homestay", ...]
   ├─ Calculate: (local_activities / total_activities) × 100
   └─ Result: 0-100

5. Overtourism Mitigation (10% weight)
   ├─ Base: 100 - (overtourism_level × 10)
   ├─ Off-season bonus: ×1.05
   ├─ Duration bonus (≥5 days): ×1.1
   ├─ Alternative activities bonus
   └─ Result: 0-100

Final Score:
total = (transport×0.30 + accommodation×0.20 + activity×0.20
       + local_engagement×0.20 + overtourism×0.10)

Result: 0-100 (100 = perfect sustainability)
```

## Carbon Calculation

### Transport Emissions

```
Carbon = distance_km × CARBON_FACTORS[transport_mode]

Examples (for 1000 km journey):
- Flight:     1000 × 0.12 = 120 kg CO2
- Car:        1000 × 0.15 = 150 kg CO2
- Bus:        1000 × 0.028 = 28 kg CO2
- Train:      1000 × 0.021 = 21 kg CO2
- Walk:       1000 × 0.0 = 0 kg CO2
```

### Accommodation Emissions

```
Carbon = num_nights × ACCOMMODATION_CARBON[type]

Examples (per night):
- Resort:     25 kg CO2
- Hotel:      15 kg CO2
- Airbnb:     12 kg CO2
- Eco Hotel:  8.5 kg CO2
- Hostel:     5.5 kg CO2
- Camping:    2 kg CO2
```

### Total Journey Emissions

```
Total CO2 = Transport Carbon + Accommodation Carbon + Activity Carbon

Example 5-day Paris trip:
├─ Flight (5800 km, 0.12): 696 kg
├─ Hotel (5 nights × 15): 75 kg
├─ Activities (museums, walks): ~5 kg
└─ Total: ~776 kg CO2 equivalent

Compare with sustainable option:
├─ Train (5800 km, 0.021): 121.8 kg
├─ Eco Hotel (5 nights × 8.5): 42.5 kg
├─ Local activities: ~3 kg
└─ Total: ~167 kg CO2 equivalent

Reduction: 78% less emissions!
```

---

## Performance Characteristics

| Operation | Complexity | Time |
|-----------|-----------|------|
| Generate itinerary | O(days × activities) | ~100ms |
| Score itinerary | O(5 dimensions) | ~10ms |
| Find matches | O(n × vector_dim) | ~50ms (n=100 travelers) |
| Compare itineraries | O(m log m) | ~5ms (m=3 itineraries) |
| Cache lookup | O(1) | <1ms |

## Future Enhancements

1. **Database Integration**
   - Replace in-memory with PostgreSQL
   - Enable persistent storage

2. **Advanced ML**
   - Neural networks for better matching
   - Personalization engine

3. **Real-Time Features**
   - WebSocket for collaborative planning
   - Live group chat

4. **API Integrations**
   - Booking.com for accommodations
   - Skyscanner for flights
   - Real carbon tracking APIs

5. **Mobile Support**
   - Native iOS/Android apps
   - Offline capabilities

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2026-01-15
