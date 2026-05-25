# Codex Task Prompt

You are implementing the MVP for RaceNavi AI.

Read `AGENTS.md` first, then implement the MVP described in `docs/PRD.md`, `docs/MVP_SCOPE.md`, `docs/API_SPEC.md`, and `docs/DATA_MODEL.md`.

## Goal

Create a working full-stack MVP with:

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Data: mock data first; SQLite or in-memory is acceptable for MVP
- Prediction: deterministic rule/model-style scoring
- Explanation: template-based Japanese explanation, with optional OpenAI API fallback only if configured
- Bet plan generation: budget + preference -> suggested ticket allocation
- Review: save proposed bet plan and show history

## Critical constraints

- Do not implement automatic betting.
- Do not integrate payment.
- Do not claim guaranteed profits.
- Use safe disclaimers.
- Use mock data unless legal racing data integration is explicitly configured.

## Deliverables

1. Backend API with endpoints defined in `docs/API_SPEC.md`
2. Frontend pages:
   - `/`
   - `/races`
   - `/races/[raceId]`
   - `/history`
3. Basic tests for:
   - prediction scoring
   - bet allocation
4. Clear setup instructions in README
5. `.env.example` for backend and frontend

## Acceptance criteria

- `uvicorn app.main:app --reload` starts backend.
- `npm run dev` starts frontend.
- Race list is visible.
- Race detail shows entries, prediction marks, explanations, and bet generator.
- User can save a plan and view it in history.
- No UI copy promises winning/profit.
