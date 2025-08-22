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
route = "/clientes"


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


# Tests


async def test_list_clients(async_client):
    response = await async_client.get(route + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "João Silva"


async def test_get_client_by_id(async_client):
    list_response = await async_client.get(f"{route}/")
    assert list_response.status_code == 200
    client = list_response.json()
    assert len(client) > 0, "Não há clientes cadastrados para testar"

    client_id = client[0]["id"]

    response = await async_client.get(f"{route}/{client_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id


async def test_get_client_not_found(async_client):
    fake_id = str(uuid4())

    response = await async_client.get(route + fake_id)

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


async def test_create_client(async_client):
    payload = {"name": "Carlos Pereira", "email": "carlos@example.com"}

    response = await async_client.post(route + "/", json=payload)

    new_id = await async_client.get(route + "/")
    clients = new_id.json()

    assert response.status_code == 201
    data = response.json()
    last_client = clients[-1]
    assert data["id"] == last_client["id"]
    assert data["name"] == "Carlos Pereira"
