"""
Image preprocessing and validation service.
Handles image loading, resizing, normalization, and validation.
"""

import io
import logging
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes and validates images for model inference."""
    
    # Standard format for model input
    DEFAULT_TARGET_SIZE = (224, 224)
    ALLOWED_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB
    
    @staticmethod
    def validate_file(file_bytes: bytes, filename: str, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, Optional[str]]:
        """
        Validate file before processing.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            max_size: Maximum allowed file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        if file_ext not in ImageProcessor.ALLOWED_FORMATS:
            return False, f"Invalid file format: {file_ext}. Allowed: {', '.join(ImageProcessor.ALLOWED_FORMATS)}"
        
        # Check file size
        if len(file_bytes) > max_size:
            size_mb = len(file_bytes) / (1024 * 1024)
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.2f}MB (max: {max_mb:.0f}MB)"
        
        return True, None
    
    @staticmethod
    def load_image(file_bytes: bytes) -> Tuple[Image.Image, Optional[str]]:
        """
        Load image from bytes.
        
        Args:
            file_bytes: Image file content as bytes
            
        Returns:
            Tuple of (PIL Image, error_message)
        """
        try:
            image = Image.open(io.BytesIO(file_bytes))
            logger.debug(f"Image loaded successfully: {image.size}, mode: {image.mode}")
            return image, None
        except Exception as e:
            error_msg = f"Failed to load image: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    @staticmethod
    def resize_image(
        image: Image.Image,
        target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE
    ) -> Tuple[Image.Image, Optional[str]]:
        """
        Resize image to target dimensions.
        
        Args:
            image: PIL Image object
            target_size: Target (width, height) tuple
            
        Returns:
            Tuple of (resized Image, error_message)
        """
        try:
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize with high-quality resampling
            resized = image.resize(target_size, Image.Resampling.LANCZOS)
            logger.debug(f"Image resized to {target_size}")
            return resized, None
        except Exception as e:
            error_msg = f"Failed to resize image: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    @staticmethod
    def normalize_image(image_array: np.ndarray) -> Tuple[np.ndarray, Optional[str]]:
        """
        Normalize image array to [0, 1] range for model input.
        
        Args:
            image_array: NumPy array of image data
            
        Returns:
            Tuple of (normalized array, error_message)
        """
        try:
            # Convert to float and normalize to [0, 1]
            normalized = image_array.astype(np.float32) / 255.0
            logger.debug(f"Image normalized. Range: [{normalized.min():.3f}, {normalized.max():.3f}]")
            return normalized, None
        except Exception as e:
            error_msg = f"Failed to normalize image: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    @staticmethod
    def preprocess_image(
        file_bytes: bytes,
        filename: str,
        target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE,
        max_size: int = MAX_FILE_SIZE
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Complete preprocessing pipeline for an image.
        
        Args:
            file_bytes: Image file content
            filename: Original filename
            target_size: Target dimensions for model
            max_size: Maximum allowed file size
            
        Returns:
            Tuple of (preprocessed numpy array, error_message)
        """
        logger.info(f"Starting preprocessing for: {filename}")
        
        # Validate file
        is_valid, error = ImageProcessor.validate_file(file_bytes, filename, max_size)
        if not is_valid:
            return None, error
        
        # Load image
        image, error = ImageProcessor.load_image(file_bytes)
        if image is None:
            return None, error
        
        # Resize image
        image, error = ImageProcessor.resize_image(image, target_size)
        if image is None:
            return None, error
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Normalize
        normalized, error = ImageProcessor.normalize_image(image_array)
        if normalized is None:
            return None, error
        
        # Add batch dimension
        batch = np.expand_dims(normalized, axis=0)
        
        logger.info(f"Preprocessing complete. Output shape: {batch.shape}")
        return batch, None
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """
        Get metadata about an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with image information
        """
        return {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
            "width": image.width,
            "height": image.height
        }
