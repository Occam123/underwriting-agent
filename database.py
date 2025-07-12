from supabase import create_client, Client
from config.Config import config


# Supabase configuration
SUPABASE_URL = config.SUPABASE.URL
SUPABASE_KEY = config.SUPABASE.KEY
# This should be the service role key
SUPABASE_SERVICE_ROLE_KEY = config.SUPABASE.SERVICE_ROLE_KEY


if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  Warning: Supabase credentials not found in environment variables")
    print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")

# Create Supabase client
supabase: Client = create_client(
    SUPABASE_URL or "", SUPABASE_KEY or "") if SUPABASE_URL and SUPABASE_KEY else None

supabase_service: Client = create_client(
    SUPABASE_URL or "", SUPABASE_SERVICE_ROLE_KEY or "") if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY else None


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    if not supabase:
        raise Exception(
            "Supabase client not initialized. Please check your environment variables.")
    return supabase


def get_supabase_service_client() -> Client:
    """Get Supabase service client instance for storage operations"""
    if not supabase_service:
        raise Exception(
            "Supabase service client not initialized. Please check SUPABASE_SERVICE_ROLE_KEY.")
    return supabase_service
