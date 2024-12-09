from fastapi import FastAPI
import requests,logging
from Config.config import settings
from src.api.v1.weather.schemas.weather_schema import WeatherData
from src.api.v1.weather.models.weather_models import Weather
from src.api.v1.utils.response_utils import Response

logger = logging.getLogger(__name__)

class WeatherService:
    def get_weather(data_weather:WeatherData):
        if not settings.OPENWEATHER_API_KEY:
            return Response(status_code=500, message="API Key is not properly Configured.", data={}).send_error_response()
        try:
            response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={data_weather.city_name},{data_weather.state_code},{data_weather.country_code}&limit={data_weather.limit}&appid={settings.OPENWEATHER_API_KEY}")
            # response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric")

            if response.status_code != 200:
                return Response(status_code=404, message="City not found.Please check Spellings in City-name and Try again", data={}).send_error_response()

            data = response.json()
            logger.info(data)
            weather_data = {
                "city": data_weather.city_name,
                "local_names": data[0]['local_names'],
                "lat": data[0]['lat'],
                "lon": data[0]['lon'],
                "country": data[0]['country'],
                "state": data[0]['state']
            }
            
            return Weather(**weather_data)
        except requests.RequestException as e:
            return Response(status_code=500, message=str(e), data={}).send_error_response()
        

# class WeatherService:
#     def get_weather(city:str):
#         if not settings.OPENWEATHER_API_KEY:
#             return Response(status_code=500, message="API Key is not properly Configured.", data={}).send_error_response()
#         try:
#             response = requests.get(f"http://api.openweathermap.org/geo/1.0/zip?zip={zip code},{country code}&appid={settings.OPENWEATHER_API_KEY}")
#             # response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric")

#             if response.status_code != 200:
#                 return Response(status_code=404, message="City not found.Please check Spellings in City-name and Try again", data={}).send_error_response()

#             data = response.json()
#             weather_data = {
#                 "city": city,
#                 "temperature": data["main"]["temp"],
#                 "feels_like": data['main']['feels_like'],
#                 "temp_min": data['main']['temp_min'],
#                 "temp_max": data['main']['temp_max'],
#                 "humidity": data["main"]["humidity"],
#                 "wind_speed": data["wind"]["speed"],
#                 "description": data['weather'][0]['description'],
#                 "visibility": data['visibility'],
#             }
            
#             return Weather(**weather_data)
#         except requests.RequestException as e:
#             return Response(status_code=500, message=str(e), data={}).send_error_response()