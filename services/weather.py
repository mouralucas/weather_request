import asyncio

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

import constants
from backend.settings import settings
from managers.weather import WeatherManager
from services.limiter import RequestLimiter

class WeatherService:
    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id
        self.weather_manager = WeatherManager(session=self.session)
        self.rate_limiter = RequestLimiter(max_requests_per_period=2, period=5)
        self.cities = constants.CITIES_IDs

    async def _fetch_weather(self, city_id: int, client: httpx.AsyncClient):
        payload = {
            "id": city_id,
            "appid": settings.open_weather_api_key,
            "units": "metric"
        }
        response = await client.get(settings.open_weather_url, params=payload)
        response = response.json()
        # Create the JSON to save in database with the id of the city, the temperature in Celsius and humidity
        data = {
            'city_id': response['id'],
            'temperature_c': response['main']['temp'],
            'humidity': response['main']['humidity'],
        }
        # save to the database
        await self.weather_manager.save_city_weather(self.user_id, data=data)
        return data


    async def get(self):
        async with httpx.AsyncClient() as client:
            # Process the list of cities
            tasks = [await self.rate_limiter.fetch_with_rate_limit(self._fetch_weather, city, client) for city in self.cities]
            results = await asyncio.gather(*[])
        return results