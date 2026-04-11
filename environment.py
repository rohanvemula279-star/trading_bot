"""Root-level import proxy for src.environment"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Re-export the environment class
from src.environment import SafetyReviewEnv

__all__ = ["SafetyReviewEnv"]
