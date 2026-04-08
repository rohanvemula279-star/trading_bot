#!/usr/bin/env python
"""
Pre-deployment validation for OpenEnv Hackathon Round 1
============================================================

This script validates your environment before submission.
All checks must pass!

Usage:
    python validate_deployment.py

Exit codes:
    0 = All checks passed ✅
    1 = Some checks failed ❌
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

try:
    import yaml
except ImportError:
    print("❌ PyYAML not found. Install it: pip install pyyaml")
    sys.exit(1)


class ValidationReport:
    def __init__(self):
        self.sections: Dict[str, Tuple[bool, List[str]]] = {}
        self.all_passed = True
    
    def add_section(self, name: str, passed: bool, messages: List[str]):
        self.sections[name] = (passed, messages)
        if not passed:
            self.all_passed = False
    
    def print_report(self):
        print("\n" + "="*70)
        print("🔍 OpenEnv Hackathon Pre-Deployment Validation Report")
        print("="*70)
        
        for section_name, (passed, messages) in self.sections.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status} | {section_name}")
            for msg in messages:
                print(f"       {msg}")
        
        print("\n" + "="*70)
        if self.all_passed:
            print("✅ ALL CHECKS PASSED - Ready for deployment!")
        else:
            print("❌ SOME CHECKS FAILED - Fix issues above before deploying")
        print("="*70 + "\n")
        
        return 0 if self.all_passed else 1


def check_openenv_yaml() -> Tuple[bool, List[str]]:
    """Check openenv.yaml structure and required fields"""
    errors = []
    
    if not Path("openenv.yaml").exists():
        return False, ["openenv.yaml not found in root directory"]
    
    try:
        with open("openenv.yaml", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {str(e)[:100]}"]
    
    if not isinstance(config, dict):
        return False, ["openenv.yaml must contain a dictionary"]
    
    # Required top-level fields
    required_fields = {
        "name": str,
        "version": (str, float),
        "description": str,
        "observation_space": dict,
        "action_space": dict,
        "tasks": list,
        "graders": dict,
    }
    
    for field, expected_type in required_fields.items():
        if field not in config:
            errors.append(f"Missing required field: {field}")
        else:
            if isinstance(expected_type, tuple):
                if not isinstance(config[field], expected_type):
                    errors.append(f"{field} has wrong type (expected {expected_type})")
            else:
                if not isinstance(config[field], expected_type):
                    errors.append(f"{field} has wrong type (expected {expected_type.__name__})")
    
    # Check spaces have type and module
    if "observation_space" in config:
        if "type" not in config["observation_space"]:
            errors.append("observation_space missing 'type' field")
        if "module" not in config["observation_space"]:
            errors.append("observation_space missing 'module' field")
    
    if "action_space" in config:
        if "type" not in config["action_space"]:
            errors.append("action_space missing 'type' field")
        if "module" not in config["action_space"]:
            errors.append("action_space missing 'module' field")
    
    # Check reward_range
    if "reward_range" in config:
        r = config["reward_range"]
        if not (isinstance(r, list) and len(r) == 2 and r[0] == 0.0 and r[1] == 1.0):
            errors.append("reward_range must be [0.0, 1.0]")
    else:
        errors.append("reward_range not specified (should be [0.0, 1.0])")
    
    # Check tasks
    if "tasks" in config:
        tasks = config["tasks"]
        if not isinstance(tasks, list) or len(tasks) == 0:
            errors.append("tasks must be a non-empty list")
        else:
            task_ids = [t.get("id") for t in tasks if isinstance(t, dict)]
            required_difficulties = {"easy", "medium", "hard"}
            found_difficulties = set([t.get("difficulty") for t in tasks if isinstance(t, dict)])
            
            if not required_difficulties.issubset(found_difficulties):
                errors.append(f"Must have all difficulty levels: {required_difficulties}")
            else:
                for diff in ["easy", "medium", "hard"]:
                    task = next((t for t in tasks if t.get("difficulty") == diff), None)
                    if task:
                        if "max_steps" not in task or not isinstance(task["max_steps"], int):
                            errors.append(f"{diff} task missing or invalid max_steps")
    
    # Check graders
    if "graders" in config:
        graders = config["graders"]
        required_graders = {"easy", "medium", "hard"}
        found_graders = set(graders.keys())
        if not required_graders.issubset(found_graders):
            errors.append(f"graders must have: {required_graders}")
    
    if not errors:
        errors.append("✓ All required fields present and valid")
        return True, errors
    return False, errors


def check_typed_models() -> Tuple[bool, List[str]]:
    """Verify typed dataclasses exist"""
    errors = []
    
    if not Path("models.py").exists():
        return False, ["models.py not found"]
    
    try:
        # Try importing the models
        import importlib.util
        spec = importlib.util.spec_from_file_location("models", "models.py")
        models_module = importlib.util.module_from_spec(spec)
        sys.modules["models"] = models_module
        spec.loader.exec_module(models_module)
        
        required_classes = ["SafetyAction", "SafetyObservation", "SafetyState"]
        for cls_name in required_classes:
            if hasattr(models_module, cls_name):
                errors.append(f"✓ {cls_name} defined")
            else:
                errors.append(f"Missing class: {cls_name}")
    
    except Exception as e:
        return False, [f"Error loading models.py: {str(e)[:100]}"]
    
    has_all = all("✓" in msg for msg in errors)
    return has_all, errors


def check_graders_implementation() -> Tuple[bool, List[str]]:
    """Verify grader functions exist"""
    errors = []
    
    if not Path("graders.py").exists():
        return False, ["graders.py not found"]
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("graders", "graders.py")
        graders_module = importlib.util.module_from_spec(spec)
        sys.modules["graders"] = graders_module
        spec.loader.exec_module(graders_module)
        
        required_functions = [
            "grade_easy_task",
            "grade_medium_task",
            "grade_hard_task",
        ]
        
        for func_name in required_functions:
            if hasattr(graders_module, func_name):
                func = getattr(graders_module, func_name)
                if callable(func):
                    errors.append(f"✓ {func_name} is callable")
                else:
                    errors.append(f"{func_name} exists but is not callable")
            else:
                errors.append(f"Missing function: {func_name}")
    
    except Exception as e:
        return False, [f"Error loading graders.py: {str(e)[:100]}"]
    
    has_all = all("✓" in msg for msg in errors)
    return has_all, errors


def check_dockerfile() -> Tuple[bool, List[str]]:
    """Validate Dockerfile"""
    errors = []
    
    if not Path("Dockerfile").exists():
        return False, ["Dockerfile not found in root"]
    
    with open("Dockerfile", encoding="utf-8") as f:
        content = f.read()
    
    # Check Python version
    if "python:3.1" in content:
        errors.append("✓ Python 3.10+ base image")
    else:
        errors.append("⚠ May not use Python 3.10+ (check FROM line)")
    
    # Check port
    if "7860" in content or "PORT" in content:
        errors.append("✓ Port configuration present")
    else:
        errors.append("⚠ Port 7860 not explicitly set (may fail on HF Spaces)")
    
    # Check requirements
    if "requirements.txt" in content:
        errors.append("✓ requirements.txt copied")
    else:
        errors.append("❌ requirements.txt not mentioned")
    
    # Check working directory
    if "WORKDIR" in content:
        errors.append("✓ WORKDIR set")
    else:
        errors.append("⚠ No WORKDIR set")
    
    has_critical = not any("❌" in e for e in errors)
    return has_critical, errors


def check_inference_script() -> Tuple[bool, List[str]]:
    """Validate inference.py format compliance"""
    errors = []
    
    if not Path("inference.py").exists():
        return False, ["inference.py not found in root directory"]
    
    with open("inference.py", encoding="utf-8") as f:
        content = f.read()
    
    # Check format tokens (CRITICAL)
    format_checks = [
        ("([START]", "[START] format token"),
        ("([STEP]", "[STEP] format token"),
        ("([END]", "[END] format token"),
    ]
    
    for token, desc in format_checks:
        if token.split("(")[1] in content:
            errors.append(f"✓ {desc} present")
        else:
            errors.append(f"❌ Missing {desc}")
    
    # Check environment variables
    env_checks = [
        ("API_BASE_URL", "API_BASE_URL env var"),
        ("MODEL_NAME", "MODEL_NAME env var"),
        ("HF_TOKEN", "HF_TOKEN env var"),
        ("OpenAI", "OpenAI client"),
    ]
    
    for pattern, desc in env_checks:
        if pattern in content:
            errors.append(f"✓ {desc}")
        else:
            errors.append(f"⚠ {desc} not found")
    
    has_critical = all("❌" not in e for e in errors)
    return has_critical, errors


def check_readme() -> Tuple[bool, List[str]]:
    """Validate README documentation"""
    errors = []
    
    if not Path("README.md").exists():
        return False, ["README.md not found"]
    
    with open("README.md", encoding="utf-8") as f:
        content = f.read().lower()
    
    sections = [
        ("environment", "Environment description"),
        ("action", "Action space documentation"),
        ("observation", "Observation space documentation"),
        ("task", "Task descriptions"),
        ("setup", "Setup instructions"),
        ("example", "Usage example or demo"),
    ]
    
    for keyword, desc in sections:
        if keyword in content:
            errors.append(f"✓ {desc}")
        else:
            errors.append(f"⚠ {desc} may be missing")
    
    return True, errors


def check_requirements_files() -> Tuple[bool, List[str]]:
    """Check requirements.txt files"""
    errors = []
    
    if not Path("requirements.txt").exists():
        return False, ["requirements.txt not found in root"]
    
    with open("requirements.txt", encoding="utf-8") as f:
        root_reqs = f.read()
    
    if "openenv" in root_reqs.lower():
        errors.append("✓ openenv-core in root requirements.txt")
    else:
        errors.append("⚠ openenv-core may be missing from root requirements.txt")
    
    if Path("server/requirements.txt").exists():
        with open("server/requirements.txt", encoding="utf-8") as f:
            server_reqs = f.read()
        
        if "openenv" in server_reqs.lower():
            errors.append("✓ openenv-core in server/requirements.txt")
        elif "fastapi" in server_reqs.lower():
            errors.append("✓ server/requirements.txt exists with dependencies")
        else:
            errors.append("⚠ server/requirements.txt may be incomplete")
    else:
        errors.append("⚠ server/requirements.txt not found")
    
    return True, errors


def check_environment_structure() -> Tuple[bool, List[str]]:
    """Verify directory structure"""
    errors = []
    
    required_dirs = [
        ("server", "Server directory"),
        ("test_data", "Test data directory (optional)"),
    ]
    
    for dir_name, desc in required_dirs:
        if Path(dir_name).exists():
            errors.append(f"✓ {desc} present")
        else:
            if "optional" in desc.lower():
                errors.append(f"⚠ {desc} not present (optional)")
            else:
                errors.append(f"❌ {desc} missing")
    
    # Check server files
    server_files = ["app.py", "requirements.txt"]
    for file in server_files:
        if Path(f"server/{file}").exists():
            errors.append(f"✓ server/{file} present")
        else:
            errors.append(f"⚠ server/{file} may be missing")
    
    return True, errors


def main():
    report = ValidationReport()
    
    # Run all checks
    print("\n🔄 Running validation checks...\n")
    
    report.add_section(
        "1️⃣  OpenEnv YAML (openenv.yaml)",
        *check_openenv_yaml()
    )
    
    report.add_section(
        "2️⃣  Typed Models (models.py)",
        *check_typed_models()
    )
    
    report.add_section(
        "3️⃣  Graders (graders.py)",
        *check_graders_implementation()
    )
    
    report.add_section(
        "4️⃣  Dockerfile",
        *check_dockerfile()
    )
    
    report.add_section(
        "5️⃣  Inference Script (inference.py)",
        *check_inference_script()
    )
    
    report.add_section(
        "6️⃣  README Documentation",
        *check_readme()
    )
    
    report.add_section(
        "7️⃣  Requirements Files",
        *check_requirements_files()
    )
    
    report.add_section(
        "8️⃣  Directory Structure",
        *check_environment_structure()
    )
    
    # Print and return exit code
    exit_code = report.print_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
