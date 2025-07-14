import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from database import get_supabase_client
from model.Property import Property, PropertyStatus


class PropertyService:
    """
    Service for creating and updating building records within a case.
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_building(
        self,
        case_id: str,
        name: str,
        structured_data: Optional[Dict[str, Any]] = None
    ) -> Property:
        """Create a new building attached to the given case."""
        building_data = {
            "id": str(uuid.uuid4()),
            "case_id": case_id,
            "name": name,
            "status": PropertyStatus.AWAITING_INFO.value,
            "structured_data": structured_data or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        try:
            result = self.supabase.table(
                "buildings").insert(building_data).execute()
            return Property(**result.data[0])
        except Exception as e:
            print(f"❌ Error creating building: {e}")
            raise

    async def update_building_status(
        self,
        building_id: str,
        status: PropertyStatus,
        structured_data: Optional[Dict[str, Any]] = None
    ) -> Property:
        """Update the status (and optionally data) of an existing building."""
        update_data: Dict[str, Any] = {
            "status": status.value,
            "updated_at": datetime.now().isoformat(),
        }
        if structured_data is not None:
            update_data["structured_data"] = structured_data

        try:
            result = (
                self.supabase
                .table("buildings")
                .update(update_data)
                .eq("id", building_id)
                .execute()
            )
            return Property(**result.data[0])
        except Exception as e:
            print(f"❌ Error updating building status: {e}")
            raise

    async def update_building_data(
        self,
        building_id: str,
        structured_data: Dict[str, Any]
    ) -> Property:
        """Replace the structured_data of an existing building."""
        update_data = {
            "structured_data": structured_data,
            "updated_at": datetime.now().isoformat(),
        }
        try:
            result = (
                self.supabase
                .table("buildings")
                .update(update_data)
                .eq("id", building_id)
                .execute()
            )
            return Property(**result.data[0])
        except Exception as e:
            print(f"❌ Error updating building data: {e}")
            raise


# Singleton instance for app-wide use
property_service = PropertyService()
