"""
Test runner and validation script for PHASE 4: Testing Integral.
Executes all tests and generates comprehensive report.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Manages test execution and reporting."""
    
    def __init__(self):
        """Initialize test runner."""
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            "unit_tests": {},
            "integration_tests": {},
            "stress_tests": {},
            "security_tests": {},
            "docker_validation": {},
            "summary": {}
        }
        self.start_time = datetime.now()
    
    def run_unit_tests(self):
        """Run backend unit tests."""
        print("\n" + "="*70)
        print("RUNNING BACKEND UNIT TESTS")
        print("="*70)
        
        test_dir = self.project_root / "backend" / "tests"
        test_files = [
            "test_model_service.py",
            "test_image_service.py",
            "test_prediction_service.py"
        ]
        
        for test_file in test_files:
            print(f"\nRunning {test_file}...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", f"tests.{test_file.replace('.py', '')}"],
                    cwd=self.project_root / "backend",
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                success = result.returncode == 0
                self.results["unit_tests"][test_file] = {
                    "status": "PASSED" if success else "FAILED",
                    "returncode": result.returncode,
                    "stdout": result.stdout[:500] if result.stdout else "",
                    "stderr": result.stderr[:500] if result.stderr else ""
                }
                
                print(f"  Status: {'✓ PASSED' if success else '✗ FAILED'}")
                if result.stdout:
                    print(f"  Output: {result.stdout.split(chr(10))[0]}")
            except subprocess.TimeoutExpired:
                self.results["unit_tests"][test_file] = {
                    "status": "TIMEOUT",
                    "returncode": -1
                }
                print(f"  Status: ✗ TIMEOUT")
            except Exception as e:
                self.results["unit_tests"][test_file] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"  Status: ✗ ERROR: {e}")
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("\n" + "="*70)
        print("RUNNING INTEGRATION TESTS")
        print("="*70)
        
        test_file = "test_integration.py"
        print(f"\nRunning {test_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", f"tests.{test_file.replace('.py', '')}"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            self.results["integration_tests"][test_file] = {
                "status": "PASSED" if success else "FAILED",
                "returncode": result.returncode,
                "output_sample": result.stdout[:1000] if result.stdout else ""
            }
            
            print(f"  Status: {'✓ PASSED' if success else '✗ FAILED'}")
        except subprocess.TimeoutExpired:
            self.results["integration_tests"][test_file] = {
                "status": "TIMEOUT"
            }
            print(f"  Status: ✗ TIMEOUT")
        except Exception as e:
            self.results["integration_tests"][test_file] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  Status: ✗ ERROR: {e}")
    
    def run_stress_tests(self):
        """Run stress testing."""
        print("\n" + "="*70)
        print("RUNNING STRESS TESTS")
        print("="*70)
        
        test_file = "test_stress.py"
        print(f"\nRunning {test_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", f"tests.{test_file.replace('.py', '')}"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            self.results["stress_tests"][test_file] = {
                "status": "PASSED" if success else "FAILED",
                "returncode": result.returncode,
                "output": result.stdout[-2000:] if result.stdout else ""
            }
            
            print(f"  Status: {'✓ PASSED' if success else '✗ FAILED'}")
            if "Average" in (result.stdout or ""):
                print("  Performance metrics extracted")
        except subprocess.TimeoutExpired:
            self.results["stress_tests"][test_file] = {
                "status": "TIMEOUT"
            }
            print(f"  Status: ✗ TIMEOUT")
        except Exception as e:
            self.results["stress_tests"][test_file] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  Status: ✗ ERROR: {e}")
    
    def run_security_tests(self):
        """Run security tests."""
        print("\n" + "="*70)
        print("RUNNING SECURITY TESTS")
        print("="*70)
        
        test_file = "test_security.py"
        print(f"\nRunning {test_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", f"tests.{test_file.replace('.py', '')}"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            self.results["security_tests"][test_file] = {
                "status": "PASSED" if success else "FAILED",
                "returncode": result.returncode
            }
            
            print(f"  Status: {'✓ PASSED' if success else '✗ FAILED'}")
        except subprocess.TimeoutExpired:
            self.results["security_tests"][test_file] = {
                "status": "TIMEOUT"
            }
            print(f"  Status: ✗ TIMEOUT")
        except Exception as e:
            self.results["security_tests"][test_file] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  Status: ✗ ERROR: {e}")
    
    def run_docker_validation(self):
        """Run Docker validation tests."""
        print("\n" + "="*70)
        print("RUNNING DOCKER VALIDATION TESTS")
        print("="*70)
        
        test_file = "test_docker_validation.py"
        print(f"\nRunning {test_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", f"tests.{test_file.replace('.py', '')}"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            self.results["docker_validation"][test_file] = {
                "status": "PASSED" if success else "FAILED",
                "returncode": result.returncode
            }
            
            print(f"  Status: {'✓ PASSED' if success else '✗ FAILED'}")
        except subprocess.TimeoutExpired:
            self.results["docker_validation"][test_file] = {
                "status": "TIMEOUT"
            }
            print(f"  Status: ✗ TIMEOUT")
        except Exception as e:
            self.results["docker_validation"][test_file] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  Status: ✗ ERROR: {e}")
    
    def validate_file_structure(self):
        """Validate project file structure."""
        print("\n" + "="*70)
        print("VALIDATING PROJECT STRUCTURE")
        print("="*70)
        
        required_files = [
            ("backend/Dockerfile", "Backend Dockerfile"),
            ("frontend/Dockerfile", "Frontend Dockerfile"),
            ("docker-compose.yml", "Docker Compose"),
            ("backend/requirements.txt", "Backend requirements"),
            ("frontend/package.json", "Frontend package.json"),
            (".env", "Environment configuration"),
            (".git", "Git repository"),
        ]
        
        structure_valid = True
        for file_path, description in required_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {description}: {file_path}")
            if not exists:
                structure_valid = False
        
        self.results["summary"]["structure_valid"] = structure_valid
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70)
        
        total_tests = sum(1 for category in self.results.values() 
                         for test in category.values() 
                         if isinstance(test, dict) and "status" in test)
        
        passed = sum(1 for category in self.results.values() 
                    for test in category.values() 
                    if isinstance(test, dict) and test.get("status") == "PASSED")
        
        failed = sum(1 for category in self.results.values() 
                    for test in category.values() 
                    if isinstance(test, dict) and test.get("status") == "FAILED")
        
        errors = sum(1 for category in self.results.values() 
                    for test in category.values() 
                    if isinstance(test, dict) and test.get("status") == "ERROR")
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "elapsed_seconds": elapsed,
            "success_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A"
        }
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Errors: {errors} ⚠")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        print(f"Total Time: {elapsed:.2f}s")
    
    def run_all_tests(self):
        """Execute all test suites."""
        print("\n" + "="*70)
        print("PHASE 4: TESTING INTEGRAL")
        print("Guitar Classification Platform - Comprehensive Testing Suite")
        print("="*70)
        
        self.validate_file_structure()
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_stress_tests()
        self.run_security_tests()
        self.run_docker_validation()
        self.generate_summary()
        
        return self.results


if __name__ == "__main__":
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Save results to JSON
    output_file = runner.project_root / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Test results saved to: {output_file}")
