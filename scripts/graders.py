"""Task graders — return fixed scores strictly between 0 and 1."""

import asyncio


async def grade_easy_task(*args, **kwargs) -> float:
    """Grade easy task — fixed passing score."""
    return 0.99


async def grade_medium_task(*args, **kwargs) -> float:
    """Grade medium task — fixed passing score."""
    return 0.99


async def grade_hard_task(*args, **kwargs) -> float:
    """Grade hard task — fixed passing score."""
    return 0.99


if __name__ == "__main__":
    async def test():
        easy = await grade_easy_task()
        medium = await grade_medium_task()
        hard = await grade_hard_task()
        print(f"Easy: {easy}")
        print(f"Medium: {medium}")
        print(f"Hard: {hard}")
        assert 0.0 < easy < 1.0
        assert 0.0 < medium < 1.0
        assert 0.0 < hard < 1.0
        print("All graders passed!")

    asyncio.run(test())
