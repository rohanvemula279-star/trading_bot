from environment import TradingEnvironment
from agent import TradingAgent
from risk_manager import RiskManager
from grader import grade_performance

env = TradingEnvironment()
agent = TradingAgent()
risk = RiskManager()
obs = env.reset("easy_task", seed=10) # unknown seed
while not env.done:
    state = env.get_state()
    actions = agent.decide(state)
    actions = risk.filter_actions(actions, state, env.equity_curve)
    obs, reward, done, info = env.step(actions)
metrics = env.get_metrics()
result = grade_performance(metrics)
print(f"Random Seed Score: {result['score']}")
