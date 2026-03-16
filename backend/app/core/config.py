"""Configuration module for FastAPI application."""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_TITLE: str = "Guitar Classification API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Web platform for guitar classification using Keras models"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # Model Configuration
    MODELS_PATH: str = "/app/models"
    MODEL_CACHE_SIZE: int = 2
    
    # Primary model configuration
    PRIMARY_MODEL_NAME: str = "best_guitar_model.keras"
    PRIMARY_MODEL_THRESHOLD: float = 0.5
    
    # Alternative model configuration
    ALTERNATIVE_MODEL_NAME: str = "best_transfer_model.keras"
    ALTERNATIVE_MODEL_THRESHOLD: float = 0.5
    
    # Image Processing Configuration
    IMAGE_MAX_SIZE: int = 4 * 1024 * 1024  # 4MB
    IMAGE_ALLOWED_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "bmp"]
    IMAGE_TARGET_SIZE: tuple = (224, 224)
    
    # Guitar Classes
    GUITAR_CLASSES: List[str] = [
        "Bajo_Electrico",
        "Guitarra_Acustica",
        "Guitarra_Electrica",
        "Guitarra_Electroacustica"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
