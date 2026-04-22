from fastapi import APIRouter, HTTPException
from app.schemas.ai import OllamaConfigRequest
from app.services.ollama_service import OllamaService

router = APIRouter()

@router.get("/ollama")
async def get_config():
    """Retrieve the current Ollama configuration."""
    return OllamaService.get_config()

@router.post("/ollama")
async def update_config(request: OllamaConfigRequest):
    """Update the Ollama configuration in the database."""
    if OllamaService.update_config(request.url, request.model, request.embedding_model):
        return {"message": "Configuration updated successfully."}
    raise HTTPException(status_code=500, detail="Failed to update configuration.")

@router.get("/models")
async def list_models():
    """List available models based on current saved configuration."""
    config = OllamaService.get_config()
    models = OllamaService.list_models_for_url(config.get("url"))
    return {"models": models}

@router.post("/test-connection")
async def test_connection(request: OllamaConfigRequest):
    """
    Test connectivity to a specific Ollama instance and return available models.
    This fulfills the requirement of 'Test Connection' and dynamic 'List Model'.
    """
    result = OllamaService.test_connection(request.url)
    if result["connected"]:
        # Also return models so the UI can populate the list immediately
        models = OllamaService.list_models_for_url(request.url)
        result["models"] = models
    return result
