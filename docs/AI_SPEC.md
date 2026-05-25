# AI / Prediction Spec

## Principle

LLM must not calculate scores, winning probability, or expected value.

Numeric evaluation is handled by:
1. Rule-based scoring
2. Mock/model-style scoring
3. Bet optimizer

LLM/template only explains the structured output.

## MVP scoring formula

For each entry:

```text
base_score =
  recentFormScore * 0.30
  + courseAptitude * 0.20
  + distanceAptitude * 0.20
  + goingAptitude * 0.10
  + jockeyScore * 0.10
  + oddsValueScore * 0.10
```

`oddsValueScore` should reward reasonable value, not just low odds.

Example:
- Very low odds with mediocre score -> possible dangerous favorite
- Medium odds with high aptitude -> value candidate

## Marks

- Highest score: ◎
- Second: ○
- Third: ▲
- High score + popularity 5 or lower: ☆
- Popularity 1 or 2 with low score/value: 危険人気馬

## Explanation template

Use reasons from the score factors.

Example:

```text
◎ {horseName} は、コース適性と距離適性の評価が高く、今回の条件に合いやすい1頭です。
特に {reason1} がプラス材料です。
ただし競馬には展開や馬場変化など不確定要素があるため、この予想は参考情報として確認してください。
```

## Bet optimizer policy

### hit_rate

Prioritize:
- 複勝
- ワイド
- 馬連少額

### balanced

Prioritize:
- ワイド
- 馬連
- 3連複

### return

Prioritize:
- 馬連
- 3連複
- 3連単少額

### Trifecta handling

Even if `allowTrifecta=true`, keep 3連単 as a small portion unless risk_level is high.

## Disallowed copy

Do not output:
- 必ず当たる
- 絶対勝てる
- 回収率が上がる
- 儲かる
- 確勝
