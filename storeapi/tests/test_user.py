import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password):
    data = {"email": email, "password": password}
    response = await async_client.post("/api/v1/users/register", json=data)
    return response

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_user_already_exists(async_client: AsyncClient):
    await register_user(async_client, "test@example.com", "1234")
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_user_not_registered(async_client: AsyncClient):
    response = await async_client.post("/api/v1/users/token", json={"email": "test@example.com", "password": "1234"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    await register_user(async_client, "test@example.com", "1234")
    response = await async_client.post(
        "/api/v1/users/token",
        json={"email": "test@example.com", "password": "1234"},
    )
    assert response.status_code == 200