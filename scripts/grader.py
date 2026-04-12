"""
Performance grader. Weights match the hackathon rubric.
"""

from typing import Dict


def grade_performance(metrics: Dict) -> Dict:
    total_ret = metrics.get("total_return", 0)
    bh_ret = metrics.get("buy_hold_return", 0)
    alpha = metrics.get("alpha", 0)
    win_rate = metrics.get("win_rate", 0)
    total_trades = metrics.get("total_trades", 0)
    max_dd = metrics.get("max_drawdown", 100)
    sharpe = metrics.get("sharpe_ratio", 0)
    pf = metrics.get("profit_factor", 0)

    if total_ret > 15:
        prof_score = 1.0
    elif total_ret > 10:
        prof_score = 0.90
    elif total_ret > 5:
        prof_score = 0.75
    elif total_ret > 2:
        prof_score = 0.60
    elif total_ret > 0:
        prof_score = 0.45
    else:
        prof_score = max(0, 0.2 + total_ret / 50)

    if alpha > 8:
        alpha_score = 1.0
    elif alpha > 4:
        alpha_score = 0.85
    elif alpha > 1:
        alpha_score = 0.65
    elif alpha > 0:
        alpha_score = 0.50
    else:
        alpha_score = max(0, 0.3 + alpha / 20)

    if win_rate >= 70:
        wr_score = 1.0
    elif win_rate >= 60:
        wr_score = 0.85
    elif win_rate >= 50:
        wr_score = 0.65
    elif win_rate >= 40:
        wr_score = 0.45
    else:
        wr_score = max(0, win_rate / 100)

    if 5 <= total_trades <= 50:
        freq_score = 1.0
    elif 3 <= total_trades <= 80:
        freq_score = 0.75
    elif total_trades > 0:
        freq_score = 0.40
    else:
        freq_score = 0.10

    if max_dd < 5:
        risk_score = 1.0
    elif max_dd < 10:
        risk_score = 0.80
    elif max_dd < 15:
        risk_score = 0.55
    elif max_dd < 25:
        risk_score = 0.30
    else:
        risk_score = 0.10

    bonus = 0.0
    if sharpe > 2.0:
        bonus += 0.03
    elif sharpe > 1.5:
        bonus += 0.02
    if pf > 2.5:
        bonus += 0.02
    elif pf > 1.8:
        bonus += 0.01

    raw = (prof_score * 0.40 + alpha_score * 0.25 + wr_score * 0.15 +
           freq_score * 0.10 + risk_score * 0.10 + bonus)
    final = min(0.99, max(0.01, raw))

    return {
        "score": round(final, 4),
        "breakdown": {
            "profitability": round(prof_score, 4),
            "alpha": round(alpha_score, 4),
            "win_rate": round(wr_score, 4),
            "frequency": round(freq_score, 4),
            "risk": round(risk_score, 4),
            "bonus": round(bonus, 4),
        },
        "metrics": metrics,
    }
