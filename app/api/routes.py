"""FastAPI routes for the Eco-Tour backend."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import (
    TripInput,
    Itinerary,
    TravelerProfile,
    GroupMatch,
    TransportMode,
    ActivityType,
)
from app.services.matching import generate_multiple_itineraries
from app.utils.similarity import (
    create_profile_vector,
    find_similar_travelers,
    calculate_group_compatibility,
    recommend_group_size,
)
import random
import string

router = APIRouter(prefix="/api", tags=["eco-tour"])

# In-memory database for demo
TRAVELER_DATABASE: dict = {}
ITINERARY_CACHE: dict = {}


@router.post("/generate-itinerary")
async def generate_itinerary_endpoint(
    trip_input: TripInput,
    num_options: int = Query(3, ge=1, le=5),
) -> dict:
    """Generate sustainable itineraries for a trip.
    
    Args:
        trip_input: User's trip preferences
        num_options: Number of itinerary options (1-5)
        
    Returns:
        Multiple itinerary options with sustainability scores
    """
    try:
        print(f"🚀 Entered generate_itinerary_endpoint: {trip_input.origin} -> {trip_input.destination}")
        itineraries = generate_multiple_itineraries(
            origin=trip_input.origin,
            destination=trip_input.destination,
            days=trip_input.days,
            transport_preference=trip_input.transport_preference,
            interests=trip_input.interests,
            count=num_options,
        )
        
        # Cache for later use
        cache_key = f"{trip_input.origin}_{trip_input.destination}_{trip_input.days}"
        ITINERARY_CACHE[cache_key] = itineraries
        
        # Serialize itineraries to dicts for proper JSON response
        print(f"📦 Serializing {len(itineraries)} itineraries...")
        serialized_itineraries = [itinerary.model_dump(mode='json') for itinerary in itineraries]
        
        print(f"✅ Returning {len(serialized_itineraries)} itineraries to frontend")
        
        return {
            "status": "success",
            "origin": trip_input.origin,
            "destination": trip_input.destination,
            "days": trip_input.days,
            "itineraries": serialized_itineraries,
            "message": f"Generated {len(itineraries)} sustainable itinerary options",
        }
    except Exception as e:
        import traceback
        print(f"❌ Error in generate_itinerary_endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/itinerary/{itinerary_id}")
async def get_itinerary_details(itinerary_id: int) -> dict:
    """Get detailed view of a specific itinerary.
    
    Args:
        itinerary_id: ID of the itinerary
        
    Returns:
        Detailed itinerary information with day-by-day breakdown
    """
    # Search through cached itineraries
    for itineraries in ITINERARY_CACHE.values():
        for itinerary in itineraries:
            if itinerary.id == itinerary_id:
                return {
                    "status": "success",
                    "itinerary": itinerary.model_dump(mode='json'),
                }
    
    raise HTTPException(status_code=404, detail="Itinerary not found")


@router.post("/traveler-profile")
async def create_traveler_profile(profile: TravelerProfile) -> dict:
    """Create or update a traveler profile for group matching.
    
    Args:
        profile: Traveler profile information
        
    Returns:
        Created profile with vector representation
    """
    try:
        # Generate profile vector
        vector = create_profile_vector(
            sustainability_score=profile.sustainability_score_min,
            interests=[str(i) for i in profile.interests],
            days=profile.trip_days,
            budget=profile.sustainability_score_min * 100,  # Mock budget
        )
        
        profile.profile_vector = vector
        
        # Store in database
        TRAVELER_DATABASE[profile.id] = profile
        
        return {
            "status": "success",
            "traveler_id": profile.id,
            "message": f"Profile created for {profile.name}",
            "profile": profile.model_dump(mode='json'),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/travelers")
async def list_travelers() -> dict:
    """List all registered travelers.
    
    Returns:
        List of traveler profiles
    """
    return {
        "status": "success",
        "count": len(TRAVELER_DATABASE),
        "travelers": [t.model_dump(mode='json') for t in TRAVELER_DATABASE.values()],
    }


@router.post("/find-group")
async def find_group_matches(
    traveler_id: str,
    destination: Optional[str] = None,
    min_similarity: float = Query(0.7, ge=0.0, le=1.0),
) -> dict:
    """Find compatible travelers for group travel.
    
    Args:
        traveler_id: ID of the reference traveler
        destination: Optional destination filter
        min_similarity: Minimum similarity threshold
        
    Returns:
        List of compatible travelers and group recommendations
    """
    if traveler_id not in TRAVELER_DATABASE:
        raise HTTPException(status_code=404, detail="Traveler not found")
    
    traveler = TRAVELER_DATABASE[traveler_id]
    
    # Build list of other travelers
    other_travelers = [
        (tid, t)
        for tid, t in TRAVELER_DATABASE.items()
        if tid != traveler_id
        and (destination is None or t.destination == destination or t.destination == traveler.destination)
    ]
    
    if not other_travelers:
        return {
            "status": "success",
            "traveler_id": traveler_id,
            "matches": [],
            "message": "No compatible travelers found",
        }
    
    # Find similar travelers
    matches = []
    for other_id, other_profile in other_travelers:
        if other_profile.profile_vector and traveler.profile_vector:
            # Calculate similarity
            similarity = sum(
                a * b
                for a, b in zip(traveler.profile_vector, other_profile.profile_vector)
            ) / (
                1e-6
                + (sum(a**2 for a in traveler.profile_vector) ** 0.5)
                * (sum(b**2 for b in other_profile.profile_vector) ** 0.5)
            )
            
            if similarity >= min_similarity:
                matches.append((other_id, other_profile, similarity))
    
    # Sort by similarity
    matches.sort(key=lambda x: x[2], reverse=True)
    
    # Create group recommendations
    group_recommendations = []
    if matches:
        # Best pair
        best_match = matches[0]
        group_recommendations.append(
            GroupMatch(
                traveler_ids=[traveler_id, best_match[0]],
                similarity_score=float(best_match[2]),
                recommended_group_size=2,
                common_interests=[
                    i for i in traveler.interests
                    if i in best_match[1].interests
                ]
                if best_match[1].interests else [],
            )
        )
        
        # Larger groups if good compatibility
        if len(matches) >= 2 and matches[0][2] > 0.8:
            group_profiles = [
                traveler.profile_vector
            ] + [
                m[1].profile_vector
                for m in matches[:2]
                if m[1].profile_vector
            ]
            
            group_size = recommend_group_size(group_profiles)
            
            group_recommendations.append(
                GroupMatch(
                    traveler_ids=[traveler_id] + [m[0] for m in matches[:group_size - 1]],
                    similarity_score=sum(m[2] for m in matches[:group_size - 1]) / (group_size - 1),
                    recommended_group_size=group_size,
                    common_interests=list(set(traveler.interests) & set(
                        i for m in matches[:group_size - 1]
                        for i in (m[1].interests or [])
                    )),
                )
            )
    
    return {
        "status": "success",
        "traveler_id": traveler_id,
        "matches_found": len(matches),
        "top_matches": [
            {
                "traveler_id": m[0],
                "name": m[1].name,
                "destination": m[1].destination,
                "similarity_score": float(m[2]),
                "common_interests": [str(i.value) if hasattr(i, 'value') else str(i) for i in traveler.interests if m[1].interests and i in m[1].interests],
            }
            for m in matches[:5]
        ],
        "group_recommendations": [gr.model_dump(mode='json') for gr in group_recommendations],
    }


@router.post("/score-itinerary")
async def score_itinerary(itinerary_id: int) -> dict:
    """Score an existing itinerary and return detailed breakdown.
    
    Takes an itinerary ID and returns its sustainability score with 
    detailed breakdown across all sustainability dimensions.
    
    Args:
        itinerary_id: ID of the itinerary to score
        
    Returns:
        Sustainability score and detailed breakdown with explanations
    """
    # Find the itinerary in cache
    found_itinerary = None
    for cached_itineraries in ITINERARY_CACHE.values():
        for itinerary in cached_itineraries:
            if itinerary.id == itinerary_id:
                found_itinerary = itinerary
                break
        if found_itinerary:
            break
    
    if not found_itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    sustainability = found_itinerary.sustainability
    breakdown = sustainability.breakdown
    
    return {
        "status": "success",
        "itinerary_id": itinerary_id,
        "title": found_itinerary.title,
        "total_score": sustainability.total_score,
        "total_carbon_kg": sustainability.total_carbon_kg,
        "breakdown": {
            "transport_score": {
                "value": breakdown.transport_score,
                "weight": "30%",
                "explanation": "Based on transport modes used (train/bus = high, flight = low)"
            },
            "accommodation_score": {
                "value": breakdown.accommodation_score,
                "weight": "20%",
                "explanation": "Based on eco-friendliness of lodging choices"
            },
            "activity_score": {
                "value": breakdown.activity_score,
                "weight": "20%",
                "explanation": "Based on environmental impact of activities"
            },
            "local_engagement_score": {
                "value": breakdown.local_engagement_score,
                "weight": "20%",
                "explanation": "Based on support for local communities and businesses"
            },
            "overtourism_score": {
                "value": breakdown.overtourism_score,
                "weight": "10%",
                "explanation": "Based on avoiding overcrowded destinations and seasons"
            },
        },
        "explanation": sustainability.explanation,
        "recommendations": [
            "Consider extending your stay to reduce per-day carbon impact",
            "Look for locally-owned restaurants and shops",
            "Opt for walking tours when available",
        ] if sustainability.total_score < 80 else [
            "Great choices! This itinerary is highly sustainable",
            "Consider sharing your experience to inspire others",
        ],
    }


@router.post("/compare-itineraries")
async def compare_itineraries(itinerary_ids: List[int]) -> dict:
    """Compare multiple itineraries side-by-side.
    
    Args:
        itinerary_ids: List of itinerary IDs to compare
        
    Returns:
        Comparison of itineraries with sustainability scores
    """
    itineraries = []
    
    for itinerary_id in itinerary_ids:
        for cached_itineraries in ITINERARY_CACHE.values():
            for itinerary in cached_itineraries:
                if itinerary.id == itinerary_id:
                    itineraries.append(itinerary)
                    break
    
    if not itineraries:
        raise HTTPException(status_code=404, detail="No matching itineraries found")
    
    # Create comparison
    comparison = {
        "status": "success",
        "count": len(itineraries),
        "itineraries": [it.model_dump(mode='json') for it in itineraries],
        "comparison": {
            "by_score": sorted(
                [
                    {
                        "id": it.id,
                        "title": it.title,
                        "score": it.sustainability.total_score,
                    }
                    for it in itineraries
                ],
                key=lambda x: x["score"],
                reverse=True,
            ),
            "by_carbon": sorted(
                [
                    {
                        "id": it.id,
                        "title": it.title,
                        "carbon_kg": it.sustainability.total_carbon_kg,
                    }
                    for it in itineraries
                ],
                key=lambda x: x["carbon_kg"],
            ),
        },
    }
    
    return comparison


@router.get("/sustainability-tips")
async def get_sustainability_tips(destination: str) -> dict:
    """Get sustainability tips for a destination.
    
    Args:
        destination: Target destination
        
    Returns:
        Tips for sustainable travel
    """
    tips = {
        "Paris": [
            "Use the extensive metro and bus system instead of taxis",
            "Rent a bike for short distances",
            "Visit local markets for farm-to-table meals",
            "Stay in eco-certified hotels in Marais district",
            "Walk along the Seine for free nature experience",
        ],
        "Tokyo": [
            "Use the world's best public transport system (trains and subways)",
            "Try local onsen (hot springs) for wellness",
            "Eat at local ramen shops instead of tourist restaurants",
            "Visit temples and gardens in the early morning to avoid crowds",
            "Use coin lockers instead of checking luggage",
        ],
        "Barcelona": [
            "Use the metro for efficient transport",
            "Visit Park Güell early morning to avoid overtourism",
            "Shop at La Boqueria market for local produce",
            "Take the beach tram instead of taxis",
            "Eat at local tapas bars in the Gothic Quarter",
        ],
        "Bangkok": [
            "Use the BTS Skytrain and MRT for fast, efficient transport",
            "Visit floating markets in the early morning",
            "Eat street food from local vendors",
            "Respect temple etiquette and dress codes",
            "Support local artisans and craft makers",
        ],
    }
    
    destination_tips = tips.get(destination, tips["Paris"])
    
    return {
        "status": "success",
        "destination": destination,
        "tips": destination_tips,
        "message": f"Sustainability tips for {destination}",
    }


@router.post("/mock-traveler-data")
async def create_mock_travelers() -> dict:
    """Create mock traveler data for testing group matching.
    
    Returns:
        Confirmation of created profiles
    """
    mock_travelers = [
        TravelerProfile(
            id="traveler_001",
            name="Alice Johnson",
            destination="Paris",
            trip_days=5,
            sustainability_score_min=85,
            interests=[ActivityType.CULTURE, ActivityType.FOOD],
            transport_preference=TransportMode.TRAIN,
            max_group_size=4,
        ),
        TravelerProfile(
            id="traveler_002",
            name="Bob Smith",
            destination="Paris",
            trip_days=5,
            sustainability_score_min=80,
            interests=[ActivityType.CULTURE, ActivityType.NATURE],
            transport_preference=TransportMode.TRAIN,
            max_group_size=5,
        ),
        TravelerProfile(
            id="traveler_003",
            name="Carol White",
            destination="Tokyo",
            trip_days=7,
            sustainability_score_min=90,
            interests=[ActivityType.CULTURE, ActivityType.LOCAL],
            transport_preference=TransportMode.TRAIN,
            max_group_size=4,
        ),
        TravelerProfile(
            id="traveler_004",
            name="David Brown",
            destination="Barcelona",
            trip_days=4,
            sustainability_score_min=70,
            interests=[ActivityType.ADVENTURE, ActivityType.NATURE],
            transport_preference=TransportMode.BUS,
            max_group_size=6,
        ),
        TravelerProfile(
            id="traveler_005",
            name="Emma Davis",
            destination="Paris",
            trip_days=5,
            sustainability_score_min=82,
            interests=[ActivityType.FOOD, ActivityType.LOCAL],
            transport_preference=TransportMode.WALK,
            max_group_size=3,
        ),
    ]
    
    created_count = 0
    for traveler in mock_travelers:
        # Create profile vectors
        vector = create_profile_vector(
            sustainability_score=traveler.sustainability_score_min,
            interests=[str(i) for i in traveler.interests],
            days=traveler.trip_days,
            budget=traveler.sustainability_score_min * 100,
        )
        traveler.profile_vector = vector
        TRAVELER_DATABASE[traveler.id] = traveler
        created_count += 1
    
    return {
        "status": "success",
        "count": created_count,
        "message": f"Created {created_count} mock travelers",
        "travelers": [{"id": t.id, "name": t.name} for t in mock_travelers],
    }


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.
    
    Returns:
        API status
    """
    return {
        "status": "healthy",
        "service": "Smart Eco Tour Backend API",
        "version": "1.0.0",
        "cached_itineraries": len(ITINERARY_CACHE),
        "registered_travelers": len(TRAVELER_DATABASE),
    }
