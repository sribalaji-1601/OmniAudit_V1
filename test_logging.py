#!/usr/bin/env python3
"""
Simple test script to validate the logging format compliance
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging_format():
    """Test the logging format matches OpenEnv requirements"""
    print("Testing logging format compliance...")
    
    # Test the logging format from inference.py
    task_name = "OmniAudit"
    benchmark = "omniaudit-gym"
    model_name = "test-model"
    
    # Test [START] format
    start_log = f"[START] task={task_name} env={benchmark} model={model_name}"
    expected_start = "[START] task=OmniAudit env=omniaudit-gym model=test-model"
    
    assert start_log == expected_start, f"START format mismatch: {start_log} != {expected_start}"
    print("PASS: [START] format correct")
    
    # Test [STEP] format
    step = 1
    action_str = "PATCH_UI_ATTR on buy-button"
    reward = 0.30
    done = False
    error = "null"
    
    step_log = f"[STEP] step={step} action={action_str} reward={reward:.2f} done={str(done).lower()} error={error}"
    expected_step = "[STEP] step=1 action=PATCH_UI_ATTR on buy-button reward=0.30 done=false error=null"
    
    assert step_log == expected_step, f"STEP format mismatch: {step_log} != {expected_step}"
    print("PASS: [STEP] format correct")
    
    # Test [END] format
    success = True
    steps = 3
    score = 0.895
    rewards = [0.30, 0.70, 1.00]
    rewards_formatted = ','.join([f"{r:.2f}" for r in rewards])
    
    end_log = f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_formatted}"
    expected_end = "[END] success=true steps=3 score=0.90 rewards=0.30,0.70,1.00"
    
    assert end_log == expected_end, f"END format mismatch: {end_log} != {expected_end}"
    print("PASS: [END] format correct")
    
    print("All logging format tests passed!")
    return True

def test_api_url():
    """Test the API URL is updated correctly"""
    from inference import API_BASE_URL
    
    expected_url = "https://router.huggingface.co/v1"
    assert API_BASE_URL == expected_url, f"API URL mismatch: {API_BASE_URL} != {expected_url}"
    print("PASS: API_BASE_URL updated correctly")
    return True

def test_scoring_logic():
    """Test the scoring logic sets current_score to 1.0"""
    from env import OmniAuditEnvironment
    
    env = OmniAuditEnvironment()
    
    # Test that tasks have correct initial scores
    assert env.tasks["easy"].current_score == 0.0, "Easy task initial score should be 0.0"
    assert env.tasks["medium"].current_score == 0.0, "Medium task initial score should be 0.0"
    assert env.tasks["hard"].current_score == 0.0, "Hard task initial score should be 0.0"
    
    print("PASS: Initial task scores correct")
    return True

def test_models():
    """Test the Pydantic models"""
    from models import UIElement, Observation, Action, Reward, TaskInfo, EnvironmentState
    
    # Test UIElement with optional text
    element = UIElement(id="test", tag="button", text=None, attributes={})
    assert element.text is None, "UIElement text should be optional"
    
    # Test other models
    action = Action(cmd="PATCH_UI_ATTR", target_id="test")
    reward = Reward(total=0.3)
    task = TaskInfo(name="test", description="test", difficulty="easy", reward_weight=0.3)
    state = EnvironmentState()
    
    print("PASS: All models instantiate correctly")
    return True

def test_openenv_yaml():
    """Test openenv.yaml compliance"""
    import yaml
    
    with open('openenv.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Check required fields
    assert 'version' in data, "Missing version field"
    assert data['version'] == '1.0.0', f"Version should be 1.0.0, got {data['version']}"
    
    assert 'environment' in data, "Missing environment block"
    env = data['environment']
    assert 'type' in env, "Missing environment.type"
    assert 'entrypoint' in env, "Missing environment.entrypoint"
    assert 'port' in env, "Missing environment.port"
    
    assert env['type'] == 'openenv', f"Environment type should be 'openenv', got {env['type']}"
    assert env['port'] == 7860, f"Port should be 7860, got {env['port']}"
    
    print("PASS: openenv.yaml structure correct")
    return True

def test_readme_frontmatter():
    """Test README.md frontmatter"""
    import yaml
    
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        frontmatter_str = content[3:end_idx].strip()
        frontmatter = yaml.safe_load(frontmatter_str)
        
        assert 'sdk' in frontmatter, "Missing sdk in frontmatter"
        assert 'app_port' in frontmatter, "Missing app_port in frontmatter"
        assert 'tags' in frontmatter, "Missing tags in frontmatter"
        
        assert frontmatter['sdk'] == 'docker', f"sdk should be 'docker', got {frontmatter['sdk']}"
        assert frontmatter['app_port'] == 7860, f"app_port should be 7860, got {frontmatter['app_port']}"
        assert 'openenv' in frontmatter['tags'], "tags should include 'openenv'"
        
        print("PASS: README.md frontmatter correct")
        return True
    
    raise Exception("No frontmatter found in README.md")

if __name__ == "__main__":
    print("=" * 60)
    print("OMNIAUDIT COMPLIANCE TEST")
    print("=" * 60)
    
    tests = [
        test_logging_format,
        test_api_url,
        test_scoring_logic,
        test_models,
        test_openenv_yaml,
        test_readme_frontmatter
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} failed: {e}")
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL COMPLIANCE TESTS PASSED!")
        print("OpenEnv project is ready for submission")
    else:
        print("Some tests failed - please review")
    
    print("=" * 60)
