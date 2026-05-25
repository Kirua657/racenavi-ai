"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export function BetPlanPanel({ raceId }: { raceId: string }) {
  const router = useRouter();
  const [budget, setBudget] = useState(3000);
  const [objective, setObjective] = useState("balanced");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [allowTrifecta, setAllowTrifecta] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (!Number.isFinite(budget) || budget < 100) {
      setError("予算は100円以上で入力してください。");
      return;
    }

    setIsLoading(true);
    const params = new URLSearchParams({
      raceId,
      budget: String(budget),
      objective,
      riskLevel,
      allowTrifecta: String(allowTrifecta),
    });
    router.push(`/bet-plans/confirm?${params.toString()}`);
  }

  return (
    <section className="card section-card bet-plan-card" id="bet-plan">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Bet Plan</p>
          <h2>買い目シミュレーション</h2>
        </div>
        <p className="muted small">AI予想を見たあと、購入は行わずに予算に合わせた買い目プランを確認用に作ります。</p>
      </div>

      <form className="form-grid compact-form-grid" onSubmit={handleSubmit}>
        <label>
          予算
          <input
            min={100}
            max={100000}
            step={100}
            type="number"
            value={budget}
            onChange={(event) => setBudget(Number(event.target.value))}
          />
        </label>
        <label>
          目的
          <select value={objective} onChange={(event) => setObjective(event.target.value)}>
            <option value="hit_rate">的中重視</option>
            <option value="balanced">バランス</option>
            <option value="return">リターン重視</option>
          </select>
        </label>
        <label>
          リスク
          <select value={riskLevel} onChange={(event) => setRiskLevel(event.target.value)}>
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
          </select>
        </label>
        <label className="check-row">
          <input
            type="checkbox"
            checked={allowTrifecta}
            onChange={(event) => setAllowTrifecta(event.target.checked)}
          />
          3連単を含める
        </label>
        <button className="button" disabled={isLoading} type="submit">
          {isLoading ? "確認画面へ移動中..." : "買い目プランを作る"}
        </button>
      </form>

      {error && <p className="error-text">{error}</p>}
    </section>
  );
}