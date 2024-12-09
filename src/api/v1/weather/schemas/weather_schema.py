from typing import Optional
from pydantic import BaseModel,Field, field_validator
from src.api.v1.utils.response_utils import Response


class WeatherData(BaseModel):
    city_name: str
    state_code: Optional[str] = None
    country_code: Optional[int] = None
    limit: Optional[int] = None

    # @field_validator('state_code')
    # def state_code_cehck(cls, value):
    #     if value < 2:
    #         return Response(status_code=400, message="Invalid Input.Please check inputed state code and try again.")
    #     return value
