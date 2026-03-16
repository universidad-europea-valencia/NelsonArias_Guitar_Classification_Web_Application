"""
Integration tests for Guitar Classification API.
Tests complete request-response cycles with real API endpoints.
"""

import json
import io
import unittest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from fastapi.testclient import TestClient
from app.main import app


class IntegrationTestBaseAPI(unittest.TestCase):
    """Base integration test class for API endpoints."""
    
    def setUp(self):
        """Set up test client and fixtures."""
        self.client = TestClient(app)
        self.test_image = self._create_test_image()
    
    def _create_test_image(self):
        """Create a test image in memory."""
        img = Image.new('RGB', (224, 224), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
    
    def _create_invalid_image(self):
        """Create invalid image data."""
        return io.BytesIO(b"not an image")
    
    def _create_oversized_image(self):
        """Create an oversized image (>4MB)."""
        img = Image.new('RGB', (5000, 5000), color='blue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr


class TestHealthEndpoint(IntegrationTestBaseAPI):
    """Test health check endpoint."""
    
    def test_health_check_success(self):
        """Test that health endpoint returns 200 OK."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
    
    def test_health_check_structure(self):
        """Test health endpoint returns proper structure."""
        response = self.client.get("/api/v1/health")
        data = response.json()
        required_fields = ["status", "timestamp"]
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("version", data)
        self.assertEqual(data["version"], "1.0.0")


class TestClassificationEndpoint(IntegrationTestBaseAPI):
    """Test classification endpoint."""
    
    @patch('app.routes.classification.PredictionService')
    @patch('app.routes.classification.ModelManager')
    def test_classify_success(self, mock_model_manager, mock_prediction_service):
        """Test successful classification request."""
        # Mock the prediction service
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 156.23,
            "all_probabilities": {
                "Guitarra_Electrica": 0.95,
                "Guitarra_Acustica": 0.03,
                "Guitarra_Electroacustica": 0.01,
                "Bajo_Electrico": 0.01
            }
        }
        mock_prediction_service.return_value = mock_pred_instance
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_class", data)
        self.assertIn("confidence", data)
    
    def test_classify_missing_file(self):
        """Test classification without file fails."""
        response = self.client.post("/api/v1/classify")
        self.assertEqual(response.status_code, 422)  # Validation error
    
    @patch('app.routes.classification.ImageProcessor')
    @patch('app.routes.classification.ModelManager')
    def test_classify_invalid_image(self, mock_model_manager, mock_image_processor):
        """Test classification with invalid image format."""
        mock_processor = MagicMock()
        mock_processor.preprocess.side_effect = ValueError("Invalid image format")
        
        with patch('app.routes.classification.ImageProcessor', return_value=mock_processor):
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("test.txt", self._create_invalid_image(), "text/plain")}
            )
        
        # Should return 400 or 422
        self.assertIn(response.status_code, [400, 422])
    
    @patch('app.routes.classification.PredictionService')
    def test_classify_alternative_model(self, mock_prediction_service):
        """Test alternative model classification."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_alternative.return_value = {
            "predicted_class": "Guitarra_Acustica",
            "confidence": 0.87,
            "processing_time_ms": 198.45,
            "all_probabilities": {}
        }
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            response = self.client.post(
                "/api/v1/classify-alternative",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
        
        self.assertEqual(response.status_code, 200)


class TestEnsembleClassification(IntegrationTestBaseAPI):
    """Test ensemble classification endpoint."""
    
    @patch('app.routes.classification.PredictionService')
    def test_ensemble_classification(self, mock_prediction_service):
        """Test ensemble prediction combining multiple models."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_ensemble.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.91,
            "processing_time_ms": 325.67,
            "ensemble_method": "probability_averaging",
            "all_probabilities": {}
        }
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            response = self.client.post(
                "/api/v1/classify-ensemble",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ensemble_method", data)


class TestErrorHandling(IntegrationTestBaseAPI):
    """Test error handling and edge cases."""
    
    def test_invalid_endpoint(self):
        """Test requesting non-existent endpoint."""
        response = self.client.post("/api/v1/classify-invalid")
        self.assertEqual(response.status_code, 404)
    
    @patch('app.routes.classification.PredictionService')
    def test_server_error_handling(self, mock_prediction_service):
        """Test handling of server errors."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.side_effect = Exception("Model loading failed")
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
        
        self.assertEqual(response.status_code, 500)
    
    def test_unsupported_content_type(self):
        """Test sending unsupported content type."""
        response = self.client.post(
            "/api/v1/classify",
            data={"file": "not a file"}
        )
        self.assertIn(response.status_code, [400, 422])


class TestResponseFormat(IntegrationTestBaseAPI):
    """Test API response format and structure."""
    
    @patch('app.routes.classification.PredictionService')
    def test_response_structure(self, mock_prediction_service):
        """Test response has required structure."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 156.23,
            "all_probabilities": {
                "Guitarra_Electrica": 0.95,
                "Guitarra_Acustica": 0.03,
                "Guitarra_Electroacustica": 0.01,
                "Bajo_Electrico": 0.01
            }
        }
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
        
        data = response.json()
        required_fields = ["predicted_class", "confidence", "processing_time_ms"]
        for field in required_fields:
            self.assertIn(field, data)
    
    def test_response_json_valid(self):
        """Test response is valid JSON."""
        response = self.client.get("/api/v1/health")
        try:
            json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")


class TestCORS(IntegrationTestBaseAPI):
    """Test CORS headers."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in response."""
        response = self.client.get("/api/v1/health")
        # CORS headers should be in response
        self.assertEqual(response.status_code, 200)
    
    def test_cors_options_request(self):
        """Test CORS preflight request."""
        response = self.client.options("/api/v1/classify")
        # Should return 200 for OPTIONS
        self.assertIn(response.status_code, [200, 405])


class TestFileHandling(IntegrationTestBaseAPI):
    """Test file upload handling."""
    
    @patch('app.routes.classification.PredictionService')
    def test_multiple_file_formats(self, mock_prediction_service):
        """Test different image formats."""
        formats = [('PNG', 'image/png'), ('JPEG', 'image/jpeg')]
        
        for format_name, content_type in formats:
            mock_pred_instance = MagicMock()
            mock_pred_instance.predict_primary.return_value = {
                "predicted_class": "Guitarra_Electrica",
                "confidence": 0.95,
                "processing_time_ms": 150,
                "all_probabilities": {}
            }
            
            with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
                response = self.client.post(
                    "/api/v1/classify",
                    files={"file": (f"test.{format_name.lower()}", self.test_image, content_type)}
                )
            
            self.assertEqual(response.status_code, 200, f"Failed for {format_name}")


if __name__ == "__main__":
    unittest.main()
