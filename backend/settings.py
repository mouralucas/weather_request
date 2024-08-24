from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database and test settings
    database_url: str = 'sqlite+aiosqlite:///dev.sqlite3'
    test_database_url: str = 'sqlite+aiosqlite:///test.sqlite3'
    echo_sql: bool = False
    echo_test_sql: bool = True
    test: bool = False

    # Project description
    project_name: str = "Cities Weather"
    project_description: str = "Service to fetch weather data for a list of cities"
    project_version: str = "0.0.1"

    # Weather API
    open_weather_url: str = 'https://api.openweathermap.org/data/2.5/weather'
    open_weather_api_key: str = ''
    open_weather_rate_limit: int = 1
    open_weather_rate_limit_period: int = 60  # in seconds

settings = Settings()
