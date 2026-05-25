# MVP Scope

## Must have

### Race list

- Show mock races.
- Display date, venue, race number, title, course, distance, start time, going.

### Race detail

- Show entries.
- Show horse name, gate, jockey, odds, running style, simple score factors.

### Prediction

- Show:
  - ◎ 本命
  - ○ 対抗
  - ▲ 単穴
  - ☆ 穴馬
  - 危険人気馬
- Show confidence and beginner explanation.

### Bet plan generation

Input:
- budget
- objective: `hit_rate`, `balanced`, `return`
- risk_level: `low`, `medium`, `high`
- allow_trifecta: boolean

Output:
- tickets
- stake per ticket
- total stake
- rationale
- disclaimer

### Save and review

- Save proposed plan.
- Show history.
- Allow manual payout/result input.
- Calculate total stake, payout, profit/loss, ROI.

## Nice to have

- Graph of ROI over time
- Favorite race conditions
- Frontend local storage fallback

## Must not have

- Automatic betting
- 馬券購入代行
- Profit guarantee copy
- Paid subscription implementation
- Real odds scraping
