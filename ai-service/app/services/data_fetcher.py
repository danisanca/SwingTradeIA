import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Mapeamento de ações brasileiras com sufixo .SA do Yahoo Finance
B3_STOCKS = {
    "PETR4": {"name": "Petrobras PN", "sector": "Petróleo & Gás"},
    "VALE3": {"name": "Vale ON", "sector": "Mineração"},
    "ITUB4": {"name": "Itaú Unibanco PN", "sector": "Financeiro"},
    "BBDC4": {"name": "Bradesco PN", "sector": "Financeiro"},
    "ABEV3": {"name": "Ambev ON", "sector": "Bebidas"},
    "WEGE3": {"name": "WEG ON", "sector": "Industrial"},
    "RENT3": {"name": "Localiza ON", "sector": "Mobilidade"},
    "MGLU3": {"name": "Magazine Luiza ON", "sector": "Varejo"},
    "BBAS3": {"name": "Banco do Brasil ON", "sector": "Financeiro"},
    "EGIE3": {"name": "Engie Brasil ON", "sector": "Energia Elétrica"},
    "VIVT3": {"name": "Telefônica ON", "sector": "Telecomunicações"},
    "SUZB3": {"name": "Suzano ON", "sector": "Papel & Celulose"},
    "LREN3": {"name": "Lojas Renner ON", "sector": "Varejo"},
    "HAPV3": {"name": "Hapvida ON", "sector": "Saúde"},
    "RADL3": {"name": "Raia Drogasil ON", "sector": "Saúde"},
}

PERIOD_MAP = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "2Y": "2y",
    "5Y": "5y",
    "MAX": "max",
}


def get_yahoo_ticker(ticker: str) -> str:
    """Converte ticker B3 para formato Yahoo Finance (adiciona .SA)"""
    if not ticker.endswith(".SA"):
        return f"{ticker.upper()}.SA"
    return ticker.upper()


def fetch_history(ticker: str, period: str = "MAX") -> pd.DataFrame:
    """
    Busca histórico OHLCV de uma ação via yfinance.
    
    Args:
        ticker: Código da ação (ex: PETR4)
        period: Período (1M, 3M, 6M, 1Y, 2Y, 5Y, MAX)
    
    Returns:
        DataFrame com colunas: Date, Open, High, Low, Close, Volume
    """
    yf_period = PERIOD_MAP.get(period.upper(), "max")
    yf_ticker = get_yahoo_ticker(ticker)

    try:
        logger.info(f"Buscando histórico de {yf_ticker} — período: {yf_period}")
        stock = yf.Ticker(yf_ticker)
        hist = stock.history(period=yf_period)

        if hist.empty:
            logger.warning(f"Nenhum dado retornado para {yf_ticker}")
            return pd.DataFrame()

        hist = hist.reset_index()
        hist["Date"] = pd.to_datetime(hist["Date"]).dt.strftime("%Y-%m-%d")
        hist = hist[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        hist = hist.dropna(subset=["Close"])
        hist = hist[hist["Close"] > 0]

        logger.info(f"Retornados {len(hist)} candles para {yf_ticker}")
        return hist

    except Exception as e:
        logger.error(f"Erro ao buscar dados de {yf_ticker}: {e}")
        raise


def fetch_quote(ticker: str) -> dict:
    """
    Busca cotação atual da ação.
    
    Returns:
        dict com price, change, changePercent, volume, previousClose
    """
    yf_ticker = get_yahoo_ticker(ticker)
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.fast_info

        current_price = getattr(info, "last_price", None)
        previous_close = getattr(info, "previous_close", None)

        change = None
        change_pct = None
        if current_price and previous_close and previous_close > 0:
            change = round(current_price - previous_close, 2)
            change_pct = round((change / previous_close) * 100, 2)

        return {
            "ticker": ticker.upper(),
            "price": round(current_price, 2) if current_price else None,
            "change": change,
            "changePercent": change_pct,
            "volume": getattr(info, "three_month_average_volume", None),
            "previousClose": round(previous_close, 2) if previous_close else None,
            "yearHigh": getattr(info, "year_high", None),
            "yearLow": getattr(info, "year_low", None),
            "marketCap": getattr(info, "market_cap", None),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar cotação de {yf_ticker}: {e}")
        raise
