"""
Prediction service for guitar classification.
Handles model inference and result formatting.
"""

import time
import logging
from typing import Dict, Optional, List, Tuple
import numpy as np
from tensorflow import keras

from app.services.model_service import ModelManager, ModelInferenceError
from app.core.config import settings

logger = logging.getLogger(__name__)


class PredictionService:
    """Handles model predictions and result formatting."""
    
    def __init__(self, model_manager: ModelManager):
        """
        Initialize PredictionService.
        
        Args:
            model_manager: ModelManager instance for loading models
        """
        self.model_manager = model_manager
        self.guitar_classes = settings.GUITAR_CLASSES
        logger.info(f"PredictionService initialized with {len(self.guitar_classes)} classes")
    
    def predict(
        self,
        image_array: np.ndarray,
        model_name: str,
        threshold: float = 0.5
    ) -> Tuple[Dict, Optional[str]]:
        """
        Run prediction on an image using specified model.
        
        Args:
            image_array: Preprocessed image array with batch dimension
            model_name: Name of the model to use
            threshold: Confidence threshold for prediction
            
        Returns:
            Tuple of (prediction result dict, error_message)
        """
        start_time = time.time()
        
        try:
            logger.info(f"Running prediction with model: {model_name}")
            
            # Load model
            model = self.model_manager.load_model(model_name)
            logger.debug(f"Model loaded: {model_name}")
            
            # Run inference
            logger.debug(f"Running inference on image with shape: {image_array.shape}")
            predictions = model.predict(image_array, verbose=0)
            logger.debug(f"Raw predictions shape: {predictions.shape}")
            
            # Get processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Parse predictions
            result = self._parse_predictions(
                predictions[0],  # Get first (only) batch element
                model_name,
                processing_time_ms,
                threshold
            )
            
            logger.info(f"Prediction complete: {result['predicted_class']} (confidence: {result['confidence']:.2%})")
            return result, None
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Prediction failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _parse_predictions(
        self,
        predictions: np.ndarray,
        model_name: str,
        processing_time_ms: float,
        threshold: float
    ) -> Dict:
        """
        Parse raw model predictions into structured result.
        
        Args:
            predictions: Raw model output (class probabilities)
            model_name: Name of the model used
            processing_time_ms: Processing time in milliseconds
            threshold: Confidence threshold
            
        Returns:
            Structured prediction result
        """
        # Get predicted class and confidence
        predicted_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_idx])
        predicted_class = self.guitar_classes[predicted_idx]
        
        # Build class probabilities dict
        class_probabilities = {
            self.guitar_classes[i]: float(predictions[i])
            for i in range(len(self.guitar_classes))
        }
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "model_used": model_name,
            "processing_time_ms": round(processing_time_ms, 2),
            "class_probabilities": class_probabilities,
            "threshold_used": threshold
        }
    
    def predict_ensemble(
        self,
        image_array: np.ndarray,
        threshold: float = 0.5
    ) -> Tuple[Dict, Optional[str]]:
        """
        Run ensemble prediction using both available models.
        Averages probabilities and selects highest confidence.
        
        Args:
            image_array: Preprocessed image array
            threshold: Confidence threshold
            
        Returns:
            Tuple of (ensemble result dict, error_message)
        """
        start_time = time.time()
        
        try:
            logger.info("Running ensemble prediction with all available models")
            
            primary_model = settings.PRIMARY_MODEL_NAME
            alternative_model = settings.ALTERNATIVE_MODEL_NAME
            
            # Get predictions from both models
            primary_result, primary_error = self.predict(
                image_array,
                primary_model,
                threshold
            )
            
            if primary_error:
                logger.warning(f"Primary model error: {primary_error}")
                # Fallback to alternative model
                alt_result, alt_error = self.predict(
                    image_array,
                    alternative_model,
                    threshold
                )
                if alt_error:
                    return None, f"Both models failed. Primary: {primary_error}, Alternative: {alt_error}"
                return alt_result, None
            
            alternative_result, alternative_error = self.predict(
                image_array,
                alternative_model,
                threshold
            )
            
            if alternative_error:
                logger.warning(f"Alternative model error: {alternative_error}")
                return primary_result, None
            
            # Ensemble results by averaging probabilities
            processing_time_ms = (time.time() - start_time) * 1000
            
            ensemble_result = self._ensemble_predictions(
                primary_result,
                alternative_result,
                processing_time_ms
            )
            
            logger.info(f"Ensemble prediction: {ensemble_result['predicted_class']} (confidence: {ensemble_result['confidence']:.2%})")
            return ensemble_result, None
            
        except Exception as e:
            error_msg = f"Ensemble prediction failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _ensemble_predictions(
        self,
        result1: Dict,
        result2: Dict,
        processing_time_ms: float
    ) -> Dict:
        """
        Ensemble two prediction results by averaging probabilities.
        
        Args:
            result1: First model prediction result
            result2: Second model prediction result
            processing_time_ms: Total processing time
            
        Returns:
            Ensemble prediction result
        """
        # Average probabilities
        probs1 = result1["class_probabilities"]
        probs2 = result2["class_probabilities"]
        
        ensemble_probs = {
            class_name: (probs1[class_name] + probs2[class_name]) / 2
            for class_name in self.guitar_classes
        }
        
        # Get highest probability class
        predicted_class = max(ensemble_probs, key=ensemble_probs.get)
        confidence = ensemble_probs[predicted_class]
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "model_used": f"ensemble({settings.PRIMARY_MODEL_NAME}, {settings.ALTERNATIVE_MODEL_NAME})",
            "processing_time_ms": round(processing_time_ms, 2),
            "class_probabilities": ensemble_probs,
            "individual_predictions": {
                "primary": {
                    "class": result1["predicted_class"],
                    "confidence": result1["confidence"]
                },
                "alternative": {
                    "class": result2["predicted_class"],
                    "confidence": result2["confidence"]
                }
            }
        }
    
    def get_model_info(self) -> Dict:
        """
        Get information about available models.
        
        Returns:
            Dictionary with model information
        """
        available_models = self.model_manager.get_available_models()
        
        return {
            "models_available": len(available_models),
            "models": available_models,
            "cache_size": self.model_manager.cache_size,
            "guitar_classes": self.guitar_classes,
            "num_classes": len(self.guitar_classes)
        }
