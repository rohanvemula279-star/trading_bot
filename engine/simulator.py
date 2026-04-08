import random
import math

# Curated news headlines for different market conditions
BULL_NEWS = [
    "Tech earnings crush estimates, S&P 500 hits all-time high.",
    "Fed signals dovish pivot, bond yields plummet as equities rally.",
    "Unemployment rate drops to 3.4%, lowest in 50 years.",
    "Consumer confidence surges to highest level since 2019.",
    "AI boom drives Nasdaq up 4% in single session.",
    "Strong GDP growth of 3.2% beats all forecasts.",
    "Major chip manufacturer announces record quarterly revenue.",
    "Retail sales data shows robust consumer spending.",
    "Housing starts jump 12%, signaling economic expansion.",
    "Global trade tensions ease as new deals signed.",
    "Biotech breakthrough sends healthcare sector soaring.",
    "Oil prices stabilize, easing inflation fears across markets.",
    "Corporate buyback programs hit $1 trillion annual pace.",
    "Emerging markets rally on strong dollar weakness.",
    "Manufacturing PMI expands for fifth consecutive month.",
]

VOLATILE_NEWS = [
    "Inflation data mixed: core CPI up 0.4%, markets whipsaw.",
    "Fed minutes reveal deep division on rate path, VIX spikes.",
    "Unexpected tech rally erases morning losses, Nasdaq flips green.",
    "Geopolitical tensions escalate: markets dive then partially recover.",
    "Bank earnings disappoint but forward guidance surprisingly strong.",
    "Crypto crash spills over into tech stocks, then bounces hard.",
    "Trade war rhetoric heats up; tariff threats rattle supply chains.",
    "Strong jobs report reignites rate hike fears, bonds sell off.",
    "Oil supply disruption sends energy stocks surging, rest of market drops.",
    "Earnings season mixed bag: 60% beat, but guidance cuts widespread.",
    "Short squeeze in meme stocks triggers broader market volatility.",
    "Treasury auction sees weak demand, 10-year yield jumps 15bps.",
    "Breaking: Major hedge fund liquidating positions across sectors.",
    "Surprise rate cut from ECB sends EUR tumbling, USD stocks mixed.",
    "Flash PMI data contradicts official numbers, analysts confused.",
    "Retail investor sentiment at extreme bearish levels — contrarian signal?",
    "Bond market inversion deepens: recession odds now at 65%.",
    "Semiconductor export ban announced; chip stocks crash 8% then recover 5%.",
]

CRASH_NEWS = [
    "Markets open normally with light volume, no significant catalysts.",
    "Slight weakness in tech names as regulatory concerns surface.",
    "BREAKING: Major bank reports massive derivative losses, stock halted.",
    "FLASH CRASH: Algorithmic selling triggers cascading liquidations across all sectors.",
    "Circuit breakers triggered on S&P 500 — trading halted for 15 minutes.",
    "Trading resumes: panic selling intensifies, VIX hits 80.",
    "BREAKING: Second major institution rumored to face margin calls.",
    "Fed emergency statement: 'Prepared to act' — markets briefly stabilize.",
    "Stabilization attempt fails, new lows hit as stop-losses cascade.",
    "Late-session bounce: bargain hunters step in, but damage is severe.",
    "Post-crash analysis: $3 trillion in market cap wiped out in single session.",
    "Regulators announce investigation into algorithmic trading systems.",
]


def generate_price_series(start_price, num_steps, regime="bull", seed=None):
    """Generate realistic price series with the given regime."""
    rng = random.Random(seed)
    prices = [start_price]
    
    for i in range(num_steps - 1):
        p = prices[-1]
        if regime == "bull":
            # Steady uptrend with small noise
            drift = 0.002 + rng.gauss(0, 0.008)
            p = p * (1 + drift)
        elif regime == "volatile":
            # High variance, slight upward bias
            drift = rng.gauss(0.001, 0.025)
            p = p * (1 + drift)
        elif regime == "crash":
            # First few steps normal, then crash, then partial recovery
            progress = i / max(num_steps - 1, 1)
            if progress < 0.15:
                drift = rng.gauss(0.0, 0.005)
            elif progress < 0.5:
                drift = rng.gauss(-0.08, 0.03)  # crash phase
            elif progress < 0.7:
                drift = rng.gauss(-0.03, 0.02)  # continued weakness
            else:
                drift = rng.gauss(0.02, 0.015)  # partial recovery
            p = p * (1 + drift)
        
        prices.append(max(p, 0.01))  # floor at 0.01
    
    return prices


def compute_rsi(prices, period=14):
    """Compute RSI for a price series."""
    if len(prices) < period + 1:
        return [50.0] * len(prices)
    
    rsi_values = [50.0] * period
    gains = []
    losses = []
    
    for i in range(1, period + 1):
        change = prices[i] - prices[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        rsi_values.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(100 - (100 / (1 + rs)))
    
    for i in range(period + 1, len(prices)):
        change = prices[i] - prices[i-1]
        gain = max(change, 0)
        loss = max(-change, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100 - (100 / (1 + rs)))
    
    return rsi_values


class Simulator:
    """
    A deterministic trading simulator that models realistic market dynamics.
    Supports three task types: easy-bull-market, medium-volatile-market, hard-flash-crash.
    """
    
    TASK_CONFIG = {
        "easy-bull-market": {
            "tickers": ["AAPL", "MSFT"],
            "start_prices": [150.0, 380.0],
            "num_steps": 10,
            "regime": "bull",
            "news_pool": BULL_NEWS,
            "initial_cash": 10000.0,
            "fee_rate": 0.001,
        },
        "medium-volatile-market": {
            "tickers": ["AAPL", "MSFT", "TSLA"],
            "start_prices": [150.0, 380.0, 250.0],
            "num_steps": 15,
            "regime": "volatile",
            "news_pool": VOLATILE_NEWS,
            "initial_cash": 10000.0,
            "fee_rate": 0.001,
        },
        "hard-flash-crash": {
            "tickers": ["AAPL", "MSFT", "TSLA", "NVDA"],
            "start_prices": [150.0, 380.0, 250.0, 800.0],
            "num_steps": 12,
            "regime": "crash",
            "news_pool": CRASH_NEWS,
            "initial_cash": 10000.0,
            "fee_rate": 0.001,
        },
    }
    
    def __init__(self, task: str, seed: int = 42):
        if task not in self.TASK_CONFIG:
            task = "easy-bull-market"
        self.task = task
        self.config = self.TASK_CONFIG[task]
        self.seed = seed
        self.rng = random.Random(seed)
        
        self.tickers = self.config["tickers"]
        self.num_steps = self.config["num_steps"]
        self.fee_rate = self.config["fee_rate"]
        self.initial_cash = self.config["initial_cash"]
        self.cash = self.initial_cash
        
        # Generate price series for each ticker
        self.price_series = {}
        self.rsi_series = {}
        for ticker, start_price in zip(self.tickers, self.config["start_prices"]):
            prices = generate_price_series(
                start_price, self.num_steps + 1, 
                self.config["regime"], 
                seed=self.rng.randint(0, 100000)
            )
            self.price_series[ticker] = prices
            self.rsi_series[ticker] = compute_rsi(prices)
        
        # Generate news for each step
        news_pool = self.config["news_pool"]
        self.news_per_step = []
        for i in range(self.num_steps + 1):
            idx = i % len(news_pool)
            self.news_per_step.append(news_pool[idx])
        
        # Portfolio state
        self.holdings = {t: 0.0 for t in self.tickers}  # shares held
        self.current_step = 0
        
        # Tracking
        self.max_portfolio = self.initial_cash
        self.max_drawdown = 0.0
        self.trade_count = 0
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value at current step."""
        value = self.cash
        for ticker in self.tickers:
            price = self.price_series[ticker][self.current_step]
            value += self.holdings[ticker] * price
        return value
    
    def get_state(self) -> dict:
        """Return the current observation."""
        if self.current_step > self.num_steps:
            return None
        
        portfolio_value = self.get_portfolio_value()
        
        market_data = []
        for ticker in self.tickers:
            price = self.price_series[ticker][self.current_step]
            prev_price = self.price_series[ticker][max(0, self.current_step - 1)]
            change = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0.0
            rsi = self.rsi_series[ticker][self.current_step]
            
            market_data.append({
                "ticker": ticker,
                "price": round(price, 2),
                "change_24h": round(change, 2),
                "rsi_14": round(rsi, 2),
                "news_headline": self.news_per_step[self.current_step],
            })
        
        return {
            "step": self.current_step,
            "portfolio_value_usd": round(portfolio_value, 2),
            "available_cash_usd": round(self.cash, 2),
            "current_holdings": {t: round(self.holdings[t], 4) for t in self.tickers},
            "market_data": market_data,
        }
    
    def step(self, actions: list) -> tuple:
        """
        Execute orders and advance one step.
        Returns (state_dict, reward, done).
        """
        if self.current_step >= self.num_steps:
            return self.get_state(), 0.0, True
        
        start_portfolio = self.get_portfolio_value()
        
        # Execute each order
        for act in actions:
            ticker = act.get("ticker", "")
            side = act.get("side", "HOLD").upper()
            amount_usd = float(act.get("amount_usd", 0.0))
            
            if ticker not in self.tickers:
                continue
            if side == "HOLD" or amount_usd <= 0:
                continue
            
            current_price = self.price_series[ticker][self.current_step]
            
            if side == "BUY":
                cost = min(amount_usd, self.cash)
                if cost <= 0:
                    continue
                shares = (cost * (1 - self.fee_rate)) / current_price
                self.cash -= cost
                self.holdings[ticker] += shares
                self.trade_count += 1
                
            elif side == "SELL":
                shares_to_sell = amount_usd / current_price
                shares_to_sell = min(shares_to_sell, self.holdings[ticker])
                if shares_to_sell <= 0:
                    continue
                proceeds = (shares_to_sell * current_price) * (1 - self.fee_rate)
                self.holdings[ticker] -= shares_to_sell
                self.cash += proceeds
                self.trade_count += 1
        
        # Advance to next step
        self.current_step += 1
        done = self.current_step >= self.num_steps
        
        end_portfolio = self.get_portfolio_value()
        
        # Update drawdown tracking
        if end_portfolio > self.max_portfolio:
            self.max_portfolio = end_portfolio
        dd = (self.max_portfolio - end_portfolio) / self.max_portfolio
        if dd > self.max_drawdown:
            self.max_drawdown = dd
        
        # Step reward: change in portfolio value (provides signal every step)
        reward = (end_portfolio - start_portfolio) / self.initial_cash
        
        state = self.get_state()
        if state is None:
            # Edge case: build final state from last valid step
            self.current_step = self.num_steps
            state = {
                "step": self.current_step,
                "portfolio_value_usd": round(end_portfolio, 2),
                "available_cash_usd": round(self.cash, 2),
                "current_holdings": {t: round(self.holdings[t], 4) for t in self.tickers},
                "market_data": [{
                    "ticker": t,
                    "price": round(self.price_series[t][min(self.current_step, len(self.price_series[t])-1)], 2),
                    "change_24h": 0.0,
                    "rsi_14": 50.0,
                    "news_headline": "Episode complete.",
                } for t in self.tickers],
            }
        
        return state, reward, done
    
    def compute_score(self) -> float:
        """
        Compute final score in [0.0, 1.0] based on task-specific criteria.
        
        Easy (bull): Score = clip(ROI / 5%, 0, 1)
        Medium (volatile): Score = clip(ROI / 8%, 0, 1), but 0 if drawdown > 10%
        Hard (crash): Score based on loss minimization vs benchmark -30% drop
        """
        final_portfolio = self.get_portfolio_value()
        roi = (final_portfolio - self.initial_cash) / self.initial_cash
        
        if self.task == "easy-bull-market":
            score = max(min(roi / 0.05, 1.0), 0.0)
        elif self.task == "medium-volatile-market":
            if self.max_drawdown > 0.10:
                score = max(min(roi / 0.08, 1.0), 0.0) * 0.5  # penalize but don't zero
            else:
                score = max(min(roi / 0.08, 1.0), 0.0)
        elif self.task == "hard-flash-crash":
            if roi > 0:
                score = 1.0
            elif roi > -0.05:
                score = 0.8
            elif roi > -0.15:
                score = 0.5
            else:
                score = max(1.0 - (abs(roi) / 0.30), 0.0)
        else:
            score = 0.0
        
        return round(score, 4)
