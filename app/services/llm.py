"""LLM integration for itinerary generation."""
import os
from typing import Optional
from dotenv import load_dotenv
import json

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TEMPLATE_ITINERARIES = {
    "eco_focused": {
        "title": "Sustainable Explorer",
        "description": "Low-carbon activities with emphasis on local culture and nature",
        "activities": [
            "morning_nature_hike",
            "local_market_visit",
            "homestay_lunch",
            "cultural_workshop",
            "evening_walk",
        ],
        "transport_mix": {"train": 0.6, "bus": 0.3, "walk": 0.1},
        "accommodation": "eco_hotel",
    },
    "adventure_focused": {
        "title": "Active Adventurer",
        "description": "Mix of adventure activities with moderate carbon footprint",
        "activities": [
            "rock_climbing",
            "kayaking",
            "local_tour",
            "hiking",
            "adventure_sport",
        ],
        "transport_mix": {"bus": 0.5, "car": 0.3, "train": 0.2},
        "accommodation": "lodge",
    },
    "culture_focused": {
        "title": "Cultural Immersion",
        "description": "Deep cultural exploration with local engagement",
        "activities": [
            "museum_visit",
            "cooking_class",
            "local_artisan_tour",
            "language_lesson",
            "traditional_ceremony",
        ],
        "transport_mix": {"walk": 0.4, "bus": 0.4, "train": 0.2},
        "accommodation": "airbnb",
    },
    "relaxation_focused": {
        "title": "Mindful Retreat",
        "description": "Relaxation and wellness with sustainable practices",
        "activities": [
            "yoga_session",
            "spa_treatment",
            "nature_meditation",
            "wellness_workshop",
            "peaceful_walk",
        ],
        "transport_mix": {"train": 0.6, "walk": 0.4},
        "accommodation": "eco_hotel",
    },
}

SAMPLE_ITINERARIES_BY_DESTINATION = {
    "Paris": {
        "day_1": [
            "9:00 AM - Arrive at Gare du Nord (Train Station)",
            "10:00 AM - Check-in at eco-hotel",
            "12:00 PM - Walk along Seine River",
            "2:00 PM - Local bistro lunch (farm-to-table)",
            "4:00 PM - Visit Musée d'Orsay",
            "7:00 PM - Dinner at local restaurant",
        ],
        "day_2": [
            "8:00 AM - Breakfast at hotel",
            "9:00 AM - Montmartre walking tour",
            "12:00 PM - Street art and local artists",
            "1:30 PM - Lunch at local café",
            "3:00 PM - Paris Museum of Science",
            "6:00 PM - Evening walk through Latin Quarter",
        ],
        "accommodation": "eco_hotel",
    },
    "Tokyo": {
        "day_1": [
            "10:00 AM - Arrive at Tokyo Station",
            "11:00 AM - Check-in at eco-friendly hotel",
            "1:00 PM - Traditional tea ceremony",
            "3:00 PM - Senso-ji Temple visit",
            "5:00 PM - Tsukiji market exploration",
            "7:00 PM - Dinner near Asakusa",
        ],
        "day_2": [
            "8:00 AM - Yoga and meditation session",
            "9:30 AM - Visit local onsen (hot spring)",
            "12:00 PM - Lunch with local guide",
            "2:00 PM - Meiji Shrine forest walk",
            "4:00 PM - Traditional craft workshop",
            "6:30 PM - Street food tour",
        ],
        "accommodation": "hotel",
    },
    "Barcelona": {
        "day_1": [
            "9:00 AM - Arrive and settle in",
            "11:00 AM - Gothic Quarter walking tour",
            "1:00 PM - Lunch at local tapas bar",
            "3:00 PM - Park Güell visit",
            "5:00 PM - Beach walk and sunset",
            "7:00 PM - Dinner with ocean view",
        ],
        "day_2": [
            "8:00 AM - Breakfast at café",
            "9:00 AM - Gaudi architecture tour",
            "12:00 PM - Local market visit (La Boqueria)",
            "2:00 PM - Mediterranean lunch",
            "4:00 PM - Beach sports or relaxation",
            "6:00 PM - Evening tapas experience",
        ],
        "accommodation": "hotel",
    },
    "Bangkok": {
        "day_1": [
            "10:00 AM - Arrive at hotel",
            "12:00 PM - Traditional floating market tour",
            "3:00 PM - Local lunch",
            "4:00 PM - Temple visit (Wat Pho)",
            "6:00 PM - Thai cooking class",
            "8:00 PM - Street food tour",
        ],
        "day_2": [
            "8:00 AM - Sunrise yoga at hotel",
            "9:30 AM - Reclining Buddha Temple",
            "12:00 PM - Local restaurant lunch",
            "2:00 PM - Traditional Thai massage",
            "4:00 PM - Night bazaar exploration",
            "7:00 PM - Dinner and evening walk",
        ],
        "accommodation": "hotel",
    },
}


def generate_prompt_for_itinerary(
    origin: str,
    destination: str,
    days: int,
    transport_preference: str,
    sustainability_weights: dict,
    interests: list,
) -> str:
    """Generate a prompt for LLM itinerary generation.
    
    Args:
        origin: Starting location
        destination: Target destination
        days: Number of days
        transport_preference: Preferred transport mode
        sustainability_weights: Dict of weight values for sustainability factors
        interests: List of interest categories
        
    Returns:
        Formatted prompt string
    """
    interests_str = ", ".join(interests) if interests else "general sightseeing"
    weights_str = "\n".join([f"  - {k}: {v}" for k, v in sustainability_weights.items()])
    
    prompt = f"""Create a sustainable {days}-day itinerary from {origin} to {destination}.

Trip Details:
- Origin: {origin}
- Destination: {destination}
- Duration: {days} days
- Preferred Transport: {transport_preference}
- Interests: {interests_str}

Sustainability Priorities:
{weights_str}

Please provide:
1. A day-by-day breakdown with specific times and activities
2. Recommended accommodation types (prefer eco-friendly options)
3. Local, low-carbon transport options
4. Activities that minimize environmental impact and support local communities
5. Brief notes on why each choice is sustainable

Format the response as a structured itinerary with clear sections for each day."""
    
    return prompt


def call_groq(prompt: str, timeout: int = 30) -> Optional[str]:
    """Call Groq API for itinerary generation.
    
    Args:
        prompt: The prompt for itinerary generation
        timeout: Request timeout in seconds (default 30)
        
    Returns:
        Generated itinerary text or None if API unavailable
    """
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_"):
        print("⚠️  Groq API key not configured. Using fallback template.")
        return None
    
    try:
        # Initialize LangChain ChatGroq client
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_tokens=4096,
            timeout=timeout,
        )
        
        # Create messages
        messages = [
            SystemMessage(content="You are an expert sustainable travel consultant. Create detailed, eco-friendly travel itineraries that minimize environmental impact while maximizing authentic local experiences."),
            HumanMessage(content=prompt)
        ]
        
        # Invoke the model
        response = llm.invoke(messages)
        
        return response.content

    except Exception as e:
        print(f"⚠️  Groq API call failed: {e}. Using fallback template.")
        return None
# Keep call_gemini as alias for backward compatibility
call_gemini = call_groq


def get_template_itinerary(
    destination: str, style: str = "eco_focused"
) -> dict:
    """Get a template itinerary for fallback.
    
    Args:
        destination: Target destination
        style: Style of itinerary (eco_focused, adventure_focused, etc.)
        
    Returns:
        Template itinerary dict
    """
    template = TEMPLATE_ITINERARIES.get(style, TEMPLATE_ITINERARIES["eco_focused"])
    
    sample = SAMPLE_ITINERARIES_BY_DESTINATION.get(
        destination,
        SAMPLE_ITINERARIES_BY_DESTINATION["Paris"],
    )
    
    return {
        "title": template["title"],
        "description": template["description"],
        "template_style": style,
        "destination": destination,
        "sample_schedule": sample,
        "accommodation": template["accommodation"],
        "transport_mix": template["transport_mix"],
        "fallback": True,
    }


def parse_llm_itinerary(llm_response: str) -> dict:
    """Parse LLM response into structured itinerary.
    
    Args:
        llm_response: Raw LLM response text
        
    Returns:
        Parsed itinerary dict
    """
    # Simple parsing - in production, this would be more sophisticated
    lines = llm_response.split("\n")
    
    itinerary = {
        "title": "AI-Generated Itinerary",
        "description": "Custom itinerary generated by AI",
        "days": {},
        "raw_response": llm_response,
        "fallback": False,
    }
    
    current_day = None
    activities = []
    
    for line in lines:
        line = line.strip()
        if "day" in line.lower() and any(char.isdigit() for char in line):
            if current_day is not None:
                itinerary["days"][current_day] = activities
            current_day = line
            activities = []
        elif line and current_day is not None:
            activities.append(line)
    
    if current_day is not None:
        itinerary["days"][current_day] = activities
    
    return itinerary
