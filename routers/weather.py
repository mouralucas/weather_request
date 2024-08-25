import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from ratelimit import sleep_and_retry, limits
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import constants
from backend.database import db_session
from backend.settings import settings
from managers.weather import WeatherManager
from services.weather import WeatherService

router = APIRouter(prefix='/weather', tags=['Weather'])


class RequestData(BaseModel):
    user_id: int = Field(..., alias='user_id')
    cities: list[int] | None = Field(None, alias='cities')


class ResponseData(BaseModel):
    title: str = Field(..., alias='title', description='Short description of the response')
    message: str = Field(..., alias='message', description='The complete description of the response')


@router.post('', summary='', description='', status_code=status.HTTP_202_ACCEPTED)
async def weather(
        request: RequestData,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(db_session)
) -> ResponseData:
    user_exists = await WeatherManager(session=session).check_user(user_id=request.user_id)
    # Check if the user already request the weather data
    if user_exists:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='User already request weather data')

    # Run the request in de background because it takes a long time to complete
    service = WeatherService(session=session, user_id=request.user_id, cities=request.cities)
    background_tasks.add_task(service.get_openweather_data)

    response = ResponseData(
        title='Collecting weather data',
        message='The system are already collecting weather data for the requested user.'
                'You can check the percentage of completion using the get endpoint /weather?user_id={user_id}'.format(user_id=request.user_id),
    )
    return response


@router.get('', summary='', description='')
async def get_weather(
        request: RequestData = Depends(),
        session: AsyncSession = Depends(db_session)
):
    # Get the percentage of processed cities
    percentage = await WeatherManager(session=session).get_complete_cities(user_id=request.user_id)

    return {'percentage': percentage}
