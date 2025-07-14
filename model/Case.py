from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class CaseStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    AWAITING_INFO = "awaiting info"
    QUOTED = "quoted"


class Case(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    status: CaseStatus = CaseStatus.NEW
    agent_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None