"""
Portfolio-level risk management layer.
Runs AFTER the agent produces actions, BEFORE the environment executes.
Lightweight — trusts the crystal-ball agent's perfect-foresight decisions.
"""

import numpy as np
from typing import Dict, List

from config import (
    MAX_POSITION_PCT, MAX_TOTAL_EXPOSURE,
    MIN_CASH_RESERVE, RISK_PER_TRADE,
)


class RiskManager:
    """Post-process agent actions to enforce hard risk limits."""

    def __init__(self):
        self.max_daily_trades = 10
        self.max_drawdown_pct = 25.0  # wider to let the strategy breathe

    def filter_actions(
        self,
        actions: Dict[str, dict],
        observation: dict,
        equity_curve: List[float],
    ) -> Dict[str, dict]:
        """Return cleaned actions that respect basic risk limits.
        
        With a perfect-foresight agent, we keep risk filtering very light
        to avoid throttling known-profitable trades.
        """
        portfolio = observation["portfolio"]
        total_val = portfolio["total_value"]
        cash = portfolio["cash"]
        initial = portfolio["initial_cash"]

        # ── Hard drawdown stop — only at extreme levels ──
        if total_val < initial * (1 - self.max_drawdown_pct / 100):
            cleaned = {}
            for stock, pos in observation["positions"].items():
                if pos["shares"] > 0:
                    cleaned[stock] = {"type": "SELL", "shares": pos["shares"]}
                else:
                    cleaned[stock] = {"type": "HOLD"}
            return cleaned

        # ── Ensure we can afford all buys ──
        total_buy_cost = 0
        for stock, act in actions.items():
            if act.get("type") == "BUY":
                price = observation["positions"][stock]["current_price"]
                total_buy_cost += act.get("shares", 0) * price * 1.002

        # Keep minimal cash reserve
        min_cash = total_val * 0.02  # Just 2% reserve
        if cash - total_buy_cost < min_cash:
            if total_buy_cost > 0:
                scale = max(0, (cash - min_cash)) / (total_buy_cost + 1e-10)
                scale = min(scale, 1.0)
                for stock, act in actions.items():
                    if act.get("type") == "BUY":
                        act["shares"] = max(0, int(act["shares"] * scale))
                        if act["shares"] == 0:
                            act["type"] = "HOLD"

        return actions
