import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from storeapi.main import app
from storeapi.routers.post import comment_table, post_table


@pytest.fixture(scope="session")
def aasync_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def db() -> Generator[None, None, None]:
    post_table.clear()
    comment_table.clear()
    yield


# Updated async_client fixture using ASGITransport.
@pytest.fixture()
def async_client(client) -> AsyncClient:
    transport = ASGITransport(app=app)
    ac = AsyncClient(transport=transport, base_url=client.base_url)
    yield ac
    asyncio.run(ac.aclose())