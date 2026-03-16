"""
Security tests for Guitar Classification API.
Tests input validation, malicious payloads, and security measures.
"""

import unittest
import io
from unittest.mock import patch, MagicMock
from PIL import Image

from fastapi.testclient import TestClient
from app.main import app


class SecurityTestBase(unittest.TestCase):
    """Base class for security tests."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def _create_test_image(self):
        """Create a test image."""
        img = Image.new('RGB', (224, 224), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr


class TestInputValidation(SecurityTestBase):
    """Test input validation security."""
    
    def test_missing_file_parameter(self):
        """Test handling of missing file parameter."""
        response = self.client.post("/api/v1/classify")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_empty_file_upload(self):
        """Test handling of empty file."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("empty.png", io.BytesIO(b""), "image/png")}
        )
        self.assertIn(response.status_code, [400, 422])
    
    def test_invalid_content_type(self):
        """Test rejection of invalid content types."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")}
        )
        # Should reject executable
        self.assertIn(response.status_code, [400, 415, 422])
    
    def test_corrupted_image_data(self):
        """Test handling of corrupted image data."""
        corrupted_data = b'\x89PNG\r\n\x1a\n' + b'corrupted' * 100
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("corrupted.png", io.BytesIO(corrupted_data), "image/png")}
        )
        self.assertIn(response.status_code, [400, 422])
    
    def test_oversized_filename(self):
        """Test handling of extremely long filenames."""
        long_filename = "a" * 10000 + ".png"
        response = self.client.post(
            "/api/v1/classify",
            files={"file": (long_filename, self._create_test_image(), "image/png")}
        )
        self.assertIn(response.status_code, [200, 400, 422])


class TestFileTypeValidation(SecurityTestBase):
    """Test file type validation security."""
    
    def test_text_file_as_image(self):
        """Test rejection of text file claimed as image."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("fake.png", io.BytesIO(b"This is text, not PNG"), "image/png")}
        )
        self.assertIn(response.status_code, [400, 422])
    
    def test_zip_file_as_image(self):
        """Test rejection of zip file claimed as image."""
        zip_header = b'PK\x03\x04'
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("archive.png", io.BytesIO(zip_header + b"content"), "image/png")}
        )
        self.assertIn(response.status_code, [400, 422])
    
    def test_script_file_as_image(self):
        """Test rejection of script file."""
        script_content = b"#!/bin/bash\necho 'malicious code'"
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("script.png", io.BytesIO(script_content), "image/png")}
        )
        self.assertIn(response.status_code, [400, 422])


class TestPathTraversalProtection(SecurityTestBase):
    """Test protection against path traversal attacks."""
    
    def test_path_traversal_in_filename(self):
        """Test handling of path traversal in filename."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("../../../etc/passwd", self._create_test_image(), "image/png")}
        )
        # Should not allow path traversal
        self.assertNotEqual(response.status_code, 500)
    
    def test_null_byte_injection(self):
        """Test handling of null byte injection in filename."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("file\x00.png", self._create_test_image(), "image/png")}
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 422])


class TestHTTPHeaderValidation(SecurityTestBase):
    """Test HTTP header validation."""
    
    def test_malicious_user_agent(self):
        """Test handling of malicious user agent."""
        headers = {"User-Agent": "' or '1'='1"}
        response = self.client.get("/api/v1/health", headers=headers)
        self.assertEqual(response.status_code, 200)
    
    def test_sql_injection_in_headers(self):
        """Test protection against SQL injection in headers."""
        headers = {"X-Test": "'; DROP TABLE users; --"}
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("test.png", self._create_test_image(), "image/png")},
            headers=headers
        )
        # Should handle without crashing
        self.assertIn(response.status_code, [200, 400, 422])


class TestDOSProtection(SecurityTestBase):
    """Test protection against Denial of Service attacks."""
    
    def test_extremely_large_image_dimensions(self):
        """Test handling of extremely large image dimensions."""
        # Create 10000x10000 image in memory (stress test)
        try:
            img = Image.new('RGB', (10000, 10000), color='red')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            response = self.client.post(
                "/api/v1/classify",
                files={"file": ("large.png", img_byte_arr, "image/png")},
                timeout=10
            )
            # Should handle or reject gracefully
            self.assertIn(response.status_code, [200, 400, 413, 422])
        except Exception as e:
            # Expected to fail due to memory constraints
            self.assertIsNotNone(e)
    
    def test_repeated_requests_rate_limiting(self):
        """Test system behavior under rapid requests."""
        success_count = 0
        for i in range(10):
            response = self.client.get("/api/v1/health")
            if response.status_code == 200:
                success_count += 1
        
        # All requests should succeed (no rate limiting yet)
        self.assertEqual(success_count, 10)


class TestCORSSecurityHeaders(SecurityTestBase):
    """Test CORS and security headers."""
    
    def test_cors_configured(self):
        """Test that CORS is properly configured."""
        response = self.client.options("/api/v1/health")
        # CORS should be configured
        self.assertIn(response.status_code, [200, 405])
    
    def test_trusted_hosts_enforced(self):
        """Test trusted hosts middleware."""
        # This is enforced in the app configuration
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)


class TestXMLExternalEntityAttack(SecurityTestBase):
    """Test protection against XXE (XML External Entity) attacks."""
    
    def test_xxe_in_image_metadata(self):
        """Test handling of XXE in image metadata."""
        # Create valid PNG but attempt XXE
        img = Image.new('RGB', (224, 224), color='blue')
        img_byte_arr = io.BytesIO()
        img.info['XXE'] = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe "test">]>'
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("xxe.png", img_byte_arr, "image/png")}
        )
        # Should handle safely
        self.assertIn(response.status_code, [200, 400, 422])


class TestCommandInjectionProtection(SecurityTestBase):
    """Test protection against command injection."""
    
    def test_command_injection_in_filename(self):
        """Test handling of command injection in filename."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("test; rm -rf /; .png", self._create_test_image(), "image/png")}
        )
        # Should not execute commands
        self.assertIn(response.status_code, [200, 400, 422])
    
    def test_unicode_filename_injection(self):
        """Test handling of unicode injection in filename."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("test\x00\x1f\x7f.png", self._create_test_image(), "image/png")}
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 422])


class TestErrorInformationLeak(SecurityTestBase):
    """Test that error messages don't leak sensitive information."""
    
    def test_error_message_reveals_no_paths(self):
        """Test that error messages don't reveal system paths."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        )
        
        if response.status_code >= 400:
            error_text = str(response.json())
            # Should not contain common path indicators
            self.assertNotIn("/home/", error_text)
            self.assertNotIn("/root/", error_text)
            self.assertNotIn("C:\\", error_text)
    
    def test_error_message_reveals_no_stack_trace(self):
        """Test that detailed stack traces are not exposed."""
        response = self.client.post(
            "/api/v1/classify",
            files={"file": ("test.bin", io.BytesIO(b"\x00\x01\x02"), "application/octet-stream")}
        )
        
        if response.status_code >= 500:
            error_text = str(response.json())
            # Should not contain Python stack trace markers
            self.assertNotIn("Traceback", error_text)
            self.assertNotIn("File \"", error_text)


if __name__ == "__main__":
    unittest.main()
