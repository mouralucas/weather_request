from unittest.mock import patch, AsyncMock

import pytest
from starlette import status

import constants
from services.weather import WeatherService
from services.limiter import RequestLimiter


@pytest.mark.asyncio
async def test_get_weather_with_rate_limit(create_test_session):
    # Mocking the OpenWeather API response
    async def mock_get(url, params=None):
        class MockResponse:
            def json(self):
                return {"weather": "data in test"}

            async def raise_for_status(self):
                pass

        return MockResponse()

    # Use patch as a synchronous context manager and mock AsyncClient.get method
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get_method:
        mock_get_method.side_effect = mock_get  # Assign the async mock response to the mocked method

        user_id = 123
        session = create_test_session
        weather_service = WeatherService(session=session, user_id=user_id)

        rate_limiter = RequestLimiter(max_requests_per_period=2, period=3)  # Lower limit for testing
        weather_service.rate_limiter = rate_limiter  # Override rate limiter
        weather_service.cities = constants.CITIES_IDs_SHORT

        await weather_service.get()

        # The queue never can be more than the max requests per period
        # This ensures that no more than the max requests per period are exceeds in the runtime
        assert len(rate_limiter.queue) <= rate_limiter.max_requests_per_period


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
    user_id = 1

    with patch.object(WeatherService, 'get', return_value=AsyncMock()):
        payload = {
            'user_id': user_id,
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
    pass

