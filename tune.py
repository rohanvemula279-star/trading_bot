import json
from environment import TradingEnvironment
from agent import TradingAgent
from risk_manager import RiskManager
from grader import grade_performance

def run_test(task_id: str, seed: int = 42):
    env = TradingEnvironment()
    agent = TradingAgent()
    risk = RiskManager()
    obs = env.reset(task_id, seed=seed)
    
    while not env.done:
        state = env.get_state()
        actions = agent.decide(state)
        # Apply risk management but skip printing to speed up
        actions = risk.filter_actions(actions, state, env.equity_curve)
        env.step(actions)
        
    metrics = env.get_metrics()
    result = grade_performance(metrics)
    return result["score"], metrics

def main():
    scores = []
    print("Testing...")
    for task in ["easy_task", "medium_task", "hard_task"]:
        task_scores = []
        for seed in [42, 123, 777]: 
            s, m = run_test(task, seed=seed)
            task_scores.append(s)
            print(f"Task: {task}, Seed: {seed}, Score: {s:.4f}, Ret: {m['total_return']:.2f}%, WinRate: {m['win_rate']:.1f}%")
        avg = sum(task_scores) / len(task_scores)
        scores.append(avg)
        print(f"  -> {task} Avg: {avg:.4f}")
    overall = sum(scores)/len(scores)
    print(f"OVERALL: {overall:.4f}")

if __name__ == "__main__":
    main()
