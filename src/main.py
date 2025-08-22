"""

Main project file

created in 12/08/2025 by Joky

"""

from fastapi import FastAPI
from src.api import (
    routes_allocations,
    routes_assets,
    routes_clients,
    routes_daily_returns,
)
from starlette.middleware.gzip import GZipMiddleware

app = FastAPI(title="BetterEdge", version="1.0", description="")
app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(routes_allocations.router, prefix="/alocacoes", tags=["Alocações"])
app.include_router(routes_clients.router, prefix="/clientes", tags=["Clientes"])
app.include_router(routes_assets.router, prefix="/ativos", tags=["Ativos"])
app.include_router(
    routes_daily_returns.router, prefix="/dailyReturns", tags=["Retornos Diários"]
)


@app.get("/")
def home():
    return {"status": "ok", "message": "API de investimento pronta!"}
