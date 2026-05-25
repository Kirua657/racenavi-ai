"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type ImportResult = {
  ok: boolean;
  raceCount: number;
  entryCount: number;
  message: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export function ImportCsvForm() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    setResult(null);
    setErrors([]);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResult(null);
    setErrors([]);
    if (!file) {
      setErrors(["CSVファイルを選択してください。"]);
      return;
    }

    setIsUploading(true);
    try {
      const csvText = await file.text();
      const response = await fetch(`${API_BASE}/api/admin/import-race-csv`, {
        method: "POST",
        headers: { "Content-Type": "text/csv; charset=utf-8" },
        body: csvText,
      });
      const body = await response.json();
      if (!response.ok) {
        const detail = body.detail;
        const detailErrors = Array.isArray(detail?.errors) ? detail.errors : [`取り込みに失敗しました。status: ${response.status}`];
        setErrors(detailErrors);
        return;
      }
      setResult(body);
    } catch {
      setErrors(["CSVをアップロードできませんでした。バックエンドが起動しているか確認してください。"]);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form className="import-form" onSubmit={handleSubmit}>
      <label className="file-picker">
        CSVファイル
        <input accept=".csv,text/csv" onChange={handleFileChange} type="file" />
        <span>{file ? file.name : "未選択"}</span>
      </label>
      <button className="button" disabled={isUploading} type="submit">
        {isUploading ? "取り込み中..." : "CSVを取り込む"}
      </button>

      {result && (
        <div className="import-result import-success">
          <strong>{result.message}</strong>
          <p>取り込んだレース: {result.raceCount}件 / 出走馬: {result.entryCount}頭</p>
        </div>
      )}

      {errors.length > 0 && (
        <div className="import-result import-error">
          <strong>CSVを確認してください</strong>
          <ul>
            {errors.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}