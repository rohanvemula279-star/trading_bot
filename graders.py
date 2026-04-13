"""Root-level import proxy for scripts.graders"""
from scripts.graders import (
    grade_easy_task, grade_medium_task, grade_hard_task,
    grade_spam_task, grade_toxicity_task, grade_pii_task
)

__all__ = [
    "grade_easy_task", "grade_medium_task", "grade_hard_task",
    "grade_spam_task", "grade_toxicity_task", "grade_pii_task"
]
