from typing import List
from pydantic import BaseModel

class Property(BaseModel):
    location_id: int
    name: str
    name_insured: str
    description: str

class Properties(BaseModel):
    properties: List[Property]
