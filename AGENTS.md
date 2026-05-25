# AGENTS.md — RaceNavi AI

## Project goal

Build an MVP for **RaceNavi AI**, a beginner-friendly horse racing support app.

The core concept is:

> Not an app that guarantees winning.  
> An app that helps beginners understand predictions, choose bet types/budget allocation, save proposed picks, and review results.

This MVP must prioritize:
1. Beginner-friendly race/prediction UI
2. AI-style explanation generated from deterministic model outputs
3. Bet plan optimization from budget and user preference
4. Saved bet plans and result review
5. Legal/safety wording: no profit guarantee, no purchase代行, no automatic betting

## Tech stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui style components are acceptable, but avoid overengineering
- Recharts for graphs if needed

### Backend
- FastAPI
- Python
- SQLAlchemy or SQLModel
- Pydantic
- PostgreSQL for production
- SQLite is acceptable for local MVP if clearly abstracted
- Redis optional; do not block MVP on Redis

### AI / prediction
- MVP may use rule-based scoring and mock model outputs.
- Do not call OpenAI API unless environment variables are present.
- LLM must not decide numeric predictions.
- LLM is only a "translator" that explains rule/model outputs in beginner-friendly Japanese.
- If no API key exists, use deterministic template explanations.

## MVP rules

Implement the smallest working product that demonstrates the core value.

Must include:
- Race list page
- Race detail page
- Prediction display: 本命・対抗・穴馬・危険人気馬
- Explanation panel
- Bet plan generator
- Bet plan save
- Results/review page
- KPI-friendly events/logs where reasonable

Do not include in MVP:
- Automatic betting
- Purchase代行
- Payment implementation
- Actual JRA-VAN integration
- Real-time odds scraping
- SNS analysis
- WIN5
- 地方競馬
- パドック画像分析

## Safety and legal constraints

- Never claim guaranteed profit.
- Never write UI text that says "必ず当たる", "勝てる", "儲かる".
- Always position predictions as reference information.
- Add disclaimer text on bet plan screens.
- Do not implement automatic betting or purchase代行.
- Use mock data for racing data unless a legal data source is configured.

## Code style

- Keep code simple and readable.
- Prefer explicit types.
- Validate API inputs with Pydantic.
- Separate services from routes.
- Add comments only where they clarify non-obvious domain logic.
- Include basic tests for scoring and bet allocation.

## Suggested commands

Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Definition of done

The MVP is done when:
- Backend starts locally.
- Frontend starts locally.
- Race list displays mock races.
- Race detail displays mock entries and predictions.
- User can generate a bet plan from budget and preference.
- User can save a bet plan.
- User can see a simple review/history screen.
- Tests pass.
