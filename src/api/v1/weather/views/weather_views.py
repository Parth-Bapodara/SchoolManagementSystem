from fastapi import APIRouter, Depends
from src.api.v1.weather.schemas.weather_schema import ReverseWeatherData, WeatherData
from src.api.v1.utils.response_utils import Response
from src.api.v1.weather.models.weather_models import Weather
from src.api.v1.weather.services.weather_service import WeatherService

router = APIRouter()

@router.post("/weather-report-geocoding")
def get_weather(data:WeatherData):
    return WeatherService.get_weather(data)

@router.post("/weather-report-reverse-geocoding")
def get_reverse_weather(data:ReverseWeatherData):
    return WeatherService.get_reverse_weather(data)



