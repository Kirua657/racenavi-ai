import Link from "next/link";
import { apiGet } from "../../../lib/api";
import { BetPlanPanel } from "./BetPlanPanel";

type Entry = {
  id: string;
  horseNumber: number;
  gateNumber: number;
  horseName: string;
  sexAge?: string;
  carriedWeight?: number;
  jockey: string;
  trainer?: string;
  bodyWeight?: string;
  odds: number;
  popularity: number;
  runningStyle: string;
};

type RaceDetail = {
  race: {
    id: string;
    date: string;
    venue: string;
    meeting?: string;
    raceNumber: number;
    name: string;
    grade?: string;
    courseType: string;
    distance: number;
    turn?: string;
    going: string;
    weather?: string;
    startTime: string;
    conditions?: string;
    dataSource?: string;
    sourceNote?: string;
  };
  entries: Entry[];
};

type ScoreBreakdown = {
  baseScore: number;
  courseBonus: number;
  distanceBonus: number;
  styleBonus: number;
  goingBonus: number;
  oddsValueBonus: number;
  finalScore: number;
};

type PredictionPick = {
  mark: string;
  horseNumber: number;
  horseName: string;
  score: number;
  confidence: number;
  reasons: string[];
  conditionAdjustment?: number;
  scoreBreakdown: ScoreBreakdown;
};

type Prediction = {
  picks: PredictionPick[];
  valuePick?: PredictionPick | null;
  dangerousFavorite?: PredictionPick | null;
  explanation: string;
};

type PredictionCard = PredictionPick & {
  cardKey: string;
  displayMark: string;
  roleLabel: string;
  roleClass: string;
  roleNote: string;
};

const ROLE_BY_MARK: Record<string, { label: string; className: string; note: string }> = {
  "◎": {
    label: "本命",
    className: "main",
    note: "まず中心に考えたい馬です。",
  },
  "○": {
    label: "対抗",
    className: "rival",
    note: "本命に近い評価の相手候補です。",
  },
  "▲": {
    label: "相手",
    className: "contender",
    note: "上位争いに加えたい候補です。",
  },
  "☆": {
    label: "穴馬",
    className: "value",
    note: "人気以上に評価したい候補です。",
  },
};

function friendlyReason(reason: string) {
  const rules: { match: string; text: string }[] = [
    { match: "東京芝2400mで差し・追込", text: "東京芝2400mでは、後ろから長く脚を使えるタイプを評価しています。" },
    { match: "東京芝2400mで距離適性", text: "今回の2400mという距離で力を出しやすい評価です。" },
    { match: "東京コース適性", text: "東京コースへの相性が良い評価です。" },
    { match: "芝1200mで逃げ・先行", text: "短距離では前に行けるスピードを評価しています。" },
    { match: "芝1200mで近走スピード", text: "最近のレースで見せたスピードを高く見ています。" },
    { match: "ダートで前に行ける", text: "ダートでは前めで運べる脚質を評価しています。" },
    { match: "ダートで馬場適性", text: "ダートの馬場に合いやすいタイプです。" },
    { match: "ダートでパワー型", text: "力のいるダートで強みを出しやすい評価です。" },
    { match: "馬場で馬場適性を強めに評価", text: "重い馬場でも力を出しやすい点を評価しています。" },
    { match: "馬場で馬場適性に不安", text: "重い馬場では少し力を出しにくい可能性があります。" },
    { match: "コース適性が高い", text: "今回の競馬場やコースが合っている評価です。" },
    { match: "距離適性が高い", text: "今回の距離が合っている評価です。" },
    { match: "近走内容の評価が高い", text: "最近の走りの内容が良い評価です。" },
    { match: "人気と能力のバランスに妙味", text: "人気よりも評価が高めで、相手に入れる妙味があります。" },
    { match: "人気薄だが総合評価が高く穴馬候補", text: "人気は高くありませんが、総合評価では上位に入っています。" },
    { match: "人気上位だが条件適性または総合評価が低い", text: "人気はありますが、今回の条件では評価が伸びきっていません。" },
    { match: "総合的なバランスが安定", text: "目立つ弱点が少なく、全体のバランスが安定しています。" },
  ];

  return rules.find((rule) => reason.includes(rule.match))?.text ?? reason;
}

function evaluationPoints(pick: PredictionPick) {
  return Array.from(new Set(pick.reasons.map(friendlyReason))).slice(0, 4);
}

function roleForPick(pick: PredictionPick, valuePick?: PredictionPick | null) {
  if (pick.mark === "☆" || valuePick?.horseNumber === pick.horseNumber) {
    return ROLE_BY_MARK["☆"];
  }
  return ROLE_BY_MARK[pick.mark] ?? {
    label: "注目",
    className: "contender",
    note: "評価上位に入った注目馬です。",
  };
}

function buildPredictionCards(prediction: Prediction): PredictionCard[] {
  const cards = prediction.picks.map((pick) => {
    const role = roleForPick(pick, prediction.valuePick);
    return {
      ...pick,
      cardKey: `${role.label}-${pick.horseNumber}`,
      displayMark: pick.mark,
      roleLabel: role.label,
      roleClass: role.className,
      roleNote: role.note,
    };
  });

  if (
    prediction.valuePick &&
    !cards.some((card) => card.horseNumber === prediction.valuePick?.horseNumber && card.roleLabel === "穴馬")
  ) {
    const role = ROLE_BY_MARK["☆"];
    cards.push({
      ...prediction.valuePick,
      cardKey: `穴馬-${prediction.valuePick.horseNumber}`,
      displayMark: "☆",
      roleLabel: role.label,
      roleClass: role.className,
      roleNote: role.note,
    });
  }

  if (prediction.dangerousFavorite) {
    cards.push({
      ...prediction.dangerousFavorite,
      cardKey: `危険人気馬-${prediction.dangerousFavorite.horseNumber}`,
      displayMark: "注",
      roleLabel: "危険人気馬",
      roleClass: "caution",
      roleNote: "人気はありますが、今回は過信しすぎないように見たい馬です。",
    });
  }

  return cards;
}

function breakdownItems(breakdown: ScoreBreakdown) {
  return [
    { label: "基礎評価", help: "近走、適性、騎手などの土台評価", value: breakdown.baseScore },
    { label: "コース加点", help: "今回の競馬場やコースが合う分", value: breakdown.courseBonus },
    { label: "距離加点", help: "今回の距離が合う分", value: breakdown.distanceBonus },
    { label: "脚質加点", help: "展開やコースに合う走り方の分", value: breakdown.styleBonus },
    { label: "馬場加点", help: "良・重・不良など馬場への合いやすさ", value: breakdown.goingBonus },
    { label: "妙味点", help: "人気とオッズのバランスで見た上乗せ", value: breakdown.oddsValueBonus },
    { label: "最終評価", help: "すべてを合わせたAI評価", value: breakdown.finalScore, isTotal: true },
  ];
}

export default async function RaceDetailPage({ params }: { params: Promise<{ raceId: string }> }) {
  const { raceId } = await params;
  const detail = await apiGet<RaceDetail>(`/api/races/${raceId}`);
  const prediction = await apiGet<Prediction>(`/api/races/${raceId}/predictions`);
  const pickByHorseNumber = new Map(prediction.picks.map((pick) => [pick.horseNumber, pick]));
  const predictionCards = buildPredictionCards(prediction);

  if (prediction.valuePick && !pickByHorseNumber.has(prediction.valuePick.horseNumber)) {
    pickByHorseNumber.set(prediction.valuePick.horseNumber, prediction.valuePick);
  }

  if (prediction.dangerousFavorite && !pickByHorseNumber.has(prediction.dangerousFavorite.horseNumber)) {
    pickByHorseNumber.set(prediction.dangerousFavorite.horseNumber, {
      ...prediction.dangerousFavorite,
      mark: "危",
    });
  }

  return (
    <div className="page-stack">
      <div className="page-heading">
        <Link className="ghost-button" href="/races">
          レース一覧
        </Link>
        <Link className="ghost-button" href="/history">
          履歴
        </Link>
      </div>

      <section className="race-header">
        <p className="eyebrow">{detail.race.date} / {detail.race.meeting}</p>
        <div className="race-title-row">
          <h1>{detail.race.venue}{detail.race.raceNumber}R {detail.race.name}</h1>
          {detail.race.grade && <span className="grade-badge on-dark">{detail.race.grade}</span>}
        </div>
        <p className="lead">
          {detail.race.courseType}{detail.race.distance}m{detail.race.turn ? `・${detail.race.turn}` : ""} /
          馬場: {detail.race.going} / 発走: {detail.race.startTime}
        </p>
        <div className="race-info-grid">
          <span>{detail.race.conditions}</span>
          <span>天気: {detail.race.weather ?? "-"}</span>
          <span>データ: {detail.race.dataSource ?? "local"}</span>
        </div>
        {detail.race.sourceNote && <p className="source-note">{detail.race.sourceNote}</p>}
      </section>

      <section className="card section-card entry-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Entries</p>
            <h2>出馬表</h2>
          </div>
          <span className="filter-count">{detail.entries.length}頭</span>
        </div>
        <div className="table-scroll">
          <table className="entry-table">
            <thead>
              <tr>
                <th>枠</th>
                <th>馬番</th>
                <th>印</th>
                <th>馬名</th>
                <th>性齢</th>
                <th>斤量</th>
                <th>騎手</th>
                <th>人気</th>
                <th>オッズ</th>
                <th>脚質</th>
                <th>AI評価</th>
              </tr>
            </thead>
            <tbody>
              {detail.entries.map((entry) => {
                const pick = pickByHorseNumber.get(entry.horseNumber);
                return (
                  <tr key={entry.id}>
                    <td>
                      <span className={`frame-badge frame-${entry.gateNumber}`}>{entry.gateNumber}</span>
                    </td>
                    <td className="horse-number">{entry.horseNumber}</td>
                    <td className="prediction-mark">{pick?.mark ?? ""}</td>
                    <td>
                      <strong>{entry.horseName}</strong>
                      <span className="subtext">{entry.trainer}</span>
                    </td>
                    <td>{entry.sexAge ?? "-"}</td>
                    <td>{entry.carriedWeight?.toFixed(1) ?? "-"}</td>
                    <td>{entry.jockey}</td>
                    <td>{entry.popularity}番</td>
                    <td>{entry.odds.toFixed(1)}倍</td>
                    <td>{entry.runningStyle}</td>
                    <td>{pick ? Math.round(pick.score) : "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card section-card prediction-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">AI Forecast</p>
            <h2>AI予想</h2>
          </div>
          <span className="prediction-note">この予想は参考情報です</span>
        </div>

        <div className="prediction-card-grid">
          {predictionCards.map((pick) => (
            <article className={`prediction-card prediction-card-${pick.roleClass}`} key={pick.cardKey}>
              <div className="prediction-card-top">
                <span className="mark">{pick.displayMark}</span>
                <div>
                  <span className="role-label">{pick.roleLabel}</span>
                  <h3>{pick.horseNumber} {pick.horseName}</h3>
                </div>
              </div>
              <p className="role-note">{pick.roleNote}</p>
              <div className="score-row">
                <span>評価 {Math.round(pick.score)}</span>
                <span>信頼度 {pick.confidence}</span>
                {pick.conditionAdjustment ? <span>条件補正 +{pick.conditionAdjustment}</span> : null}
              </div>
              <div className="evaluation-box">
                <strong>評価ポイント</strong>
                <ul>
                  {evaluationPoints(pick).map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              </div>
              <details className="score-breakdown">
                <summary>スコア内訳を開く</summary>
                <div className="score-breakdown-list">
                  {breakdownItems(pick.scoreBreakdown).map((item) => (
                    <div className={item.isTotal ? "score-breakdown-total" : ""} key={item.label}>
                      <span>{item.label}</span>
                      <p>{item.help}</p>
                      <strong>{item.value >= 0 && !item.isTotal ? "+" : ""}{item.value.toFixed(1)}点</strong>
                    </div>
                  ))}
                </div>
              </details>
            </article>
          ))}
        </div>

        <p className="prediction-explanation">{prediction.explanation}</p>
        <p className="disclaimer-note">この予想は参考情報です。的中や利益を保証するものではありません。</p>
      </section>

      <BetPlanPanel raceId={raceId} />
    </div>
  );
}