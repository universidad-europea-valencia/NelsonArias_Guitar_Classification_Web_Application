"""Classification routes for guitar image classification."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.schemas import ClassificationResponse, ErrorResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file format
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.IMAGE_ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"File format not allowed. Allowed: {', '.join(settings.IMAGE_ALLOWED_FORMATS)}"
            )
        
        # This is a stub implementation
        # Full implementation will include actual model inference
        return ClassificationResponse(
            predicted_class="Guitarra_Electrica",
            confidence=0.85,
            model_used=settings.PRIMARY_MODEL_NAME,
            processing_time_ms=150.0,
            class_probabilities={
                "Bajo_Electrico": 0.05,
                "Guitarra_Acustica": 0.05,
                "Guitarra_Electrica": 0.85,
                "Guitarra_Electroacustica": 0.05
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing image")


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
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.IMAGE_ALLOWED_FORMATS:
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        # Stub implementation
        return ClassificationResponse(
            predicted_class="Guitarra_Electrica",
            confidence=0.82,
            model_used=settings.ALTERNATIVE_MODEL_NAME,
            processing_time_ms=160.0,
            class_probabilities={
                "Bajo_Electrico": 0.06,
                "Guitarra_Acustica": 0.06,
                "Guitarra_Electrica": 0.82,
                "Guitarra_Electroacustica": 0.06
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing image")
