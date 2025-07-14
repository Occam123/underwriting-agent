from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class PropertyStatus(str, Enum):
    AWAITING_INFO = "awaiting info"
    DATA_EXTRACTED = "data extracted"
    QUOTED = "quoted"


class Property(BaseModel):
    id: Optional[str] = None
    case_id: str
    name: str
    status: PropertyStatus = PropertyStatus.AWAITING_INFO
    structured_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
