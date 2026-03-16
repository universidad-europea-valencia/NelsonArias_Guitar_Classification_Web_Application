"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class GuitarClass(str, Enum):
    """Enumeration of guitar classes."""
    BAJO_ELECTRICO = "Bajo_Electrico"
    GUITARRA_ACUSTICA = "Guitarra_Acustica"
    GUITARRA_ELECTRICA = "Guitarra_Electrica"
    GUITARRA_ELECTROACUSTICA = "Guitarra_Electroacustica"


class ModelSelection(str, Enum):
    """Available models for classification."""
    PRIMARY = "primary"
    ALTERNATIVE = "alternative"
    ENSEMBLE = "ensemble"


class ClassificationResponse(BaseModel):
    """Response model for guitar classification."""
    
    predicted_class: GuitarClass = Field(..., description="Predicted guitar class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_used: str = Field(..., description="Name of the model used")
    processing_time_ms: float = Field(..., description="Time taken to process image")
    class_probabilities: Optional[Dict[str, float]] = Field(
        None, 
        description="Probabilities for all classes"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    models_available: int = Field(..., description="Number of available models")
    models: List[str] = Field(..., description="List of available models")


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Dict] = Field(None, description="Additional error details")


class ImageMetadata(BaseModel):
    """Metadata about uploaded image."""
    
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
