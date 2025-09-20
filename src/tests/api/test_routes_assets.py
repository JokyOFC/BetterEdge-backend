import asyncio
import pytest_asyncio
from src.db.database import get_session
from httpx import AsyncClient, ASGITransport
from src.main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from src.config import settings

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DATABASE_URL = settings.DATABASE_URL

base_url = "http://test"
route = "/ativos"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(async_session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

async def test_list_assets(async_client):
    response = await async_client.get(route + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    

async def test_list_assets_by_id(async_client):
    list_assets = await async_client.get(f"{route}/")
    assert list_assets.status_code == 200
    assets = list_assets.json()
    assert len(assets) > 0, "Não há assets para testar"
    
    asset_id = assets[0]["id"]
    
    response = await async_client.get(f"{route}/{asset_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == asset_id
    

async def test_get_asset_not_found(async_client):
    fake_id = str(uuid4())

    response = await async_client.get(route + fake_id)

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"
    

async def test_get_asset_by_ticker(async_client):
    list_assets = await async_client.get(f"{route}/")
    assert list_assets.status_code == 200
    assets = list_assets.json()
    assert len(assets) > 0, "Não há assets para testar"
    
    ticker_id = assets[0]["ticker"]
    
    response = await async_client.get(f"{route}/ticker/{ticker_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == ticker_id

async def test_post_asset(async_client):
    
    payload = {
        "ticker": "BPAC11.SA",
        "name": "Banco BTG Pactual SA Unit",
        "asset_type": "acao",
        "currency":"BRL",
        "default_fee_rate": "46.03", 
        "has_dividend": True
    }
    
    response = await async_client.post(route + "/", json=payload)
    new_id = await async_client.get(route + "/")
    assets = new_id.json()
    
    assert response.status_code == 201
    data = response.json()
    last_asset = assets[-1]
    assert data["id"] == last_asset["id"]
    