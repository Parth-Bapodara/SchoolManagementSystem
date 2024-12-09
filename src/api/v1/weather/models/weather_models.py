from pydantic import BaseModel

class Weather(BaseModel):
    city: str
    local_names: dict
    lat: float
    lon: float
    country: str
    state: str
    
# class Weather(BaseModel):
#     city: str
#     temperature: float
#     feels_like: float
#     temp_min: float
#     temp_max: float
#     humidity: float
#     wind_speed: float
#     description: str
#     visibility: int
