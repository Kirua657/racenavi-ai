"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "../../lib/api";

type ResultFormProps = {
  planId: string;
  initialFirst?: number;
  initialHit?: boolean;
  initialMainPickFinish?: number;
  initialMemo?: string;
  initialPayout?: number;
  initialSecond?: number;
  initialThird?: number;
};

function optionalNumber(value: string) {
  return value.trim() === "" ? null : Number(value);
}

export function ResultForm({
  planId,
  initialFirst,
  initialHit = false,
  initialMainPickFinish,
  initialMemo = "",
  initialPayout = 0,
  initialSecond,
  initialThird,
}: ResultFormProps) {
  const router = useRouter();
  const [hit, setHit] = useState(initialHit);
  const [payout, setPayout] = useState(String(initialPayout));
  const [first, setFirst] = useState(initialFirst ? String(initialFirst) : "");
  const [second, setSecond] = useState(initialSecond ? String(initialSecond) : "");
  const [third, setThird] = useState(initialThird ? String(initialThird) : "");
  const [mainPickFinish, setMainPickFinish] = useState(
    initialMainPickFinish ? String(initialMainPickFinish) : "",
  );
  const [memo, setMemo] = useState(initialMemo);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError("");
    try {
      await apiPost(`/api/bet-plans/${planId}/result`, {
        hit,
        payout: Number(payout),
        first: optionalNumber(first),
        second: optionalNumber(second),
        third: optionalNumber(third),
        mainPickFinish: optionalNumber(mainPickFinish),
        memo,
      });
      router.refresh();
    } catch {
      setError("結果を保存できませんでした。バックエンドが起動しているか確認してください。");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form className="result-form" onSubmit={handleSubmit}>
      <label className="check-row">
        <input checked={hit} onChange={(event) => setHit(event.target.checked)} type="checkbox" />
        的中
      </label>
      <label>
        払戻
        <input
          min={0}
          step={100}
          type="number"
          value={payout}
          onChange={(event) => setPayout(event.target.value)}
        />
      </label>
      <label>
        1着
        <input min={1} max={18} type="number" value={first} onChange={(event) => setFirst(event.target.value)} />
      </label>
      <label>
        2着
        <input min={1} max={18} type="number" value={second} onChange={(event) => setSecond(event.target.value)} />
      </label>
      <label>
        3着
        <input min={1} max={18} type="number" value={third} onChange={(event) => setThird(event.target.value)} />
      </label>
      <label>
        本命の着順
        <input
          min={1}
          type="number"
          value={mainPickFinish}
          onChange={(event) => setMainPickFinish(event.target.value)}
        />
      </label>
      <label className="memo-field">
        メモ
        <input value={memo} onChange={(event) => setMemo(event.target.value)} />
      </label>
      <button className="ghost-button" disabled={isSaving} type="submit">
        {isSaving ? "保存中..." : "結果を保存"}
      </button>
      {error && <p className="error-text">{error}</p>}
    </form>
  );
}