"""
evaluate.py — Avaliação do agente DQN vs estratégia Buy & Hold

Uso:
    python evaluate.py --ticker PETR4 --model-path ../ai-service/app/models/dqn_weights.pth
"""
import argparse
import os
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelo.environment import SwingTradeEnv
from modelo.dqn_network import DQNAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def fetch_test_data(ticker: str, test_ratio: float = 0.2) -> pd.DataFrame:
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    df = yf.Ticker(yf_ticker).history(period="max")
    df = df.reset_index()
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna()
    split = int(len(df) * (1 - test_ratio))
    return df.iloc[split:].reset_index(drop=True)


def run_dqn(env: SwingTradeEnv, agent: DQNAgent) -> list[float]:
    """Roda o agente DQN no ambiente e retorna o histórico de patrimônio"""
    state, _ = env.reset()
    history = [env.initial_balance]
    done = False
    while not done:
        action = agent.act(state, training=False)
        state, _, done, _, _ = env.step(action)
        history.append(env.net_worth)
    return history


def run_buy_and_hold(df: pd.DataFrame, initial_balance: float = 10_000.0) -> list[float]:
    """Simula compra no primeiro dia e mantém até o final"""
    if df.empty:
        return [initial_balance]
    first_price = float(df["Close"].iloc[0])
    shares = initial_balance / first_price
    return [shares * float(df["Close"].iloc[i]) for i in range(len(df))]


def evaluate(ticker: str, model_path: str, test_ratio: float = 0.2, initial_balance: float = 10_000.0):
    logger.info(f"📊 Avaliando agente DQN para {ticker}")

    # Dados de teste
    test_df = fetch_test_data(ticker, test_ratio)
    logger.info(f"Período de teste: {test_df['Date'].iloc[0]} → {test_df['Date'].iloc[-1]} ({len(test_df)} dias)")

    # Ambiente
    env = SwingTradeEnv(df=test_df, window=10, initial_balance=initial_balance)
    state_size = env.observation_space.shape[0]

    # Agente
    agent = DQNAgent(state_size=state_size, action_size=3)
    if os.path.exists(model_path):
        agent.load(model_path)
    else:
        logger.warning(f"Modelo não encontrado em {model_path} — usando agente aleatório")

    # Executar estratégias
    dqn_history = run_dqn(env, agent)
    bah_history = run_buy_and_hold(test_df, initial_balance)

    # Alinhar tamanhos
    min_len = min(len(dqn_history), len(bah_history))
    dqn_history = dqn_history[:min_len]
    bah_history = bah_history[:min_len]
    dates = pd.to_datetime(test_df["Date"].values[:min_len])

    # Métricas
    dqn_final = dqn_history[-1]
    bah_final = bah_history[-1]
    dqn_return = (dqn_final - initial_balance) / initial_balance * 100
    bah_return = (bah_final - initial_balance) / initial_balance * 100

    logger.info("\n" + "="*50)
    logger.info(f"  RESULTADO — {ticker} — Período de Teste")
    logger.info("="*50)
    logger.info(f"  DQN Agent:     R${dqn_final:,.2f}  ({dqn_return:+.2f}%)")
    logger.info(f"  Buy & Hold:    R${bah_final:,.2f}  ({bah_return:+.2f}%)")
    logger.info(f"  Outperformance: {dqn_return - bah_return:+.2f}%")
    logger.info("="*50)

    # Plotar gráfico comparativo
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]})
    fig.patch.set_facecolor("#0a0d14")
    fig.suptitle(f"SwingTradeIA — {ticker} | DQN vs Buy & Hold", fontsize=14, color="white", fontweight="bold")

    ax1 = axes[0]
    ax1.set_facecolor("#141928")
    ax1.plot(dates, dqn_history, color="#48bb78", linewidth=2, label=f"DQN ({dqn_return:+.2f}%)")
    ax1.plot(dates, bah_history, color="#fc8181", linewidth=2, linestyle="--", label=f"Buy & Hold ({bah_return:+.2f}%)")
    ax1.axhline(y=initial_balance, color="#4a5568", linewidth=1, linestyle=":", alpha=0.7)
    ax1.set_ylabel("Patrimônio (R$)", color="white")
    ax1.tick_params(colors="white", axis="both")
    ax1.legend(facecolor="#1a2035", labelcolor="white", fontsize=11)
    ax1.spines["bottom"].set_color("#2d3748")
    ax1.spines["left"].set_color("#2d3748")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(True, color="#1a2035", alpha=0.7)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b/%Y"))

    # Preço da ação
    ax2 = axes[1]
    ax2.set_facecolor("#141928")
    ax2.plot(dates, test_df["Close"].values[:min_len], color="#4299e1", linewidth=1.5)
    ax2.set_ylabel("Preço (R$)", color="white")
    ax2.set_xlabel("Data", color="white")
    ax2.tick_params(colors="white", axis="both")
    ax2.spines["bottom"].set_color("#2d3748")
    ax2.spines["left"].set_color("#2d3748")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(True, color="#1a2035", alpha=0.7)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b/%Y"))

    plt.tight_layout()
    chart_path = f"evaluation_{ticker}.png"
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), dpi=150, bbox_inches="tight")
    logger.info(f"\n📈 Gráfico salvo em: {chart_path}")
    plt.show()

    return {
        "ticker": ticker,
        "dqn_final": dqn_final,
        "bah_final": bah_final,
        "dqn_return_pct": dqn_return,
        "bah_return_pct": bah_return,
        "outperformance_pct": dqn_return - bah_return,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avaliar agente DQN vs Buy & Hold")
    parser.add_argument("--ticker", type=str, default="PETR4")
    parser.add_argument("--model-path", type=str, default="../ai-service/app/models/dqn_weights.pth")
    parser.add_argument("--test-ratio", type=float, default=0.2)
    parser.add_argument("--initial-balance", type=float, default=10_000.0)
    args = parser.parse_args()

    evaluate(
        ticker=args.ticker,
        model_path=args.model_path,
        test_ratio=args.test_ratio,
        initial_balance=args.initial_balance,
    )
