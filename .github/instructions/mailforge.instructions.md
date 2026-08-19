---
description: "Use when working in the MailForge project: backend FastAPI, frontend React/Vite, environment config, or campaign API fixes. Follow the canonical project contract from context.json, keep local dev safe, and avoid repeated loops or unnecessary terminal commands."
applyTo: "**/*.{py,js,jsx,ts,tsx,json,md}" 
---

# MailForge project instructions

## Source of truth
- Treat [context.json](context.json) as the canonical project specification.
- Preserve the architecture described there: FastAPI backend, React/Vite frontend, PostgreSQL, Redis, and clean-layer separation.
- Keep the backend and frontend aligned with the project contract instead of improvising new patterns.

## Local development rules
- Use the existing venv in the workspace for Python work: `./venv/Scripts/Activate.ps1` in PowerShell.
- Do not automatically run terminal commands, install packages, or start servers unless the user explicitly asks.
- When the user wants commands, provide the exact commands for them to run manually and keep them minimal.
- Prefer editor/runtime validation over shell activity when possible.

## Environment and security
- Keep secrets in `.env` and do not commit them.
- Match the values in `.env.example` and the project settings in [backend/app/core/config.py](backend/app/core/config.py).
- Never expose secrets to the frontend or API responses.
- Keep JWT and provider credentials out of logs.

## API and browser behavior
- Keep CORS configured for local development origins such as `http://localhost:5173` and `http://localhost:8000`.
- Prefer Vite proxy rules for browser-to-backend development when the frontend is using relative paths like `/auth` and `/campaigns`.
- Ensure campaign routes accept the `Authorization` header and payload shape expected by the frontend.
- Preserve request/response contracts between [backend/app/api/routes/campaigns.py](backend/app/api/routes/campaigns.py) and [frontend/src/services/campaignApi.js](frontend/src/services/campaignApi.js).

## Project standards
- Prefer the existing service/repository structure and Pydantic schemas instead of introducing ad hoc wrappers.
- Validate route and schema changes with the smallest relevant checks.
- Keep code readable and consistent with the current repo style.
- When building or fixing features, favor the actual user workflow: authentication, templates, campaigns, and audience management.

## Working style
- Do not loop on repeated exploratory passes when the root cause is clear.
- Make the fix once, keep it minimal, and verify the changed behavior.
- If a change affects both backend and frontend, update both sides together.
- If the task is code generation, prefer directly implementing the fix in the repo instead of discussing theory.

## Manual startup commands
Provide these only when the user asks for startup steps:

Backend:
```powershell
cd backend
..\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

These commands are examples for manual execution only; do not run them automatically in this session unless the user explicitly asks.
