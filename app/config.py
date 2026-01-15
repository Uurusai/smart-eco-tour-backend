"""Configuration file for Smart Eco Tour Backend."""
import os
from pathlib import Path
from typing import Optional

# Project root
PROJECT_ROOT = Path(__file__).parent

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()

# API Configuration
API_TITLE = "Smart Eco Tour Backend API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
AI-powered sustainable travel itinerary generator with group matching capabilities.

## Key Features:
- 🌍 Sustainable itinerary generation (3-5 options)
- 🔥 Carbon footprint tracking
- 🎯 Sustainability scoring (0-100)
- 👥 Intelligent group matching
- 🚆 Multi-destination support

## Getting Started:
1. POST `/api/generate-itinerary` - Generate sustainable itineraries
2. POST `/api/traveler-profile` - Create traveler profiles
3. POST `/api/find-group` - Find compatible travel companions
4. GET `/api/health` - Check API status
"""

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",      # React dev server
    "http://localhost:5173",      # Vite dev server
    "http://localhost:8080",      # Alt port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

if DEBUG:
    CORS_ORIGINS.append("*")  # Allow all origins in development

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# LLM Configuration
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000

# Sustainability Scoring Defaults
DEFAULT_SUSTAINABILITY_WEIGHTS = {
    "carbon": 0.4,
    "local": 0.3,
    "culture": 0.2,
    "overtourism": 0.1,
}

SCORING_WEIGHTS = {
    "transport": 0.30,
    "accommodation": 0.20,
    "activity": 0.20,
    "local_engagement": 0.20,
    "overtourism": 0.10,
}

# Similarity Matching Configuration
DEFAULT_SIMILARITY_THRESHOLD = 0.7
MAX_GROUP_SIZE = 8
MIN_GROUP_SIZE = 2

# Cache Settings
ITINERARY_CACHE_MAX_SIZE = 1000
TRAVELER_CACHE_MAX_SIZE = 5000

# Database (for future use)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./eco_tour.db"
)

# Destinations with activities
SUPPORTED_DESTINATIONS = [
    "Paris",
    "Tokyo",
    "Barcelona",
    "Bangkok",
    "New York",
    "London",
    "Amsterdam",
    "Rome",
    "Sydney",
    "Bali",
]

# Default values
DEFAULT_TRIP_DURATION = 5  # days
DEFAULT_BUDGET = 2000  # USD
DEFAULT_GROUP_SIZE = 2

# API Rate Limiting (for future use)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 3600  # seconds (1 hour)

# Timeouts
REQUEST_TIMEOUT = 30  # seconds
LLM_REQUEST_TIMEOUT = 60  # seconds

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "eco_tour.log",
            "level": LOG_LEVEL,
        },
    },
    "loggers": {
        "app": {
            "handlers": ["default", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Feature Flags
FEATURES = {
    "llm_generation": True,
    "group_matching": True,
    "carbon_tracking": True,
    "sustainability_scoring": True,
    "mock_data": True,
    "api_docs": DEBUG,
}

# Version Info
__version__ = "1.0.0"
__author__ = "Smart Eco Tour Team"
