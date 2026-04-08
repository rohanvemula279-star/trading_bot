"""
Central configuration for the entire trading system.
All parameters tuned for maximum performance.
"""

import os
from typing import Dict, List

# ─── Server ──────────────────────────────────────────────
PORT = int(os.environ.get("PORT", 7860))
HOST = os.environ.get("HOST", "0.0.0.0")

# ─── Task Definitions ────────────────────────────────────
TASKS: Dict[str, dict] = {
    "easy_task": {
        "stocks": ["ALPHA"],
        "trading_days": 50,
        "warmup_days": 50,
        "initial_cash": 100_000,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
        "regime_changes": 2,
    },
    "medium_task": {
        "stocks": ["ALPHA", "BETA"],
        "trading_days": 100,
        "warmup_days": 50,
        "initial_cash": 150_000,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
        "regime_changes": 5,
    },
    "hard_task": {
        "stocks": ["ALPHA", "BETA", "GAMMA", "DELTA"],
        "trading_days": 200,
        "warmup_days": 50,
        "initial_cash": 200_000,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
        "regime_changes": 10,
    },
}

# ─── Stock DNA ────────────────────────────────────────────
STOCK_PROFILES = {
    "ALPHA":  {"base_price": 150.0, "base_vol": 0.20, "beta": 1.2, "sector": "tech"},
    "BETA":   {"base_price":  80.0, "base_vol": 0.12, "beta": 0.6, "sector": "utilities"},
    "GAMMA":  {"base_price": 120.0, "base_vol": 0.18, "beta": 1.0, "sector": "industrial"},
    "DELTA":  {"base_price": 200.0, "base_vol": 0.25, "beta": 1.5, "sector": "growth"},
}

# ─── Regime Parameters (annualised) ──────────────────────
REGIMES = {
    "BULL":     {"drift":  0.20, "vol_mult": 0.80},
    "BEAR":     {"drift": -0.12, "vol_mult": 1.40},
    "SIDEWAYS": {"drift":  0.02, "vol_mult": 0.60},
}

# ── Risk Management ──────────────────────────────────────
RISK_PER_TRADE = 0.03          # Risk 3% of portfolio per trade
MAX_POSITION_PCT = 0.50        # Never put more than 50% in one trade
MAX_TOTAL_EXPOSURE = 0.95      # Max 95% of capital deployed

# ── ATR-Based Levels ─────────────────────────────────────
SL_ATR_MULT = 1.5              # Stop loss = entry - 1.5 * ATR
TP_ATR_MULT = 3.0              # Take profit = entry + 3.0 * ATR (2:1 R:R)
TRAIL_ATR_MULT = 2.0           # Trailing stop = peak - 2.0 * ATR
TRAIL_ACTIVATION_R = 1.0       # Activate trail after 1R of profit

# ── Signal Thresholds ────────────────────────────────────
SIGNAL_THRESHOLD_BUY = 0.25    # Composite signal > 0.25 → BUY
SIGNAL_THRESHOLD_SELL = -0.15  # Composite signal < -0.15 → SELL
CONFIDENCE_BOOST = 1.5         # Scale up position for signal > 0.85

# ── Indicator Params ─────────────────────────────────────
RSI_PERIOD = 14
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 70
EMA_FAST = 12
EMA_SLOW = 26
ATR_PERIOD = 14
VOLUME_SPIKE_MULT = 1.5        # Volume > 1.5x avg = spike
MIN_ATR_FLOOR = 0.001          # Prevent division by near-zero ATR

MIN_CASH_RESERVE = 0.05
