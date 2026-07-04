from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market_data, dqn

app = FastAPI(
    title="SwingTradeIA — AI Service",
    description="Serviço de dados de mercado e recomendações DQN para Swing Trade em ações brasileiras",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_data.router, prefix="/market-data", tags=["Market Data"])
app.include_router(dqn.router, prefix="/dqn", tags=["DQN"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "SwingTradeIA AI Service"}
