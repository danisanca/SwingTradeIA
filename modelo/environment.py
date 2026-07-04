"""
ambiente.py — Ambiente Gymnasium customizado para Swing Trade na B3
"""
import gymnasium as gym
import numpy as np
import pandas as pd
from typing import Optional


class SwingTradeEnv(gym.Env):
    """
    Ambiente de trading para Swing Trade em ações brasileiras.
    
    Observação (state): janela dos últimos N dias com features normalizadas
    Ações: 0=SELL, 1=HOLD, 2=BUY
    Recompensa: variação percentual do portfólio - custo de transação
    """
    metadata = {"render_modes": []}

    # Custo de transação (corretagem + spread) — estimado para B3
    TRANSACTION_COST = 0.001  # 0.1%

    def __init__(self, df: pd.DataFrame, window: int = 10, initial_balance: float = 10_000.0):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.window = window
        self.initial_balance = initial_balance

        # features por dia: close_pct, volume_ratio, rsi_norm, macd_norm, bb_pct
        self.n_features = 5
        obs_size = window * self.n_features

        self.action_space = gym.spaces.Discrete(3)  # SELL=0, HOLD=1, BUY=2
        self.observation_space = gym.spaces.Box(
            low=-5.0, high=5.0, shape=(obs_size,), dtype=np.float32
        )

        self._precompute_features()
        self.reset()

    def _precompute_features(self):
        """Pré-calcula features normalizadas para o dataset inteiro"""
        import ta
        close = self.df["Close"]
        volume = self.df["Volume"]
        high = self.df["High"]
        low = self.df["Low"]

        # Variação percentual do fechamento
        self.close_pct = close.pct_change().fillna(0).clip(-0.2, 0.2).values

        # Volume ratio (vs média de 20 dias)
        vol_ma20 = volume.rolling(20).mean().fillna(method='bfill')
        self.volume_ratio = (volume / vol_ma20).clip(0, 5).fillna(1.0).values

        # RSI normalizado
        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi().fillna(50)
        self.rsi_norm = (rsi / 100.0).values

        # MACD normalizado (diferença / preço)
        macd_diff = ta.trend.MACD(close=close).macd_diff().fillna(0)
        self.macd_norm = (macd_diff / close).clip(-0.05, 0.05).fillna(0).values

        # Bollinger Band %B
        bb = ta.volatility.BollingerBands(close=close, window=20)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        bb_range = bb_upper - bb_lower
        pct_b = ((close - bb_lower) / bb_range.replace(0, np.nan)).fillna(0.5).clip(0, 1)
        self.bb_pct = pct_b.values

    def _get_obs(self) -> np.ndarray:
        """Retorna o vetor de observação para o step atual"""
        start = self.current_step - self.window
        end = self.current_step
        features = np.column_stack([
            self.close_pct[start:end],
            self.volume_ratio[start:end],
            self.rsi_norm[start:end],
            self.macd_norm[start:end],
            self.bb_pct[start:end],
        ])
        return features.flatten().astype(np.float32)

    def reset(self, *, seed: Optional[int] = None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.prev_net_worth = self.initial_balance
        return self._get_obs(), {}

    def step(self, action: int):
        current_price = float(self.df["Close"].iloc[self.current_step])
        cost = 0.0

        if action == 2 and self.shares_held == 0:  # BUY
            shares = int(self.balance / current_price)
            if shares > 0:
                cost = shares * current_price * self.TRANSACTION_COST
                self.shares_held = shares
                self.balance -= (shares * current_price + cost)

        elif action == 0 and self.shares_held > 0:  # SELL
            revenue = self.shares_held * current_price
            cost = revenue * self.TRANSACTION_COST
            self.balance += revenue - cost
            self.shares_held = 0

        # Atualizar patrimônio
        self.net_worth = self.balance + self.shares_held * current_price
        reward = (self.net_worth - self.prev_net_worth) / self.prev_net_worth
        self.prev_net_worth = self.net_worth

        self.current_step += 1
        done = self.current_step >= len(self.df) - 1

        return self._get_obs(), float(reward), done, False, {}

    def render(self):
        print(f"Step: {self.current_step} | Net Worth: R${self.net_worth:.2f} | Shares: {self.shares_held}")
