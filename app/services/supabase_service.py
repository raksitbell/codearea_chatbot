import os
from typing import Optional, Any
from supabase import Client, create_client
from fastapi import HTTPException
from app.core.config import settings

class SupabaseService:
    """
    Service to handle connections and interactions with Supabase.
    Centralizes client management and environment variable handling.
    """
    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Returns a singleton instance of the Supabase client.
        Raises HTTPException if configuration is missing.
        """
        if cls._instance is None:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_SERVICE_ROLE_KEY
            
            if not url or not key:
                raise HTTPException(
                    status_code=503,
                    detail="Supabase configuration is missing in the environment."
                )
            
            cls._instance = create_client(url, key)
            
        return cls._instance

# Direct access for simpler imports
def get_supabase() -> Client:
    return SupabaseService.get_client()
