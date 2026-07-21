$ErrorActionPreference = "Stop"

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}

function Get-DotEnvValue {
    param([string]$Name, [string]$Default)

    $Line = Get-Content .env |
        Where-Object { $_ -match "^$([Regex]::Escape($Name))=" } |
        Select-Object -Last 1
    if (-not $Line) {
        return $Default
    }

    return $Line.Split("=", 2)[1].Trim().Trim('"').Trim("'")
}

$ChatModel = Get-DotEnvValue "OLLAMA_CHAT_MODEL" "qwen3:4b"
$EmbedModel = Get-DotEnvValue "OLLAMA_EMBED_MODEL" "nomic-embed-text"

docker compose exec ollama ollama pull $ChatModel
docker compose exec ollama ollama pull $EmbedModel

Write-Host "CodeArea chatbot is ready on port 11434."
