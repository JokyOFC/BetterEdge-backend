import redis.asyncio as redis
import asyncio
import yfinance as yf
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.config import settings
from src.tasks.celery_app import app


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

redis = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

@app.task(name="refresh_quotes")
def refresh_quotes():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.create_task(_refresh_quotes_async())
    else:
        return loop.run_until_complete(_refresh_quotes_async())
    
async def _refresh_quotes_async():
    async for session in get_session():
        tickers = await _get_distinct_tickers(session)
        for symbol in tickers:
            try:
                
                cached = await _get_price_from_cache(symbol)
                if cached:
                    price, prev = cached
                else:
                    price, prev = await _fetch_price(symbol)
                    await _set_price_to_cache(symbol, price, prev)
                await _save_quote(session, symbol, price, prev)
            except Exception as e:
                print(f"Erro ao atualizar {symbol}: {e}")
        await session.commit()
        
async def _get_distinct_tickers(session: AsyncSession):
    from sqlalchemy import select
    from src.db.models.core_models import Asset
    res = await session.execute(select(Asset.ticker).distinct())
    print(res)
    return [row[0] for row in res.all()]

async def _fetch_price(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="2d")
    if data.empty:
        raise ValueError(f"Sem dados para {symbol}")
    if len(data) == 1 :
        price = float(data["Close"].iloc[-1])
        prev = price
    else:
        price = float(data["Close"].iloc[-1])
        prev = float(data["Close"].iloc[-2])
        
    return price, prev

async def _save_quote(session: AsyncSession, symbol: str, price: float, prev: float):
    from datetime import datetime, timezone
    from src.db.models.core_models import PriceQuote
    from sqlalchemy.dialects.postgresql import insert
    
    stmt = insert(PriceQuote).values(
        ticker=symbol,
        price=price,
        prev_close=prev,
        updated_at=datetime.now(timezone.utc),
    ).on_conflict_do_update(
        index_elements=["ticker"],  # coluna única
        set_={
            "price": price,
            "prev_close": prev,
            "updated_at": datetime.now(timezone.utc),
        },
    )
    await session.execute(stmt)
    
async def _get_price_from_cache(symbol: str):
    key = f"price:{symbol}"
    data = await redis.get(key)
    if data:
        price, prev = map(float, data.split(","))
        return price, prev
    return None

async def _set_price_to_cache(symbol: str, price: float, prev: float):
    key = f"price:{symbol}"
    await redis.set(key, f"{price},{prev}", ex=settings.YF_CACHE_TTL_SEC)
    

