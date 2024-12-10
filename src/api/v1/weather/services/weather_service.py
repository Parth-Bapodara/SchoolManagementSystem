from fastapi import FastAPI
import requests,logging
from Config.config import settings
from src.api.v1.weather.schemas.weather_schema import WeatherData,ReverseWeatherData
from src.api.v1.weather.models.weather_models import Weather
from src.api.v1.utils.response_utils import Response

logger = logging.getLogger(__name__)

class WeatherService:
     #GEO Coding
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
            
            weather_list=[]
            for item in data:
                 local_names_en = item.get("local_names", {}).get("en")
                 weather_data = {
                         "city_name": data_weather.city_name,
                         "local_names": local_names_en,
                         "lat": item.get("lat"),
                         "lon": item.get("lon"),
                         "country": item.get("country"),
                         "state": item.get("state")
                     }
                 weather_list.append(weather_data)
            if not weather_list:
                return Response(status_code=200, message="No city found at given coordinates.", data=weather_list).send_success_response()
            return Response(status_code=200, message="Records Fetched Successfully.", data=weather_list).send_success_response()

        except requests.RequestException as e:
            return Response(status_code=500, message=str(e), data={}).send_error_response()
        
      #Reverse GEO Coding
     def get_reverse_weather(data_reverse_weather:ReverseWeatherData):
         
        if not settings.OPENWEATHER_API_KEY:
            return Response(status_code=500, message="API Key is not properly Configured.", data={}).send_error_response()
        try:
            response = requests.get(f"http://api.openweathermap.org/geo/1.0/reverse?lat={data_reverse_weather.lat}&lon={data_reverse_weather.lon}&limit={data_reverse_weather.limit}&appid={settings.OPENWEATHER_API_KEY}")

            if response.status_code != 200:
                return Response(status_code=404, message="Latitute and Longtitude not found.Please check Try again", data={}).send_error_response()
            
            data = response.json()
            logger.info(data)

            weather_list = []
            for item in data:
                local_names_en = item.get("local_names", {}).get("en")
                weather_data = {
                         "city": item.get("name"),
                         "local_names": local_names_en,
                         "country": item.get("country"),
                         "state": item.get("state")
                     }
                weather_list.append(weather_data)
                
            if not weather_list:
                return Response(status_code=200, message="No city found at given coordinates.", data=weather_list).send_success_response()
            return Response(status_code=200, message="Records Fetched Successfully.", data=weather_list).send_success_response()
        
        except requests.RequestException as e:
            return Response(status_code=500, message=str(e), data={}).send_error_response()

#Normal Data Fetching from openweather API
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

# weather_data = {
            #     "city": data_weather.city_name,
            #     "local_names": data[0]['local_names'],
            #     "lat": data[0]['lat'],
            #     "lon": data[0]['lon'],
            #     "country": data[0]['country'],
            #     "state": data[0]['state']
            # }
            
            # return Weather(**weather_data)