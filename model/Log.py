from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class LogType(str, Enum):
    INFO = "info"
    ACTION = "action"
    MILESTONE = "milestone"
    ERROR = "error"


class Log(BaseModel):
    id: Optional[str] = None
    case_id: Optional[str] = None
    building_id: Optional[str] = None
    linked_message_id: Optional[str] = None
    log_type: LogType
    content: str
    timestamp: Optional[datetime] = None
