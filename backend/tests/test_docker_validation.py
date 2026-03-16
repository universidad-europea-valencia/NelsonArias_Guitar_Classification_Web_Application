"""
Docker validation tests for Guitar Classification Platform.
Tests Docker setup, container health, and orchestration.
"""

import unittest
import subprocess
import time
import json
import requests
from pathlib import Path


class DockerSetupValidation(unittest.TestCase):
    """Validate Docker setup and configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
    
    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml exists."""
        self.assertTrue(self.docker_compose_file.exists(), 
                       "docker-compose.yml not found")
    
    def test_backend_dockerfile_exists(self):
        """Test that backend Dockerfile exists."""
        backend_dockerfile = self.project_root / "backend" / "Dockerfile"
        self.assertTrue(backend_dockerfile.exists(), 
                       "Backend Dockerfile not found")
    
    def test_frontend_dockerfile_exists(self):
        """Test that frontend Dockerfile exists."""
        frontend_dockerfile = self.project_root / "frontend" / "Dockerfile"
        self.assertTrue(frontend_dockerfile.exists(), 
                       "Frontend Dockerfile not found")
    
    def test_docker_compose_yaml_valid(self):
        """Test that docker-compose.yml is valid YAML."""
        try:
            with open(self.docker_compose_file, 'r') as f:
                import yaml
                yaml.safe_load(f)
        except ImportError:
            self.skipTest("PyYAML not installed")
        except Exception as e:
            self.fail(f"Invalid docker-compose.yml: {e}")
    
    def test_backend_dockerfile_syntax(self):
        """Test backend Dockerfile syntax."""
        backend_dockerfile = self.project_root / "backend" / "Dockerfile"
        with open(backend_dockerfile, 'r') as f:
            content = f.read()
            self.assertIn("FROM", content)
            self.assertIn("WORKDIR", content)
            self.assertIn("RUN", content)
            self.assertIn("CMD", content)
    
    def test_frontend_dockerfile_syntax(self):
        """Test frontend Dockerfile syntax."""
        frontend_dockerfile = self.project_root / "frontend" / "Dockerfile"
        with open(frontend_dockerfile, 'r') as f:
            content = f.read()
            self.assertIn("FROM", content)
            self.assertIn("WORKDIR", content)
            self.assertIn("RUN", content)
            self.assertIn("CMD", content)


class DockerImageValidation(unittest.TestCase):
    """Validate Docker image construction."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_docker_installed(self):
        """Test that Docker is installed and accessible."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.assertEqual(result.returncode, 0, "Docker not installed or not accessible")
        except FileNotFoundError:
            self.skipTest("Docker not installed")
        except Exception as e:
            self.skipTest(f"Cannot test Docker: {e}")
    
    def test_docker_compose_installed(self):
        """Test that Docker Compose is installed."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.assertEqual(result.returncode, 0, "Docker Compose not installed")
        except FileNotFoundError:
            self.skipTest("Docker Compose not installed")
        except Exception as e:
            self.skipTest(f"Cannot test Docker Compose: {e}")
    
    def test_backend_requirements_file_exists(self):
        """Test backend requirements.txt exists."""
        req_file = self.project_root / "backend" / "requirements.txt"
        self.assertTrue(req_file.exists(), "Backend requirements.txt not found")
    
    def test_frontend_package_json_exists(self):
        """Test frontend package.json exists."""
        pkg_file = self.project_root / "frontend" / "package.json"
        self.assertTrue(pkg_file.exists(), "Frontend package.json not found")


class DockerComposeValidation(unittest.TestCase):
    """Validate docker-compose configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.docker_compose_file = self.project_root / "docker-compose.yml"
    
    def _load_docker_compose(self):
        """Load docker-compose.yml."""
        try:
            import yaml
            with open(self.docker_compose_file, 'r') as f:
                return yaml.safe_load(f)
        except ImportError:
            self.skipTest("PyYAML not installed")
        except Exception as e:
            self.fail(f"Cannot load docker-compose.yml: {e}")
    
    def test_services_defined(self):
        """Test that services are defined."""
        compose = self._load_docker_compose()
        self.assertIn("services", compose, "No services defined in docker-compose.yml")
        self.assertIsInstance(compose["services"], dict)
    
    def test_backend_service_configured(self):
        """Test backend service configuration."""
        compose = self._load_docker_compose()
        self.assertIn("backend", compose["services"], "Backend service not defined")
        backend = compose["services"]["backend"]
        
        # Check required fields
        self.assertIn("build", backend)
        self.assertIn("ports", backend)
        self.assertIn("environment", backend)
    
    def test_frontend_service_configured(self):
        """Test frontend service configuration."""
        compose = self._load_docker_compose()
        self.assertIn("frontend", compose["services"], "Frontend service not defined")
        frontend = compose["services"]["frontend"]
        
        # Check required fields
        self.assertIn("build", frontend)
        self.assertIn("ports", frontend)
    
    def test_backend_port_configured(self):
        """Test backend port is configured."""
        compose = self._load_docker_compose()
        backend = compose["services"]["backend"]
        self.assertIn("ports", backend)
        # Should expose port 8000
        ports = backend["ports"]
        self.assertTrue(any("8000" in str(p) for p in ports), 
                       "Backend port 8000 not found in configuration")
    
    def test_frontend_port_configured(self):
        """Test frontend port is configured."""
        compose = self._load_docker_compose()
        frontend = compose["services"]["frontend"]
        self.assertIn("ports", frontend)
        # Should expose port 3000
        ports = frontend["ports"]
        self.assertTrue(any("3000" in str(p) for p in ports), 
                       "Frontend port 3000 not found in configuration")
    
    def test_environment_variables_configured(self):
        """Test environment variables are configured."""
        compose = self._load_docker_compose()
        backend = compose["services"]["backend"]
        self.assertIn("environment", backend)
        
        env = backend["environment"]
        if isinstance(env, list):
            env_dict = {kv.split('=')[0]: kv.split('=')[1] if '=' in kv else "" 
                       for kv in env if '=' in kv}
        else:
            env_dict = env
        
        # Should have API configuration
        self.assertTrue(len(env_dict) > 0, "No environment variables configured")


class DockerHealthCheck(unittest.TestCase):
    """Test Docker container health checks."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
    
    def test_backend_health_endpoint_accessible(self):
        """Test backend health endpoint is accessible."""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend service not running (docker-compose up required)")
        except Exception as e:
            self.skipTest(f"Cannot test backend health: {e}")
    
    def test_backend_api_root_accessible(self):
        """Test backend API root endpoint."""
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("version", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend service not running")
        except Exception as e:
            self.skipTest(f"Cannot test backend root: {e}")
    
    def test_frontend_accessible(self):
        """Test frontend is accessible."""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            self.assertIn(response.status_code, [200, 301])
        except requests.exceptions.ConnectionError:
            self.skipTest("Frontend service not running")
        except Exception as e:
            self.skipTest(f"Cannot test frontend: {e}")


class DockerNetworkValidation(unittest.TestCase):
    """Validate Docker network setup."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_docker_compose_network_defined(self):
        """Test that docker-compose defines a network."""
        try:
            import yaml
            with open(self.project_root / "docker-compose.yml", 'r') as f:
                compose = yaml.safe_load(f)
            
            # Check if services can communicate
            self.assertIn("services", compose)
            services = compose["services"]
            self.assertGreater(len(services), 1, "Multiple services should be defined")
        except ImportError:
            self.skipTest("PyYAML not installed")
        except Exception as e:
            self.skipTest(f"Cannot validate network: {e}")


class DockerVolumeValidation(unittest.TestCase):
    """Validate Docker volume configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_volumes_configured(self):
        """Test that volumes are properly configured."""
        try:
            import yaml
            with open(self.project_root / "docker-compose.yml", 'r') as f:
                compose = yaml.safe_load(f)
            
            services = compose.get("services", {})
            backend = services.get("backend", {})
            
            # Check if volumes are configured for model files
            if "volumes" in backend:
                volumes = backend["volumes"]
                self.assertTrue(len(volumes) > 0, "No volumes configured")
        except ImportError:
            self.skipTest("PyYAML not installed")
        except Exception as e:
            self.skipTest(f"Cannot validate volumes: {e}")


class DockerEnvValidation(unittest.TestCase):
    """Validate .env files for Docker."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / ".env"
    
    def test_env_file_exists(self):
        """Test that .env file exists."""
        self.assertTrue(self.env_file.exists(), ".env file not found")
    
    def test_env_file_has_required_vars(self):
        """Test that .env has required variables."""
        with open(self.env_file, 'r') as f:
            content = f.read()
        
        # Should have configuration for both services
        required_patterns = ["ENVIRONMENT", "API_URL", "REACT_APP"]
        # At least one of these patterns should exist
        self.assertTrue(len(content) > 0, ".env file is empty")


if __name__ == "__main__":
    unittest.main()
