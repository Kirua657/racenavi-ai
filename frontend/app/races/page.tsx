import Link from "next/link";
import { apiGet } from "../../lib/api";

type Race = {
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
};

type SearchParams = Record<string, string | string[] | undefined>;

function paramValue(params: SearchParams, key: string) {
  const value = params[key];
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function uniqueSorted<T extends string | number>(values: T[]) {
  return Array.from(new Set(values)).sort((a, b) => String(a).localeCompare(String(b), "ja"));
}

function filterRaces(races: Race[], params: SearchParams) {
  const date = paramValue(params, "date");
  const venue = paramValue(params, "venue");
  const courseType = paramValue(params, "courseType");
  const distance = paramValue(params, "distance");
  const keyword = paramValue(params, "q").trim().toLowerCase();

  return races.filter((race) => {
    if (date && race.date !== date) return false;
    if (venue && race.venue !== venue) return false;
    if (courseType && race.courseType !== courseType) return false;
    if (distance && race.distance !== Number(distance)) return false;
    if (keyword && !race.name.toLowerCase().includes(keyword)) return false;
    return true;
  });
}

export default async function RacesPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const [races, params] = await Promise.all([apiGet<Race[]>("/api/races"), searchParams]);
  const filteredRaces = filterRaces(races, params);
  const dates = uniqueSorted(races.map((race) => race.date));
  const venues = uniqueSorted(races.map((race) => race.venue));
  const courseTypes = uniqueSorted(races.map((race) => race.courseType));
  const distances = uniqueSorted(races.map((race) => race.distance));

  const date = paramValue(params, "date");
  const venue = paramValue(params, "venue");
  const courseType = paramValue(params, "courseType");
  const distance = paramValue(params, "distance");
  const keyword = paramValue(params, "q");

  return (
    <div className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Races</p>
          <h1>開催レース</h1>
        </div>
        <div className="page-actions">
          <Link className="ghost-button" href="/admin/import">
            CSV取り込み
          </Link>
          <Link className="ghost-button" href="/history">
            保存した予想
          </Link>
        </div>
      </div>

      <section className="card guidance-card">
        <strong>基本の流れ</strong>
        <p>
          レースを選ぶと、AI予想・評価理由・買い目シミュレーションを確認できます。買い目は購入ではなく、保存してあとから振り返るための予想メモです。
        </p>
      </section>

      <form className="card filter-panel toolbar-card" action="/races">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Search</p>
            <h2>レースを探す</h2>
          </div>
          <span className="filter-count">{filteredRaces.length} / {races.length}件</span>
        </div>
        <div className="filter-grid compact-form-grid">
          <label>
            開催日
            <select name="date" defaultValue={date}>
              <option value="">すべて</option>
              {dates.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            競馬場
            <select name="venue" defaultValue={venue}>
              <option value="">すべて</option>
              {venues.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            コース
            <select name="courseType" defaultValue={courseType}>
              <option value="">すべて</option>
              {courseTypes.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            距離
            <select name="distance" defaultValue={distance}>
              <option value="">すべて</option>
              {distances.map((item) => (
                <option key={item} value={item}>{item}m</option>
              ))}
            </select>
          </label>
          <label className="keyword-field">
            レース名
            <input name="q" defaultValue={keyword} placeholder="例: ダービー" />
          </label>
        </div>
        <div className="filter-actions">
          <button className="button" type="submit">絞り込む</button>
          <Link className="ghost-button" href="/races">条件クリア</Link>
        </div>
      </form>

      <div className="race-list race-results">
        {filteredRaces.length === 0 && (
          <section className="card empty-state">
            <h2>条件に合うレースがありません</h2>
            <p className="muted">条件を少し広げるか、CSVでレースデータを追加してください。</p>
          </section>
        )}
        {filteredRaces.map((race) => (
          <Link key={race.id} className="card race-card" href={`/races/${race.id}`}>
            <div>
              <p className="muted">{race.date} {race.startTime} / {race.meeting}</p>
              <h2>
                {race.venue}{race.raceNumber}R {race.name}
                {race.grade && <span className="grade-badge">{race.grade}</span>}
              </h2>
            </div>
            <p className="race-meta">
              {race.courseType}{race.distance}m{race.turn ? `・${race.turn}` : ""} / 馬場: {race.going}
              {race.weather ? ` / 天気: ${race.weather}` : ""}
            </p>
            <span className="race-card-action">AI予想と買い目プランを見る</span>
          </Link>
        ))}
      </div>
    </div>
  );
}