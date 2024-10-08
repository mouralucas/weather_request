import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from backend.database import db_session
from backend.database import test_sessionmanager
from main import app
from managers.weather import WeatherManager
from models.weather import Base


# Basic configuration to run the tests, with data and Session mocks

@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def create_data_in_database(create_test_session):
    # Add mock data to the database for the user_id=1
    data_list = []
    user_id = 1
    data = {
        'city_id': 12345,
        'temp_c': 35,
        'humidity': 48
    }
    data_1 = await WeatherManager(create_test_session).save_city_weather(user_id, data)

    data = {
        'city_id': 12345,
        'temp_c': 24,
        'humidity': 76
    }
    data_2 = await WeatherManager(create_test_session).save_city_weather(user_id, data)

    data_list.append(data_1)
    data_list.append(data_2)

    return data_list


@pytest_asyncio.fixture(scope='function')
async def create_test_session():
    # Create a new database session for tests
    async with test_sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with test_sessionmanager.session() as session:
        yield session


@pytest_asyncio.fixture(scope='function', autouse=True)
def override_db_session(create_test_session):
    # Overrides the database session, in this case using test_sessionmanager.
    app.dependency_overrides[db_session] = lambda: create_test_session


@pytest_asyncio.fixture(scope='function', autouse=True)
async def client():
    # Create the test client for all tests
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
