"""

yfinance router to search tickers

"""
from fastapi import APIRouter, Query
import httpx

router = APIRouter()

YF_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}

@router.get('/search')
async def search_ticker(q: str = Query(..., min_length=1), quotes_count: int = 8):
    
    params = {"q": q, "quotes_count": quotes_count, "news_count": 0}
    async with httpx.AsyncClient(timeout=8, headers=headers) as client:
        r = await client.get(YF_SEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()
    results = []
    for it in data.get("quotes", [])[:quotes_count]:
        if not it.get("symbol"):
            continue
        results.append({
                "symbol":  it["symbol"],
                "shortname": it.get("shortname"),
                "exchDisp": it.get("exchDisp"),
                "typeDisp": it.get("typeDisp"),
            })
    
    return {"results": results}