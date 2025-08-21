import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from uuid import uuid4

transport = ASGITransport(app=app)
base_url = "http://localhost:8000"
route = "/clients"

@pytest.mark.asyncio
async def test_list_clients():
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.get(route + "/")
        
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "João Silva"
    
@pytest.mark.asyncio
async def test_get_client_by_id():
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        
        list_response = await ac.get(route)
        client_id = list_response.json()[0]["id"]
        
        response = await ac.get(route + "/" + client_id)
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id

@pytest.mark.asyncio
async def test_get_client_not_found():
    
    fake_id = str(uuid4())
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
    
        response = await ac.get(route + fake_id)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"
    
@pytest.mark.asyncio
async def test_create_client():
    
    payload = {"name": "Carlos Pereira", "email": "carlos@example.com"}
    
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        response = await ac.post(route + "/", json=payload)
        
        new_id = await ac.get(route)
    
    assert response.status_code == 200
    data = response.json()
    new_id_len = len(new_id)
    assert data["id"] == new_id[new_id_len - 1]["id"]
    assert data["name"] == "Carlos Pereira"