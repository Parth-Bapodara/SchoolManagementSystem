from typing import Optional
from pydantic import BaseModel,Field, field_validator
from src.api.v1.utils.response_utils import Response
from pydantic_extra_types.coordinate import Longitude, Latitude, Coordinate

class WeatherData(BaseModel):
    city_name: str
    state_code: Optional[str] = Field(default="")
    country_code: Optional[int] = None
    limit: Optional[int] = None

class ReverseWeatherData(BaseModel):
    lat: float = Field(default=0.00)
    lon: float = Field(default=0.00)
    limit: Optional[int] = None

    # @field_validator('lat')
    # def lat_check(cls,value):
    #     if value > 90 and value < -90:
    #         return Response(status_code=422, message="Invalid Input for Latitute.It should be in between -90 and 90.", data={}).send_error_response()
    
    # @field_validator('lon')
    # def lon_check(cls,value):
    #     if value > 180 and value < -180:
    #         return Response(status_code=422, message="Invalid Input for Longtitute.It should be in between -90 and 90.", data={}).send_error_response()

