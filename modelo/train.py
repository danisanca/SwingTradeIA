"""
train.py — Loop de treinamento do agente DQN para Swing Trade B3

Uso:
    python train.py --ticker PETR4 --episodes 500
    python train.py --ticker VALE3 --episodes 1000 --train-ratio 0.8
"""
import argparse
import os
import sys
import logging
import numpy as np
import yfinance as yf

# Adiciona diretório pai ao path para importar ambiente e rede
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelo.environment import SwingTradeEnv
from modelo.dqn_network import DQNAgent
from modelo.replay_buffer import ReplayBuffer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_EPISODES = 500
DEFAULT_BATCH_SIZE = 64
DEFAULT_BUFFER_CAPACITY = 50_000
DEFAULT_TRAIN_RATIO = 0.8       # 80% dos dados para treino, 20% para teste
DEFAULT_WINDOW = 10             # dias de janela de observação
DEFAULT_WARMUP_STEPS = 500      # passos antes de iniciar o aprendizado
MODEL_SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "ai-service", "app", "models")


def fetch_data(ticker: str) -> "pd.DataFrame":
    import pandas as pd
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    logger.info(f"Baixando dados de {yf_ticker} (histórico máximo)...")
    df = yf.Ticker(yf_ticker).history(period="max")
    if df.empty:
        raise ValueError(f"Nenhum dado encontrado para {yf_ticker}")
    df = df.reset_index()
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna()
    logger.info(f"Total de {len(df)} candles diários carregados.")
    return df


def split_data(df, train_ratio: float):
    n = len(df)
    split = int(n * train_ratio)
    return df.iloc[:split].reset_index(drop=True), df.iloc[split:].reset_index(drop=True)


def train(
    ticker: str,
    episodes: int = DEFAULT_EPISODES,
    batch_size: int = DEFAULT_BATCH_SIZE,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
    window: int = DEFAULT_WINDOW,
    warmup_steps: int = DEFAULT_WARMUP_STEPS,
    save_best: bool = True,
):
    # 1. Dados
    df = fetch_data(ticker)
    train_df, test_df = split_data(df, train_ratio)
    logger.info(f"Treino: {len(train_df)} candles | Teste: {len(test_df)} candles")

    # 2. Ambiente e Agente
    env = SwingTradeEnv(df=train_df, window=window)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        lr=1e-4,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.997,
        target_update_freq=50,
    )
    buffer = ReplayBuffer(capacity=DEFAULT_BUFFER_CAPACITY, batch_size=batch_size)

    # 3. Loop de Treinamento
    best_net_worth = 0.0
    rewards_history = []
    losses_history = []

    logger.info(f"🚀 Iniciando treinamento — {episodes} episódios — Ticker: {ticker}")
    logger.info(f"   State size: {state_size} | Actions: {action_size} | Window: {window}d")

    for ep in range(1, episodes + 1):
        state, _ = env.reset()
        total_reward = 0.0
        ep_losses = []
        done = False

        while not done:
            action = agent.act(state, training=True)
            next_state, reward, done, _, _ = env.step(action)
            buffer.push(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            # Só aprende após warmup e quando buffer tem amostras suficientes
            if len(buffer) > warmup_steps and buffer.ready():
                batch = buffer.sample()
                loss = agent.learn(batch)
                ep_losses.append(loss)

        rewards_history.append(total_reward)
        avg_loss = np.mean(ep_losses) if ep_losses else 0.0
        losses_history.append(avg_loss)

        # Salvar melhor modelo
        if save_best and env.net_worth > best_net_worth:
            best_net_worth = env.net_worth
            os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
            save_path = os.path.join(MODEL_SAVE_DIR, f"dqn_weights.pth")
            agent.save(save_path)
            logger.info(f"   💾 Novo melhor: R${best_net_worth:.2f} — salvo em {save_path}")

        # Log a cada 50 episódios
        if ep % 50 == 0 or ep == 1:
            avg_reward = np.mean(rewards_history[-50:])
            logger.info(
                f"Ep {ep:4d}/{episodes} | "
                f"Reward: {avg_reward:+.4f} | "
                f"Loss: {avg_loss:.5f} | "
                f"Epsilon: {agent.epsilon:.3f} | "
                f"Net Worth: R${env.net_worth:.2f}"
            )

    logger.info(f"\n✅ Treinamento concluído! Melhor patrimônio: R${best_net_worth:.2f}")
    return agent, train_df, test_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinar agente DQN para Swing Trade B3")
    parser.add_argument("--ticker", type=str, default="PETR4", help="Código da ação (ex: PETR4)")
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--train-ratio", type=float, default=DEFAULT_TRAIN_RATIO)
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP_STEPS)
    args = parser.parse_args()

    train(
        ticker=args.ticker,
        episodes=args.episodes,
        batch_size=args.batch_size,
        train_ratio=args.train_ratio,
        window=args.window,
        warmup_steps=args.warmup,
    )
