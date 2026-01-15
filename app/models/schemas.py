"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class TransportMode(str, Enum):
    """Supported transport modes."""
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    WALK = "walk"


class ActivityType(str, Enum):
    """Types of activities."""
    NATURE = "nature"
    CULTURE = "culture"
    ADVENTURE = "adventure"
    LOCAL = "local"
    FOOD = "food"


class DayActivity(BaseModel):
    """Single activity in an itinerary."""
    time: str
    activity: str
    location: str
    transport: TransportMode
    duration_hours: float
    carbon_emission_kg: float = 0.0


class DayPlan(BaseModel):
    """Full day plan."""
    day: int
    date: Optional[str] = None
    activities: List[DayActivity]
    accommodation: str
    accommodation_carbon_kg: float = 0.0
    total_carbon_kg: float = 0.0


class ScoreBreakdown(BaseModel):
    """Breakdown of sustainability score."""
    transport_score: float = Field(0.0, ge=0, le=100)
    accommodation_score: float = Field(0.0, ge=0, le=100)
    activity_score: float = Field(0.0, ge=0, le=100)
    local_engagement_score: float = Field(0.0, ge=0, le=100)
    overtourism_score: float = Field(0.0, ge=0, le=100)


class ItinerarySustainability(BaseModel):
    """Sustainability metrics for itinerary."""
    total_score: float = Field(0.0, ge=0, le=100)
    breakdown: ScoreBreakdown
    total_carbon_kg: float
    explanation: str


class Itinerary(BaseModel):
    """Complete itinerary with sustainability details."""
    id: int
    title: str
    description: str
    days: List[DayPlan]
    sustainability: ItinerarySustainability
    preferred_transport: TransportMode


class TripInput(BaseModel):
    """User input for trip planning."""
    origin: str
    destination: str
    days: int
    transport_preference: TransportMode
    budget: Optional[float] = None
    interests: List[ActivityType] = []
    sustainability_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "carbon": 0.4,
            "local": 0.3,
            "culture": 0.2,
            "overtourism": 0.1,
        }
    )


class TravelerProfile(BaseModel):
    """Profile of a traveler for group matching."""
    id: str
    name: str
    destination: str
    trip_days: int
    sustainability_score_min: float
    interests: List[ActivityType]
    max_group_size: int = 5
    transport_preference: TransportMode
    profile_vector: Optional[List[float]] = None


class GroupMatch(BaseModel):
    """Matched travelers for group trip."""
    traveler_ids: List[str]
    similarity_score: float
    recommended_group_size: int
    common_interests: List[ActivityType]


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: str
