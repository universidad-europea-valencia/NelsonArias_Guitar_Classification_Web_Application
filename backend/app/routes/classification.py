"""Classification routes for guitar image classification."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import settings
from app.schemas import ClassificationResponse
from app.services.image_service import ImageProcessor
from app.services.model_service import ModelManager
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services globally
_model_manager: ModelManager = None
_prediction_service: PredictionService = None


def get_prediction_service() -> PredictionService:
    """Get or initialize prediction service."""
    global _model_manager, _prediction_service
    
    if _prediction_service is None:
        _model_manager = ModelManager(
            models_path=settings.MODELS_PATH,
            cache_size=settings.MODEL_CACHE_SIZE
        )
        _prediction_service = PredictionService(_model_manager)
        logger.info("Prediction service initialized")
    
    return _prediction_service


@router.post("/classify", response_model=ClassificationResponse)
async def classify_image(file: UploadFile = File(...)):
    """
    Classify a guitar image using the primary model.
    
    Args:
        file: Image file uploaded by the client
        
    Returns:
        ClassificationResponse: Predicted guitar class and confidence score
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    try:
        logger.info(f"Received classification request for: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file bytes
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        logger.debug(f"File size: {len(file_bytes)} bytes")
        
        # Preprocess image
        logger.debug("Starting image preprocessing")
        image_array, error = ImageProcessor.preprocess_image(
            file_bytes=file_bytes,
            filename=file.filename,
            target_size=tuple(settings.IMAGE_TARGET_SIZE),
            max_size=settings.IMAGE_MAX_SIZE
        )
        
        if image_array is None:
            logger.warning(f"Image preprocessing failed: {error}")
            raise HTTPException(status_code=400, detail=f"Invalid image: {error}")
        
        logger.debug(f"Image preprocessed successfully. Shape: {image_array.shape}")
        
        # Get prediction service
        prediction_service = get_prediction_service()
        
        # Run prediction
        logger.debug(f"Running prediction with model: {settings.PRIMARY_MODEL_NAME}")
        result, error = prediction_service.predict(
            image_array=image_array,
            model_name=settings.PRIMARY_MODEL_NAME,
            threshold=settings.PRIMARY_MODEL_THRESHOLD
        )
        
        if result is None:
            logger.error(f"Prediction failed: {error}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {error}")
        
        # Format response
        response = ClassificationResponse(
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            model_used=result["model_used"],
            processing_time_ms=result["processing_time_ms"],
            class_probabilities=result["class_probabilities"]
        )
        
        logger.info(f"Classification successful: {result['predicted_class']} ({result['confidence']:.2%})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during classification: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Classification failed")


@router.post("/classify-alternative")
async def classify_alternative(file: UploadFile = File(...)):
    """
    Classify a guitar image using the alternative model.
    
    Args:
        file: Image file uploaded by the client
        
    Returns:
        ClassificationResponse: Predicted guitar class and confidence score
    """
    try:
        logger.info(f"Received alternative classification request for: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file bytes
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        logger.debug(f"File size: {len(file_bytes)} bytes")
        
        # Preprocess image
        logger.debug("Starting image preprocessing")
        image_array, error = ImageProcessor.preprocess_image(
            file_bytes=file_bytes,
            filename=file.filename,
            target_size=tuple(settings.IMAGE_TARGET_SIZE),
            max_size=settings.IMAGE_MAX_SIZE
        )
        
        if image_array is None:
            logger.warning(f"Image preprocessing failed: {error}")
            raise HTTPException(status_code=400, detail=f"Invalid image: {error}")
        
        logger.debug(f"Image preprocessed successfully. Shape: {image_array.shape}")
        
        # Get prediction service
        prediction_service = get_prediction_service()
        
        # Run prediction
        logger.debug(f"Running prediction with model: {settings.ALTERNATIVE_MODEL_NAME}")
        result, error = prediction_service.predict(
            image_array=image_array,
            model_name=settings.ALTERNATIVE_MODEL_NAME,
            threshold=settings.ALTERNATIVE_MODEL_THRESHOLD
        )
        
        if result is None:
            logger.error(f"Prediction failed: {error}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {error}")
        
        # Format response
        response = ClassificationResponse(
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            model_used=result["model_used"],
            processing_time_ms=result["processing_time_ms"],
            class_probabilities=result["class_probabilities"]
        )
        
        logger.info(f"Alternative classification successful: {result['predicted_class']} ({result['confidence']:.2%})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during classification: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Classification failed")


@router.post("/classify-ensemble")
async def classify_ensemble(file: UploadFile = File(...)):
    """
    Classify a guitar image using ensemble of all available models.
    
    Args:
        file: Image file uploaded by the client
        
    Returns:
        ClassificationResponse: Ensemble prediction result
    """
    try:
        logger.info(f"Received ensemble classification request for: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file bytes
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        logger.debug(f"File size: {len(file_bytes)} bytes")
        
        # Preprocess image
        logger.debug("Starting image preprocessing")
        image_array, error = ImageProcessor.preprocess_image(
            file_bytes=file_bytes,
            filename=file.filename,
            target_size=tuple(settings.IMAGE_TARGET_SIZE),
            max_size=settings.IMAGE_MAX_SIZE
        )
        
        if image_array is None:
            logger.warning(f"Image preprocessing failed: {error}")
            raise HTTPException(status_code=400, detail=f"Invalid image: {error}")
        
        logger.debug(f"Image preprocessed successfully. Shape: {image_array.shape}")
        
        # Get prediction service
        prediction_service = get_prediction_service()
        
        # Run ensemble prediction
        logger.debug("Running ensemble prediction with all models")
        result, error = prediction_service.predict_ensemble(
            image_array=image_array,
            threshold=0.5
        )
        
        if result is None:
            logger.error(f"Ensemble prediction failed: {error}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {error}")
        
        # Format response
        response = ClassificationResponse(
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            model_used=result["model_used"],
            processing_time_ms=result["processing_time_ms"],
            class_probabilities=result["class_probabilities"]
        )
        
        logger.info(f"Ensemble classification successful: {result['predicted_class']} ({result['confidence']:.2%})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during ensemble classification: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Ensemble classification failed")
