# CodeArea chatbot

This repository runs Ollama independently on a Windows Desktop. It exposes the native chat and embedding API at `http://<windows-host>:11434` for the CodeArea Next.js application.

It intentionally contains no FastAPI proxy, ChromaDB, Supabase integration, PDF ingestion, or standalone administration UI. Problem retrieval and learner-safe pgvector indexing belong to the root CodeArea application.

## Initialize

Open PowerShell in `utils/chatbot`:

```powershell
Copy-Item .env.example .env
docker compose up -d
.\setup.ps1
docker compose ps
```

The setup script pulls the chat and embedding models configured in `.env`. Models persist in the `ollama-data` Docker volume.

Configure the root application with the Windows host name or IP and the native Ollama port:

```dotenv
OLLAMA_URL=http://windows-host:11434
OLLAMA_CHAT_MODEL=qwen3:4b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

Verify connectivity from the CodeArea host:

```bash
curl http://windows-host:11434/api/tags
```

Restrict Windows Firewall inbound TCP `11434` to the CodeArea host on a private LAN or VPN. Ollama's native API is unauthenticated and must not be exposed publicly.
