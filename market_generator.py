"""
Regime-switching Geometric Brownian Motion market generator.
Produces realistic OHLCV data for 1-4 correlated stocks.
"""

import numpy as np
from typing import Dict, List, Tuple
from config import STOCK_PROFILES, REGIMES


class MarketGenerator:
    """Generate synthetic multi-stock market data with regime switching."""

    def __init__(self, seed: int | None = None):
        self.rng = np.random.default_rng(seed)

    # ──────────────────────────────────────────────────────
    def generate(
        self,
        stock_names: List[str],
        total_days: int,
        regime_changes: int = 4,
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Returns {stock_name: {"prices","highs","lows","volumes"}}
        """
        regimes = self._make_regime_sequence(total_days, regime_changes)
        corr_matrix = self._build_correlation(stock_names)
        chol = np.linalg.cholesky(corr_matrix)

        result: Dict[str, Dict[str, np.ndarray]] = {}
        # generate correlated random normals
        z_raw = self.rng.standard_normal((total_days, len(stock_names)))
        z_corr = z_raw @ chol.T

        for idx, name in enumerate(stock_names):
            prof = STOCK_PROFILES.get(name, STOCK_PROFILES["ALPHA"])
            prices, highs, lows, volumes = self._single_stock(
                prof, regimes, z_corr[:, idx], total_days
            )
            result[name] = {
                "prices": prices,
                "highs": highs,
                "lows": lows,
                "volumes": volumes,
            }
        return result

    # ──────────────────────────────────────────────────────
    def _make_regime_sequence(self, total_days: int, n_changes: int) -> List[str]:
        names = list(REGIMES.keys())
        boundaries = sorted(self.rng.integers(10, total_days - 10, size=n_changes))
        boundaries = [0] + list(boundaries) + [total_days]
        seq: List[str] = []
        cur = self.rng.choice(names)
        for i in range(len(boundaries) - 1):
            length = boundaries[i + 1] - boundaries[i]
            seq.extend([cur] * length)
            # pick a DIFFERENT regime next
            others = [r for r in names if r != cur]
            cur = self.rng.choice(others)
        return seq[:total_days]

    # ──────────────────────────────────────────────────────
    def _single_stock(
        self,
        prof: dict,
        regimes: List[str],
        z: np.ndarray,
        total_days: int,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        dt = 1 / 252
        price = prof["base_price"]
        prices = np.empty(total_days)
        highs  = np.empty(total_days)
        lows   = np.empty(total_days)
        volumes = np.empty(total_days)

        beta = prof["beta"]
        base_vol = prof["base_vol"]

        for t in range(total_days):
            reg = REGIMES[regimes[t]]
            mu = reg["drift"] * beta * dt
            sigma = base_vol * reg["vol_mult"] * np.sqrt(dt)

            ret = mu - 0.5 * sigma ** 2 + sigma * z[t]
            price = price * np.exp(ret)
            prices[t] = price

            # intraday range from ATR-like model
            spread = base_vol * reg["vol_mult"] * price * np.sqrt(dt)
            highs[t] = price + abs(self.rng.normal(0, spread * 0.6))
            lows[t]  = price - abs(self.rng.normal(0, spread * 0.6))
            lows[t]  = max(lows[t], price * 0.90)  # floor

            vol_base = 1_000_000 * (1 + beta * 0.5)
            volumes[t] = max(100_000, self.rng.normal(vol_base, vol_base * 0.3))

        return prices, highs, lows, volumes

    # ──────────────────────────────────────────────────────
    @staticmethod
    def _build_correlation(names: List[str]) -> np.ndarray:
        n = len(names)
        if n == 1:
            return np.array([[1.0]])
        # sector-based correlations
        sectors = [STOCK_PROFILES.get(s, {}).get("sector", "x") for s in names]
        corr = np.eye(n)
        for i in range(n):
            for j in range(i + 1, n):
                if sectors[i] == sectors[j]:
                    c = 0.70
                else:
                    c = 0.30
                corr[i, j] = c
                corr[j, i] = c
        # ensure positive-definite
        eigvals = np.linalg.eigvalsh(corr)
        if eigvals.min() < 1e-6:
            corr += np.eye(n) * (1e-6 - eigvals.min())
        return corr
