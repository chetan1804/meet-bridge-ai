# MeetBridge AI Backend

This backend provides a health-checked FastAPI application shell, environment configuration, and a SQLAlchemy/Alembic foundation. Feature tables will be added through their owning feature migrations rather than pre-created.

## Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database migrations

Start PostgreSQL first, then apply migrations from `backend/`:

```bash
alembic upgrade head
```

The initial migration establishes the Alembic baseline without creating product tables. Use `alembic revision --autogenerate -m "..."` only when a feature introduces SQLAlchemy models.

## API endpoints

- `GET /health`
- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/organizations`
- `GET /api/organizations`
- `GET /api/organizations/{organization_id}`
- `GET|POST /api/organizations/{organization_id}/members`

Every registered account receives a personal workspace. Shared workspace endpoints require a bearer token and scope resource access through the caller's membership; inaccessible workspace IDs return `404` to avoid disclosing another tenant's data.
