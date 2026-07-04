from fastapi import APIRouter, HTTPException
from app.services.data_fetcher import fetch_history, B3_STOCKS
from app.services.indicators import calculate_indicators, generate_composite_signal
from app.services.dqn_agent import dqn_recommend
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/recommend/{ticker}")
async def get_recommendation(ticker: str):
    """
    Retorna a recomendação completa para uma ação:
    - Indicadores técnicos (RSI, MACD, Bollinger, MA, Volume)
    - Sinal DQN (se modelo disponível)
    - Sinal composto de análise técnica (fallback)
    """
    ticker = ticker.upper()
    if ticker not in B3_STOCKS:
        raise HTTPException(status_code=404, detail=f"Ação {ticker} não encontrada")

    try:
        # Buscar dados históricos (1 ano para cálculo de indicadores)
        df = fetch_history(ticker, "1Y")
        if df.empty or len(df) < 30:
            raise HTTPException(status_code=422, detail="Dados insuficientes para análise")

        # Calcular indicadores técnicos
        indicators = calculate_indicators(df)

        # Sinal de análise técnica
        technical_signal = generate_composite_signal(indicators)

        # Tentar sinal DQN
        dqn_result = dqn_recommend(df)

        # Sinal final: DQN se disponível, fallback para técnico
        if dqn_result.get("available"):
            final_signal = {
                "signal": dqn_result["signal"],
                "confidence": dqn_result["confidence"],
                "source": "dqn",
            }
        else:
            final_signal = {
                "signal": technical_signal["signal"],
                "confidence": technical_signal["confidence"],
                "source": "technical",
            }

        return {
            "ticker": ticker,
            "name": B3_STOCKS[ticker]["name"],
            "finalSignal": final_signal,
            "dqn": dqn_result,
            "technicalSignal": technical_signal,
            "indicators": indicators,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar recomendação para {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
