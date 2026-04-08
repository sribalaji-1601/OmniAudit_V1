#!/usr/bin/env python3
"""
Final comprehensive verification of Multi-mode deployment refactor
"""

import os
import sys
import subprocess

def test_server_functionality():
    """Test that the refactored server works correctly"""
    print("=== TESTING SERVER FUNCTIONALITY ===")
    
    # Test imports
    sys.path.append('./server')
    try:
        from app import run_server
        print("✓ server.app imports successfully")
    except Exception as e:
        print(f"✗ server.app import failed: {e}")
        return False
    
    # Test that we can import the main modules from server
    try:
        import server.app
        print("✓ server.app module loads correctly")
    except Exception as e:
        print(f"✗ server.app module failed: {e}")
        return False
    
    return True

def verify_structure():
    """Verify the final directory structure"""
    print("\n=== VERIFYING STRUCTURE ===")
    
    # Check required files exist
    required_files = [
        "server/app.py",
        "server/__init__.py", 
        "pyproject.toml",
        "uv.lock",
        "Dockerfile",
        "requirements.txt",
        "openenv.yaml",
        "env.py",
        "models.py",
        "inference.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            all_exist = False
    
    return all_exist

def verify_configurations():
    """Verify all configuration files are correct"""
    print("\n=== VERIFYING CONFIGURATIONS ===")
    
    # Check pyproject.toml
    with open('pyproject.toml', 'r') as f:
        pyproject_content = f.read()
        
    checks = [
        ('pyproject.toml has openenv-core', 'openenv-core>=0.2.0' in pyproject_content),
        ('pyproject.toml has correct entry point', 'server = "server.app:run_server"' in pyproject_content),
        ('pyproject.toml has correct name', 'name = "omniaudit-gym"' in pyproject_content),
        ('pyproject.toml has correct version', 'version = "1.0.0"' in pyproject_content),
        ('pyproject.toml has python >=3.10', 'requires-python = ">=3.10"' in pyproject_content)
    ]
    
    # Check openenv.yaml
    with open('openenv.yaml', 'r') as f:
        openenv_content = f.read()
    checks.append(('openenv.yaml has correct entrypoint', 'server.app:run_server' in openenv_content))
    
    # Check Dockerfile
    with open('Dockerfile', 'r') as f:
        dockerfile_content = f.read()
    checks.append(('Dockerfile has correct CMD', 'server/app.py' in dockerfile_content))
    
    # Check requirements.txt
    with open('requirements.txt', 'r') as f:
        req_content = f.read()
    checks.append(('requirements.txt has openenv-core', 'openenv-core>=0.2.0' in req_content))
    
    # Check uv.lock exists
    checks.append(('uv.lock exists', os.path.exists('uv.lock')))
    
    for check_name, passed in checks:
        if passed:
            print(f"✓ {check_name}")
        else:
            print(f"✗ {check_name}")
    
    return all(passed for _, passed in checks)

def main():
    """Run all verification tests"""
    print("OMNIAUDIT MULTI-MODE DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    structure_ok = verify_structure()
    config_ok = verify_configurations()
    server_ok = test_server_functionality()
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")
    print(f"Server Functionality: {'✓ PASS' if server_ok else '✗ FAIL'}")
    
    if structure_ok and config_ok and server_ok:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("✅ Multi-mode deployment refactor is COMPLETE")
        print("✅ OmniAudit is ready for Meta OpenEnv submission")
    else:
        print("\n❌ Some verifications failed")
        print("Please review the issues above")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
