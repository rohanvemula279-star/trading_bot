import os
from inference import _fallback_action, MAX_STEPS
def pad(text, width=90):
    text = str(text)
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    return f"| {text.ljust(width - 4)} |\\n"

def separator(width=90, char="-"):
    return f"+{char * (width - 2)}+\\n"

def evaluate_task_local(task_name, log_file):
    os.environ["TASK_NAME"] = task_name
    from server.app import TradingEnvironment
    from models import TradingAction, SingleOrder
    import json
    
    log_file.write(f"\\n\\n")
    log_file.write(separator(90, "="))
    log_file.write(pad(f"EVALUATING TASK: {task_name}"))
    log_file.write(separator(90, "="))
    
    env = TradingEnvironment()
    obs = env.reset()
    
    score = 0.0
    done = False
    
    log_file.write(pad(f"[INIT] Start Portfolio: ${obs.portfolio_value_usd:,.2f} | Cash: ${obs.available_cash_usd:,.2f}"))
    log_file.write(separator())
    
    for step in range(1, MAX_STEPS + 1):
        if done:
            break
            
        action_dict = _fallback_action(obs.model_dump())
        log_file.write(pad(""))
        log_file.write(pad(f"[STEP {step}]"))
        log_file.write(pad("Market Data:"))
        for md in obs.market_data:
            log_file.write(pad(f"  | {md.ticker}: ${md.price:.2f} (News: '{md.news_headline}')"))
            
        log_file.write(pad(""))
        log_file.write(pad(f"Decision logic: {action_dict['reasoning']}"))
        log_file.write(pad("Orders Executed:"))
        
        for o in action_dict['orders']:
            if o['side'] != 'HOLD':
                amt = "ALL" if o['amount_usd'] > 100000 else f"${o['amount_usd']:.2f}"
                log_file.write(pad(f"  | -> {o['side']} {o['ticker']} amount: {amt}"))
            
        action_obj = TradingAction(
            reasoning=action_dict["reasoning"],
            orders=[SingleOrder(**o) for o in action_dict["orders"]]
        )
        
        obs = env.step(action_obj)
        done = obs.done
        
        log_file.write(pad(""))
        log_file.write(pad(f"Result: Portfolio Value: ${obs.portfolio_value_usd:,.2f} | Available Cash: ${obs.available_cash_usd:,.2f}"))
        log_file.write(separator())
        
        if done:
            meta = obs.metadata or {}
            score = meta.get("score", 0.0)
            
    log_file.write(pad(f"[{task_name}] Final End Score: {score:.4f}"))
    log_file.write(separator(90, "="))
    return score

if __name__ == "__main__":
    tasks = ["easy-bull-market", "medium-volatile-market", "hard-flash-crash"]
    scores = []
    
    with open("performance_report.txt", "w") as f:
        f.write(separator(90, "*"))
        f.write(pad("AGENT PERFORMANCE REPORT (CRYSTAL BALL HEURISTIC)"))
        f.write(separator(90, "*"))
        
        for t in tasks:
            scores.append(evaluate_task_local(t, f))
        
        avg = sum(scores) / len(scores)
        f.write("\\n")
        f.write(separator(90, "#"))
        f.write(pad(f"OVERALL AVERAGE SCORE: {avg * 100:.2f}%"))
        f.write(separator(90, "#"))
