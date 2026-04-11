"""Root-level import proxy for scripts.graders"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add scripts to path
scripts_path = Path(__file__).parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Re-export all grader functions
from scripts.graders import grade_easy_task, grade_medium_task, grade_hard_task

__all__ = ["grade_easy_task", "grade_medium_task", "grade_hard_task"]
