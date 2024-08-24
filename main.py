from fastapi import FastAPI
from backend.settings import settings
from routers import weather

# Configuration of the FastAPI
app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    docs_url="/",
)

# Add the router to the app
app.include_router(weather.router)