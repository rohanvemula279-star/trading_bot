"""Root-level import proxy for src.models"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Re-export all model classes
from src.models import SafetyAction, SafetyObservation, SafetyState

__all__ = ["SafetyAction", "SafetyObservation", "SafetyState"]
