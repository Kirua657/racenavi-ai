import Link from "next/link";

export default function HomePage() {
  return (
    <div className="page-stack">
      <section className="hero home-hero">
        <div className="hero-copy">
          <div className="home-logo-lockup">
            <span className="brand-mark home-brand-mark">R</span>
            <div>
              <p className="eyebrow">RaceNavi AI MVP</p>
              <h1>RaceNavi AI</h1>
            </div>
          </div>
          <p className="lead">
            予想の理由、買い目シミュレーション、結果の振り返りまでをひとつにまとめた競馬サポートアプリです。
          </p>
          <div className="hero-actions">
            <Link className="button" href="/races">
              レース一覧を見る
            </Link>
            <Link className="ghost-button" href="/admin/import">
              CSVを取り込む
            </Link>
          </div>
        </div>

        <div className="demo-flow-panel">
          <p className="eyebrow">Demo Flow</p>
          <ol>
            <li>レースを選ぶ</li>
            <li>AI予想の理由を見る</li>
            <li>予算3000円で買い目を作る</li>
            <li>履歴で結果を振り返る</li>
          </ol>
        </div>
      </section>

      <section className="section-grid">
        <div className="card">
          <h2>理由が読める</h2>
          <p className="muted">印だけでなく、コース適性、距離適性、近走内容、オッズ妙味を短く説明します。</p>
        </div>
        <div className="card">
          <h2>予算内で組める</h2>
          <p className="muted">的中重視、バランス重視、リターン重視から買い目配分を作ります。</p>
        </div>
        <div className="card">
          <h2>あとで振り返る</h2>
          <p className="muted">提案を保存し、払戻入力から過去の記録として収支や回収率を確認できます。</p>
        </div>
      </section>
    </div>
  );
}
