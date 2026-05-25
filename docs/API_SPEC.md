# API Spec

Base URL: `http://localhost:8000`

## GET /health

Response:

```json
{
  "status": "ok"
}
```

## GET /api/races

Response:

```json
[
  {
    "id": "tokyo-2026-05-31-11",
    "date": "2026-05-31",
    "venue": "東京",
    "raceNumber": 11,
    "name": "日本ダービー",
    "courseType": "芝",
    "distance": 2400,
    "going": "良",
    "startTime": "15:40"
  }
]
```

## GET /api/races/{race_id}

Response:

```json
{
  "race": {},
  "entries": []
}
```

## GET /api/races/{race_id}/predictions

Response:

```json
{
  "raceId": "tokyo-2026-05-31-11",
  "generatedAt": "2026-05-31T12:00:00Z",
  "picks": [],
  "dangerousFavorite": {},
  "explanation": "初心者向け解説"
}
```

## POST /api/bet-plans

Request:

```json
{
  "raceId": "tokyo-2026-05-31-11",
  "budget": 3000,
  "objective": "balanced",
  "riskLevel": "medium",
  "allowTrifecta": true
}
```

Response:

```json
{
  "id": "plan_001",
  "raceId": "tokyo-2026-05-31-11",
  "budget": 3000,
  "tickets": [],
  "totalStake": 3000,
  "rationale": "買い目提案の理由",
  "disclaimer": "この提案は参考情報であり、的中や利益を保証するものではありません。"
}
```

## GET /api/bet-plans

Response:

```json
[
  {}
]
```

## POST /api/bet-plans/{plan_id}/result

Request:

```json
{
  "payout": 3200,
  "hit": true,
  "memo": "ワイド的中"
}
```

Response:

```json
{
  "ok": true,
  "plan": {}
}
```
