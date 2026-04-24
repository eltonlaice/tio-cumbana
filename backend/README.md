# Tio Cumbana — Backend

FastAPI + Opus 4.7 multimodal pipeline.

## Setup

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `POST /api/consult` — multipart: `photo`, `audio`, `farmer_phone`. Returns Tio Cumbana response (text + synthesised voice URL).
- `POST /api/proactive` — scripted proactive-trigger demo.
- `GET /health` — liveness.
