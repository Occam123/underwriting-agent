from typing import List, Optional
import uuid
from datetime import datetime
from database import get_supabase_client
from model.Case import (
    Case, CaseStatus
)

class CaseService:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_case(self, title: str, customer_id: str) -> Case:
        """Create a new case"""
        case_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "status": CaseStatus.NEW.value,
            "agent_summary": None,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "case_year": 2025,
            "customer_id": customer_id

        }
        
        try:
            result = self.supabase.table("cases").insert(case_data).execute()
            return Case(**result.data[0])
        except Exception as e:
            print(f"❌ Error creating case: {str(e)}")
            raise

    async def get_case(self, case_id: str) -> Optional[Case]:
        """Get a case by ID"""
        try:
            result = self.supabase.table("cases").select("*").eq("id", case_id).execute()
            if result.data:
                return Case(**result.data[0])
            return None
        except Exception as e:
            print(f"❌ Error getting case: {str(e)}")
            raise

    async def update_case_status(self, case_id: str, status: CaseStatus, agent_summary: Optional[str] = None) -> Case:
        """Update case status and summary"""
        update_data = {
            "status": status.value,
            "last_updated": datetime.now().isoformat()
        }
        if agent_summary:
            update_data["agent_summary"] = agent_summary

        try:
            result = self.supabase.table("cases").update(update_data).eq("id", case_id).execute()
            return Case(**result.data[0])
        except Exception as e:
            print(f"❌ Error updating case status: {str(e)}")
            raise

    async def list_cases(
        self,
        status: Optional[CaseStatus] = None,
        customer_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Case]:
        """List cases, optionally filtered by status and/or customer_id."""
        try:
            query = self.supabase.table("cases").select("*")
            if status:
                query = query.eq("status", status.value)
            if customer_id:
                query = query.eq("customer_id", customer_id)
            query = query.range(offset, offset + limit - 1)
            result = query.execute()
            return [Case(**row) for row in result.data]
        except Exception as e:
            print(f"❌ Error listing cases: {str(e)}")
            raise

case_service = CaseService()