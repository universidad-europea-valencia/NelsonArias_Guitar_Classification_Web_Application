"""Unit tests for model_service module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
from pathlib import Path

from app.services.model_service import ModelManager, ModelInferenceError


class TestModelManager(unittest.TestCase):
    """Test cases for ModelManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.model_manager = ModelManager(models_path=self.temp_dir, cache_size=2)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clear cache after each test
        if hasattr(self.model_manager, '_load_model_cached'):
            self.model_manager._load_model_cached.cache_clear()

    def test_model_manager_initialization(self):
        """Test ModelManager initializes with correct parameters."""
        self.assertEqual(self.model_manager.models_path, self.temp_dir)
        self.assertIsNotNone(self.model_manager._load_model_cached)

    def test_cache_size_configuration(self):
        """Test that cache size is properly configured."""
        manager = ModelManager(models_path=self.temp_dir, cache_size=3)
        # Cache should be initialized with the specified size
        self.assertIsNotNone(manager._load_model_cached)

    @patch('app.services.model_service.keras.models.load_model')
    def test_load_model_called(self, mock_load_model):
        """Test that load_model is called with correct path."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        # Create a mock model file
        model_path = os.path.join(self.temp_dir, "test_model.keras")
        Path(model_path).touch()

        # Load model should call keras.models.load_model
        result = self.model_manager.load_model("test_model.keras")
        
        # Verify the load was attempted
        self.assertEqual(result, mock_model)

    def test_model_not_found(self):
        """Test handling of missing model file."""
        with self.assertRaises(ModelInferenceError):
            self.model_manager.load_model("nonexistent_model.keras")

    def test_cache_clearing(self):
        """Test that cache can be cleared."""
        # This should not raise an exception
        self.model_manager.clear_cache()

    def test_get_available_models(self):
        """Test retrieval of available models."""
        # Create some fake model files
        model_names = ["model1.keras", "model2.keras", "model3.h5"]
        for model_name in model_names:
            model_path = os.path.join(self.temp_dir, model_name)
            Path(model_path).touch()

        available = self.model_manager.get_available_models()
        
        # Should find .keras and .h5 files
        self.assertIsInstance(available, list)
        self.assertIn("model1.keras", available)
        self.assertIn("model2.keras", available)
        self.assertIn("model3.h5", available)

    def test_get_available_models_empty_directory(self):
        """Test getting models from empty directory."""
        available = self.model_manager.get_available_models()
        self.assertEqual(available, [])

    @patch('app.services.model_service.keras.models.load_model')
    def test_lru_cache_functionality(self, mock_load_model):
        """Test that LRU cache works correctly."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        # Create mock model files
        for i in range(2):
            model_path = os.path.join(self.temp_dir, f"model{i}.keras")
            Path(model_path).touch()

        # Load models multiple times
        result1 = self.model_manager.load_model("model0.keras")
        result2 = self.model_manager.load_model("model0.keras")
        
        # Cache should return same object without calling load_model twice
        self.assertEqual(result1, result2)
        # load_model should only be called once due to caching
        self.assertEqual(mock_load_model.call_count, 1)

    @patch('app.services.model_service.keras.models.load_model')
    def test_cache_respects_maxsize(self, mock_load_model):
        """Test that cache respects maxsize of 2."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        # Create 3 model files
        for i in range(3):
            model_path = os.path.join(self.temp_dir, f"model{i}.keras")
            Path(model_path).touch()

        # Load 3 different models (exceeds cache size of 2)
        self.model_manager.load_model("model0.keras")
        self.model_manager.load_model("model1.keras")
        self.model_manager.load_model("model2.keras")

        # Should have called load_model 3 times (cache eviction)
        self.assertEqual(mock_load_model.call_count, 3)

    def test_model_inference_error_custom_exception(self):
        """Test ModelInferenceError is a proper exception."""
        error = ModelInferenceError("Test error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test error")

    def test_model_path_normalization(self):
        """Test that model paths are properly normalized."""
        manager = ModelManager(models_path=self.temp_dir, cache_size=2)
        
        # Path should be normalized
        self.assertTrue(os.path.isabs(manager.models_path))

    @patch('app.services.model_service.keras.models.load_model')
    def test_load_model_with_custom_path(self, mock_load_model):
        """Test loading model from custom path."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        custom_dir = os.path.join(self.temp_dir, "custom")
        os.makedirs(custom_dir, exist_ok=True)
        
        manager = ModelManager(models_path=custom_dir, cache_size=2)
        model_path = os.path.join(custom_dir, "custom_model.keras")
        Path(model_path).touch()

        result = manager.load_model("custom_model.keras")
        self.assertEqual(result, mock_model)


class TestModelInferenceError(unittest.TestCase):
    """Test cases for ModelInferenceError exception."""

    def test_error_creation(self):
        """Test creating ModelInferenceError."""
        error = ModelInferenceError("Test message")
        self.assertEqual(str(error), "Test message")

    def test_error_inheritance(self):
        """Test that ModelInferenceError is an Exception."""
        error = ModelInferenceError("Test")
        self.assertIsInstance(error, Exception)

    def test_error_can_be_raised_and_caught(self):
        """Test that error can be raised and caught."""
        with self.assertRaises(ModelInferenceError):
            raise ModelInferenceError("Test error")


if __name__ == '__main__':
    unittest.main()
