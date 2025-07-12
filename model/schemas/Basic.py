from typing import List, Optional
from pydantic import BaseModel

class ListOfStrings(BaseModel):
    values: List[str] = []

class StringValue(BaseModel):
    value: Optional[str] = None