"""Unit tests for image_service module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import io
import numpy as np
from PIL import Image

from app.services.image_service import ImageProcessor, ImagePreprocessingError


class TestImageProcessor(unittest.TestCase):
    """Test cases for ImageProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.target_size = (224, 224)
        self.max_size = 4 * 1024 * 1024  # 4MB

    def create_test_image(self, size=(100, 100), format='PNG', mode='RGB'):
        """Create a test image in bytes format."""
        img = Image.new(mode, size, color=(255, 0, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes.getvalue()

    def test_preprocess_image_valid_png(self):
        """Test preprocessing a valid PNG image."""
        image_bytes = self.create_test_image(format='PNG')
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (1, 224, 224, 3))

    def test_preprocess_image_valid_jpg(self):
        """Test preprocessing a valid JPEG image."""
        image_bytes = self.create_test_image(format='JPEG')
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test.jpg',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (1, 224, 224, 3))

    def test_preprocess_image_rgba_conversion(self):
        """Test that RGBA images are converted to RGB."""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=img_bytes.getvalue(),
            filename='test_rgba.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        # Should be converted to RGB (3 channels)
        self.assertEqual(result.shape[3], 3)

    def test_preprocess_image_resizing(self):
        """Test that image is resized to target size."""
        image_bytes = self.create_test_image(size=(500, 500))
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test_resize.png',
            target_size=(224, 224),
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        # Should be resized to target size
        self.assertEqual(result.shape[1:3], (224, 224))

    def test_preprocess_image_normalization(self):
        """Test that image values are normalized to [0, 1]."""
        image_bytes = self.create_test_image()
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test_norm.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        # Values should be between 0 and 1
        self.assertGreaterEqual(result.min(), 0.0)
        self.assertLessEqual(result.max(), 1.0)

    def test_preprocess_image_batch_dimension(self):
        """Test that batch dimension is added."""
        image_bytes = self.create_test_image()
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test_batch.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        # Should have batch dimension (1, H, W, C)
        self.assertEqual(len(result.shape), 4)
        self.assertEqual(result.shape[0], 1)

    def test_preprocess_image_invalid_file(self):
        """Test preprocessing invalid/corrupted image."""
        result, error = ImageProcessor.preprocess_image(
            file_bytes=b'not an image',
            filename='test_invalid.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_preprocess_image_empty_file(self):
        """Test preprocessing empty file."""
        result, error = ImageProcessor.preprocess_image(
            file_bytes=b'',
            filename='test_empty.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_preprocess_image_unsupported_format(self):
        """Test preprocessing unsupported file format."""
        result, error = ImageProcessor.preprocess_image(
            file_bytes=b'some binary content',
            filename='test.xyz',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_preprocess_image_file_too_large(self):
        """Test that oversized files are rejected."""
        # Create a large image
        large_img = Image.new('RGB', (2000, 2000), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        large_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=img_bytes.getvalue(),
            filename='test_large.png',
            target_size=self.target_size,
            max_size=1024 * 100  # Only 100KB allowed
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertIn('exceed', error.lower())

    def test_validate_file_extension_valid(self):
        """Test file extension validation for valid formats."""
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        
        for ext in valid_extensions:
            filename = f'test.{ext}'
            # Should not raise exception
            ImageProcessor.validate_file(
                filename=filename,
                max_size=self.max_size,
                file_size=1000
            )

    def test_validate_file_extension_invalid(self):
        """Test file extension validation for invalid formats."""
        result = ImageProcessor.validate_file(
            filename='test.txt',
            max_size=self.max_size,
            file_size=1000
        )
        
        self.assertIsNotNone(result)
        self.assertIn('format', result.lower())

    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation."""
        result = ImageProcessor.validate_file(
            filename='test.png',
            max_size=1000,
            file_size=2000
        )
        
        self.assertIsNotNone(result)
        self.assertIn('exceed', result.lower())

    def test_validate_file_valid(self):
        """Test valid file passes validation."""
        result = ImageProcessor.validate_file(
            filename='test.png',
            max_size=1000000,
            file_size=500000
        )
        
        self.assertIsNone(result)

    def test_preprocess_image_returns_numpy_array(self):
        """Test that preprocessed image is a numpy array."""
        image_bytes = self.create_test_image()
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertIsInstance(result, np.ndarray)

    def test_preprocess_image_dtype_float32(self):
        """Test that preprocessed image has float32 dtype."""
        image_bytes = self.create_test_image()
        
        result, error = ImageProcessor.preprocess_image(
            file_bytes=image_bytes,
            filename='test.png',
            target_size=self.target_size,
            max_size=self.max_size
        )
        
        self.assertIsNone(error)
        self.assertEqual(result.dtype, np.float32)

    def test_preprocess_image_different_input_sizes(self):
        """Test preprocessing images of different sizes."""
        sizes = [(50, 50), (300, 200), (400, 400)]
        
        for size in sizes:
            image_bytes = self.create_test_image(size=size)
            
            result, error = ImageProcessor.preprocess_image(
                file_bytes=image_bytes,
                filename='test.png',
                target_size=self.target_size,
                max_size=self.max_size
            )
            
            self.assertIsNone(error)
            self.assertIsNotNone(result)
            # All should be resized to target size
            self.assertEqual(result.shape[1:3], self.target_size)


class TestImagePreprocessingError(unittest.TestCase):
    """Test cases for ImagePreprocessingError exception."""

    def test_error_creation(self):
        """Test creating ImagePreprocessingError."""
        error = ImagePreprocessingError("Test message")
        self.assertEqual(str(error), "Test message")

    def test_error_inheritance(self):
        """Test that ImagePreprocessingError is an Exception."""
        error = ImagePreprocessingError("Test")
        self.assertIsInstance(error, Exception)

    def test_error_can_be_raised_and_caught(self):
        """Test that error can be raised and caught."""
        with self.assertRaises(ImagePreprocessingError):
            raise ImagePreprocessingError("Test error")


if __name__ == '__main__':
    unittest.main()
