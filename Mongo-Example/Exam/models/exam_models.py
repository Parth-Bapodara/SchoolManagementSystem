from pydantic import BaseModel

class ToDo(BaseModel):
    name: str
    description: str
    complete: bool