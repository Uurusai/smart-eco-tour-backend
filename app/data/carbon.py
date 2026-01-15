"""Carbon emission factors and environmental data."""

# CO2 emission factors (kg per kilometer or per night)
CARBON_FACTORS = {
    "flight": 0.12,  # kg CO2 per km
    "train": 0.021,  # kg CO2 per km
    "bus": 0.028,  # kg CO2 per km
    "car": 0.15,  # kg CO2 per km
    "walk": 0.0,  # kg CO2 per km
}

# Accommodation carbon footprint (kg CO2 per night)
ACCOMMODATION_CARBON = {
    "eco_hotel": 8.5,
    "hotel": 15.0,
    "hostel": 5.5,
    "airbnb": 12.0,
    "resort": 25.0,
    "camping": 2.0,
    "lodge": 10.0,
}

# Overtourism indices (1-10, higher = more overtourism)
OVERTOURISM_INDEX = {
    "Venice": 9.5,
    "Barcelona": 8.5,
    "Paris": 7.5,
    "Rome": 8.0,
    "Amsterdam": 8.2,
    "Tokyo": 7.0,
    "New York": 7.8,
    "London": 7.0,
    "Bangkok": 7.5,
    "Bali": 8.0,
    "Dubai": 6.5,
    "Bangkok": 7.5,
    "Miami": 6.0,
    "Sydney": 5.5,
    "Berlin": 6.0,
    "Prague": 7.5,
    "Copenhagen": 5.5,
    "Stockholm": 5.0,
    "Zurich": 4.5,
    "Vienna": 6.5,
}

# Activity carbon footprint (kg CO2 per activity)
ACTIVITY_CARBON = {
    "nature_hiking": 0.0,
    "nature_wildlife_tour": 2.5,
    "nature_safari": 8.0,
    "culture_museum": 0.5,
    "culture_local_tour": 1.0,
    "culture_cooking_class": 0.3,
    "adventure_skydiving": 5.0,
    "adventure_rock_climbing": 0.2,
    "adventure_kayaking": 0.5,
    "local_market": 0.0,
    "local_homestay": 0.0,
    "food_street_food": 0.1,
    "food_fine_dining": 1.5,
    "food_farm_to_table": 0.2,
}

# Distance between major cities (km) - simplified
CITY_DISTANCES = {
    ("New York", "Boston"): 350,
    ("New York", "Washington"): 370,
    ("London", "Paris"): 350,
    ("London", "Amsterdam"): 380,
    ("Paris", "Amsterdam"): 430,
    ("Tokyo", "Kyoto"): 475,
    ("Tokyo", "Osaka"): 515,
    ("Bangkok", "Phuket"): 865,
    ("Barcelona", "Madrid"): 630,
    ("Rome", "Venice"): 390,
    ("Sydney", "Melbourne"): 714,
    ("Singapore", "Bangkok"): 1065,
    ("Dubai", "Abu Dhabi"): 140,
    ("Bali", "Jakarta"): 1610,
}


def get_carbon_for_transport(mode: str, distance_km: float) -> float:
    """Calculate carbon emissions for transport.
    
    Args:
        mode: Transport mode (flight, train, bus, car, walk)
        distance_km: Distance in kilometers
        
    Returns:
        Carbon emissions in kg CO2
    """
    factor = CARBON_FACTORS.get(mode.lower(), 0.0)
    return factor * distance_km


def get_accommodation_carbon(accommodation_type: str) -> float:
    """Get carbon footprint for accommodation type.
    
    Args:
        accommodation_type: Type of accommodation
        
    Returns:
        Carbon emissions in kg CO2 per night
    """
    return ACCOMMODATION_CARBON.get(accommodation_type.lower(), 12.0)


def get_overtourism_score(destination: str) -> float:
    """Get overtourism index for destination.
    
    Args:
        destination: Destination city name
        
    Returns:
        Overtourism score (1-10)
    """
    return OVERTOURISM_INDEX.get(destination, 5.0)


def get_activity_carbon(activity_type: str) -> float:
    """Get carbon footprint for activity type.
    
    Args:
        activity_type: Type of activity
        
    Returns:
        Carbon emissions in kg CO2
    """
    return ACTIVITY_CARBON.get(activity_type.lower(), 0.5)


def estimate_distance(origin: str, destination: str) -> float:
    """Estimate distance between two cities.
    
    Args:
        origin: Origin city
        destination: Destination city
        
    Returns:
        Estimated distance in km
    """
    key = tuple(sorted([origin, destination]))
    if key in CITY_DISTANCES:
        return CITY_DISTANCES[key]
    # Default estimate for unknown cities
    return 800.0
