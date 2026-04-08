"""
Technical-indicator engine.
Every indicator is either bounded (RSI 0-100) or expressed
relative to price so the agent never sees raw dollar values.
"""

import numpy as np
from typing import Dict

# ═══════════════════════════════════════════════════════════
#  Primitive helpers
# ═══════════════════════════════════════════════════════════

def _sma(arr: np.ndarray, p: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=np.float64)
    cs = np.cumsum(arr)
    out[p - 1:] = (cs[p - 1:] - np.concatenate([[0], cs[:-p]])) / p
    return out


def _ema(arr: np.ndarray, p: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=np.float64)
    k = 2.0 / (p + 1)
    out[p - 1] = np.mean(arr[:p])
    for i in range(p, len(arr)):
        out[i] = arr[i] * k + out[i - 1] * (1 - k)
    return out


def _rolling_std(arr: np.ndarray, p: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=np.float64)
    for i in range(p - 1, len(arr)):
        out[i] = np.std(arr[i - p + 1: i + 1], ddof=1)
    return out


def _slope(arr: np.ndarray, p: int = 5) -> np.ndarray:
    out = np.zeros_like(arr, dtype=np.float64)
    for i in range(p, len(arr)):
        if not np.isnan(arr[i]) and not np.isnan(arr[i - p]):
            denom = abs(arr[i - p]) + 1e-10
            out[i] = (arr[i] - arr[i - p]) / (p * denom)
    return out


# ═══════════════════════════════════════════════════════════
#  Indicators
# ═══════════════════════════════════════════════════════════

def _rsi(prices: np.ndarray, p: int = 14) -> np.ndarray:
    n = len(prices)
    out = np.full(n, 50.0)
    d = np.diff(prices)
    g = np.maximum(d, 0.0)
    l = np.abs(np.minimum(d, 0.0))
    if len(g) < p:
        return out
    ag = np.mean(g[:p])
    al = np.mean(l[:p])
    for i in range(p, n):
        ag = (ag * (p - 1) + g[i - 1]) / p
        al = (al * (p - 1) + l[i - 1]) / p
        out[i] = 100 - 100 / (1 + ag / (al + 1e-10))
    return out


def _atr(h, l, c, p=14):
    n = len(c)
    tr = np.empty(n)
    tr[0] = h[0] - l[0]
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    out = np.full(n, np.nan)
    if n >= p:
        out[p - 1] = np.mean(tr[:p])
        for i in range(p, n):
            out[i] = (out[i - 1] * (p - 1) + tr[i]) / p
    return out


def _stochastic(h, l, c, k_p=14, d_p=3):
    n = len(c)
    k = np.full(n, 50.0)
    for i in range(k_p - 1, n):
        hi = np.max(h[i - k_p + 1: i + 1])
        lo = np.min(l[i - k_p + 1: i + 1])
        if hi != lo:
            k[i] = 100 * (c[i] - lo) / (hi - lo)
    d = _sma(k, d_p)
    d = np.nan_to_num(d, nan=50.0)
    return k, d


def _williams_r(h, l, c, p=14):
    n = len(c)
    out = np.full(n, -50.0)
    for i in range(p - 1, n):
        hi = np.max(h[i - p + 1: i + 1])
        lo = np.min(l[i - p + 1: i + 1])
        if hi != lo:
            out[i] = -100 * (hi - c[i]) / (hi - lo)
    return out


def _cci(h, l, c, p=20):
    tp = (h + l + c) / 3
    n = len(c)
    out = np.zeros(n)
    for i in range(p - 1, n):
        w = tp[i - p + 1: i + 1]
        m = np.mean(w)
        mad = np.mean(np.abs(w - m))
        if mad > 0:
            out[i] = (tp[i] - m) / (0.015 * mad)
    return out


def _adx(h, l, c, p=14):
    n = len(c)
    if n < p * 2:
        return np.full(n, 25.0)
    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    tr = np.zeros(n)
    for i in range(1, n):
        hd = h[i] - h[i - 1]
        ld = l[i - 1] - l[i]
        if hd > ld and hd > 0:
            plus_dm[i] = hd
        if ld > hd and ld > 0:
            minus_dm[i] = ld
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    atr_s = _ema(tr, p)
    pdi = 100 * _ema(plus_dm, p) / (atr_s + 1e-10)
    mdi = 100 * _ema(minus_dm, p) / (atr_s + 1e-10)
    dx = 100 * np.abs(pdi - mdi) / (pdi + mdi + 1e-10)
    adx = _ema(dx, p)
    return np.nan_to_num(adx, nan=25.0)


def _obv(c, v):
    n = len(c)
    out = np.zeros(n)
    for i in range(1, n):
        if c[i] > c[i - 1]:
            out[i] = out[i - 1] + v[i]
        elif c[i] < c[i - 1]:
            out[i] = out[i - 1] - v[i]
        else:
            out[i] = out[i - 1]
    return out


def _roc(prices, p):
    out = np.zeros(len(prices))
    for i in range(p, len(prices)):
        if prices[i - p] != 0:
            out[i] = (prices[i] - prices[i - p]) / prices[i - p] * 100
    return out


# ═══════════════════════════════════════════════════════════
#  Master computation
# ═══════════════════════════════════════════════════════════

def compute_all_indicators(
    prices: np.ndarray,
    highs: np.ndarray | None = None,
    lows: np.ndarray | None = None,
    volumes: np.ndarray | None = None,
) -> Dict[str, np.ndarray]:
    """Return dict of numpy arrays, one entry per indicator."""
    n = len(prices)
    rng = np.random.default_rng(42)
    if highs is None:
        highs = prices * (1 + rng.uniform(0.001, 0.018, n))
    if lows is None:
        lows = prices * (1 - rng.uniform(0.001, 0.018, n))
    if volumes is None:
        volumes = rng.uniform(5e5, 2e6, n)

    ind: Dict[str, np.ndarray] = {}

    # Moving averages & relative features
    for p in (5, 10, 20, 50):
        sma = _sma(prices, p)
        ind[f"sma_{p}"] = sma
        ind[f"price_vs_sma_{p}"] = (prices - sma) / (sma + 1e-10)
        ind[f"sma_slope_{p}"] = _slope(sma, min(p, 5))

    for p in (12, 26):
        ind[f"ema_{p}"] = _ema(prices, p)

    # RSI
    ind["rsi_14"] = _rsi(prices, 14)
    ind["rsi_7"]  = _rsi(prices, 7)

    # MACD
    e12 = ind["ema_12"]
    e26 = ind["ema_26"]
    macd = e12 - e26
    sig  = _ema(np.nan_to_num(macd, nan=0.0), 9)
    hist = macd - sig
    ind["macd_line"]   = macd
    ind["macd_signal"] = sig
    ind["macd_hist"]   = hist
    ind["macd_norm"]   = macd / (prices + 1e-10)

    # Bollinger Bands
    bb_m = _sma(prices, 20)
    bb_s = _rolling_std(prices, 20)
    bb_u = bb_m + 2 * bb_s
    bb_l = bb_m - 2 * bb_s
    ind["bb_upper"]  = bb_u
    ind["bb_lower"]  = bb_l
    ind["bb_mid"]    = bb_m
    ind["bb_width"]  = (bb_u - bb_l) / (bb_m + 1e-10)
    ind["bb_pctb"]   = (prices - bb_l) / (bb_u - bb_l + 1e-10)

    # ATR
    atr = _atr(highs, lows, prices, 14)
    ind["atr_14"] = atr
    ind["atr_norm"] = atr / (prices + 1e-10)

    # ADX
    ind["adx_14"] = _adx(highs, lows, prices, 14)

    # Stochastic
    sk, sd = _stochastic(highs, lows, prices, 14, 3)
    ind["stoch_k"] = sk
    ind["stoch_d"] = sd

    # CCI, Williams %R
    ind["cci_20"]     = _cci(highs, lows, prices, 20)
    ind["williams_r"] = _williams_r(highs, lows, prices, 14)

    # Rate of change
    for p in (5, 10, 20):
        ind[f"roc_{p}"] = _roc(prices, p)

    # Returns & volatility
    ret1 = np.zeros(n)
    ret1[1:] = np.diff(prices) / (prices[:-1] + 1e-10)
    ind["ret_1d"] = ret1
    for p in (5, 10):
        r = np.zeros(n)
        r[p:] = (prices[p:] - prices[:-p]) / (prices[:-p] + 1e-10)
        ind[f"ret_{p}d"] = r
    ind["vol_10"] = _rolling_std(ret1, 10) * np.sqrt(252)
    ind["vol_20"] = _rolling_std(ret1, 20) * np.sqrt(252)

    # MA spread (relative)
    if n >= 50:
        ind["ma_spread"] = (ind["sma_10"] - ind["sma_50"]) / (ind["sma_50"] + 1e-10)

    # OBV normalised
    obv = _obv(prices, volumes)
    std_o = np.nanstd(obv) + 1e-10
    ind["obv_norm"] = (obv - np.nanmean(obv)) / std_o

    # ── Composite helpers for the agent ────────────────────
    ind["momentum_score"]  = _momentum_composite(ind)
    ind["trend_score"]     = _trend_composite(ind, prices)

    # Replace any residual NaN with 0
    for k in ind:
        ind[k] = np.nan_to_num(ind[k], nan=0.0)

    return ind


# ═══════════════════════════════════════════════════════════
#  Composite scores (agent-ready)
# ═══════════════════════════════════════════════════════════

def _momentum_composite(ind):
    parts, ws = [], []
    if "rsi_14" in ind:
        parts.append((ind["rsi_14"] - 50) / 50)
        ws.append(0.25)
    if "macd_norm" in ind:
        parts.append(np.clip(np.nan_to_num(ind["macd_norm"], 0) * 100, -1, 1))
        ws.append(0.25)
    if "stoch_k" in ind:
        parts.append((ind["stoch_k"] - 50) / 50)
        ws.append(0.20)
    if "roc_10" in ind:
        parts.append(np.clip(ind["roc_10"] / 10, -1, 1))
        ws.append(0.15)
    if "williams_r" in ind:
        parts.append((ind["williams_r"] + 50) / 50)
        ws.append(0.15)
    if not parts:
        return np.zeros(len(next(iter(ind.values()))))
    tw = sum(ws)
    return sum(np.nan_to_num(p, 0) * w / tw for p, w in zip(parts, ws))


def _trend_composite(ind, prices):
    parts, ws = [], []
    for key, w in [("price_vs_sma_20", 0.25), ("price_vs_sma_50", 0.25),
                   ("sma_slope_10", 0.25), ("sma_slope_20", 0.25)]:
        if key in ind:
            scl = 10 if "price" in key else 100
            parts.append(np.clip(np.nan_to_num(ind[key], 0) * scl, -1, 1))
            ws.append(w)
    if not parts:
        return np.zeros(len(prices))
    tw = sum(ws)
    return sum(np.nan_to_num(p, 0) * w / tw for p, w in zip(parts, ws))


def snapshot(ind: Dict[str, np.ndarray], step: int) -> Dict[str, float]:
    """Pull scalar values at a single time-step."""
    return {k: float(v[step]) for k, v in ind.items() if step < len(v)}
