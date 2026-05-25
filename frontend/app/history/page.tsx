import Link from "next/link";
import { apiGet } from "../../lib/api";
import { ResultForm } from "./ResultForm";

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

type PredictionPick = {
  mark?: string;
  horseNumber: number;
  horseName: string;
  score?: number;
  confidence?: number;
};

type PredictionSnapshot = {
  picks: PredictionPick[];
  valuePick?: PredictionPick | null;
  dangerousFavorite?: PredictionPick | null;
};

type PlanResult = {
  payout: number;
  hit: boolean;
  first?: number | null;
  second?: number | null;
  third?: number | null;
  mainPickFinish?: number | null;
  memo?: string;
};

type BetPlan = {
  id: string;
  raceId: string;
  race?: RaceSummary;
  budget: number;
  totalStake: number;
  rationale: string;
  strategyNotes?: string[];
  tickets: { betType: string; combination: string; stake: number }[];
  predictionSnapshot?: PredictionSnapshot;
  result?: PlanResult | null;
};

type HistorySummary = {
  totalStake: number;
  reviewedStake: number;
  totalPayout: number;
  profit: number;
  roi: number;
  hitCount: number;
  resultCount: number;
  hitRate: number;
  mainPickShowCount: number;
  mainPickResultCount: number;
  mainPickShowRate: number;
  valuePickGoodRunCount: number;
  dangerousFavoriteMissCount: number;
  note: string;
};

function raceTitle(plan: BetPlan) {
  if (!plan.race) return plan.raceId;
  return `${plan.race.venue}${plan.race.raceNumber}R ${plan.race.name}`;
}

function statusBadge(plan: BetPlan) {
  if (!plan.result) return { label: "未振り返り", className: "status-pending" };
  return plan.result.hit
    ? { label: "的中入力", className: "status-hit" }
    : { label: "不的中入力", className: "status-miss" };
}

function finishText(value?: number | null) {
  return value ? `${value}着` : "未入力";
}

function mainPick(plan: BetPlan) {
  return (
    plan.predictionSnapshot?.picks.find((pick) => pick.mark === "◎") ??
    plan.predictionSnapshot?.picks[0]
  );
}

function topThreeNumbers(result?: PlanResult | null) {
  return [result?.first, result?.second, result?.third].filter(
    (horseNumber): horseNumber is number => typeof horseNumber === "number",
  );
}

function rankOfPick(result: PlanResult | null | undefined, pick?: PredictionPick | null) {
  if (!result || !pick) return null;
  const ranks = [result.first, result.second, result.third];
  const index = ranks.findIndex((horseNumber) => horseNumber === pick.horseNumber);
  return index >= 0 ? index + 1 : null;
}

function predictionReviewItems(plan: BetPlan) {
  const result = plan.result;
  if (!result) {
    return ["レース後の着順を入力すると、本命・穴馬・危険人気馬の振り返りがここに表示されます。"];
  }

  const items: string[] = [];
  const main = mainPick(plan);
  const valuePick = plan.predictionSnapshot?.valuePick;
  const dangerous = plan.predictionSnapshot?.dangerousFavorite;
  const topThree = topThreeNumbers(result);

  if (main && result.mainPickFinish) {
    items.push(
      result.mainPickFinish <= 3
        ? `本命の${main.horseName}は${result.mainPickFinish}着。上位に来て、中心評価は振り返りやすい結果でした。`
        : `本命の${main.horseName}は${result.mainPickFinish}着。今回は馬券圏内までは届きませんでした。`,
    );
  } else if (main) {
    items.push(`本命の${main.horseName}の着順を入力すると、中心評価の振り返りができます。`);
  }

  if (valuePick) {
    const rank = rankOfPick(result, valuePick);
    if (rank) {
      items.push(`穴馬候補の${valuePick.horseName}は${rank}着。人気以上に走ったかを確認しやすい結果です。`);
    } else if (topThree.length > 0) {
      items.push(`穴馬候補の${valuePick.horseName}は3着以内には入りませんでした。次回は条件や相手関係を見直せます。`);
    }
  }

  if (dangerous) {
    const rank = rankOfPick(result, dangerous);
    if (rank) {
      items.push(`危険人気馬の${dangerous.horseName}は${rank}着。注意評価が外れた可能性があるので理由を見直したい結果です。`);
    } else if (topThree.length > 0) {
      items.push(`危険人気馬の${dangerous.horseName}は3着以内に入らず、過信しない判断は振り返り材料になります。`);
    }
  }

  items.push(
    result.hit
      ? `買い目シミュレーションは的中扱い。入力した払戻額は${result.payout.toLocaleString()}円でした。`
      : "買い目シミュレーションは不的中扱い。惜しかった点や買い方の広げ方をメモしておくと次に活かせます。",
  );

  return items;
}

export default async function HistoryPage() {
  const [plans, summary] = await Promise.all([
    apiGet<BetPlan[]>("/api/bet-plans"),
    apiGet<HistorySummary>("/api/bet-plans/summary"),
  ]);

  return (
    <div className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Review</p>
          <h1>保存した予想</h1>
        </div>
        <Link className="ghost-button" href="/races">
          レース一覧
        </Link>
      </div>

      <section className="card guidance-card">
        <strong>ここは購入履歴ではありません</strong>
        <p>
          レース詳細で作成したAI予想と買い目シミュレーションを保存する場所です。レース後の振り返りは任意で、実際の購入や投票は行いません。
        </p>
      </section>

      <section className="card summary-card dashboard-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Summary</p>
            <h2>シミュレーション振り返り</h2>
          </div>
          <strong className={summary.profit >= 0 ? "profit" : "loss"}>
            振り返り済み仮想収支 {summary.profit.toLocaleString()}円
          </strong>
        </div>
        <div className="summary-metrics">
          <div>
            <span>保存した想定額</span>
            <strong>{summary.totalStake.toLocaleString()}円</strong>
          </div>
          <div>
            <span>振り返り済み想定額</span>
            <strong>{summary.reviewedStake.toLocaleString()}円</strong>
          </div>
          <div>
            <span>入力済み払戻</span>
            <strong>{summary.totalPayout.toLocaleString()}円</strong>
          </div>
          <div>
            <span>仮想回収率</span>
            <strong>{summary.roi}%</strong>
          </div>
          <div>
            <span>的中率（入力分）</span>
            <strong>
              {summary.hitRate}% <small>({summary.hitCount}/{summary.resultCount})</small>
            </strong>
          </div>
          <div>
            <span>本命複勝圏率</span>
            <strong>
              {summary.mainPickShowRate}% <small>({summary.mainPickShowCount}/{summary.mainPickResultCount})</small>
            </strong>
          </div>
          <div>
            <span>穴馬好走</span>
            <strong>{summary.valuePickGoodRunCount}件</strong>
          </div>
          <div>
            <span>注意馬見送り</span>
            <strong>{summary.dangerousFavoriteMissCount}件</strong>
          </div>
        </div>
        <p className="disclaimer-note">{summary.note}</p>
      </section>

      <div className="race-list history-list">
        {plans.length === 0 && <p className="muted">保存した予想はまだありません。</p>}
        {plans.map((plan) => {
          const payout = plan.result?.payout ?? 0;
          const profit = plan.result ? payout - plan.totalStake : 0;
          const badge = statusBadge(plan);
          const main = mainPick(plan);
          const payoutText = plan.result ? `${payout.toLocaleString()}円` : "未入力";
          return (
            <section key={plan.id} className="card history-card">
              <div className="summary-row">
                <div>
                  <p className="muted">
                    {plan.race?.date} {plan.race?.startTime} / {plan.race?.meeting}
                  </p>
                  <h2>{raceTitle(plan)}</h2>
                </div>
                <div className="result-status-block">
                  <span className={`status-badge ${badge.className}`}>{badge.label}</span>
                  <strong className={plan.result ? (profit >= 0 ? "profit" : "loss") : "muted"}>
                    {plan.result ? `${profit.toLocaleString()}円` : "振り返り未入力"}
                  </strong>
                </div>
              </div>

              <div className="result-detail-grid">
                <div>
                  <span>想定額</span>
                  <strong>{plan.totalStake.toLocaleString()}円</strong>
                </div>
                <div>
                  <span>払戻入力</span>
                  <strong>{payoutText}</strong>
                </div>
                <div>
                  <span>1着 / 2着 / 3着</span>
                  <strong>
                    {finishText(plan.result?.first)} / {finishText(plan.result?.second)} / {finishText(plan.result?.third)}
                  </strong>
                </div>
                <div>
                  <span>本命</span>
                  <strong>{main ? `${main.horseNumber} ${main.horseName}` : "-"}</strong>
                  <small>{finishText(plan.result?.mainPickFinish)}</small>
                </div>
              </div>

              <div className="ticket-list">
                {plan.tickets.map((ticket, idx) => (
                  <div className="ticket" key={idx}>
                    <span>{ticket.betType}</span>
                    <strong>{ticket.combination}</strong>
                    <span>{ticket.stake.toLocaleString()}円</span>
                  </div>
                ))}
              </div>
              <p className="muted">{plan.rationale}</p>
              {plan.strategyNotes && plan.strategyNotes.length > 0 && (
                <ul className="strategy-note-list">
                  {plan.strategyNotes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              )}

              <div className="review-box">
                <strong>AI予想の振り返り</strong>
                <ul>
                  {predictionReviewItems(plan).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                {plan.result?.memo && <p className="muted small">メモ: {plan.result.memo}</p>}
              </div>

              <details className="result-panel result-editor">
                <summary>
                  <strong>レース後の振り返り（任意）</strong>
                  <span className="muted small">実際の着順や仮の払戻額を入れると、AI予想の振り返りが詳しくなります。</span>
                </summary>
                <ResultForm
                  initialFirst={plan.result?.first ?? undefined}
                  initialHit={plan.result?.hit}
                  initialMainPickFinish={plan.result?.mainPickFinish ?? undefined}
                  initialMemo={plan.result?.memo}
                  initialPayout={plan.result?.payout}
                  initialSecond={plan.result?.second ?? undefined}
                  initialThird={plan.result?.third ?? undefined}
                  planId={plan.id}
                />
              </details>
            </section>
          );
        })}
      </div>
    </div>
  );
}