from fastapi import APIRouter, Depends
from src.api.v1.weather.schemas.weather_schema import WeatherData
from src.api.v1.utils.response_utils import Response
from src.api.v1.weather.models.weather_models import Weather
from src.api.v1.weather.services.weather_service import WeatherService

router = APIRouter()

@router.post("/weather-report")
def get_weather(data:WeatherData):
    return WeatherService.get_weather(data)






