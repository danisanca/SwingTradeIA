import logging
import os

import numpy as np
import pandas as pd
import ta

logger = logging.getLogger(__name__)

# Verificar se PyTorch está disponível
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch não disponível — usando fallback de análise técnica")


class DQNNetwork(nn.Module if TORCH_AVAILABLE else object):
    """
    Rede neural do agente DQN.
    Input: estado (features normalizadas de 10 dias)
    Output: Q-values para as 3 ações (SELL=0, HOLD=1, BUY=2)
    """
    def __init__(self, state_size: int = 30, action_size: int = 3):
        if TORCH_AVAILABLE:
            super(DQNNetwork, self).__init__()
            self.net = nn.Sequential(
                nn.Linear(state_size, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, action_size),
            )

    def forward(self, x):
        if TORCH_AVAILABLE:
            return self.net(x)


ACTION_MAP = {0: "SELL", 1: "HOLD", 2: "BUY"}
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "dqn_weights.pth")


def build_state(df: pd.DataFrame, window: int = 10) -> np.ndarray | None:
    """
    Constrói o vetor de estado para o agente DQN a partir dos últimos N dias.
    
    Features por dia (3 features × 10 dias = 30 features):
    - close_pct: variação percentual do fechamento
    - volume_ratio: volume / média 20 dias
    - rsi_norm: RSI normalizado (0-1)
    """
    if len(df) < window + 20:
        return None

    try:
        close = df["Close"]
        volume = df["Volume"]
        rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
        volume_ma20 = volume.rolling(20).mean()

        state_features = []
        for i in range(-window, 0):
            close_pct = float((close.iloc[i] - close.iloc[i - 1]) / close.iloc[i - 1]) if i > -len(df) else 0
            vol_ratio = float(volume.iloc[i] / volume_ma20.iloc[i]) if volume_ma20.iloc[i] > 0 else 1.0
            rsi_norm = float(rsi.iloc[i] / 100.0) if not np.isnan(rsi.iloc[i]) else 0.5

            # Normalizar e clipar
            state_features.extend([
                np.clip(close_pct, -0.2, 0.2),
                np.clip(vol_ratio, 0, 5),
                rsi_norm,
            ])

        return np.array(state_features, dtype=np.float32)

    except Exception as e:
        logger.error(f"Erro ao construir estado DQN: {e}")
        return None


def dqn_recommend(df: pd.DataFrame) -> dict:
    """
    Executa o agente DQN para gerar uma recomendação.
    Se o modelo não estiver disponível, retorna None para usar fallback.
    """
    if not TORCH_AVAILABLE:
        return {"available": False, "reason": "PyTorch não instalado"}

    if not os.path.exists(WEIGHTS_PATH):
        return {"available": False, "reason": "Modelo DQN ainda não treinado"}

    state = build_state(df)
    if state is None:
        return {"available": False, "reason": "Dados insuficientes para o estado DQN"}

    try:
        model = DQNNetwork(state_size=30, action_size=3)
        model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
        model.eval()

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = model(state_tensor).numpy()[0]

        # Softmax para transformar Q-values em probabilidades
        q_exp = np.exp(q_values - np.max(q_values))
        probs = q_exp / q_exp.sum()

        action = int(np.argmax(q_values))
        confidence = round(float(probs[action]) * 100, 1)

        return {
            "available": True,
            "signal": ACTION_MAP[action],
            "confidence": confidence,
            "qValues": {"SELL": round(float(q_values[0]), 4), "HOLD": round(float(q_values[1]), 4), "BUY": round(float(q_values[2]), 4)},
            "probabilities": {"SELL": round(float(probs[0]) * 100, 1), "HOLD": round(float(probs[1]) * 100, 1), "BUY": round(float(probs[2]) * 100, 1)},
            "source": "dqn",
        }

    except Exception as e:
        logger.error(f"Erro na inferência DQN: {e}")
        return {"available": False, "reason": str(e)}
