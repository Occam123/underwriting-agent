import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from database import get_supabase_client
from model.Log import (
    Log, LogType
)

class LogService:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def log_event(
            self, 
            log_type: LogType, 
            content: str, 
            case_id: Optional[str] = None, 
            building_id: Optional[str] = None, 
            linked_message_id: Optional[str] = None
        ) -> Log:
        """Log an event"""
        log_data = {
            "id": str(uuid.uuid4()),
            "case_id": case_id,
            "building_id": building_id,
            "linked_message_id": linked_message_id,
            "log_type": log_type.value,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table("logs").insert(log_data).execute()
            return Log(**result.data[0])
        except Exception as e:
            print(f"❌ Error logging event: {str(e)}")
            raise

log_service = LogService()