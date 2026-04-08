"""Quick score check across all tasks and seeds."""
import json
from environment import TradingEnvironment
from agent import TradingAgent
from risk_manager import RiskManager
from grader import grade_performance

results = {}
for task_id in ["easy_task", "medium_task", "hard_task"]:
    task_scores = []
    for seed in [42, 123, 777, 2024, 9999]:
        env = TradingEnvironment()
        agent = TradingAgent()
        risk = RiskManager()
        obs = env.reset(task_id, seed=seed)
        while not env.done:
            state = env.get_state()
            actions = agent.decide(state)
            actions = risk.filter_actions(actions, state, env.equity_curve)
            obs, reward, done, info = env.step(actions)
        metrics = env.get_metrics()
        result = grade_performance(metrics)
        score = result["score"]
        task_scores.append(score)
        tr = metrics["total_return"]
        al = metrics["alpha"]
        dd = metrics["max_drawdown"]
        wr = metrics["win_rate"]
        tt = metrics["total_trades"]
        sh = metrics["sharpe_ratio"]
        print(f"  {task_id} seed={seed}: score={score:.4f} ret={tr:+.2f}% alpha={al:+.2f}% dd={dd:.2f}% wr={wr:.1f}% trades={tt} sharpe={sh:.2f}")
    avg = sum(task_scores) / len(task_scores)
    results[task_id] = avg
    print(f"  >>> {task_id} avg: {avg:.4f}\n")

overall = sum(results.values()) / len(results)
print(f"OVERALL: {overall:.4f}")
