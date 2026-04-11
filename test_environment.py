#!/usr/bin/env python3
"""
Environment Validation Script
Tests all imports, dependencies, and core functionality
"""

import sys
import os
import json
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*70)
    print("TEST 1: Checking imports...")
    print("="*70)
    
    tests = [
        ("environment", "SafetyReviewEnv", lambda: __import__('environment').SafetyReviewEnv),
        ("models", "SafetyAction", lambda: __import__('models').SafetyAction),
        ("models", "SafetyObservation", lambda: __import__('models').SafetyObservation),
        ("models", "SafetyState", lambda: __import__('models').SafetyState),
        ("graders", "grade_easy_task", lambda: __import__('graders').grade_easy_task),
        ("graders", "grade_medium_task", lambda: __import__('graders').grade_medium_task),
        ("graders", "grade_hard_task", lambda: __import__('graders').grade_hard_task),
    ]
    
    passed = 0
    failed = 0
    
    for module, name, import_func in tests:
        try:
            import_func()
            print(f"  [PASS] {module}.{name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {module}.{name}: {e}")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_test_data():
    """Check if test data files exist"""
    print("\n" + "="*70)
    print("TEST 2: Checking test data files...")
    print("="*70)
    
    test_files = [
        "src/test_data/easy_cases.json",
        "src/test_data/medium_cases.json",
        "src/test_data/hard_cases.json",
    ]
    
    passed = 0
    failed = 0
    
    for file_path in test_files:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    count = len(data)
                print(f"  [PASS] {file_path} ({count} cases)")
                passed += 1
            except Exception as e:
                print(f"  [FAIL] {file_path} (invalid JSON): {e}")
                failed += 1
        else:
            print(f"  [FAIL] {file_path} (not found)")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_environment_instantiation():
    """Test creating environment instances"""
    print("\n" + "="*70)
    print("TEST 3: Testing environment instantiation...")
    print("="*70)
    
    try:
        from environment import SafetyReviewEnv
        env = SafetyReviewEnv(task="easy")
        print(f"  [PASS] SafetyReviewEnv instantiated for 'easy' task")
        
        obs = env.reset()
        print(f"  [PASS] Environment reset successful")
        print(f"         - Episode ID: {obs.episode_id if hasattr(obs, 'episode_id') else 'N/A'}")
        print(f"         - Model output: {obs.model_output[:50]}..." if obs.model_output else "         - Model output: (empty)")
        
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Check if required packages are installed"""
    print("\n" + "="*70)
    print("TEST 4: Checking dependencies...")
    print("="*70)
    
    packages = [
        ("openenv-core", "openenv"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("openai", "openai"),
        ("python-dotenv", "dotenv"),
    ]
    
    passed = 0
    failed = 0
    
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"  [PASS] {package_name}")
            passed += 1
        except ImportError:
            print(f"  [FAIL] {package_name} not installed")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return failed == 0


def test_env_variables():
    """Check environment variables"""
    print("\n" + "="*70)
    print("TEST 5: Checking environment variables...")
    print("="*70)
    
    # Load .env if it exists
    from pathlib import Path
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"  [PASS] Loaded .env file")
    
    required_vars = ["API_BASE_URL", "MODEL_NAME"]
    passed = 0
    failed = 0
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your-{var.lower()}-here":
            print(f"  [PASS] {var} = {value[:30]}...")
            passed += 1
        else:
            print(f"  [WARN] {var} not set or using placeholder")
            failed += 0  # Warning, not failure
    
    print(f"\nResult: {passed} set properly")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AI SAFETY REVIEW ENVIRONMENT - VALIDATION SUITE")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Test Data Files", test_test_data()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Environment Vars", test_env_variables()))
    results.append(("Environment Instantiation", test_environment_instantiation()))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All environment tests PASSED!")
        print("\nYour environment is ready for the hackathon!")
        return 0
    else:
        print("\n✗ Some tests FAILED. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
