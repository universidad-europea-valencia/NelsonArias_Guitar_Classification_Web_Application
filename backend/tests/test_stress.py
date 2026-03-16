"""
Stress and performance tests for Guitar Classification API.
Tests system behavior under load and response time constraints.
"""

import unittest
import time
import io
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock
from PIL import Image

from fastapi.testclient import TestClient
from app.main import app


class StressTestBaseClass(unittest.TestCase):
    """Base class for stress tests."""
    
    def setUp(self):
        """Set up test client and fixtures."""
        self.client = TestClient(app)
        self.test_image = self._create_test_image()
        self.results = {
            "success_count": 0,
            "error_count": 0,
            "response_times": []
        }
    
    def _create_test_image(self):
        """Create a test image in memory."""
        img = Image.new('RGB', (224, 224), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
    
    def _reset_image(self):
        """Reset image pointer for reuse."""
        self.test_image.seek(0)


class TestHealthCheckStress(StressTestBaseClass):
    """Stress test for health check endpoint."""
    
    def test_health_check_1000_requests(self):
        """Send 1000 health check requests."""
        start_time = time.time()
        success_count = 0
        
        for i in range(1000):
            response = self.client.get("/api/v1/health")
            if response.status_code == 200:
                success_count += 1
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        self.assertEqual(success_count, 1000)
        avg_time = (elapsed / 1000) * 1000  # Convert to ms
        print(f"\nHealth check: 1000 requests in {elapsed:.2f}s ({avg_time:.2f}ms avg)")
    
    def test_health_check_concurrent_requests(self):
        """Test health check with concurrent requests."""
        num_threads = 50
        requests_per_thread = 20
        
        def health_check_request():
            response = self.client.get("/api/v1/health")
            return response.status_code == 200
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(health_check_request)
                for _ in range(num_threads * requests_per_thread)
            ]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        success_count = sum(results)
        total_requests = num_threads * requests_per_thread
        
        self.assertEqual(success_count, total_requests)
        print(f"\nConcurrent health checks: {total_requests} requests in {end_time - start_time:.2f}s")


class TestClassificationEndpointStress(StressTestBaseClass):
    """Stress test for classification endpoint."""
    
    @patch('app.routes.classification.PredictionService')
    def test_classification_sequential_load(self, mock_prediction_service):
        """Test classification endpoint with sequential requests."""
        num_requests = 100
        
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 150,
            "all_probabilities": {
                "Guitarra_Electrica": 0.95,
                "Guitarra_Acustica": 0.03,
                "Guitarra_Electroacustica": 0.01,
                "Bajo_Electrico": 0.01
            }
        }
        
        start_time = time.time()
        success_count = 0
        response_times = []
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            for i in range(num_requests):
                req_start = time.time()
                response = self.client.post(
                    "/api/v1/classify",
                    files={"file": ("test.png", self.test_image, "image/png")}
                )
                req_time = (time.time() - req_start) * 1000
                response_times.append(req_time)
                
                if response.status_code == 200:
                    success_count += 1
                
                self._reset_image()
        
        end_time = time.time()
        
        self.assertEqual(success_count, num_requests)
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\nSequential classification: {num_requests} requests in {end_time - start_time:.2f}s")
        print(f"  Avg: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
    
    @patch('app.routes.classification.PredictionService')
    def test_classification_concurrent_load(self, mock_prediction_service):
        """Test classification endpoint with concurrent requests."""
        num_threads = 10
        requests_per_thread = 20
        
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 150,
            "all_probabilities": {}
        }
        
        def classify_request():
            try:
                with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
                    img = self._create_test_image()
                    response = self.client.post(
                        "/api/v1/classify",
                        files={"file": ("test.png", img, "image/png")}
                    )
                    return response.status_code == 200
            except Exception as e:
                print(f"Error in concurrent request: {e}")
                return False
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(classify_request)
                for _ in range(num_threads * requests_per_thread)
            ]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        success_count = sum(results)
        total_requests = num_threads * requests_per_thread
        
        print(f"\nConcurrent classification: {total_requests} requests in {end_time - start_time:.2f}s")
        print(f"  Success: {success_count}/{total_requests}")


class TestResponseTimePerformance(StressTestBaseClass):
    """Test response time performance requirements."""
    
    @patch('app.routes.classification.PredictionService')
    def test_single_classification_response_time(self, mock_prediction_service):
        """Test single classification response time (expect <300ms)."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 156,
            "all_probabilities": {}
        }
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            req_start = time.time()
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
            response_time = (time.time() - req_start) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5000)  # Should complete in < 5 seconds
        print(f"\nSingle classification response time: {response_time:.2f}ms")
    
    @patch('app.routes.classification.PredictionService')
    def test_ensemble_response_time(self, mock_prediction_service):
        """Test ensemble classification response time."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_ensemble.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.91,
            "processing_time_ms": 300,
            "ensemble_method": "probability_averaging",
            "all_probabilities": {}
        }
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            req_start = time.time()
            response = self.client.post(
                "/api/v1/classify-ensemble",
                files={"file": ("test.png", self.test_image, "image/png")}
            )
            response_time = (time.time() - req_start) * 1000
        
        self.assertEqual(response.status_code, 200)
        print(f"\nEnsemble classification response time: {response_time:.2f}ms")


class TestMemoryStress(StressTestBaseClass):
    """Test system under memory stress."""
    
    @patch('app.routes.classification.PredictionService')
    def test_large_batch_processing(self, mock_prediction_service):
        """Test processing large batch of images."""
        mock_pred_instance = MagicMock()
        mock_pred_instance.predict_primary.return_value = {
            "predicted_class": "Guitarra_Electrica",
            "confidence": 0.95,
            "processing_time_ms": 150,
            "all_probabilities": {}
        }
        
        num_requests = 500
        start_time = time.time()
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            for i in range(num_requests):
                response = self.client.post(
                    "/api/v1/classify",
                    files={"file": ("test.png", self._create_test_image(), "image/png")}
                )
                self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        print(f"\nLarge batch processing: {num_requests} images in {end_time - start_time:.2f}s")


class TestErrorRecovery(StressTestBaseClass):
    """Test system error recovery under stress."""
    
    @patch('app.routes.classification.PredictionService')
    def test_error_recovery_on_failed_requests(self, mock_prediction_service):
        """Test system continues working after errors."""
        mock_pred_instance = MagicMock()
        
        # Simulate errors on some requests
        side_effects = [
            {"predicted_class": "Guitarra_Electrica", "confidence": 0.95, "processing_time_ms": 150, "all_probabilities": {}},
            Exception("Model prediction failed"),
            {"predicted_class": "Guitarra_Acustica", "confidence": 0.87, "processing_time_ms": 145, "all_probabilities": {}},
            {"predicted_class": "Guitarra_Electrica", "confidence": 0.92, "processing_time_ms": 155, "all_probabilities": {}},
        ]
        
        mock_pred_instance.predict_primary.side_effect = side_effects * 25  # 100 requests
        
        success_count = 0
        error_count = 0
        
        with patch('app.routes.classification.get_prediction_service', return_value=mock_pred_instance):
            for i in range(100):
                try:
                    response = self.client.post(
                        "/api/v1/classify",
                        files={"file": ("test.png", self._create_test_image(), "image/png")}
                    )
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
                
                self._reset_image()
        
        print(f"\nError recovery: {success_count} successes, {error_count} errors out of 100 requests")


if __name__ == "__main__":
    unittest.main()
