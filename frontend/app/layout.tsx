import Link from "next/link";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "RaceNavi AI",
  description: "予想の理由から買い方までサポートする競馬アプリ",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <header className="site-header">
          <div className="site-header-inner">
            <Link className="brand-link" href="/">
              <span className="brand-mark">R</span>
              <span>
                <strong>RaceNavi AI</strong>
                <small>競馬予想サポートMVP</small>
              </span>
            </Link>
            <nav className="site-nav" aria-label="主要ナビゲーション">
              <Link href="/races">レース一覧</Link>
              <Link href="/history">保存した予想</Link>
              <Link href="/admin/import">CSV取り込み</Link>
            </nav>
          </div>
        </header>
        <main className="app-shell">{children}</main>
        <footer className="site-footer">
          <p>RaceNavi AIは予想情報と学習用の記録を整理するMVPです。結果を約束するものではありません。</p>
        </footer>
      </body>
    </html>
  );
}