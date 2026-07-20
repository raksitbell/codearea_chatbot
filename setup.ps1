$ErrorActionPreference = "Stop"

docker compose exec ollama ollama pull qwen3:4b
docker compose exec ollama ollama pull nomic-embed-text

Write-Host "CodeArea chatbot is ready on port 11434."
