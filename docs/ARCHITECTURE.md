# Architecture

## Overview

```text
Next.js Frontend
  ↓ HTTP
FastAPI Backend
  ↓
Prediction Service / Bet Optimizer / Explanation Service
  ↓
Database or Mock Repository
```

## Frontend

Pages:
- `/` landing
- `/races` race list
- `/races/[raceId]` race detail and bet generator
- `/history` saved plans and review

## Backend

Modules:
- `api/races.py`
- `api/predictions.py`
- `api/bet_plans.py`
- `services/prediction_service.py`
- `services/bet_optimizer.py`
- `services/explanation_service.py`
- `core/mock_data.py`

## Data strategy

MVP uses mock data to avoid data licensing problems.  
Future integration can use official/legal data sources after confirmation.

## Explanation strategy

1. Rule/model outputs generate structured prediction facts.
2. Explanation service turns those facts into beginner-friendly Japanese.
3. OpenAI API is optional and disabled by default.
4. Template explanation is the fallback.

## Deployment target

Local development first.  
Docker Compose can be added for backend, frontend, PostgreSQL, and Redis later.
