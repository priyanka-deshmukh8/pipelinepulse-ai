# PipelinePulse AI — Data Incident Copilot

An AI-assisted backend for tracking data-pipeline incidents, classifying failures, retrieving similar historical incidents, and drafting root-cause summaries, remediation steps, and closure notes.

> **Safety:** Recommendations are advisory. The service does not rerun pipelines, change production infrastructure, or close incidents automatically. Review every recommendation before acting. Use synthetic or sanitized logs only.

## Features

- FastAPI REST API with interactive OpenAPI docs.
- Incident creation, listing, retrieval, status updates, and retry-count tracking.
- Failure classification for common permission, connectivity, schema/data-quality, and Spark/compute errors.
- Historical incident retrieval using a transparent lexical baseline.
- Optional Azure OpenAI analysis when configured; deterministic fallback works without credentials.
- PostgreSQL via Docker Compose; SQLite for quick local development.
- Pytest API tests and GitHub Actions CI.

## Architecture

```text
Client / Swagger UI
        |
        v
FastAPI routes ---- Pydantic validation
        |
        +---- SQLAlchemy ---- PostgreSQL / SQLite
        |
        +---- Incident analysis service
                  |---- Failure classification fallback
                  |---- Historical incident retrieval (lexical baseline)
                  |---- Optional Azure OpenAI
```

## Run locally (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

The default database is local SQLite, so no cloud credentials are required for the first run.

## Run with Docker and PostgreSQL

1. Copy `.env.example` to `.env`.
2. Ensure Docker Desktop is running.
3. Run:

```powershell
docker compose up --build
```

Open http://localhost:8000/docs. Docker Compose overrides the database URL to use the included PostgreSQL service.

## Configure Azure OpenAI (optional)

Set these values in your local `.env` file:

```dotenv
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR_KEY
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT=YOUR_CHAT_DEPLOYMENT_NAME
```

Never commit `.env` or expose keys in screenshots, logs, issues, or source code. The configured deployment must support JSON-object response formatting. Without complete configuration, the service uses its deterministic fallback.

## API quick start

Create an incident:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d "{\"pipeline_name\":\"daily-sales-load\",\"error_message\":\"CAST_INVALID_INPUT: empty string cannot be cast to INT\"}"
```

Analyze it (replace `1` with the returned ID):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/incidents/1/analyze
```

Other endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/incidents` | Create incident |
| GET | `/api/v1/incidents` | List incidents; optional `status`, `limit`, `offset` |
| GET | `/api/v1/incidents/{id}` | Get incident |
| POST | `/api/v1/incidents/{id}/analyze` | Classify and draft recommendations |
| POST | `/api/v1/incidents/{id}/retry-count` | Increment retry count |
| PATCH | `/api/v1/incidents/{id}/status` | Update status |

## Tests

```powershell
pytest -q
```

## Roadmap

- Replace lexical retrieval with embedding-based semantic retrieval and a vector store (for example, pgvector or Azure AI Search).
- Add authenticated access, tenant isolation, audit events, and rate limiting before production use.
- Add offline evaluation datasets for retrieval quality and AI output quality.
- Add deployment configuration for a managed hosting provider and managed PostgreSQL.

## Current limitations

This is an initial portfolio MVP. It does not yet implement true vector embeddings, multi-tenant authorization, automated retries, or production-grade audit logging. Do not use it to make unsupervised changes to production pipelines.
# pipelinepulse-ai
