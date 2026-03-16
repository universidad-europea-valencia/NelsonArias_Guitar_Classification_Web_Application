"""
FastAPI application main module for Guitar Classification Platform.
Handles routing, configuration, and integration of all backend components.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routes import health, classification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Guitar Classification API",
    description="API for classifying guitar images using Keras models",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure TrustedHost middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.TRUSTED_HOSTS
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(classification.router, prefix="/api/v1", tags=["Classification"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Guitar Classification API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
