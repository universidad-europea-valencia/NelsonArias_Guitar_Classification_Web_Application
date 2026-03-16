"""
Model loading and management service.
Handles lazy loading, caching, and lifecycle of Keras models.
"""

import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Tuple
import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading and caching of Keras models with LRU cache."""
    
    def __init__(self, models_path: str, cache_size: int = 2):
        """
        Initialize ModelManager.
        
        Args:
            models_path: Path to directory containing .keras model files
            cache_size: Number of models to cache in memory (LRU)
        """
        self.models_path = Path(models_path)
        self.cache_size = cache_size
        self._model_cache: Dict[str, keras.Model] = {}
        self._load_model_with_cache = lru_cache(maxsize=cache_size)(
            self._load_model_impl
        )
        logger.info(f"ModelManager initialized with path: {models_path}, cache_size: {cache_size}")
    
    def _load_model_impl(self, model_name: str) -> keras.Model:
        """
        Load a Keras model from disk (actual implementation).
        This method is wrapped with lru_cache.
        
        Args:
            model_name: Name of the model file (e.g., 'best_guitar_model.keras')
            
        Returns:
            Loaded Keras model
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        model_path = self.models_path / model_name
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            logger.info(f"Loading model: {model_name}")
            model = keras.models.load_model(str(model_path))
            logger.info(f"Successfully loaded model: {model_name}")
            return model
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
    
    def load_model(self, model_name: str) -> keras.Model:
        """
        Load a model with caching support.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Cached or newly loaded Keras model
        """
        return self._load_model_with_cache(model_name)
    
    def get_available_models(self) -> Dict[str, dict]:
        """
        Get list of available models in the models directory.
        
        Returns:
            Dictionary with model info {model_name: {size, path}}
        """
        available = {}
        
        if not self.models_path.exists():
            logger.warning(f"Models path does not exist: {self.models_path}")
            return available
        
        for file_path in self.models_path.glob("*.keras"):
            try:
                file_size = file_path.stat().st_size
                available[file_path.name] = {
                    "path": str(file_path),
                    "size_mb": round(file_size / (1024 * 1024), 2)
                }
            except Exception as e:
                logger.warning(f"Error getting info for {file_path.name}: {str(e)}")
        
        return available
    
    def clear_cache(self):
        """Clear the LRU cache."""
        self._load_model_with_cache.cache_clear()
        logger.info("Model cache cleared")
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information or None if not found
        """
        available = self.get_available_models()
        return available.get(model_name)


class ModelInferenceError(Exception):
    """Exception raised when model inference fails."""
    pass


class ImagePreprocessingError(Exception):
    """Exception raised when image preprocessing fails."""
    pass
