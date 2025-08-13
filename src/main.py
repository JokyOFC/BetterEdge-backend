'''

Main project file

created in 12/08/2025 by Joky

'''

from fastapi import FastAPI
from api import routes_allocations, routes_assets, routes_clients, routes_daily_returns

app = FastAPI(title="BetterEdge", version="1.0", description="")

app.include_router(routes_allocations.router, prefix="/alocacoes", tags=["Alocações"])
app.include_router(routes_clients.router, prefix="/clientes", tags=["Clientes"])
app.include_router(routes_assets.router, prefix="/ativos", tags=["Ativos"])
app.include_router(routes_daily_returns.router, prefix="/dailyReturns", tags=["Retornos Diários"])

@app.get("/")
def home():
    return {"status": "ok", "message": "API de investimento pronta!"}
