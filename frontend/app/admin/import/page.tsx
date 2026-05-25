import Link from "next/link";
import { ImportCsvForm } from "./ImportCsvForm";

export default function AdminImportPage() {
  return (
    <div className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>CSV取り込み</h1>
        </div>
        <Link className="ghost-button" href="/races">
          レース一覧
        </Link>
      </div>

      <section className="card import-panel admin-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Import</p>
            <h2>レースCSVをアップロード</h2>
          </div>
          <span className="filter-count">local CSV</span>
        </div>
        <p className="muted">
          手元で作成したCSVを取り込み、backend/app/data/races.json を更新します。外部サイトからの自動取得は行いません。
        </p>
        <ImportCsvForm />
      </section>

      <section className="card admin-help-grid">
        <div>
          <p className="eyebrow">Format</p>
          <h2>必要な主な列</h2>
          <p className="muted small">
            race_id, date, venue, race_number, race_name, course_type, distance, going, start_time,
            horse_number, gate_number, horse_name, sex_age, jockey, weight, odds, popularity,
            running_style, recent_form_score, course_aptitude, distance_aptitude, going_aptitude,
            jockey_score, recent_speed_score, power_score
          </p>
        </div>
        <div className="admin-note">
          <strong>取り込み前の確認</strong>
          <p>1行につき1頭です。同じ race_id の行が1つのレースとしてまとめられます。</p>
        </div>
      </section>
    </div>
  );
}