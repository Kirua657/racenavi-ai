"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiPost } from "../../../lib/api";

type Ticket = {
  betType: string;
  combination: string;
  stake: number;
};

type BetPlan = {
  id: string;
  budget: number;
  totalStake: number;
  tickets: Ticket[];
  rationale: string;
  strategyNotes?: string[];
  disclaimer: string;
};

export function BetPlanPanel({ raceId }: { raceId: string }) {
  const [budget, setBudget] = useState(3000);
  const [objective, setObjective] = useState("balanced");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [allowTrifecta, setAllowTrifecta] = useState(false);
  const [plan, setPlan] = useState<BetPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const nextPlan = await apiPost<BetPlan>("/api/bet-plans", {
        raceId,
        budget,
        objective,
        riskLevel,
        allowTrifecta,
      });
      setPlan(nextPlan);
    } catch {
      setError("買い目プランを作成できませんでした。バックエンドが起動しているか確認してください。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="card section-card bet-plan-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Bet Plan</p>
          <h2>買い目生成</h2>
        </div>
        <p className="muted small">作成した買い目は自動で履歴に保存されます。</p>
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
          {isLoading ? "作成中..." : "買い目を作る"}
        </button>
      </form>

      {error && <p className="error-text">{error}</p>}

      {plan && (
        <div className="plan-result">
          <div className="success-banner">
            <strong>買い目を保存しました</strong>
            <span>履歴画面であとから振り返れます。</span>
          </div>

          <div className="plan-summary-grid">
            <div>
              <span>予算</span>
              <strong>{plan.budget.toLocaleString()}円</strong>
            </div>
            <div>
              <span>合計金額</span>
              <strong>{plan.totalStake.toLocaleString()}円</strong>
            </div>
            <div>
              <span>買い目数</span>
              <strong>{plan.tickets.length}点</strong>
            </div>
          </div>

          <div className="ticket-list">
            {plan.tickets.map((ticket, index) => (
              <div className="ticket" key={`${ticket.betType}-${ticket.combination}-${index}`}>
                <span>{ticket.betType}</span>
                <strong>{ticket.combination}</strong>
                <span>{ticket.stake.toLocaleString()}円</span>
              </div>
            ))}
          </div>

          <div className="plan-copy">
            <strong>提案理由</strong>
            <p>{plan.rationale}</p>
            {plan.strategyNotes && plan.strategyNotes.length > 0 && (
              <ul className="strategy-note-list">
                {plan.strategyNotes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            )}
          </div>
          <p className="disclaimer-note">{plan.disclaimer}</p>

          <div className="plan-actions">
            <Link className="button" href="/history">
              履歴で確認する
            </Link>
            <Link className="ghost-button" href="/races">
              他のレースを見る
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}
