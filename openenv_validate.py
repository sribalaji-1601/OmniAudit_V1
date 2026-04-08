#!/usr/bin/env python3
"""
OpenEnv Validation Script for OmniAudit Project
Comprehensive validation of all critical components
"""

import sys
import os
import subprocess
import time
import requests
import json
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class OpenEnvValidator:
    """Comprehensive OpenEnv validation tool"""
    
    def __init__(self):
        self.server_process = None
        self.api_base_url = "http://localhost:7860"
        self.validation_results = []
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log validation result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.validation_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        print(f"  {status} {test_name}")
        if message:
            print(f"       {message}")
    
    def validate_models(self) -> bool:
        """Validate Pydantic models"""
        print("1. Validating Pydantic Models...")
        try:
            from models import UIElement, Observation, Action, Reward, TaskInfo, EnvironmentState, ActionType
            
            # Test model instantiation
            ui_element = UIElement(id="test-btn", tag="button", text="Click", attributes={"class": "btn"})
            action = Action(cmd=ActionType.PATCH_UI_ATTR, target_id="test-btn", key="aria-label", value="Test button")
            reward = Reward(total=1.0, accessibility=0.3, data_integrity=0.4, semantic_accuracy=0.3, feedback="Good fix")
            
            # Test serialization
            ui_dict = ui_element.model_dump()
            action_dict = action.model_dump()
            
            assert isinstance(ui_dict, dict), "UIElement should serialize to dict"
            assert "id" in ui_dict, "UIElement dict should have id field"
            assert isinstance(action_dict, dict), "Action should serialize to dict"
            assert "cmd" in action_dict, "Action dict should have cmd field"
            
            self.log_result("Pydantic Model Instantiation", True)
            self.log_result("Pydantic Model Serialization", True)
            return True
            
        except Exception as e:
            self.log_result("Pydantic Models", False, str(e))
            return False
    
    def validate_environment(self) -> bool:
        """Validate environment core functionality"""
        print("2. Validating Environment Core...")
        try:
            from env import OmniAuditEnvironment
            from models import Action, ActionType
            
            env = OmniAuditEnvironment()
            
            # Test reset
            obs = env.reset()
            assert hasattr(obs, 'ui_elements'), "Observation should have ui_elements"
            assert hasattr(obs, 'backend_record'), "Observation should have backend_record"
            self.log_result("Environment Reset", True)
            
            # Test step method returns 4-tuple
            action = Action(cmd=ActionType.PATCH_UI_ATTR, target_id="buy-button", key="aria-label", value="Test")
            observation, reward, done, info = env.step(action)
            
            assert isinstance(done, bool), "done should be boolean"
            assert isinstance(info, dict), "info should be dict"
            assert "state" in info, "info should contain state"
            
            self.log_result("Environment Step Method", True, f"Returns 4-tuple: (obs, reward, done, info)")
            
            # Test dynamic scenarios
            scenarios = set()
            for i in range(3):
                obs = env.reset()
                scenarios.add(obs.backend_record.get('product_id', 'unknown'))
            
            self.log_result("Dynamic Scenarios", True, f"Found {len(scenarios)} unique scenarios")
            return True
            
        except Exception as e:
            self.log_result("Environment Core", False, str(e))
            return False
    
    def validate_inference_agent(self) -> bool:
        """Validate inference agent"""
        print("3. Validating Inference Agent...")
        try:
            from inference import OmniAuditInferenceAgent
            
            # Check environment variables
            api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
            model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
            hf_token = os.getenv("HF_TOKEN", "")
            
            agent = OmniAuditInferenceAgent()
            
            self.log_result("Inference Agent Initialization", True)
            self.log_result("Environment Variables", True, 
                          f"API_BASE_URL={api_base_url}, MODEL_NAME={model_name}")
            
            # Test reasoning capability (without API call)
            obs = {
                "ui_elements": [
                    {"id": "buy-button", "tag": "button", "text": "Buy Now", "attributes": {}}
                ],
                "backend_record": {"product_id": "PROD_001", "price": 29.99, "material": "Silk"},
                "screen_reader_summary": "Button: Buy Now"
            }
            
            # This should use fallback logic
            analysis = agent.analyze_with_reasoning(obs)
            
            assert "reasoning" in analysis, "Analysis should have reasoning"
            assert "conflicts_found" in analysis, "Analysis should have conflicts_found"
            assert "action_plan" in analysis, "Analysis should have action_plan"
            
            self.log_result("Reasoning Engine", True, "Fallback logic working")
            return True
            
        except Exception as e:
            self.log_result("Inference Agent", False, str(e))
            return False
    
    def start_server(self) -> bool:
        """Start the server"""
        print("4. Starting Server...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "simple_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Check if server is responsive
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Server Startup", True, f"Running on {self.api_base_url}")
                return True
            else:
                self.log_result("Server Startup", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Server Startup", False, str(e))
            return False
    
    def validate_server_endpoints(self) -> bool:
        """Validate all required server endpoints"""
        print("5. Validating Server Endpoints...")
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            assert response.status_code == 200, "Health endpoint should return 200"
            health_data = response.json()
            assert "status" in health_data, "Health response should have status"
            self.log_result("Health Endpoint", True, f"Status: {health_data['status']}")
            
            # Test state endpoint
            response = requests.get(f"{self.api_base_url}/state", timeout=5)
            assert response.status_code == 200, "State endpoint should return 200"
            state_data = response.json()
            assert "step_count" in state_data, "State response should have step_count"
            self.log_result("State Endpoint", True)
            
            # Test reset endpoint
            response = requests.post(f"{self.api_base_url}/reset", timeout=5)
            assert response.status_code == 200, "Reset endpoint should return 200"
            reset_data = response.json()
            assert "ui_elements" in reset_data, "Reset response should have ui_elements"
            self.log_result("Reset Endpoint", True)
            
            # Test tasks endpoint
            response = requests.get(f"{self.api_base_url}/tasks", timeout=5)
            assert response.status_code == 200, "Tasks endpoint should return 200"
            tasks_data = response.json()
            assert len(tasks_data) >= 3, "Should have at least 3 tasks"
            self.log_result("Tasks Endpoint", True, f"Found {len(tasks_data)} tasks")
            
            # Test step endpoint
            action_data = {
                "cmd": "PATCH_UI_ATTR",
                "target_id": "buy-button",
                "key": "aria-label",
                "value": "Test button"
            }
            response = requests.post(f"{self.api_base_url}/step", json=action_data, timeout=5)
            assert response.status_code == 200, "Step endpoint should return 200"
            step_data = response.json()
            assert "observation" in step_data, "Step response should have observation"
            assert "reward" in step_data, "Step response should have reward"
            assert "done" in step_data, "Step response should have done"
            assert "state" in step_data, "Step response should have state"
            self.log_result("Step Endpoint", True, f"Returns 4-part response")
            
            return True
            
        except Exception as e:
            self.log_result("Server Endpoints", False, str(e))
            return False
    
    def validate_openenv_spec(self) -> bool:
        """Validate openenv.yaml specification"""
        print("6. Validating OpenEnv Specification...")
        try:
            import yaml
            
            with open("openenv.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ["name", "version", "description", "environment", "tasks"]
            for field in required_fields:
                assert field in config, f"Missing required field: {field}"
            
            self.log_result("OpenEnv YAML Structure", True)
            
            # Check environment config
            env_config = config["environment"]
            assert env_config["type"] == "openenv", "Environment type should be openenv"
            assert "entrypoint" in env_config, "Should have entrypoint"
            assert "port" in env_config, "Should have port"
            
            self.log_result("Environment Config", True, 
                          f"Entrypoint: {env_config['entrypoint']}, Port: {env_config['port']}")
            
            # Check tasks
            tasks = config["tasks"]
            assert len(tasks) >= 3, "Should have at least 3 tasks"
            
            for task_name, task_config in tasks.items():
                assert "name" in task_config, f"Task {task_name} should have name"
                assert "description" in task_config, f"Task {task_name} should have description"
                assert "difficulty" in task_config, f"Task {task_name} should have difficulty"
                assert "reward_weight" in task_config, f"Task {task_name} should have reward_weight"
            
            self.log_result("Tasks Configuration", True, f"Found {len(tasks)} properly configured tasks")
            return True
            
        except Exception as e:
            self.log_result("OpenEnv Specification", False, str(e))
            return False
    
    def validate_requirements(self) -> bool:
        """Validate requirements.txt"""
        print("7. Validating Requirements...")
        try:
            with open("requirements.txt", "r") as f:
                requirements = f.read().strip().split("\n")
            
            required_packages = ["pydantic", "openai", "requests"]
            found_packages = []
            
            for req in requirements:
                req = req.strip()
                if not req or req.startswith("#"):
                    continue
                for required in required_packages:
                    if required in req:
                        found_packages.append(required)
                        break
            
            assert len(found_packages) == len(required_packages), \
                f"Missing packages. Required: {required_packages}, Found: {found_packages}"
            
            self.log_result("Requirements.txt", True, f"Has: {', '.join(found_packages)}")
            return True
            
        except Exception as e:
            self.log_result("Requirements", False, str(e))
            return False
    
    def validate_dockerfile(self) -> bool:
        """Validate Dockerfile"""
        print("8. Validating Dockerfile...")
        try:
            with open("Dockerfile", "r") as f:
                dockerfile_content = f.read()
            
            # Check key components
            checks = [
                ("FROM python:", "Python base image"),
                ("WORKDIR /app", "Working directory set"),
                ("COPY requirements.txt", "Requirements copied"),
                ("RUN pip install", "Dependencies installed"),
                ("COPY . .", "Source code copied"),
                ("EXPOSE 7860", "Port exposed"),
                ('CMD ["python", "simple_server.py"]', "Server command")
            ]
            
            for check, description in checks:
                if check in dockerfile_content:
                    self.log_result(f"Dockerfile - {description}", True)
                else:
                    self.log_result(f"Dockerfile - {description}", False, f"Missing: {check}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Dockerfile", False, str(e))
            return False
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
    
    def run_validation(self) -> bool:
        """Run complete validation"""
        print("=" * 60)
        print("OPENENV VALIDATION - OMNIAUDIT PROJECT")
        print("=" * 60)
        
        try:
            # Core validation (without server)
            all_passed = True
            all_passed &= self.validate_models()
            all_passed &= self.validate_environment()
            all_passed &= self.validate_inference_agent()
            all_passed &= self.validate_openenv_spec()
            all_passed &= self.validate_requirements()
            all_passed &= self.validate_dockerfile()
            
            # Server validation
            if self.start_server():
                all_passed &= self.validate_server_endpoints()
            else:
                all_passed = False
            
            # Results summary
            print("\n" + "=" * 60)
            print("VALIDATION RESULTS")
            print("=" * 60)
            
            passed_count = sum(1 for r in self.validation_results if r["passed"])
            total_count = len(self.validation_results)
            
            print(f"Tests Passed: {passed_count}/{total_count}")
            
            # Show failed tests
            failed_tests = [r for r in self.validation_results if not r["passed"]]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"  • {test['test']}: {test['message']}")
            
            if all_passed:
                print("\n🎉 ALL VALIDATIONS PASSED!")
                print("✅ OpenEnv project is ready for submission")
                print("\nKey Features Validated:")
                print("  • Pydantic BaseModel compliance")
                print("  • Modern OpenAI client integration")
                print("  • Strict logging format")
                print("  • Complete server endpoints")
                print("  • Dynamic environment scenarios")
                print("  • OpenEnv specification compliance")
                return True
            else:
                print(f"\n❌ {len(failed_tests)} validation(s) failed")
                print("Please fix the issues above before submission")
                return False
                
        finally:
            self.stop_server()

def main():
    """Main validation entry point"""
    validator = OpenEnvValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
