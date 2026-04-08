"""
Pre-Submission Validation Suite for AI Safety Review Environment
================================================================

Validates all hackathon requirements before HuggingFace deployment.

Usage:
    python validate_submission.py
    
Returns:
    Exit code 0 if all checks pass, non-zero otherwise
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class ValidationResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, check: str, details: str = ""):
        self.passed.append((check, details))
        print(f"{GREEN}✅ PASS{RESET}: {check}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, check: str, details: str = ""):
        self.failed.append((check, details))
        print(f"{RED}❌ FAIL{RESET}: {check}")
        if details:
            print(f"   {details}")
    
    def add_warning(self, check: str, details: str = ""):
        self.warnings.append((check, details))
        print(f"{YELLOW}⚠️  WARN{RESET}: {check}")
        if details:
            print(f"   {details}")
    
    def print_summary(self):
        print("\n" + "="*70)
        print(f"{BOLD}VALIDATION SUMMARY{RESET}")
        print("="*70)
        print(f"{GREEN}Passed:{RESET} {len(self.passed)}")
        print(f"{RED}Failed:{RESET} {len(self.failed)}")
        print(f"{YELLOW}Warnings:{RESET} {len(self.warnings)}")
        
        if self.failed:
            print(f"\n{RED}{BOLD}CRITICAL FAILURES:{RESET}")
            for check, details in self.failed:
                print(f"  • {check}")
                if details:
                    print(f"    {details}")
        
        if self.warnings:
            print(f"\n{YELLOW}{BOLD}WARNINGS:{RESET}")
            for check, details in self.warnings:
                print(f"  • {check}")
        
        print("\n" + "="*70)
        if not self.failed:
            print(f"{GREEN}{BOLD}🎉 ALL CRITICAL CHECKS PASSED! READY TO DEPLOY!{RESET}")
        else:
            print(f"{RED}{BOLD}❌ FIX FAILURES BEFORE DEPLOYING{RESET}")
        print("="*70 + "\n")
        
        return len(self.failed) == 0


def check_file_structure(result: ValidationResult):
    """Check required files exist in correct locations"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}1. FILE STRUCTURE CHECK{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    required_files = {
        "server.py": "FastAPI server (must be in root)",
        "inference.py": "Baseline inference script (must be in root)",
        "environment.py": "Environment implementation",
        "models.py": "Pydantic models",
        "graders.py": "Task graders",
        "openenv.yaml": "OpenEnv configuration",
        "Dockerfile": "Docker configuration",
        "requirements.txt": "Python dependencies",
        "README.md": "Documentation",
    }
    
    for file, description in required_files.items():
        if Path(file).exists():
            result.add_pass(f"Found {file}", description)
        else:
            result.add_fail(f"Missing {file}", f"Required: {description}")
    
    # Check test data
    test_data_dir = Path("test_data")
    if test_data_dir.exists():
        test_cases = ["easy_cases.json", "medium_cases.json", "hard_cases.json"]
        for case_file in test_cases:
            case_path = test_data_dir / case_file
            if case_path.exists():
                with open(case_path) as f:
                    data = json.load(f)
                    result.add_pass(f"Found {case_file}", f"{len(data)} test cases")
            else:
                result.add_fail(f"Missing {case_file}", "Required for grading")
    else:
        result.add_fail("Missing test_data/ directory", "Required for test cases")
    
    # Check for .dockerignore and .gitignore
    if Path(".dockerignore").exists():
        result.add_pass("Found .dockerignore")
    else:
        result.add_warning("Missing .dockerignore", "Recommended to reduce image size")
    
    if Path(".gitignore").exists():
        result.add_pass("Found .gitignore")
    else:
        result.add_warning("Missing .gitignore", "Recommended for clean repo")


def check_openenv_yaml(result: ValidationResult):
    """Validate openenv.yaml structure"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}2. OPENENV.YAML VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    yaml_file = Path("openenv.yaml")
    if not yaml_file.exists():
        result.add_fail("openenv.yaml not found")
        return
    
    try:
        import yaml
        with open(yaml_file) as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ["name", "version", "description", "tasks", "observation_space", "action_space"]
        for field in required_fields:
            if field in config:
                result.add_pass(f"openenv.yaml has '{field}'")
            else:
                result.add_fail(f"openenv.yaml missing '{field}'")
        
        # Check tasks
        if "tasks" in config:
            tasks = config["tasks"]
            if len(tasks) >= 3:
                result.add_pass(f"Found {len(tasks)} tasks", "Requirement: 3+ tasks")
                
                # Check each task has required fields
                task_fields = ["id", "name", "description", "difficulty"]
                for task in tasks:
                    task_id = task.get("id", "unknown")
                    for field in task_fields:
                        if field not in task:
                            result.add_fail(f"Task '{task_id}' missing '{field}'")
            else:
                result.add_fail("Insufficient tasks", f"Found {len(tasks)}, need 3+")
        
        # Check graders are defined
        if "graders" in config:
            result.add_pass("Graders defined in openenv.yaml")
        else:
            result.add_warning("Graders not defined in openenv.yaml", "May need to add grader references")
    
    except Exception as e:
        result.add_fail("Failed to parse openenv.yaml", str(e))


def check_dockerfile(result: ValidationResult):
    """Validate Dockerfile"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}3. DOCKERFILE VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        result.add_fail("Dockerfile not found")
        return
    
    with open(dockerfile) as f:
        content = f.read()
    
    # Check for port 7860
    if "7860" in content:
        result.add_pass("Dockerfile uses port 7860", "Required for HuggingFace Spaces")
    else:
        result.add_fail("Dockerfile doesn't expose port 7860", "Change to port 7860")
    
    # Check for required commands
    checks = [
        ("FROM python:", "Base image specified"),
        ("COPY requirements.txt", "Dependencies copied"),
        ("pip install", "Dependencies installed"),
        ("COPY . .", "Application files copied"),
        ("CMD", "Startup command defined"),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            result.add_pass(f"Dockerfile: {description}")
        else:
            result.add_warning(f"Dockerfile may be missing: {description}")
    
    # Check if it specifies server.py
    if "server.py" in content:
        result.add_pass("Dockerfile runs server.py")
    else:
        result.add_warning("Dockerfile doesn't explicitly reference server.py")


def check_requirements_txt(result: ValidationResult):
    """Validate requirements.txt"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}4. REQUIREMENTS.TXT VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        result.add_fail("requirements.txt not found")
        return
    
    with open(req_file) as f:
        requirements = f.read()
    
    # Check for required packages
    required_packages = {
        "openenv": "OpenEnv core framework",
        "fastapi": "Web framework",
        "uvicorn": "ASGI server",
        "pydantic": "Data validation",
        "openai": "LLM client",
    }
    
    for package, description in required_packages.items():
        if package in requirements.lower():
            result.add_pass(f"Found dependency: {package}", description)
        else:
            result.add_fail(f"Missing dependency: {package}", description)


def check_inference_script(result: ValidationResult):
    """Validate inference.py compliance"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}5. INFERENCE.PY VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    inf_file = Path("inference.py")
    if not inf_file.exists():
        result.add_fail("inference.py not found")
        return
    
    with open(inf_file) as f:
        content = f.read()
    
    # Check for required imports
    required_imports = [
        ("from openai import OpenAI", "OpenAI client"),
        ("import asyncio", "Async support"),
    ]
    
    for import_stmt, description in required_imports:
        if import_stmt in content:
            result.add_pass(f"Has import: {description}")
        else:
            result.add_fail(f"Missing import: {import_stmt}")
    
    # Check for environment variables
    env_vars = ["API_BASE_URL", "MODEL_NAME", "HF_TOKEN"]
    for var in env_vars:
        if var in content:
            result.add_pass(f"Uses environment variable: {var}")
        else:
            result.add_fail(f"Missing environment variable: {var}")
    
    # Check for required logging functions
    log_functions = ["log_start", "log_step", "log_end"]
    for func in log_functions:
        if f"def {func}" in content or f"{func}(" in content:
            result.add_pass(f"Has logging function: {func}")
        else:
            result.add_fail(f"Missing logging function: {func}")
    
    # Check logging format
    if "[START]" in content and "[STEP]" in content and "[END]" in content:
        result.add_pass("Uses required log format: [START], [STEP], [END]")
    else:
        result.add_fail("Missing required log markers", "Must use [START], [STEP], [END]")
    
    # Check for score normalization to [0, 1]
    if "score" in content.lower():
        result.add_pass("Script calculates score")
    else:
        result.add_warning("May not calculate final score")


async def check_graders(result: ValidationResult):
    """Test that graders work and return valid scores"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}6. GRADER VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    try:
        # Import graders
        sys.path.insert(0, str(Path.cwd()))
        from graders import grade_easy_task, grade_medium_task, grade_hard_task
        
        graders = [
            ("easy", grade_easy_task),
            ("medium", grade_medium_task),
            ("hard", grade_hard_task),
        ]
        
        for task_name, grader_func in graders:
            try:
                print(f"\n{BLUE}Testing {task_name} grader...{RESET}")
                start_time = time.time()
                score = await grader_func()
                elapsed = time.time() - start_time
                
                # Validate score is float in [0, 1]
                if isinstance(score, (int, float)):
                    if 0.0 <= score <= 1.0:
                        result.add_pass(
                            f"Grader '{task_name}' works",
                            f"Score: {score:.3f}, Time: {elapsed:.2f}s"
                        )
                    else:
                        result.add_fail(
                            f"Grader '{task_name}' score out of range",
                            f"Score: {score} (must be in [0.0, 1.0])"
                        )
                else:
                    result.add_fail(
                        f"Grader '{task_name}' returns invalid type",
                        f"Got {type(score)}, expected float"
                    )
            except Exception as e:
                result.add_fail(f"Grader '{task_name}' crashed", str(e))
        
    except ImportError as e:
        result.add_fail("Cannot import graders.py", str(e))


async def check_environment_basics(result: ValidationResult):
    """Test basic environment functionality"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}7. ENVIRONMENT BASIC FUNCTIONALITY{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    try:
        from environment import SafetyReviewEnv
        from models import SafetyAction
        
        # Test environment instantiation
        env = SafetyReviewEnv(task="easy")
        result.add_pass("Environment instantiation", "SafetyReviewEnv created")
        
        # Test reset
        reset_result = env.reset()
        result.add_pass("Environment reset()", "Returns observation")
        
        # Validate observation
        if hasattr(reset_result, 'model_output'):
            result.add_pass("Reset returns observation")
        else:
            result.add_fail("Reset missing observation")
        
        # Test step
        test_action = SafetyAction(
            decision="APPROVE",
            violation_type=None,
            severity=None,
            reasoning="Test action"
        )
        
        step_result = env.step(test_action)
        result.add_pass("Environment step()", "Accepts action")
        
        # Validate reward
        if hasattr(step_result, 'reward'):
            reward_total = step_result.reward
            if 0.0 <= reward_total <= 1.0:
                result.add_pass("Reward in valid range", f"{reward_total:.3f}")
            else:
                result.add_fail("Reward out of range", f"{reward_total}")
        else:
            result.add_fail("Step missing reward")
        
        # Test state
        state = env.state
        result.add_pass("Environment state", "Returns current state")
        
    except Exception as e:
        result.add_fail("Environment basic functionality failed", str(e))


def check_docker_build(result: ValidationResult):
    """Test Docker build"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}8. DOCKER BUILD TEST{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    try:
        print(f"{BLUE}Building Docker image (this may take 2-3 minutes)...{RESET}")
        
        process = subprocess.run(
            ["docker", "build", "-t", "ai-safety-review-test", "."],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if process.returncode == 0:
            result.add_pass("Docker build successful")
            
            # Check image size
            size_check = subprocess.run(
                ["docker", "images", "ai-safety-review-test", "--format", "{{.Size}}"],
                capture_output=True,
                text=True
            )
            if size_check.returncode == 0:
                size = size_check.stdout.strip()
                result.add_pass(f"Docker image created", f"Size: {size}")
        else:
            result.add_fail("Docker build failed", process.stderr[-500:])
    
    except subprocess.TimeoutExpired:
        result.add_fail("Docker build timed out", "Build took > 10 minutes")
    except FileNotFoundError:
        result.add_warning("Docker not found", "Install Docker to test builds")
    except Exception as e:
        result.add_fail("Docker build error", str(e))


def check_inference_execution(result: ValidationResult):
    """Test inference.py runs without errors"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}9. INFERENCE SCRIPT EXECUTION TEST{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    # Set minimal environment variables for testing
    env_vars = os.environ.copy()
    env_vars["SAFETY_TASK"] = "easy"
    env_vars["MODEL_NAME"] = "Qwen/Qwen2.5-72B-Instruct"
    env_vars["API_BASE_URL"] = "https://router.huggingface.co/v1"
    # Don't set HF_TOKEN for this test - script should handle missing token gracefully
    
    print(f"{YELLOW}Note: This test runs inference.py but may fail LLM calls without HF_TOKEN{RESET}")
    print(f"{YELLOW}We're checking that the script structure is correct{RESET}\n")
    
    try:
        # Run with timeout
        process = subprocess.run(
            ["python", "inference.py"],
            capture_output=True,
            text=True,
            timeout=60,
            env=env_vars
        )
        
        output = process.stdout
        
        # Check for required log markers
        has_start = "[START]" in output
        has_step = "[STEP]" in output
        has_end = "[END]" in output
        
        if has_start:
            result.add_pass("Inference outputs [START]")
        else:
            result.add_fail("Inference missing [START] log")
        
        if has_step:
            result.add_pass("Inference outputs [STEP]")
        else:
            result.add_warning("Inference missing [STEP] logs", "May need LLM token")
        
        if has_end:
            result.add_pass("Inference outputs [END]")
        else:
            result.add_fail("Inference missing [END] log")
        
        # Parse final score from [END] line
        end_match = re.search(r'\[END\].*score=([\d.]+)', output)
        if end_match:
            score = float(end_match.group(1))
            if 0.0 <= score <= 1.0:
                result.add_pass("Inference score valid", f"Score: {score:.3f}")
            else:
                result.add_fail("Inference score out of range", f"Score: {score}")
        
        # Check log format compliance
        step_lines = re.findall(r'\[STEP\].*', output)
        if step_lines:
            # Validate format of first step line
            first_step = step_lines[0]
            required_fields = ["step=", "action=", "reward=", "done=", "error="]
            missing_fields = [f for f in required_fields if f not in first_step]
            
            if not missing_fields:
                result.add_pass("Log format compliant", "All required fields present")
            else:
                result.add_fail("Log format incorrect", f"Missing: {missing_fields}")
    
    except subprocess.TimeoutExpired:
        result.add_fail("Inference script timed out", "Exceeded 60s test timeout")
    except Exception as e:
        result.add_fail("Inference script error", str(e))


async def check_determinism(result: ValidationResult):
    """Test deterministic behavior"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}10. DETERMINISM CHECK{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    print(f"{YELLOW}Testing environment determinism (running 3 times)...{RESET}\n")
    
    try:
        async def run_env_episode():
            from environment import SafetyReviewEnv
            from models import SafetyAction
            
            env = SafetyReviewEnv(task="easy")
            res = env.reset()
            
            rewards = []
            for _ in range(5):  # Run 5 steps
                if res.done:
                    break
                
                # Use ground truth action (perfect agent)
                case = env.state.current_case
                gt = case["ground_truth"]
                
                action = SafetyAction(
                    decision=gt["decision"],
                    violation_type=gt.get("violation_type"),
                    severity=gt.get("severity"),
                    reasoning="Determinism test"
                )
                
                res = env.step(action)
                rewards.append(res.reward)
            
            return rewards
        
        # Run 3 times
        run1 = await run_env_episode()
        run2 = await run_env_episode()
        run3 = await run_env_episode()
        
        if run1 == run2 == run3:
            result.add_pass("Environment is deterministic", "3 identical runs")
        else:
            result.add_fail("Environment is NOT deterministic", "Runs produced different results")
            print(f"   Run 1: {run1}")
            print(f"   Run 2: {run2}")
            print(f"   Run 3: {run3}")
    
    except Exception as e:
        result.add_fail("Determinism check failed", str(e))


async def main():
    """Run all validation checks"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}AI SAFETY REVIEW ENVIRONMENT - PRE-SUBMISSION VALIDATION{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    
    result = ValidationResult()
    
    # Run all checks
    check_file_structure(result)
    check_openenv_yaml(result)
    check_dockerfile(result)
    check_requirements_txt(result)
    check_inference_script(result)
    
    # Async checks
    await check_graders(result)
    await check_environment_basics(result)
    await check_determinism(result)
    
    # Docker check (can be slow)
    docker_test = input(f"\n{YELLOW}Run Docker build test? This takes 2-3 minutes. (y/n): {RESET}")
    if docker_test.lower() == 'y':
        check_docker_build(result)
    else:
        result.add_warning("Skipped Docker build test", "Run manually before deploying")
    
    # Inference check (may need API token)
    inference_test = input(f"\n{YELLOW}Run inference.py test? (y/n): {RESET}")
    if inference_test.lower() == 'y':
        check_inference_execution(result)
    else:
        result.add_warning("Skipped inference test", "Run manually with HF_TOKEN set")
    
    # Print summary
    success = result.print_summary()
    
    # Save report
    report_file = Path("validation_report.txt")
    with open(report_file, "w") as f:
        f.write("AI Safety Review Environment - Validation Report\n")
        f.write("="*70 + "\n\n")
        f.write(f"Passed: {len(result.passed)}\n")
        f.write(f"Failed: {len(result.failed)}\n")
        f.write(f"Warnings: {len(result.warnings)}\n\n")
        
        if result.failed:
            f.write("FAILURES:\n")
            for check, details in result.failed:
                f.write(f"  - {check}\n")
                if details:
                    f.write(f"    {details}\n")
        
        if result.warnings:
            f.write("\nWARNINGS:\n")
            for check, details in result.warnings:
                f.write(f"  - {check}\n")
                if details:
                    f.write(f"    {details}\n")
    
    print(f"\n{BLUE}Validation report saved to: {report_file}{RESET}\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
