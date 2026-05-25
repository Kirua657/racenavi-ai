# Implementation Tasks

## Phase 0 — Setup

- [ ] Create backend FastAPI app
- [ ] Create frontend Next.js app
- [ ] Add CORS from frontend to backend
- [ ] Add mock data

## Phase 1 — Backend API

- [ ] `GET /health`
- [ ] `GET /api/races`
- [ ] `GET /api/races/{race_id}`
- [ ] `GET /api/races/{race_id}/predictions`
- [ ] `POST /api/bet-plans`
- [ ] `GET /api/bet-plans`
- [ ] `POST /api/bet-plans/{plan_id}/result`

## Phase 2 — Prediction Service

- [ ] Create rule-based score
- [ ] Generate marks: ◎, ○, ▲, ☆, 危険
- [ ] Generate confidence score
- [ ] Generate beginner-friendly explanation

## Phase 3 — Bet Optimizer

- [ ] Input: race_id, budget, objective, risk_level, allow_trifecta
- [ ] Output: tickets, total stake, rationale, disclaimer
- [ ] Ensure allocation does not exceed budget
- [ ] Avoid too many tickets for beginner UI

## Phase 4 — Frontend

- [ ] Race list page
- [ ] Race detail page
- [ ] Prediction panel
- [ ] Bet plan form
- [ ] Bet plan result card
- [ ] Save plan button
- [ ] History page

## Phase 5 — Review

- [ ] Add simple result input
- [ ] Show hit/miss, stake, payout, profit/loss
- [ ] Show total stake, total payout, ROI

## Phase 6 — Tests

- [ ] Unit test prediction order
- [ ] Unit test dangerous favorite logic
- [ ] Unit test bet allocation budget cap
- [ ] API smoke tests
