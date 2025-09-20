import asyncio
import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.db.models.core_models import PriceQuote

CACHE_TTL = settings.YF_CACHE_TTL_SEC

async def _fetch_quote_yf(ticker:str) -> tuple[float, float]:
    
    def _sync_fetch():
        
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = float(info.get("last_price"))
        prev = float(info.get("previous_close"))
        
        return price, prev
    
    return await asyncio.to_thread(_sync_fetch())

async def get_quote(session: AsyncSession, ticker: str) -> tuple[float, float]:
    q = await session.execute(select(PriceQuote).where(PriceQuote.ticker == ticker))
    pq = q.scalar_one_or_none()
    now = datetime.utcnow()
    if pq and (now - pq.updated_at) < timedelta(seconds=CACHE_TTL):
        return float(pq.price), float(pq.prev_close)
    
    price, prev = await _fetch_quote_yf(ticker)
    if pq:
        pq.price, pq.prev_close, pq.updated_at = price, prev, now
    else:
        pq = PriceQuote(ticker=ticker, price=price, prev_close=prev, updated_at=now)
        session.add(pq)
        
    await session.commit()
    return price, prev
    
