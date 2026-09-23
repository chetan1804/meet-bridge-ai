# MeetBridge AI Frontend

This frontend is a Next.js application that renders the live meeting copilot shell described in the product specification. It includes the meeting UI, transcript panel, question panel, action controls, and a modern Tailwind layout for incremental iteration.

## Configuration

The browser API base URL is configured through `NEXT_PUBLIC_API_URL`. It defaults to `http://localhost:8000` for local development; set it in the root `.env` file when deploying the frontend separately.

## Authentication

The dashboard requires a user session. Start the backend and apply its migrations before registering at `/register`; the session token is kept in browser local storage for this incremental client-side implementation.

The desktop dashboard includes a workspace switcher populated from the organization API and a settings page. The selected workspace is retained in browser local storage; feature data will become tenant-scoped when its domain APIs are added.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000
