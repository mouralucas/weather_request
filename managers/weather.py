from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.weather import WeatherData


class WeatherManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_user(self, user_id: int) -> bool:
        """
         This functions checks if the user already exists in database
         If exists, return True, that indicates that the user already made a request
            and the user must be unique for each request
        """
        select_stmt = select(WeatherData).where(WeatherData.user_id == user_id)

        result = await self.session.scalars(select_stmt)
        result = result.all()

        return True if result else False

    async def save_city_weather(self, user_id: int, data: dict[str, Any]):
        """
        This functions saves the weather data to the database
        """
        weather = WeatherData(user_id=user_id, data=data)
        self.session.add(weather)
        await self.session.commit()
        await self.session.refresh(weather)

        return weather

    async def get_complete_cities(self, user_id: int):
        """
        This functions gets the percentage of processed cities
        """
        select_stmt = select(WeatherData).where(WeatherData.user_id == user_id).order_by(WeatherData.request_date)

        processed = await self.session.scalars(select_stmt)
        processed = processed.all()

        return processed
