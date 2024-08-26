import asyncio

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

import constants
from backend.settings import settings
from managers.weather import WeatherManager
from services.limiter import RequestLimiter


class WeatherService:
    def __init__(self, session: AsyncSession, user_id: int, request_limiter=None, cities=None):
        self.session = session
        self.user_id = user_id
        self.weather_manager = WeatherManager(session=self.session)
        self.request_limiter = request_limiter or RequestLimiter
        self.cities = cities or constants.CITIES_IDs

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

    async def get_openweather_data(self):
        async with httpx.AsyncClient() as client:
            # Process the list of cities
            tasks = [await self.request_limiter.call_external_api(self._fetch_weather, city, client) for city in self.cities]
            results = await asyncio.gather(*[])
        return results

    async def get_percentage(self) -> float:
        # Get the list of processed cities
        processed_cities = await WeatherManager(session=self.session).get_complete_cities(self.user_id)

        # Calculate the percentage of processed cities
        qtd_processed = len(processed_cities) if processed_cities else 0
        completion_percent = (qtd_processed / len(self.cities)) * 100

        return completion_percent