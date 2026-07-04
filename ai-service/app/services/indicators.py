import logging

import pandas as pd
import ta

logger = logging.getLogger(__name__)


def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    Calcula todos os indicadores técnicos a partir de um DataFrame OHLCV.
    
    Args:
        df: DataFrame com colunas Date, Open, High, Low, Close, Volume
    
    Returns:
        dict com todos os indicadores e suas interpretações
    """
    if df.empty or len(df) < 30:
        return {"error": "Dados insuficientes para calcular indicadores"}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # ── RSI (14 períodos) ──────────────────────────────────────────────────────
    rsi_series = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    rsi = round(float(rsi_series.iloc[-1]), 2) if not rsi_series.empty else None

    rsi_signal = "neutro"
    if rsi is not None:
        if rsi > 70:
            rsi_signal = "sobrecomprado"
        elif rsi < 30:
            rsi_signal = "sobrevendido"

    # ── MACD (12, 26, 9) ──────────────────────────────────────────────────────
    macd_indicator = ta.trend.MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    macd_line = macd_indicator.macd()
    macd_signal_line = macd_indicator.macd_signal()
    macd_hist = macd_indicator.macd_diff()

    macd_val = round(float(macd_line.iloc[-1]), 4) if not macd_line.empty else None
    macd_signal_val = round(float(macd_signal_line.iloc[-1]), 4) if not macd_signal_line.empty else None
    macd_hist_val = round(float(macd_hist.iloc[-1]), 4) if not macd_hist.empty else None

    macd_trend = "neutro"
    if macd_val is not None and macd_signal_val is not None:
        if macd_val > macd_signal_val:
            macd_trend = "alta"
        elif macd_val < macd_signal_val:
            macd_trend = "baixa"

    # ── Bandas de Bollinger (20, 2σ) ──────────────────────────────────────────
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    bb_upper = round(float(bb.bollinger_hband().iloc[-1]), 2) if not bb.bollinger_hband().empty else None
    bb_middle = round(float(bb.bollinger_mavg().iloc[-1]), 2) if not bb.bollinger_mavg().empty else None
    bb_lower = round(float(bb.bollinger_lband().iloc[-1]), 2) if not bb.bollinger_lband().empty else None

    current_price = round(float(close.iloc[-1]), 2)
    bb_position = "meio"
    if bb_upper and bb_lower and bb_upper != bb_lower:
        pct_b = (current_price - bb_lower) / (bb_upper - bb_lower)
        if pct_b > 0.8:
            bb_position = "próximo da banda superior"
        elif pct_b < 0.2:
            bb_position = "próximo da banda inferior"

    # ── Médias Móveis Simples ──────────────────────────────────────────────────
    ma9 = round(float(ta.trend.SMAIndicator(close=close, window=9).sma_indicator().iloc[-1]), 2)
    ma21 = round(float(ta.trend.SMAIndicator(close=close, window=21).sma_indicator().iloc[-1]), 2)
    ma50 = round(float(ta.trend.SMAIndicator(close=close, window=50).sma_indicator().iloc[-1]), 2) if len(df) >= 50 else None
    ma200 = round(float(ta.trend.SMAIndicator(close=close, window=200).sma_indicator().iloc[-1]), 2) if len(df) >= 200 else None

    # Verificar cruzamentos
    ma9_prev = float(ta.trend.SMAIndicator(close=close, window=9).sma_indicator().iloc[-2]) if len(df) > 9 else None
    ma21_prev = float(ta.trend.SMAIndicator(close=close, window=21).sma_indicator().iloc[-2]) if len(df) > 21 else None

    cross_signal = "sem cruzamento"
    if ma9_prev and ma21_prev:
        if ma9 > ma21 and ma9_prev <= ma21_prev:
            cross_signal = "golden cross (alta)"
        elif ma9 < ma21 and ma9_prev >= ma21_prev:
            cross_signal = "death cross (baixa)"
        elif ma9 > ma21:
            cross_signal = "tendência de alta"
        else:
            cross_signal = "tendência de baixa"

    # ── Volume ────────────────────────────────────────────────────────────────
    volume_ma20 = float(volume.rolling(window=20).mean().iloc[-1]) if len(df) >= 20 else None
    current_volume = int(volume.iloc[-1])
    volume_ratio = round(current_volume / volume_ma20, 2) if volume_ma20 and volume_ma20 > 0 else None

    volume_signal = "normal"
    if volume_ratio:
        if volume_ratio > 1.5:
            volume_signal = "acima da média"
        elif volume_ratio < 0.5:
            volume_signal = "abaixo da média"

    # ── Dados de variação ──────────────────────────────────────────────────────
    prev_close = round(float(close.iloc[-2]), 2) if len(df) > 1 else None
    day_change = round(current_price - prev_close, 2) if prev_close else None
    day_change_pct = round((day_change / prev_close) * 100, 2) if prev_close and prev_close > 0 else None

    open_price = round(float(df["Open"].iloc[-1]), 2)
    high_price = round(float(df["High"].iloc[-1]), 2)
    low_price = round(float(df["Low"].iloc[-1]), 2)

    # Máxima/Mínima 52 semanas (últimos 252 dias úteis)
    lookback_52w = min(252, len(df))
    high_52w = round(float(high.tail(lookback_52w).max()), 2)
    low_52w = round(float(low.tail(lookback_52w).min()), 2)

    return {
        "price": {
            "current": current_price,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "previousClose": prev_close,
            "change": day_change,
            "changePercent": day_change_pct,
            "high52w": high_52w,
            "low52w": low_52w,
        },
        "rsi": {
            "value": rsi,
            "signal": rsi_signal,
            "interpretation": f"RSI em {rsi} — {rsi_signal}",
        },
        "macdData": {
            "macd": macd_val,
            "signal": macd_signal_val,
            "histogram": macd_hist_val,
            "trend": macd_trend,
            "interpretation": f"MACD indica tendência de {macd_trend}",
        },
        "bollingerBands": {
            "upper": bb_upper,
            "middle": bb_middle,
            "lower": bb_lower,
            "position": bb_position,
            "interpretation": f"Preço {bb_position}",
        },
        "movingAverages": {
            "ma9": ma9,
            "ma21": ma21,
            "ma50": ma50,
            "ma200": ma200,
            "crossSignal": cross_signal,
            "interpretation": cross_signal,
        },
        "volume": {
            "current": current_volume,
            "ma20": int(volume_ma20) if volume_ma20 else None,
            "ratio": volume_ratio,
            "signal": volume_signal,
            "interpretation": f"Volume {volume_signal} (ratio: {volume_ratio}x)",
        },
    }


def generate_composite_signal(indicators: dict) -> dict:
    """
    Gera um sinal composto (BUY/HOLD/SELL) com base em todos os indicadores técnicos.
    Usado como fallback quando o modelo DQN não está disponível.
    """
    score = 0
    max_score = 0

    # RSI
    rsi = indicators.get("rsi", {})
    if rsi.get("value") is not None:
        max_score += 2
        rsi_val = rsi["value"]
        if rsi_val < 30:
            score += 2  # sobrevendido = sinal de compra
        elif rsi_val < 45:
            score += 1
        elif rsi_val > 70:
            score -= 2  # sobrecomprado = sinal de venda
        elif rsi_val > 60:
            score -= 1

    # MACD
    macd = indicators.get("macdData", {})
    if macd.get("trend"):
        max_score += 2
        if macd["trend"] == "alta":
            score += 2
        elif macd["trend"] == "baixa":
            score -= 2

    # Bollinger Bands
    bb = indicators.get("bollingerBands", {})
    if bb.get("position"):
        max_score += 2
        if "inferior" in bb["position"]:
            score += 2
        elif "superior" in bb["position"]:
            score -= 2

    # Médias Móveis
    ma = indicators.get("movingAverages", {})
    if ma.get("crossSignal"):
        max_score += 2
        if "golden" in ma["crossSignal"] or "alta" in ma["crossSignal"]:
            score += 2
        elif "death" in ma["crossSignal"] or "baixa" in ma["crossSignal"]:
            score -= 2

    # Volume confirma o movimento
    vol = indicators.get("volume", {})
    if vol.get("ratio") and vol["ratio"] > 1.5 and score != 0:
        score = int(score * 1.2)  # amplifica sinal com volume alto

    if max_score == 0:
        return {"signal": "HOLD", "confidence": 50.0, "source": "technical"}

    confidence = min(abs(score) / max_score * 100, 100)

    if score > 2:
        signal = "BUY"
    elif score < -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "confidence": round(confidence, 1),
        "score": score,
        "maxScore": max_score,
        "source": "technical",
    }
