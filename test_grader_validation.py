#!/usr/bin/env python
"""
Platform Grader Validation Test
================================
Simulates exactly what the hackathon platform validator does:
1. Parses openenv.yaml
2. For each task, resolves the grader using module:function format
3. Calls the grader and checks the score is strictly in (0, 1)
4. Counts tasks with valid graders (needs >= 3)

Run:
    python test_grader_validation.py
"""

import importlib
import sys
from pathlib import Path

# Ensure we're running from the project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def resolve_grader(grader_string: str):
    """
    Resolve a grader string in module:function format.
    This is how the hackathon platform resolves graders.

    Examples:
        "graders:grade_easy_task" -> graders.grade_easy_task
        "tasks.easy.grader:grade" -> tasks.easy.grader.grade
    """
    if ":" not in grader_string:
        print(f"  ERROR: Grader string '{grader_string}' does not use colon-separated format")
        print(f"         Expected format: 'module:function' (e.g., 'graders:grade_easy_task')")
        print(f"         Got dot-separated format which the platform CANNOT parse!")
        return None

    module_path, func_name = grader_string.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"  ERROR: Cannot import module '{module_path}': {e}")
        return None

    if not hasattr(module, func_name):
        print(f"  ERROR: Module '{module_path}' has no function '{func_name}'")
        return None

    func = getattr(module, func_name)
    if not callable(func):
        print(f"  ERROR: '{module_path}.{func_name}' is not callable")
        return None

    return func


def main():
    print("=" * 70)
    print("HACKATHON PLATFORM GRADER VALIDATION SIMULATOR")
    print("=" * 70)

    # ── Step 1: Parse openenv.yaml ──────────────────────────────────────
    print("\n[1] Parsing openenv.yaml...")
    yaml_path = project_root / "openenv.yaml"
    if not yaml_path.exists():
        print("FAIL: openenv.yaml not found!")
        sys.exit(1)

    with open(yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print("FAIL: openenv.yaml is not a valid dictionary")
        sys.exit(1)

    print("  OK: openenv.yaml parsed successfully")

    # ── Step 2: Check tasks exist ───────────────────────────────────────
    print("\n[2] Checking tasks...")
    tasks = config.get("tasks", [])
    if not isinstance(tasks, list):
        print("FAIL: 'tasks' is not a list")
        sys.exit(1)

    print(f"  Found {len(tasks)} task(s)")

    if len(tasks) < 3:
        print(f"FAIL: Need at least 3 tasks, found {len(tasks)}")
        sys.exit(1)

    # ── Step 3: Validate each task has required fields ──────────────────
    print("\n[3] Validating task fields...")
    required_fields = ["id", "name", "description", "difficulty", "grader"]
    all_valid = True

    for i, task in enumerate(tasks):
        task_id = task.get("id", f"task_{i}")
        missing = [f for f in required_fields if f not in task]
        if missing:
            print(f"  FAIL: Task '{task_id}' missing fields: {missing}")
            all_valid = False
        else:
            print(f"  OK: Task '{task_id}' has all required fields")

    if not all_valid:
        print("FAIL: Some tasks have missing fields")
        sys.exit(1)

    # ── Step 4: Resolve graders (THE CRITICAL CHECK) ────────────────────
    print("\n[4] Resolving graders (module:function format)...")
    tasks_with_graders = 0
    grader_results = {}

    for task in tasks:
        task_id = task["id"]
        grader_str = task["grader"]
        print(f"\n  Task '{task_id}': grader = '{grader_str}'")

        # Check format uses colon
        if ":" not in grader_str:
            print(f"    FAIL: No colon found in grader string!")
            print(f"    The platform expects 'module:function' format")
            print(f"    Currently: '{grader_str}' (dot-only format)")
            grader_results[task_id] = {"resolved": False, "reason": "no colon in format"}
            continue

        grader_func = resolve_grader(grader_str)
        if grader_func is None:
            grader_results[task_id] = {"resolved": False, "reason": "import/resolve failed"}
            continue

        print(f"    OK: Resolved to {grader_func.__module__}.{grader_func.__name__}")

        # Call the grader
        try:
            score = grader_func()
            print(f"    OK: Grader returned score = {score}")
        except Exception as e:
            print(f"    FAIL: Grader crashed: {e}")
            grader_results[task_id] = {"resolved": False, "reason": f"crash: {e}"}
            continue

        # Validate score type
        if not isinstance(score, (int, float)):
            print(f"    FAIL: Score is {type(score).__name__}, expected float")
            grader_results[task_id] = {"resolved": False, "reason": f"bad type: {type(score).__name__}"}
            continue

        # Validate score range: strictly between 0 and 1
        if score <= 0.0 or score >= 1.0:
            print(f"    FAIL: Score {score} is NOT strictly in (0, 1)")
            print(f"    The platform REJECTS scores of exactly 0.0 or 1.0")
            grader_results[task_id] = {"resolved": False, "reason": f"score {score} out of range"}
            continue

        print(f"    OK: Score {score} is strictly in (0, 1)")
        grader_results[task_id] = {"resolved": True, "score": score}
        tasks_with_graders += 1

    # ── Step 5: Check top-level graders map ─────────────────────────────
    print("\n\n[5] Checking top-level 'graders' map...")
    graders_map = config.get("graders", {})
    if isinstance(graders_map, dict) and len(graders_map) >= 3:
        print(f"  OK: Found {len(graders_map)} grader entries in top-level map")
        for key, val in graders_map.items():
            if ":" in str(val):
                print(f"    OK: graders.{key} = '{val}' (colon format)")
            else:
                print(f"    WARN: graders.{key} = '{val}' (missing colon!)")
    else:
        print(f"  WARN: Top-level graders map has {len(graders_map)} entries (need 3+)")

    # ── Step 6: Check environment_class format ──────────────────────────
    print("\n[6] Checking environment_class format...")
    env_class = config.get("environment_class", "")
    if ":" in env_class:
        print(f"  OK: environment_class = '{env_class}' (colon format)")
    elif env_class:
        print(f"  WARN: environment_class = '{env_class}' (may need colon format)")
    else:
        print(f"  WARN: environment_class not specified")

    # ── Step 7: Verify environment imports work ─────────────────────────
    print("\n[7] Verifying environment and models import...")
    try:
        from environment import SafetyReviewEnv
        print("  OK: SafetyReviewEnv imported")
    except Exception as e:
        print(f"  FAIL: Cannot import SafetyReviewEnv: {e}")

    try:
        from models import SafetyAction, SafetyObservation, SafetyState
        print("  OK: SafetyAction, SafetyObservation, SafetyState imported")
    except Exception as e:
        print(f"  FAIL: Cannot import models: {e}")

    # ── Step 8: Quick environment test ──────────────────────────────────
    print("\n[8] Quick environment smoke test...")
    try:
        env = SafetyReviewEnv(task="easy")
        obs = env.reset()
        print(f"  OK: reset() returned observation")
        print(f"      reward = {obs.reward} (strictly in (0,1): {0.0 < obs.reward < 1.0})")
        print(f"      average_score = {obs.metadata.get('average_score')} (strictly in (0,1): {0.0 < obs.metadata.get('average_score', 0) < 1.0})")

        action = SafetyAction(decision="APPROVE", reasoning="Test", violation_type=None, severity=None)
        obs2 = env.step(action)
        print(f"  OK: step() returned observation")
        print(f"      reward = {obs2.reward} (strictly in (0,1): {0.0 < obs2.reward < 1.0})")
    except Exception as e:
        print(f"  FAIL: Environment error: {e}")

    # ── FINAL VERDICT ───────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print(f"\nTasks with valid graders: {tasks_with_graders} / {len(tasks)}")
    print(f"Required minimum: 3")

    for task_id, result in grader_results.items():
        status = "PASS" if result.get("resolved") else "FAIL"
        detail = f"score={result.get('score', 'N/A')}" if result.get("resolved") else result.get("reason", "unknown")
        print(f"  [{status}] {task_id}: {detail}")

    print()
    if tasks_with_graders >= 3:
        print("[PASS] At least 3 tasks have valid graders!")
        print("   Your submission should pass the 'tasks with graders' check.")
        sys.exit(0)
    else:
        print("[FAIL] Not enough tasks with graders!")
        print(f"   Only {tasks_with_graders} task(s) have valid graders, need 3+")
        print()
        print("   Common fixes:")
        print("   1. Use colon format: 'graders:grade_easy_task' (NOT 'graders.grade_easy_task')")
        print("   2. Ensure graders.py is importable from the project root")
        print("   3. Ensure grader functions return float strictly in (0, 1)")
        sys.exit(1)


if __name__ == "__main__":
    main()
