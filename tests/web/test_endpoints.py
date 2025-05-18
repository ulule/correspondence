import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthcheck(aclient: AsyncClient):
    response = await aclient.get("/healthcheck")
    assert response.status_code == 200
