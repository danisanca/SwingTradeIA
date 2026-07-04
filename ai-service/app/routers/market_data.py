from fastapi import APIRouter, HTTPException, Query
from app.services.data_fetcher import fetch_history, fetch_quote, B3_STOCKS
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stocks")
async def list_stocks():
    """Retorna a lista de todas as ações monitoradas"""
    return [
        {"ticker": ticker, "name": info["name"], "sector": info["sector"]}
        for ticker, info in B3_STOCKS.items()
    ]


@router.get("/quote/{ticker}")
async def get_quote(ticker: str):
    """Retorna a cotação atual de uma ação"""
    ticker = ticker.upper()
    if ticker not in B3_STOCKS:
        raise HTTPException(status_code=404, detail=f"Ação {ticker} não encontrada")
    try:
        quote = fetch_quote(ticker)
        info = B3_STOCKS.get(ticker, {})
        return {**quote, "name": info.get("name"), "sector": info.get("sector")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{ticker}")
async def get_history(
    ticker: str,
    period: str = Query(default="MAX", description="Período: 1M, 3M, 6M, 1Y, 2Y, 5Y, MAX"),
):
    """
    Retorna o histórico OHLCV de uma ação.
    
    - **ticker**: Código da ação (ex: PETR4)
    - **period**: Período de dados (padrão: MAX)
    """
    ticker = ticker.upper()
    try:
        df = fetch_history(ticker, period)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para {ticker}")

        candles = df.to_dict(orient="records")
        return {
            "ticker": ticker,
            "period": period,
            "totalCandles": len(candles),
            "candles": candles,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes/all")
async def get_all_quotes():
    """Retorna cotações de todas as ações monitoradas (pode ser lento)"""
    results = []
    for ticker, info in B3_STOCKS.items():
        try:
            quote = fetch_quote(ticker)
            results.append({**quote, "name": info["name"], "sector": info["sector"]})
        except Exception as e:
            logger.warning(f"Falha ao buscar cotação de {ticker}: {e}")
            results.append({
                "ticker": ticker,
                "name": info["name"],
                "sector": info["sector"],
                "price": None,
                "error": True,
            })
    return results
