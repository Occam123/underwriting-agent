from datetime import datetime
from config.Config import config

def json_default(obj):
    from helpers import datetime_to_string  
    if isinstance(obj, datetime):
        return datetime_to_string(datetime=obj, format=config.DATETIME.OUTPUT_FORMAT)
    raise TypeError(f"Type {type(obj)} not serializable")