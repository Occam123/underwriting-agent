from typing import Optional
import uuid
from database import get_supabase_client
from model.Customer import Customer


class CustomerService:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_customer(self, customer_name: str) -> Customer:
        """create a customer"""
        customer_data = {
            "id": str(uuid.uuid4()),
            "name": customer_name
        }

        try:
            result = self.supabase.table(
                "customers").insert(customer_data).execute()
            return Customer(**result.data[0])
        except Exception as e:
            print(f"❌ Error creating customer: {str(e)}")
            raise

    async def get_customer_by_name(self, customer_name: str) -> Optional[Customer]:
        """Get a customer by name. Returns the first match or None."""
        try:
            result = self.supabase.table("customers").select(
                "*").eq("name", customer_name).execute()
            if result.data:
                return Customer(**result.data[0])
            return None
        except Exception as e:
            print(f"❌ Error getting customer by name: {str(e)}")
            raise


customer_service = CustomerService()
