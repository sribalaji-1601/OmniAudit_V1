#!/usr/bin/env python3
"""
Quick OpenEnv Validation - Fast checks for core functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_validate():
    """Quick validation of critical components"""
    print("🔍 Quick OpenEnv Validation")
    print("=" * 40)
    
    try:
        # 1. Test models
        from models import UIElement, Action, ActionType
        ui = UIElement(id="test", tag="button", text="Test", attributes={})
        action = Action(cmd=ActionType.PATCH_UI_ATTR, target_id="test")
        print("✅ Pydantic models")
        
        # 2. Test environment
        from env import OmniAuditEnvironment
        env = OmniAuditEnvironment()
        obs = env.reset()
        obs, reward, done, info = env.step(action)
        print("✅ Environment core")
        
        # 3. Test inference
        from inference import OmniAuditInferenceAgent
        agent = OmniAuditInferenceAgent()
        print("✅ Inference agent")
        
        # 4. Test config files
        assert os.path.exists("openenv.yaml"), "openenv.yaml missing"
        assert os.path.exists("requirements.txt"), "requirements.txt missing"
        assert os.path.exists("Dockerfile"), "Dockerfile missing"
        assert os.path.exists("simple_server.py"), "simple_server.py missing"
        print("✅ Project files")
        
        # 5. Test environment variables
        api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        hf_token = os.getenv("HF_TOKEN", "")
        print(f"✅ Environment vars: API={api_base_url}, MODEL={model_name}")
        
        print("\n🎉 Quick validation PASSED!")
        print("Run 'python openenv_validate.py' for full validation")
        return True
        
    except Exception as e:
        print(f"❌ Quick validation FAILED: {e}")
        return False

if __name__ == "__main__":
    success = quick_validate()
    sys.exit(0 if success else 1)
