import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API de investimento pronta!"}
