"""Quick focused test: one seed per task, output to file."""
import json
from environment import TradingEnvironment
from agent import TradingAgent
from risk_manager import RiskManager
from grader import grade_performance


def run_one(task_id, seed=42):
    env = TradingEnvironment()
    agent = TradingAgent()
    risk_mgr = RiskManager()

    obs = env.reset(task_id, seed=seed)
    total_reward = 0.0

    while not env.done:
        state = env.get_state()
        actions = agent.decide(state)
        actions = risk_mgr.filter_actions(actions, state, env.equity_curve)
        obs, reward, done, info = env.step(actions)
        total_reward += reward

    metrics = env.get_metrics()
    result = grade_performance(metrics)
    return metrics, result


lines = []
all_scores = []
for task in ["easy_task", "medium_task", "hard_task"]:
    seed_scores = []
    for seed in [42, 123, 777, 2024, 9999]:
        m, r = run_one(task, seed)
        seed_scores.append(r["score"])

    avg = sum(seed_scores) / len(seed_scores)
    all_scores.append(avg)
    lines.append(f"{task:14s}  scores={[round(s,4) for s in seed_scores]}  avg={avg:.4f}")

    # Show detail for seed=42
    m, r = run_one(task, 42)
    lines.append(f"  [seed=42] ret={m['total_return']:+.2f}%  alpha={m['alpha']:+.2f}%  "
          f"sharpe={m['sharpe_ratio']:.2f}  dd={m['max_drawdown']:.2f}%  "
          f"wr={m['win_rate']:.1f}%  pf={m['profit_factor']:.2f}  "
          f"trades={m['total_trades']}  score={r['score']:.4f}")
    lines.append(f"  breakdown: {json.dumps(r['breakdown'])}")
    lines.append("")

overall = sum(all_scores) / len(all_scores)
lines.append(f"OVERALL AVERAGE: {overall:.4f}")

output = "\n".join(lines)
with open("test_results.txt", "w") as f:
    f.write(output)
print(output)
