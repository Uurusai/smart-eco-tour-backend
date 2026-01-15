"""Sustainability scoring engine."""
from typing import Dict, List, Tuple
from app.models.schemas import ScoreBreakdown, ItinerarySustainability, Itinerary
from app.data.carbon import (
    get_carbon_for_transport,
    get_accommodation_carbon,
    get_overtourism_score,
    get_activity_carbon,
)

TRANSPORT_SCORES = {
    "walk": 100,
    "train": 85,
    "bus": 80,
    "car": 40,
    "flight": 20,
}

LOCAL_ENGAGEMENT_FACTORS = {
    "cooking_class": 0.95,
    "homestay_visit": 0.90,
    "local_tour": 0.85,
    "market_visit": 0.80,
    "cultural_workshop": 0.85,
    "museum": 0.60,
    "resort_activity": 0.20,
    "tourist_spot": 0.40,
}


def calculate_transport_score(
    activities: List[Dict],
    transport_preference: str,
    total_distance_km: float,
) -> float:
    """Calculate transport sustainability score.
    
    Args:
        activities: List of activities with transport info
        transport_preference: Preferred transport mode
        total_distance_km: Total distance to travel
        
    Returns:
        Score 0-100
    """
    if not activities:
        return 50.0
    
    transport_modes = [a.get("transport", "car") for a in activities]
    scores = [TRANSPORT_SCORES.get(mode, 50) for mode in transport_modes]
    
    base_score = sum(scores) / len(scores) if scores else 50.0
    
    # Penalize long distances with high-carbon transport
    if total_distance_km > 500:
        if transport_preference == "flight":
            base_score *= 0.6
        elif transport_preference in ["car"]:
            base_score *= 0.7
    
    return min(100.0, max(0.0, base_score))


def calculate_accommodation_score(accommodation_type: str, days: int) -> float:
    """Calculate accommodation sustainability score.
    
    Args:
        accommodation_type: Type of accommodation
        days: Number of nights
        
    Returns:
        Score 0-100
    """
    accommodation_scores = {
        "eco_hotel": 90,
        "camping": 95,
        "hostels": 80,
        "airbnb": 75,
        "hotel": 60,
        "resort": 30,
        "lodge": 85,
    }
    
    score = accommodation_scores.get(accommodation_type.lower(), 60.0)
    
    # Slight bonus for longer stays (less daily impact)
    if days >= 7:
        score *= 1.05
    elif days <= 2:
        score *= 0.95
    
    return min(100.0, max(0.0, score))


def calculate_activity_score(
    activities: List[Dict],
    destination: str,
) -> float:
    """Calculate activity sustainability score.
    
    Args:
        activities: List of activities
        destination: Destination city
        
    Returns:
        Score 0-100
    """
    if not activities:
        return 50.0
    
    activity_scores = []
    overtourism = get_overtourism_score(destination)
    
    for activity in activities:
        activity_type = activity.get("type", "general")
        base_score = LOCAL_ENGAGEMENT_FACTORS.get(activity_type, 50.0) * 100
        
        # Adjust for overtourism at destination
        if overtourism > 7.0:
            # High overtourism - prefer local/cultural activities
            if activity_type in ["cooking_class", "local_tour", "cultural_workshop"]:
                base_score *= 1.1
            elif activity_type == "tourist_spot":
                base_score *= 0.7
        
        activity_scores.append(base_score)
    
    return min(100.0, max(0.0, sum(activity_scores) / len(activity_scores)))


def calculate_local_engagement_score(activities: List[Dict]) -> float:
    """Calculate local community engagement score.
    
    Args:
        activities: List of activities
        
    Returns:
        Score 0-100
    """
    if not activities:
        return 50.0
    
    local_activities = 0
    for activity in activities:
        activity_type = activity.get("type", "").lower()
        if any(keyword in activity_type for keyword in [
            "local", "cooking", "homestay", "market", "cultural", "workshop"
        ]):
            local_activities += 1
    
    engagement_percentage = (local_activities / len(activities)) * 100
    return min(100.0, engagement_percentage)


def calculate_overtourism_mitigation_score(
    destination: str,
    activities: List[Dict],
    days: int,
) -> float:
    """Calculate overtourism mitigation score.
    
    Args:
        destination: Target destination
        activities: List of activities
        days: Number of days
        
    Returns:
        Score 0-100
    """
    overtourism_level = get_overtourism_score(destination)
    
    # Base score inversely proportional to overtourism
    base_score = 100.0 - (overtourism_level * 10)
    
    # Bonus for visiting during off-peak season (simplified heuristic)
    # In production, would check actual travel dates
    base_score *= 1.05
    
    # Bonus for longer stays (less impact per day)
    if days >= 5:
        base_score *= 1.1
    
    # Check for alternative activities (non-mainstream tourist spots)
    unique_activities = sum(1 for a in activities if a.get("type") in [
        "local_tour", "cultural_workshop", "homestay_visit", "market_visit"
    ])
    
    if unique_activities > 0:
        base_score *= (1.0 + (unique_activities / len(activities)) * 0.2)
    
    return min(100.0, max(0.0, base_score))


def calculate_carbon_footprint(
    activities: List[Dict],
    accommodation_type: str,
    days: int,
    total_distance_km: float = 0,
) -> float:
    """Calculate total carbon footprint.
    
    Args:
        activities: List of activities with transport
        accommodation_type: Type of accommodation
        days: Number of days
        total_distance_km: Total distance traveled
        
    Returns:
        Total CO2 in kg
    """
    total_carbon = 0.0
    
    # Transport carbon
    for activity in activities:
        transport = activity.get("transport", "walk")
        distance = activity.get("distance", 0)
        if distance > 0:
            total_carbon += get_carbon_for_transport(transport, distance)
    
    # Accommodation carbon
    accommodation_carbon = get_accommodation_carbon(accommodation_type)
    total_carbon += accommodation_carbon * days
    
    # Activity carbon
    for activity in activities:
        activity_type = activity.get("type", "")
        total_carbon += get_activity_carbon(activity_type)
    
    return total_carbon


def generate_explanation(
    breakdown: ScoreBreakdown,
    total_score: float,
    total_carbon: float,
) -> str:
    """Generate human-readable explanation of sustainability score.
    
    Args:
        breakdown: Score breakdown
        total_score: Overall score
        total_carbon: Total carbon footprint
        
    Returns:
        Explanation string
    """
    # Determine rating
    if total_score >= 85:
        rating = "🌿 Excellent Eco-Conscious Choice"
        sentiment = "This itinerary demonstrates strong sustainability commitments."
    elif total_score >= 70:
        rating = "🌱 Good Sustainable Travel"
        sentiment = "This itinerary balances travel experience with environmental responsibility."
    elif total_score >= 50:
        rating = "⚠️  Moderate Environmental Impact"
        sentiment = "Consider adjusting transport or activity choices for lower impact."
    else:
        rating = "🔴 High Environmental Impact"
        sentiment = "We recommend choosing alternative transport or activities."
    
    # Find strongest area
    breakdown_dict = {
        "transport": breakdown.transport_score,
        "accommodation": breakdown.accommodation_score,
        "activities": breakdown.activity_score,
        "local engagement": breakdown.local_engagement_score,
        "overtourism mitigation": breakdown.overtourism_score,
    }
    
    strongest = max(breakdown_dict, key=breakdown_dict.get)
    weakest = min(breakdown_dict, key=breakdown_dict.get)
    
    explanation = f"""
{rating}

{sentiment}

Key Metrics:
- Overall Score: {total_score:.1f}/100
- Total Carbon: {total_carbon:.1f} kg CO2

Breakdown:
- Transport: {breakdown.transport_score:.1f}/100
- Accommodation: {breakdown.accommodation_score:.1f}/100
- Activities: {breakdown.activity_score:.1f}/100
- Local Engagement: {breakdown.local_engagement_score:.1f}/100
- Overtourism Mitigation: {breakdown.overtourism_score:.1f}/100

Strengths: Your {strongest} choices are excellent for sustainability.
Opportunities: Consider improving {weakest} to increase sustainability.

Tips to improve your score:
1. Use public transport or walking when possible
2. Choose eco-friendly accommodations
3. Engage with local communities and artisans
4. Visit less crowded attractions to reduce overtourism impact
5. Offset carbon with verified carbon credit programs
""".strip()
    
    return explanation


def calculate_itinerary_sustainability(
    destination: str,
    days: int,
    transport_preference: str,
    activities: List[Dict] = None,
    accommodation: str = "hotel",
    total_distance_km: float = 0,
) -> ItinerarySustainability:
    """Calculate comprehensive sustainability score for itinerary.
    
    Args:
        destination: Target destination
        days: Number of days
        transport_preference: Preferred transport
        activities: List of planned activities
        accommodation: Type of accommodation
        total_distance_km: Total distance to travel
        
    Returns:
        ItinerarySustainability object
    """
    if activities is None:
        activities = []
    
    # Calculate individual scores
    transport_score = calculate_transport_score(activities, transport_preference, total_distance_km)
    accommodation_score = calculate_accommodation_score(accommodation, days)
    activity_score = calculate_activity_score(activities, destination)
    local_engagement_score = calculate_local_engagement_score(activities)
    overtourism_score = calculate_overtourism_mitigation_score(destination, activities, days)
    
    # Calculate weighted total score
    breakdown = ScoreBreakdown(
        transport_score=transport_score,
        accommodation_score=accommodation_score,
        activity_score=activity_score,
        local_engagement_score=local_engagement_score,
        overtourism_score=overtourism_score,
    )
    
    # Weighted average (can be customized)
    weights = {
        "transport": 0.30,
        "accommodation": 0.20,
        "activity": 0.20,
        "local_engagement": 0.20,
        "overtourism": 0.10,
    }
    
    total_score = (
        breakdown.transport_score * weights["transport"]
        + breakdown.accommodation_score * weights["accommodation"]
        + breakdown.activity_score * weights["activity"]
        + breakdown.local_engagement_score * weights["local_engagement"]
        + breakdown.overtourism_score * weights["overtourism"]
    )
    
    # Calculate carbon
    total_carbon = calculate_carbon_footprint(activities, accommodation, days, total_distance_km)
    
    # Generate explanation
    explanation = generate_explanation(breakdown, total_score, total_carbon)
    
    return ItinerarySustainability(
        total_score=min(100.0, max(0.0, total_score)),
        breakdown=breakdown,
        total_carbon_kg=total_carbon,
        explanation=explanation,
    )
