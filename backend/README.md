# MeetBridge AI Backend

This backend is the initial FastAPI scaffold for MeetBridge AI. It provides a health-checked application shell, environment configuration, and database-ready structure for future repository, service, and AI modules.

## Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API endpoints

- `GET /health`
- `GET /api/health`
