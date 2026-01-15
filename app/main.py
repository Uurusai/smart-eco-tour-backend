"""Main FastAPI application for Smart Eco Tour Backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.api import routes
from app.models.schemas import TripInput, Itinerary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Eco Tour Backend API",
    description="AI-powered sustainable travel itinerary generator with group matching",
    version="1.0.0",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Smart Eco Tour Backend starting up...")
    logger.info("✅ API endpoints registered")
    logger.info("📡 CORS enabled for frontend integration")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Smart Eco Tour Backend shutting down...")


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "status": "active",
        "name": "Smart Eco Tour Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate_itinerary": "POST /api/generate-itinerary",
            "get_itinerary": "GET /api/itinerary/{id}",
            "create_profile": "POST /api/traveler-profile",
            "find_groups": "POST /api/find-group",
            "compare_itineraries": "POST /api/compare-itineraries",
            "sustainability_tips": "GET /api/sustainability-tips",
            "health": "GET /api/health",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        },
    )
