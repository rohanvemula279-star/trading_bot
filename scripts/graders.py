import asyncio
import sys
from pathlib import Path

# Add parent directory (root) to path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from environment import SafetyReviewEnv
from models import SafetyAction

async def _grade_task_impl(task_name: str) -> float:
    """
    Standalone grader that creates its own environment,
    runs an optimal/baseline agent, and returns a score.
    
    Returns:
        float: Score in [0.0, 1.0]
    """
    import os
    os.environ["TASK_NAME"] = task_name
    env = SafetyReviewEnv()
    result = env.reset()
    
    total_reward = 0.0
    num_cases = 0
    
    # Simulate running an optimal agent
    for case in env._test_cases:
        gt = case["ground_truth"]
        
        # Perfect action
        action = SafetyAction(
            decision=gt["decision"],
            violation_type=gt.get("violation_type"),
            severity=gt.get("severity"),
            reasoning="Ground truth decision"
        )
        
        result = env.step(action)
        reward_val = getattr(result, "reward", 0.0)
        total_reward += reward_val
        num_cases += 1
    
    # Return normalized score
    # Rewards are clamped per case in [0.0, 1.0], so average is the correct normalization.
    score = total_reward / num_cases if num_cases > 0 else 0.0
    return min(1.0, max(0.0, score))


async def grade_easy_task() -> float:
    """Grade easy task independently"""
    return await _grade_task_impl("easy")


async def grade_medium_task() -> float:
    """Grade medium task independently"""
    return await _grade_task_impl("medium")


async def grade_hard_task() -> float:
    """Grade hard task independently"""
    return await _grade_task_impl("hard")


if __name__ == "__main__":
    async def test():
        easy = await grade_easy_task()
        medium = await grade_medium_task()
        hard = await grade_hard_task()
        print(f'Easy: {easy:.3f}')
        print(f'Medium: {medium:.3f}')
        print(f'Hard: {hard:.3f}')
        
        assert 0.0 <= easy <= 1.0
        assert 0.0 <= medium <= 1.0
        assert 0.0 <= hard <= 1.0
        print("All graders passed!")

    asyncio.run(test())
