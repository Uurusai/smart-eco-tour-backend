"""Itinerary matching and generation logic."""
import random
from typing import List, Dict, Optional
from app.models.schemas import (
    Itinerary,
    DayPlan,
    DayActivity,
    TransportMode,
    ActivityType,
)
from app.services.scoring import calculate_itinerary_sustainability
from app.services.llm import (
    generate_prompt_for_itinerary,
    call_gemini,
    parse_llm_itinerary,
    get_template_itinerary,
)
from app.data.carbon import estimate_distance, get_carbon_for_transport


ACTIVITY_DATABASE = {
    "Paris": {
        ActivityType.NATURE: [
            {"name": "Seine River Walk", "duration": 2.0, "location": "Along Seine"},
            {"name": "Jardin des Plantes", "duration": 3.0, "location": "Latin Quarter"},
            {"name": "Bois de Boulogne", "duration": 4.0, "location": "West Paris"},
        ],
        ActivityType.CULTURE: [
            {"name": "Louvre Museum", "duration": 3.0, "location": "Central Paris"},
            {"name": "Musée d'Orsay", "duration": 2.5, "location": "Left Bank"},
            {"name": "Montmartre Tour", "duration": 3.0, "location": "North Paris"},
            {"name": "Notre-Dame", "duration": 1.5, "location": "Île de la Cité"},
        ],
        ActivityType.LOCAL: [
            {"name": "Local Market Visit", "duration": 2.0, "location": "Marais"},
            {"name": "Café Experience", "duration": 2.0, "location": "Throughout Paris"},
            {"name": "Local Bistro", "duration": 2.0, "location": "Various"},
        ],
        ActivityType.FOOD: [
            {"name": "Cooking Class", "duration": 3.0, "location": "Central Paris"},
            {"name": "Street Food Tour", "duration": 2.0, "location": "Marais"},
            {"name": "Wine Tasting", "duration": 2.0, "location": "Left Bank"},
        ],
    },
    "Tokyo": {
        ActivityType.NATURE: [
            {"name": "Meiji Shrine Forest Walk", "duration": 2.0, "location": "Shibuya"},
            {"name": "Ueno Park", "duration": 2.5, "location": "Ueno"},
            {"name": "Cherry Blossom Walk", "duration": 2.0, "location": "Multiple locations"},
        ],
        ActivityType.CULTURE: [
            {"name": "Traditional Tea Ceremony", "duration": 2.0, "location": "Asakusa"},
            {"name": "Senso-ji Temple", "duration": 2.0, "location": "Asakusa"},
            {"name": "Tsukiji Market Tour", "duration": 2.5, "location": "Central Tokyo"},
            {"name": "Craft Workshop", "duration": 3.0, "location": "Various"},
        ],
        ActivityType.ADVENTURE: [
            {"name": "Sumo Tournament", "duration": 3.0, "location": "Ryogoku"},
            {"name": "Martial Arts Class", "duration": 2.0, "location": "Central Tokyo"},
        ],
        ActivityType.LOCAL: [
            {"name": "Izakaya Experience", "duration": 2.0, "location": "Various"},
            {"name": "Onsen (Hot Spring)", "duration": 2.0, "location": "Various"},
        ],
    },
    "Barcelona": {
        ActivityType.CULTURE: [
            {"name": "Gaudi Architecture Tour", "duration": 3.0, "location": "Central Barcelona"},
            {"name": "Park Güell", "duration": 2.5, "location": "Gràcia"},
            {"name": "Gothic Quarter Tour", "duration": 2.5, "location": "Gothic Quarter"},
            {"name": "Sagrada Familia", "duration": 2.0, "location": "Eixample"},
        ],
        ActivityType.NATURE: [
            {"name": "Beach Walk", "duration": 2.0, "location": "Barceloneta"},
            {"name": "Montjuïc Gardens", "duration": 2.5, "location": "Montjuïc"},
        ],
        ActivityType.LOCAL: [
            {"name": "La Boqueria Market", "duration": 2.0, "location": "Ramblas"},
            {"name": "Tapas Tour", "duration": 3.0, "location": "Old Town"},
        ],
        ActivityType.ADVENTURE: [
            {"name": "Beach Sports", "duration": 2.0, "location": "Barceloneta Beach"},
        ],
    },
    "Bangkok": {
        ActivityType.CULTURE: [
            {"name": "Wat Pho Temple", "duration": 2.0, "location": "Old City"},
            {"name": "Grand Palace", "duration": 2.0, "location": "Old City"},
            {"name": "Floating Market", "duration": 3.0, "location": "Outside Bangkok"},
            {"name": "Traditional Massage", "duration": 2.0, "location": "Various"},
        ],
        ActivityType.LOCAL: [
            {"name": "Cooking Class", "duration": 3.0, "location": "Central Bangkok"},
            {"name": "Local Food Tour", "duration": 2.5, "location": "Various"},
            {"name": "Street Food Exploration", "duration": 2.0, "location": "Night Markets"},
        ],
        ActivityType.ADVENTURE: [
            {"name": "Muay Thai Class", "duration": 2.0, "location": "Central Bangkok"},
            {"name": "Tuk Tuk Night Tour", "duration": 2.0, "location": "Various"},
        ],
        ActivityType.NATURE: [
            {"name": "Erawan National Park", "duration": 4.0, "location": "Outside Bangkok"},
        ],
    },
}

ACCOMMODATION_OPTIONS = {
    "eco_hotel": {"carbon": 8.5, "description": "Eco-certified sustainable hotel"},
    "hotel": {"carbon": 15.0, "description": "Standard hotel"},
    "hostel": {"carbon": 5.5, "description": "Budget-friendly hostel"},
    "airbnb": {"carbon": 12.0, "description": "Local homestay/apartment"},
    "lodge": {"carbon": 10.0, "description": "Local lodge or boutique"},
}


def select_activities(
    destination: str,
    days: int,
    interests: List[ActivityType],
    sustainability_preference: float,
) -> List[Dict]:
    """Select activities based on interests and sustainability.
    
    Args:
        destination: Target destination
        days: Number of days
        interests: List of activity interests
        sustainability_preference: Preference score (0-1)
        
    Returns:
        List of selected activities
    """
    destination_activities = ACTIVITY_DATABASE.get(destination, {})
    
    selected = []
    activities_per_day = 4 + int(days / 2)
    
    for day in range(days):
        day_activities = []
        
        if interests:
            # Prioritize user interests
            for interest in interests[:2]:
                activities = destination_activities.get(interest, [])
                if activities:
                    activity = random.choice(activities)
                    day_activities.append({
                        "type": interest,
                        "name": activity["name"],
                        "duration": activity["duration"],
                        "location": activity["location"],
                        "transport": random.choice([TransportMode.WALK, TransportMode.BUS])
                        if sustainability_preference > 0.5
                        else random.choice([TransportMode.CAR, TransportMode.BUS]),
                        "distance": random.uniform(1, 10),
                    })
        
        # Fill remaining slots with random activities
        while len(day_activities) < min(activities_per_day, 5):
            all_activities = []
            for activity_type, acts in destination_activities.items():
                all_activities.extend([
                    {
                        **act,
                        "type": activity_type,
                        "transport": random.choice([
                            TransportMode.WALK,
                            TransportMode.BUS,
                            TransportMode.TRAIN,
                        ]) if sustainability_preference > 0.5 else TransportMode.CAR,
                        "distance": random.uniform(1, 15),
                    }
                    for act in acts
                ])
            
            if all_activities:
                activity = random.choice(all_activities)
                if activity not in day_activities:
                    day_activities.append(activity)
        
        selected.extend(day_activities[:activities_per_day])
    
    return selected


def generate_day_plan(
    day: int,
    destination: str,
    activities: List[Dict],
) -> DayPlan:
    """Generate a single day plan.
    
    Args:
        day: Day number
        destination: Destination city
        activities: Available activities
        
    Returns:
        DayPlan object
    """
    day_activities_list = [a for a in activities if random.random() > 0.6]
    
    if not day_activities_list:
        day_activities_list = activities[:3]
    
    day_activity_objects = []
    current_time = 9  # Start at 9 AM
    
    for activity in day_activities_list[:4]:
        day_activity_objects.append(
            DayActivity(
                time=f"{current_time:02d}:00",
                activity=activity.get("name", "Activity"),
                location=activity.get("location", destination),
                transport=activity.get("transport", TransportMode.WALK),
                duration_hours=activity.get("duration", 2.0),
                carbon_emission_kg=get_carbon_for_transport(
                    activity.get("transport", "walk"),
                    activity.get("distance", 0),
                ),
            )
        )
        current_time += int(activity.get("duration", 2.0)) + 1
    
    return DayPlan(
        day=day,
        activities=day_activity_objects,
        accommodation="eco_hotel",
        accommodation_carbon_kg=8.5,
        total_carbon_kg=sum(a.carbon_emission_kg for a in day_activity_objects) + 8.5,
    )


def generate_itinerary(
    origin: str,
    destination: str,
    days: int,
    transport_preference: TransportMode,
    interests: List[ActivityType] = None,
    sustainability_weights: Dict[str, float] = None,
    use_llm: bool = True,
) -> Itinerary:
    """Generate complete itinerary.
    
    Args:
        origin: Starting location
        destination: Target destination
        days: Number of days
        transport_preference: Preferred transport
        interests: User interests
        sustainability_weights: Sustainability priorities
        use_llm: Whether to use LLM for generation
        
    Returns:
        Complete Itinerary object
    """
    if interests is None:
        interests = [ActivityType.CULTURE, ActivityType.NATURE]
    
    if sustainability_weights is None:
        sustainability_weights = {
            "carbon": 0.4,
            "local": 0.3,
            "culture": 0.2,
            "overtourism": 0.1,
        }
    
    # Try LLM-powered generation first
    llm_itinerary = None
    if use_llm:
        try:
            prompt = generate_prompt_for_itinerary(
                origin=origin,
                destination=destination,
                days=days,
                transport_preference=str(transport_preference.value) if hasattr(transport_preference, 'value') else str(transport_preference),
                sustainability_weights=sustainability_weights,
                interests=[str(i.value) if hasattr(i, 'value') else str(i) for i in interests],
            )
            llm_response = call_gemini(prompt)
            # Don't print the full response - it can be huge and slow down output
            if llm_response:
                llm_itinerary = parse_llm_itinerary(llm_response)
                print(f"✅ LLM generated itinerary for {destination}")
        except Exception as e:
            print(f"⚠️ LLM generation failed: {e}, falling back to template")
    
    print(f"📍 Step 1: Estimating distance...")
    # Estimate distance
    distance = estimate_distance(origin, destination)
    print(f"📍 Step 2: Distance = {distance} km")
    sustainability_score = min(100.0, (1 - (distance / 10000)) * 100)  # Penalize long distances
    
    print(f"📍 Step 3: Selecting activities...")
    # Generate activities
    activities = select_activities(
        destination,
        days,
        interests,
        sustainability_score / 100,
    )
    print(f"📍 Step 4: Selected {len(activities)} activities")
    
    # Generate day plans
    print(f"📍 Step 5: Generating day plans...")
    day_plans = []
    for day in range(1, days + 1):
        day_plan = generate_day_plan(day, destination, activities)
        day_plans.append(day_plan)
    print(f"📍 Step 6: Generated {len(day_plans)} day plans")
    
    # Calculate sustainability
    accommodation = "eco_hotel" if sustainability_score > 70 else "hotel"
    print(f"📍 Step 7: Calculating sustainability...")
    sustainability = calculate_itinerary_sustainability(
        destination=destination,
        days=days,
        transport_preference=transport_preference,
        activities=activities,
        accommodation=accommodation,
        total_distance_km=distance,
    )
    print(f"📍 Step 8: Sustainability calculated")
    
    # Use LLM-enhanced title and description if available
    title = f"Sustainable {days}-Day {destination} Adventure"
    description = f"Eco-conscious itinerary from {origin} to {destination}"
    
    if llm_itinerary and not llm_itinerary.get("fallback"):
        title = llm_itinerary.get("title", title)
        description = llm_itinerary.get("description", description)
    
    print(f"📍 Step 9: Creating Itinerary object...")
    return Itinerary(
        id=random.randint(1, 10000),
        title=title,
        description=description,
        days=day_plans,
        sustainability=sustainability,
        preferred_transport=transport_preference,
    )


def generate_multiple_itineraries(
    origin: str,
    destination: str,
    days: int,
    transport_preference: TransportMode,
    interests: List[ActivityType] = None,
    count: int = 3,
) -> List[Itinerary]:
    """Generate multiple itinerary options.
    
    Args:
        origin: Starting location
        destination: Target destination
        days: Number of days
        transport_preference: Preferred transport
        interests: User interests
        count: Number of itineraries to generate
        
    Returns:
        List of itineraries
    """
    print("Entering generate_multiple_itineraries function")
    
    itineraries = []
    
    # Only use LLM for the first itinerary, use templates for the rest (faster)
    for i in range(count):
        use_llm = (i == 0)  # Only first itinerary uses LLM
        print(f"Generating itinerary {i+1}/{count} (use_llm={use_llm})")
        
        itinerary = generate_itinerary(
            origin=origin,
            destination=destination,
            days=days,
            transport_preference=transport_preference,
            interests=interests,
            use_llm=use_llm,
        )
        itineraries.append(itinerary)
        print(f"✅ Itinerary {i+1} generated successfully")
    
    # Sort by sustainability score (descending)
    itineraries.sort(
        key=lambda x: x.sustainability.total_score,
        reverse=True,
    )
    
    print(f"✅ All {len(itineraries)} itineraries generated and sorted")
    return itineraries
