# Data Model

## Race

```ts
type Race = {
  id: string;
  date: string;
  venue: string;
  raceNumber: number;
  name: string;
  courseType: "芝" | "ダート";
  distance: number;
  going: "良" | "稍重" | "重" | "不良";
  startTime: string;
};
```

## Entry

```ts
type Entry = {
  id: string;
  raceId: string;
  horseNumber: number;
  gateNumber: number;
  horseName: string;
  jockey: string;
  trainer?: string;
  odds: number;
  popularity: number;
  runningStyle: "逃げ" | "先行" | "差し" | "追込";
  recentFormScore: number;
  courseAptitude: number;
  distanceAptitude: number;
  goingAptitude: number;
  jockeyScore: number;
};
```

## Prediction

```ts
type Prediction = {
  raceId: string;
  generatedAt: string;
  picks: PredictionPick[];
  dangerousFavorite?: PredictionPick;
  explanation: string;
};
```

## PredictionPick

```ts
type PredictionPick = {
  mark: "◎" | "○" | "▲" | "☆" | "危険";
  entryId: string;
  horseName: string;
  score: number;
  confidence: number;
  reasons: string[];
};
```

## BetPlan

```ts
type BetPlan = {
  id: string;
  raceId: string;
  createdAt: string;
  budget: number;
  objective: "hit_rate" | "balanced" | "return";
  riskLevel: "low" | "medium" | "high";
  allowTrifecta: boolean;
  tickets: Ticket[];
  totalStake: number;
  rationale: string;
  disclaimer: string;
  result?: BetResult;
};
```

## Ticket

```ts
type Ticket = {
  betType: "単勝" | "複勝" | "ワイド" | "馬連" | "馬単" | "3連複" | "3連単";
  combination: string;
  stake: number;
};
```

## BetResult

```ts
type BetResult = {
  payout: number;
  hit: boolean;
  memo?: string;
};
```
