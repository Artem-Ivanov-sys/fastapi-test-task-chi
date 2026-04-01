import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.db import create_table_if_not_exist, drop_tables
from app.db_init.seed_data import fill_test_data
import asyncio
from asgi_lifespan import LifespanManager
from app.db.db import get_engine

ENGINE = get_engine()

# async def get_token(client: AsyncClient, username, password):
#     response = await client.post("/token", data={
#         "username": username,
#         "password": password
#     })
#     return response.json()["access_token"]

# @pytest.fixture(scope="session", autouse=True)
# def event_loop():
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()

# @pytest_asyncio.fixture(scope="function", autouse=True)
# async def db_prepare():
#     await drop_tables()
#     await create_table_if_not_exist()
#     await fill_test_data()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_users_one(client):
    # async with LifespanManager(app=app) as manager:
    #     transport = ASGITransport(app=manager.app)
    #     async with AsyncClient(transport=transport, base_url="http://test") as ac:
    #         response = await ac.get(f"/users/{'user1'}")
    response = await client.get(f"/users/{'user1'}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user1"


@pytest.mark.asyncio
async def test_get_users_many(client):
    # async with LifespanManager(app=app) as manager:
    #     transport = ASGITransport(app=manager.app)
    #     async with AsyncClient(transport=transport, base_url="http://test") as ac:
    #         response = await ac.get(f"/users/")
    response = await client.get(f"/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3