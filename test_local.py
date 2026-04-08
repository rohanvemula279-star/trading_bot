"""
Run this locally to verify everything works before deploying.
    python test_local.py
"""

import json
from environment import TradingEnvironment
from agent import TradingAgent
from risk_manager import RiskManager
from grader import grade_performance


def run_test(task_id: str, seed: int = 42):
    env = TradingEnvironment()
    agent = TradingAgent()
    risk = RiskManager()

    print(f"\n{'='*60}")
    print(f"  TASK: {task_id}")
    print(f"{'='*60}")

    obs = env.reset(task_id, seed=seed)
    print(f"  Initial cash   : ${obs['portfolio']['cash']:,.2f}")
    print(f"  Stocks         : {list(obs['market'].keys())}")
    print(f"  Trading days   : {obs['total_steps']}")
    print()

    step = 0
    total_reward = 0

    while not env.done:
        state = env.get_state()
        actions = agent.decide(state)
        actions = risk.filter_actions(actions, state, env.equity_curve)
        obs, reward, done, info = env.step(actions)
        total_reward += reward
        step += 1

        # Print key actions
        for stock, act in actions.items():
            if act["type"] != "HOLD":
                p = state["market"][stock]["price"]
                print(f"  Day {step:3d} | {stock:6s} | {act['type']:4s} "
                      f"{act.get('shares',''):>5} @ ${p:>8.2f} | "
                      f"Portfolio: ${obs['portfolio']['total_value']:>12,.2f}")

    # Final metrics
    metrics = env.get_metrics()
    result = grade_performance(metrics)

    print(f"\n  {'-'*50}")
    print(f"  Final equity   : ${metrics['final_equity']:>12,.2f}")
    print(f"  Total return   : {metrics['total_return']:>+8.2f}%")
    print(f"  Buy & hold     : {metrics['buy_hold_return']:>+8.2f}%")
    print(f"  Alpha          : {metrics['alpha']:>+8.2f}%")
    print(f"  Max drawdown   : {metrics['max_drawdown']:>8.2f}%")
    print(f"  Sharpe ratio   : {metrics['sharpe_ratio']:>8.2f}")
    print(f"  Win rate       : {metrics['win_rate']:>8.1f}%")
    print(f"  Profit factor  : {metrics['profit_factor']:>8.2f}")
    print(f"  Total trades   : {metrics['total_trades']}")
    print(f"  {'-'*50}")
    print(f"  SCORE          : {result['score']:.4f}")
    print(f"  Breakdown      : {json.dumps(result['breakdown'], indent=4)}")
    print()

    return result["score"]


if __name__ == "__main__":
    scores = []
    for task in ["easy_task", "medium_task", "hard_task"]:
        # Run with multiple seeds for robustness
        task_scores = []
        for seed in [42, 123, 777, 2024, 9999]:
            s = run_test(task, seed=seed)
            task_scores.append(s)
        avg = sum(task_scores) / len(task_scores)
        print(f"  >>> {task} average across 5 seeds: {avg:.4f}")
        scores.append(avg)

    overall = sum(scores) / len(scores)
    print(f"\n{'='*60}")
    print(f"  OVERALL AVERAGE SCORE: {overall:.4f}")
    print(f"{'='*60}")
