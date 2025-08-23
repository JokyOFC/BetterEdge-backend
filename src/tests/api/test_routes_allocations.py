import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from uuid import uuid4

transport = ASGITransport(app=app)
base_url = "http://localhost:8000"
route = "/alocacoes"


@pytest.mark.asyncio
async def test_list_allocations():
    async with AsyncClient(
        transport=transport, base_url=base_url, follow_redirects=True
    ) as ac:
        # search for (asset)

        response = await ac.get(route + "/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_allocations_by_id():
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        list_alocations = await ac.get(route)
        alocation_id = list_alocations.json()[0]["id"]

        response = await ac.get(route + "/" + alocation_id)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alocation_id


@pytest.mark.asyncio
async def test_get_allocation_by_client_id():
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        list_clients = await ac.get("/clients/")
        clients_id = list_clients.json()[0]["id"]

        response = await ac.get(route + "?client=" + clients_id)

    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == clients_id
    assert isinstance(data["allocations"], list)


@pytest.mark.asyncio
async def test_fake_get_allocations_by_id():
    fake_id = uuid4()

    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.get(route + "/" + fake_id)

    assert response.status_code == 404
    assert response.json()["detail"] == "Allocation not found"


@pytest.mark.asyncio
async def test_post_allocation():
    async with AsyncClient(
        transport=transport, base_url=base_url, follow_redirects=True
    ) as ac:
        response = await ac.post(route + "/", json={"asset": "PETR4", "percetage": 50})

    assert response.status_code == 200
    assert response.json() == {}
