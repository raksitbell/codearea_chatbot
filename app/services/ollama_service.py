import os
import ollama
from typing import List, Optional, Dict, Any
from app.services.supabase_service import get_supabase

class OllamaService:
    """
    Service to handle low-level interactions with the Ollama instance.
    Includes configuration management and connectivity verification.
    """

    @staticmethod
    def get_config() -> Dict[str, str]:
        """
        Retrieves Ollama configuration from Supabase 'system_settings'.
        """
        try:
            sb = get_supabase()
            res = sb.table("system_settings").select("value").eq("key", "ollama_config").single().execute()
            if res.data and "value" in res.data:
                return res.data["value"]
        except Exception as e:
            print(f"Ollama Config Error: {e}")
            
        return {
            "url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_CHAT_MODEL", "ai-tutor")
        }

    @staticmethod
    def update_config(url: str, model: str) -> bool:
        """
        Persists Ollama configuration to Supabase.
        """
        try:
            sb = get_supabase()
            sb.table("system_settings").upsert({
                "key": "ollama_config",
                "value": {"url": url, "model": model},
                "updated_at": "now()"
            }).execute()
            return True
        except Exception as e:
            print(f"Ollama Update Error: {e}")
            return False

    @staticmethod
    def list_models_for_url(url: str) -> List[str]:
        """
        Lists models available at a specific Ollama URL.
        Used for the 'Test Connection' and dynamic listing features.
        """
        try:
            client = ollama.Client(host=url)
            res = client.list()
            return [m["name"] for m in (res.get("models") or []) if "name" in m]
        except Exception as e:
            print(f"Ollama listing failed for {url}: {e}")
            return []

    @staticmethod
    def test_connection(url: str) -> Dict[str, Any]:
        """
        Verifies connectivity to a specific Ollama instance.
        """
        try:
            client = ollama.Client(host=url)
            # Short test with list() to verify accessibility
            models = client.list()
            return {
                "connected": True,
                "models_count": len(models.get("models", [])),
                "message": "Connection established successfully."
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "message": f"Failed to connect to {url}"
            }
