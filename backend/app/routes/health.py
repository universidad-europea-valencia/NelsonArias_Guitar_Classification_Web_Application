"""Health check routes."""

from fastapi import APIRouter
from app.core.config import settings
from app.schemas import HealthResponse
import os

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running and models are available.
    
    Returns:
        HealthResponse: Status, version, and available models information
    """
    # Check available models
    models_path = settings.MODELS_PATH
    available_models = []
    
    if os.path.exists(models_path):
        available_models = [
            f for f in os.listdir(models_path) 
            if f.endswith('.keras')
        ]
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        models_available=len(available_models),
        models=available_models
    )


@router.get("/status")
async def status():
    """Get detailed status information."""
    return {
        "service": "Guitar Classification API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "models_path": settings.MODELS_PATH,
        "model_cache_size": settings.MODEL_CACHE_SIZE,
        "guitar_classes": settings.GUITAR_CLASSES
    }
