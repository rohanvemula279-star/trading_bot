"""
Test harness. Run this to measure your actual success rate.
If it's not 90%+, the RL optimizer will learn from failures and improve.
"""

import time
import json
from agent import PowerAgent
from agent_core import TaskStatus


TEST_SUITE = [
    # ── Code Writing ──
    {
        "task": "Write a Python function that checks if a string is a palindrome. Return just the function.",
        "type": "code_write",
        "validate": lambda r: "def " in str(r.output) and "palindrome" in str(r.output).lower(),
    },
    {
        "task": "Write a Python function to find the nth Fibonacci number using memoization.",
        "type": "code_write",
        "validate": lambda r: "def " in str(r.output) and ("memo" in str(r.output).lower() or "cache" in str(r.output).lower() or "dict" in str(r.output).lower()),
    },
    {
        "task": "Write a Python class called Stack with push, pop, peek, and is_empty methods.",
        "type": "code_write",
        "validate": lambda r: "class Stack" in str(r.output) and "push" in str(r.output),
    },

    # ── Analysis ──
    {
        "task": "Explain what a deadlock is in operating systems in 2-3 sentences.",
        "type": "analysis",
        "validate": lambda r: len(str(r.output)) > 50 and any(w in str(r.output).lower() for w in ["process", "resource", "wait", "lock"]),
    },
    {
        "task": "What is the time complexity of binary search and why?",
        "type": "analysis",
        "validate": lambda r: "log" in str(r.output).lower() and ("n" in str(r.output).lower()),
    },

    # ── Data ──
    {
        "task": "Parse this JSON and tell me all the names: {\"users\": [{\"name\": \"Alice\", \"age\": 30}, {\"name\": \"Bob\", \"age\": 25}]}",
        "type": "data",
        "validate": lambda r: "Alice" in str(r.output) and "Bob" in str(r.output),
    },
    {
        "task": "Calculate the mean of these numbers: 10, 20, 30, 40, 50",
        "type": "data",
        "validate": lambda r: "30" in str(r.output),
    },

    # ── Code Debug ──
    {
        "task": """Fix this Python code:
def add_numbers(a, b):
    return a + c
        
It should add a and b.""",
        "type": "code_debug",
        "validate": lambda r: "return a + b" in str(r.output) or ("a" in str(r.output) and "b" in str(r.output) and "c" not in str(r.output).replace("func", "")),
    },

    # ── Planning ──
    {
        "task": "Design a simple REST API for a todo list app. List the endpoints.",
        "type": "planning",
        "validate": lambda r: any(method in str(r.output).upper() for method in ["GET", "POST", "DELETE", "PUT"]) and "todo" in str(r.output).lower(),
    },

    # ── General ──
    {
        "task": "Convert 100 Celsius to Fahrenheit.",
        "type": "general",
        "validate": lambda r: "212" in str(r.output),
    },
    {
        "task": "What is 17 * 23?",
        "type": "general",
        "validate": lambda r: "391" in str(r.output),
    },
    {
        "task": "List 5 sorting algorithms.",
        "type": "general",
        "validate": lambda r: sum(1 for alg in ["bubble", "merge", "quick", "insertion", "selection", "heap", "radix", "bucket", "tim", "shell", "counting"] if alg in str(r.output).lower()) >= 4,
    },

    # ── Harder tasks ──
    {
        "task": "Write a Python decorator that retries a function up to 3 times if it raises an exception.",
        "type": "code_write",
        "validate": lambda r: "def " in str(r.output) and ("retry" in str(r.output).lower() or "wrapper" in str(r.output).lower()) and "except" in str(r.output),
    },
    {
        "task": "Explain the difference between TCP and UDP in a table format.",
        "type": "analysis",
        "validate": lambda r: "TCP" in str(r.output) and "UDP" in str(r.output) and len(str(r.output)) > 100,
    },
    {
        "task": "Write a SQL query to find the top 5 customers by total order amount from tables 'customers' and 'orders'.",
        "type": "code_write",
        "validate": lambda r: "SELECT" in str(r.output).upper() and ("JOIN" in str(r.output).upper() or "join" in str(r.output)),
    },
]


def run_tests(num_rounds: int = 1):
    """Run full test suite and report results."""
    agent = PowerAgent()

    all_results = []

    for round_num in range(1, num_rounds + 1):
        print(f"\n{'='*60}")
        print(f"  TEST ROUND {round_num}/{num_rounds}")
        print(f"{'='*60}\n")

        round_results = []

        for i, test in enumerate(TEST_SUITE, 1):
            print(f"  [{i}/{len(TEST_SUITE)}] {test['task'][:60]}...")

            start = time.time()
            result = agent.run(test["task"])
            elapsed = time.time() - start

            # Validate
            try:
                passed = (
                    result.status == TaskStatus.SUCCESS
                    and test["validate"](result)
                )
            except Exception:
                passed = False

            status_icon = "✅" if passed else "❌"
            print(f"  {status_icon}  [{elapsed:.1f}s] confidence={result.confidence:.2f}")
            if not passed:
                output_preview = str(result.output)[:100] if result.output else result.error[:100]
                print(f"      Output: {output_preview}")

            round_results.append({
                "task": test["task"][:80],
                "type": test["type"],
                "passed": passed,
                "confidence": result.confidence,
                "attempts": result.attempts,
                "latency": elapsed,
            })

        all_results.extend(round_results)

        # Round summary
        passed_count = sum(1 for r in round_results if r["passed"])
        total = len(round_results)
        rate = (passed_count / total) * 100

        print(f"\n  Round {round_num} Result: {passed_count}/{total} = {rate:.1f}%")

    # Final summary
    total_passed = sum(1 for r in all_results if r["passed"])
    total_tests = len(all_results)
    overall_rate = (total_passed / total_tests) * 100

    print(f"\n{'='*60}")
    print(f"  FINAL RESULT: {total_passed}/{total_tests} = {overall_rate:.1f}%")
    print(f"{'='*60}")

    # Per-type breakdown
    from collections import defaultdict
    by_type = defaultdict(lambda: {"passed": 0, "total": 0})
    for r in all_results:
        by_type[r["type"]]["total"] += 1
        if r["passed"]:
            by_type[r["type"]]["passed"] += 1

    print("\n  By task type:")
    for tt, stats in sorted(by_type.items()):
        type_rate = (stats["passed"] / stats["total"]) * 100
        bar = "█" * int(type_rate / 5) + "░" * (20 - int(type_rate / 5))
        print(f"    {tt:15s} {bar} {type_rate:5.1f}% ({stats['passed']}/{stats['total']})")

    # RL report
    print("\n  RL Optimizer Report:")
    report = agent.optimizer.get_report()
    print(json.dumps(report, indent=4))

    # Save results
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "overall_rate": overall_rate,
            "results": all_results,
            "rl_report": report,
        }, f, indent=2)
    print("\n  Results saved to test_results.json")

    return overall_rate


if __name__ == "__main__":
    import sys
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rate = run_tests(num_rounds=rounds)

    if rate >= 90:
        print("\n🎉 TARGET ACHIEVED: 90%+ success rate!")
    else:
        print(f"\n⚡ Current: {rate:.1f}%. Run more rounds to let RL optimize.")
        print("   python test_agent.py 5    # Run 5 rounds for RL learning")
