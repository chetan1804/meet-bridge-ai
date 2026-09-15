# MeetBridge AI

MeetBridge AI is a real-time AI meeting copilot designed to listen with consent, understand what is being asked, retrieve relevant context from personal and organizational knowledge bases, and suggest concise responses during live meetings.

## Monorepo structure

- `frontend/` — Next.js + React + TypeScript + Tailwind UI
- `backend/` — FastAPI + SQLAlchemy + Pydantic service layer
- `infrastructure/` — deployment and infrastructure support
- `docs/` — product, architecture, and development notes
- `scripts/` — automation and local helper scripts

## Key product principles

- visible consent and recording state
- privacy-first, opt-in meeting capture
- tenant-aware access control
- AI reasoning that clearly distinguishes transcript, interpretation, evidence, and suggested response
- modular, provider-based LLM and speech integrations

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

## Architecture notes

The initial scaffold intentionally keeps the setup incremental and production-minded. It includes a real-time UI shell, a health-checked API, environment configuration, and a database/runtime foundation for future implementation via the 40-commit incremental roadmap in the product brief.

## Git workflow

This project is intentionally structured to advance in small, reviewable steps. Each meaningful milestone should be committed separately, with tests and documentation updated before continuing.
