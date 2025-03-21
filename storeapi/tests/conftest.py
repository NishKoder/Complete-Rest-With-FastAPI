import asyncio
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"
from storeapi.database import database, user_table
from storeapi.main import app


@pytest.fixture(scope="session")
def aasync_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def db() -> Generator[None, None, None]:
    await database.connect()
    yield
    await database.disconnect()
    yield


# Updated async_client fixture using ASGITransport.
@pytest.fixture()
def async_client(client) -> AsyncClient:
    transport = ASGITransport(app=app)
    ac = AsyncClient(transport=transport, base_url=client.base_url)
    yield ac
    asyncio.run(ac.aclose())


@pytest.fixture()
async def register_user(async_client) -> None:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/api/v1/users/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    result = await database.fetch_one(query)
    user_details["id"] = result["id"]
    return user_details
