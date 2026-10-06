# MeetBridge AI

MeetBridge AI is a real-time AI meeting copilot designed to listen with consent, understand what is being asked, retrieve relevant context from personal and organizational knowledge bases, and suggest concise responses during live meetings.

Version: 1.0.0

## Product overview

The project delivers a privacy-aware meeting assistant with:
- voice and transcript capture flow
- meeting state tracking and semantic retrieval
- question detection and suggested responses
- knowledge base retrieval with evaluation metrics
- enterprise controls such as auth, RBAC, audit logging, rate limits, and secure uploads

## Monorepo structure

- `frontend/` — Next.js + React + TypeScript + Tailwind UI
- `backend/` — FastAPI + SQLAlchemy + Pydantic service layer
- `infrastructure/` — deployment and infrastructure support
- `docs/` — architecture, checklists, and walkthroughs

## Local development

1. Copy `.env.example` to `.env` and update secrets.
2. Start infrastructure:
   ```bash
   docker compose up -d postgres redis
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. Install backend dependencies:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Open http://localhost:3000

## Production deployment target

MeetBridge AI is designed for a containerized deployment model with:
- AWS ALB in front of the frontend and API
- ECS Fargate or EKS services for runtime workloads
- RDS PostgreSQL for application data
- Redis for temporary state and caching
- Secrets Manager for JWT keys and provider secrets
- CloudWatch for logging and observability

See [docs/architecture.md](docs/architecture.md) for the architecture view, [docs/release-checklist.md](docs/release-checklist.md) for release gates, [docs/security-checklist.md](docs/security-checklist.md) for security controls, and [docs/demo-walkthrough.md](docs/demo-walkthrough.md) for the product walkthrough.

## Release status

This repository is prepared as a v1.0.0 release candidate with the key operating, quality, and release artifacts in place:
- backend tests and critical-flow coverage
- frontend type-checking
- production runtime configuration validation
- Docker container definitions
- GitHub Actions CI workflow
- architecture and deployment documentation

## Git workflow

This project is intentionally structured to advance in small, reviewable steps. Each milestone is committed separately with tests and documentation maintained before continuing.
