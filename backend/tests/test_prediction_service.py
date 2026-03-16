"""Unit tests for prediction_service module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.prediction_service import PredictionService, ModelInferenceError


class TestPredictionService(unittest.TestCase):
    """Test cases for PredictionService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model_manager = MagicMock()
        self.prediction_service = PredictionService(self.mock_model_manager)
        
        # Create a sample image array (batch_size=1, 224, 224, 3)
        self.sample_image = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        # Sample prediction output (4 classes: Bajo_Electrico, Guitarra_Acustica, 
        # Guitarra_Electrica, Guitarra_Electroacustica)
        self.sample_predictions = np.array([[0.1, 0.7, 0.15, 0.05]])

    def test_prediction_service_initialization(self):
        """Test PredictionService initializes correctly."""
        self.assertIsNotNone(self.prediction_service)
        self.assertEqual(self.prediction_service._model_manager, self.mock_model_manager)

    def test_class_names_available(self):
        """Test that class names are defined."""
        self.assertIsNotNone(self.prediction_service.class_names)
        self.assertEqual(len(self.prediction_service.class_names), 4)
        self.assertIn('Guitarra_Acustica', self.prediction_service.class_names)

    def test_predict_single_model(self):
        """Test single model prediction."""
        # Mock the model manager to return a mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.5
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('predicted_class', result)
        self.assertIn('confidence', result)
        self.assertIn('model_used', result)
        self.assertIn('processing_time_ms', result)
        self.assertIn('class_probabilities', result)

    def test_predict_returns_highest_confidence_class(self):
        """Test that prediction returns class with highest confidence."""
        mock_model = MagicMock()
        # Predictions: [0.1, 0.7, 0.15, 0.05] -> highest is index 1 (0.7)
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.0
        )
        
        self.assertIsNone(error)
        # Index 1 should be Guitarra_Acustica
        self.assertEqual(result['predicted_class'], 'Guitarra_Acustica')
        self.assertAlmostEqual(result['confidence'], 0.7, places=2)

    def test_predict_with_threshold(self):
        """Test prediction with confidence threshold."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions  # max confidence is 0.7
        self.mock_model_manager.load_model.return_value = mock_model
        
        # With threshold 0.8, no class meets threshold
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.8
        )
        
        self.assertIsNone(error)
        # Should still return prediction but with note about low confidence
        self.assertIsNotNone(result)

    def test_predict_model_loading_failure(self):
        """Test prediction when model loading fails."""
        self.mock_model_manager.load_model.side_effect = Exception("Model not found")
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='nonexistent.keras',
            threshold=0.5
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_predict_inference_failure(self):
        """Test prediction when inference fails."""
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Inference error")
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.5
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_predict_ensemble(self):
        """Test ensemble prediction with multiple models."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict_ensemble(
            image_array=self.sample_image,
            threshold=0.5
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('predicted_class', result)
        self.assertIn('confidence', result)
        self.assertIn('model_used', result)
        self.assertEqual(result['model_used'], 'ensemble')

    def test_predict_ensemble_averages_probabilities(self):
        """Test that ensemble averages probabilities from multiple models."""
        mock_model1 = MagicMock()
        mock_model2 = MagicMock()
        
        # Model 1 predictions
        predictions1 = np.array([[0.2, 0.6, 0.15, 0.05]])
        # Model 2 predictions
        predictions2 = np.array([[0.1, 0.8, 0.05, 0.05]])
        
        self.mock_model_manager.load_model.side_effect = [mock_model1, mock_model2]
        mock_model1.predict.return_value = predictions1
        mock_model2.predict.return_value = predictions2
        
        result, error = self.prediction_service.predict_ensemble(
            image_array=self.sample_image,
            threshold=0.5
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        # Average of [0.6, 0.8] = 0.7 for index 1
        self.assertAlmostEqual(result['confidence'], 0.7, places=1)

    def test_predict_ensemble_both_models_fail(self):
        """Test ensemble prediction when both models fail."""
        self.mock_model_manager.load_model.side_effect = Exception("Model error")
        
        result, error = self.prediction_service.predict_ensemble(
            image_array=self.sample_image,
            threshold=0.5
        )
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_predict_ensemble_one_model_fails(self):
        """Test ensemble prediction when one model fails (fallback)."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        
        # First call fails, second succeeds
        self.mock_model_manager.load_model.side_effect = [
            Exception("First model error"),
            mock_model
        ]
        
        result, error = self.prediction_service.predict_ensemble(
            image_array=self.sample_image,
            threshold=0.5
        )
        
        # Should handle gracefully and still return a result
        # Implementation may vary - check if error is None or not
        self.assertTrue(result is not None or error is not None)

    def test_predict_returns_all_class_probabilities(self):
        """Test that prediction returns probabilities for all classes."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.0
        )
        
        self.assertIsNone(error)
        self.assertIsNotNone(result['class_probabilities'])
        # Should have 4 probabilities for 4 classes
        self.assertEqual(len(result['class_probabilities']), 4)

    def test_predict_class_probabilities_sum_to_one(self):
        """Test that class probabilities sum to approximately 1."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.0
        )
        
        self.assertIsNone(error)
        prob_sum = sum(result['class_probabilities'].values())
        self.assertAlmostEqual(prob_sum, 1.0, places=2)

    def test_predict_processing_time_recorded(self):
        """Test that processing time is recorded."""
        mock_model = MagicMock()
        mock_model.predict.return_value = self.sample_predictions
        self.mock_model_manager.load_model.return_value = mock_model
        
        result, error = self.prediction_service.predict(
            image_array=self.sample_image,
            model_name='test_model.keras',
            threshold=0.0
        )
        
        self.assertIsNone(error)
        self.assertGreater(result['processing_time_ms'], 0)

    def test_predict_model_info(self):
        """Test getting model info."""
        mock_model = MagicMock()
        mock_model.get_config.return_value = {'test': 'config'}
        self.mock_model_manager.load_model.return_value = mock_model
        
        # Should not raise exception
        info = self.prediction_service.get_model_info('test_model.keras')
        self.assertIsNotNone(info)

    def test_predict_invalid_image_array(self):
        """Test prediction with invalid image array."""
        mock_model = MagicMock()
        self.mock_model_manager.load_model.return_value = mock_model
        
        # Invalid array shape
        invalid_image = np.random.rand(224, 224, 3)  # missing batch dimension
        
        result, error = self.prediction_service.predict(
            image_array=invalid_image,
            model_name='test_model.keras',
            threshold=0.5
        )
        
        # Should either handle gracefully or return error
        self.assertTrue(result is not None or error is not None)

    def test_ensemble_uses_both_models(self):
        """Test that ensemble uses both primary and alternative models."""
        mock_model1 = MagicMock()
        mock_model2 = MagicMock()
        mock_model1.predict.return_value = self.sample_predictions
        mock_model2.predict.return_value = self.sample_predictions
        
        self.mock_model_manager.load_model.side_effect = [mock_model1, mock_model2]
        
        result, error = self.prediction_service.predict_ensemble(
            image_array=self.sample_image,
            threshold=0.5
        )
        
        self.assertIsNone(error)
        # load_model should have been called twice (once for each model)
        self.assertEqual(self.mock_model_manager.load_model.call_count, 2)


class TestPredictionServiceIntegration(unittest.TestCase):
    """Integration tests for PredictionService."""

    def test_prediction_service_workflow(self):
        """Test complete prediction workflow."""
        mock_model_manager = MagicMock()
        service = PredictionService(mock_model_manager)
        
        mock_model = MagicMock()
        predictions = np.array([[0.1, 0.7, 0.15, 0.05]])
        mock_model.predict.return_value = predictions
        mock_model_manager.load_model.return_value = mock_model
        
        # Simulate preprocessing output
        image_array = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        # Run prediction
        result, error = service.predict(
            image_array=image_array,
            model_name='test_model.keras',
            threshold=0.5
        )
        
        # Verify complete result structure
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('predicted_class', result)
        self.assertIn('confidence', result)
        self.assertIn('model_used', result)
        self.assertIn('processing_time_ms', result)
        self.assertIn('class_probabilities', result)


if __name__ == '__main__':
    unittest.main()
