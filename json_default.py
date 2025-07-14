from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from config.Config import config

def json_default(obj):
    from helpers import datetime_to_string  
    # 1) Datetimes → formatted strings
    if isinstance(obj, datetime):
        return datetime_to_string(datetime=obj, format=config.DATETIME.OUTPUT_FORMAT)
    
    # 2) Pydantic models → dict
    if isinstance(obj, BaseModel):
        # use .dict() so nested models are handled too
        return obj.dict()
    
    # 3) Enums → their raw value
    if isinstance(obj, Enum):
        return obj.value

    # Let the JSON encoder know we can’t handle this
    raise TypeError(f"Type {type(obj)} not serializable")