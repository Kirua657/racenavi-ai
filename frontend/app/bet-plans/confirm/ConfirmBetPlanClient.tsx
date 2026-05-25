"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiPost } from "../../../lib/api";

export type BetPlanRequest = {
  raceId: string;
  budget: number;
  objective: "hit_rate" | "balanced" | "return";
  riskLevel: "low" | "medium" | "high";
  allowTrifecta: boolean;
};

type Ticket = {
  betType: string;
  combination: string;
  stake: number;
};

type RaceSummary = {
  id: string;
  date?: string;
  venue?: string;
  meeting?: string;
  raceNumber?: number;
  name?: string;
  grade?: string;
  courseType?: string;
  distance?: number;
  going?: string;
  startTime?: string;
};

type BetPlan = {
  id: string;
  raceId: string;
  race?: RaceSummary;
  budget: number;
  objective: BetPlanRequest["objective"];
  riskLevel: BetPlanRequest["riskLevel"];
  allowTrifecta: boolean;
  totalStake: number;
  tickets: Ticket[];
  rationale: string;
  strategyNotes?: string[];
  disclaimer: string;
};

const OBJECTIVE_LABELS: Record<BetPlanRequest["objective"], string> = {
  hit_rate: "的中重視",
  balanced: "バランス",
  return: "リターン重視",
};

const RISK_LABELS: Record<BetPlanRequest["riskLevel"], string> = {
  low: "低",
  medium: "中",
  high: "高",
};

function raceTitle(plan: BetPlan) {
  if (!plan.race) return plan.raceId;
  return `${plan.race.venue}${plan.race.raceNumber}R ${plan.race.name}`;
}

export function ConfirmBetPlanClient({ request }: { request: BetPlanRequest }) {
  const router = useRouter();
  const [plan, setPlan] = useState<BetPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPreview() {
      if (!request.raceId) {
        setError("レース情報が見つかりませんでした。レース詳細からもう一度作成してください。");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError("");
      try {
        const preview = await apiPost<BetPlan>("/api/bet-plans/preview", request);
        if (active) setPlan(preview);
      } catch {
        if (active) setError("買い目プランの確認画面を表示できませんでした。バックエンドが起動しているか確認してください。");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    loadPreview();
    return () => {
      active = false;
    };
  }, [request]);

  async function handleSave() {
    setIsSaving(true);
    setError("");
    try {
      const saved = await apiPost<BetPlan>("/api/bet-plans", request);
      router.push(`/history?saved=${saved.id}`);
    } catch {
      setError("予想メモを保存できませんでした。少し待ってからもう一度試してください。");
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <div className="page-stack">
        <section className="card section-card plan-confirm-card">
          <p className="eyebrow">Bet Plan</p>
          <h1>買い目を確認しています</h1>
          <p className="muted">内容を作成しています。少しだけお待ちください。</p>
        </section>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="page-stack">
        <section className="card section-card plan-confirm-card">
          <p className="eyebrow">Bet Plan</p>
          <h1>買い目プラン確認</h1>
          <p className="error-text">{error || "買い目プランを表示できませんでした。"}</p>
          <div className="plan-actions">
            <Link className="button" href="/races">
              レース一覧へ戻る
            </Link>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Bet Plan Confirmation</p>
          <h1>買い目プラン確認</h1>
        </div>
        <div className="page-actions">
          <Link className="ghost-button" href={`/races/${request.raceId}#bet-plan`}>
            内容を修正
          </Link>
          <Link className="ghost-button" href="/history">
            保存した予想
          </Link>
        </div>
      </div>

      <section className="race-header confirm-header">
        <p className="eyebrow">まだ保存した予想には追加されていません</p>
        <div className="race-title-row">
          <h1>{raceTitle(plan)}</h1>
          {plan.race?.grade && <span className="grade-badge on-dark">{plan.race.grade}</span>}
        </div>
        <p className="lead">
          {plan.race?.date} {plan.race?.startTime} / {plan.race?.courseType}{plan.race?.distance}m / 馬場: {plan.race?.going}
        </p>
      </section>

      <section className="card section-card plan-confirm-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Preview</p>
            <h2>この予想メモを保存しますか？</h2>
          </div>
          <span className="filter-count">{plan.tickets.length}点</span>
        </div>

        <div className="pending-banner">
          <strong>確認中のシミュレーションです</strong>
          <span>下の保存ボタンを押すまで、保存した予想には追加されません。</span>
        </div>
        <p className="simulation-notice">
          この画面では馬券購入・投票は行いません。AI予想をもとに、買い目と金額配分の考え方を保存するための確認画面です。
        </p>

        <div className="plan-summary-grid">
          <div>
            <span>入力予算</span>
            <strong>{plan.budget.toLocaleString()}円</strong>
          </div>
          <div>
            <span>合計想定額</span>
            <strong>{plan.totalStake.toLocaleString()}円</strong>
          </div>
          <div>
            <span>目的 / リスク</span>
            <strong>{OBJECTIVE_LABELS[plan.objective]}・{RISK_LABELS[plan.riskLevel]}</strong>
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

        {error && <p className="error-text">{error}</p>}

        <div className="plan-actions confirm-actions">
          <button className="button" disabled={isSaving} onClick={handleSave} type="button">
            {isSaving ? "保存中..." : "この予想メモを保存"}
          </button>
          <Link className="ghost-button" href={`/races/${request.raceId}#bet-plan`}>
            作り直す
          </Link>
        </div>
      </section>
    </div>
  );
}