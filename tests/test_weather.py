from collections import deque
from unittest.mock import patch, AsyncMock

import pytest
from starlette import status

import constants
from services.weather import WeatherService
from services.limiter import RequestLimiter


@pytest.mark.asyncio
async def test_get_openweather_data(create_test_session):
    # Mocking the OpenWeather API response
    async def mock_get(url, params=None):
        class MockResponse:
            def json(self):
                return {
                    'id': "31",
                    'main': {
                        'temp': 35,
                        'humidity': 65
                    }
                }

            async def raise_for_status(self):
                pass

        return MockResponse()

    # Use patch as a synchronous context manager and mock AsyncClient.get method
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get_method:
        mock_get_method.side_effect = mock_get  # Assign the async mock response to the mocked method

        user_id = 123
        session = create_test_session
        weather_service = WeatherService(session=session, user_id=user_id)

        # Lower request limit for testing
        request_limiter = RequestLimiter
        max_limit = 2
        request_limiter.MAX_REQUESTS_PER_PERIOD = max_limit
        request_limiter.PERIOD = 10
        request_limiter.REQUEST_QUEUE = deque(maxlen=max_limit)

        # Override request limiter in WeatherService
        weather_service.request_limiter = request_limiter
        # User a short list of cities
        weather_service.cities = constants.CITIES_IDs_SHORT

        await weather_service.get_openweather_data()

        # The queue never can be more than the max requests per period
        # This ensures that no more than the max requests per period are exceeds in the runtime
        assert len(request_limiter.REQUEST_QUEUE) == request_limiter.MAX_REQUESTS_PER_PERIOD


@pytest.mark.asyncio
async def test_get_percentage(create_test_session, create_data_in_database):
    user_id = 1
    session = create_test_session # use mocked session
    data_processed = create_data_in_database # create mack data
    cities = constants.CITIES_IDs_SHORT  # use the short list in tests
    weather_service = WeatherService(session=session, user_id=user_id, cities=cities)

    response = await weather_service.get_percentage()

    assert type(response) is float
    assert len(data_processed) / len(cities) * 100 == response


@pytest.mark.asyncio
async def test_weather_endpoint_user_already_exists(client, create_data_in_database):
    """
        The rule is that user_id must be unique for each request, that means if the id exists in table
        the user already made a request to the server
    """
    payload = {
        'user_id': 1,
    }
    response = await client.post("/weather", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User already request weather data"}


@pytest.mark.asyncio
async def test_weather_endpoint_new_user(client):
    async def mock_get(url, params=None):
        class MockResponse:
            def json(self):
                return {
                    'id': "31",
                    'main': {
                        'temp': 35,
                        'humidity': 65
                    }
                }

            async def raise_for_status(self):
                pass

        return MockResponse()

    # Use patch as a synchronous context manager and mock AsyncClient.get method
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get_method:
        mock_get_method.side_effect = mock_get  # Assign the async mock response to the mocked method

        # Override the limiter to test faster
        request_limiter = RequestLimiter
        max_limit = 2
        request_limiter.MAX_REQUESTS_PER_PERIOD = max_limit
        request_limiter.PERIOD = 11
        request_limiter.REQUEST_QUEUE = deque(maxlen=max_limit)

        user_id = 456

        payload = {
            'user_id': user_id,
            'cities': constants.CITIES_IDs_SHORT,  # Pass a short list of cities in test
        }
        response = await client.post("/weather", json=payload)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {
            "title": "Collecting weather data",
            "message": "The system are already collecting weather data for the requested user."
                       "You can check the percentage of completion using the get endpoint /weather?user_id={user_id}".format(user_id=user_id),
        }


@pytest.mark.asyncio
async def test_get_endpoint(client, create_test_session):
    # Mocking the OpenWeather API response
    async def mock_get(url, params=None):
        class MockResponse:
            def json(self):
                return {
                    'id': "31",
                    'main': {
                        'temp': 35,
                        'humidity': 65
                    }
                }

        return MockResponse()

    # Use patch as a synchronous context manager and mock AsyncClient.get method
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get_method:
        mock_get_method.side_effect = mock_get  # Assign the async mock response to the mocked method

        # Override the limiter to test faster
        request_limiter = RequestLimiter
        max_limit = 2
        request_limiter.MAX_REQUESTS_PER_PERIOD = max_limit
        request_limiter.PERIOD = 10
        request_limiter.REQUEST_QUEUE = deque(maxlen=max_limit)

        user_id = 123

        payload = {
            'user_id': user_id,
            'cities': constants.CITIES_IDs_SHORT,  # Pass a short list of cities in test
        }
        response = await client.post("/weather", json=payload)
        assert response.status_code == status.HTTP_202_ACCEPTED

    # The get endpoint do not need to mock the get call to OpenWeather
    response = await client.get("/weather", params={'user_id': user_id})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'percentage' in data
