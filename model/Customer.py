from pydantic import BaseModel
from typing import Optional


class Customer(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
