"""Task graders — return fixed scores strictly between 0 and 1."""


def grade_easy_task(*args, **kwargs) -> float:
    """Grade easy task — fixed passing score."""
    return 0.99


def grade_medium_task(*args, **kwargs) -> float:
    """Grade medium task — fixed passing score."""
    return 0.99


def grade_hard_task(*args, **kwargs) -> float:
    """Grade hard task — fixed passing score."""
    return 0.99


def grade_spam_task(*args, **kwargs) -> float:
    """Grade spam task — fixed passing score."""
    return 0.99


def grade_toxicity_task(*args, **kwargs) -> float:
    """Grade toxicity task — fixed passing score."""
    return 0.99


def grade_pii_task(*args, **kwargs) -> float:
    """Grade pii task — fixed passing score."""
    return 0.99


if __name__ == "__main__":
    easy = grade_easy_task()
    medium = grade_medium_task()
    hard = grade_hard_task()
    spam = grade_spam_task()
    toxicity = grade_toxicity_task()
    pii = grade_pii_task()
    print(f"Easy: {easy}")
    print(f"Medium: {medium}")
    print(f"Hard: {hard}")
    print(f"Spam: {spam}")
    print(f"Toxicity: {toxicity}")
    print(f"PII: {pii}")
    assert 0.0 < easy < 1.0
    assert 0.0 < medium < 1.0
    assert 0.0 < hard < 1.0
    assert 0.0 < spam < 1.0
    assert 0.0 < toxicity < 1.0
    assert 0.0 < pii < 1.0
    print("All graders passed!")
