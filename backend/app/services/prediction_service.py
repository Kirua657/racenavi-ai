from datetime import datetime, timezone


MARKS = ["◎", "○", "▲"]
FRONT_RUNNING_STYLES = {"逃げ", "先行"}
CLOSING_STYLES = {"差し", "追込"}
HEAVY_GOING = {"重", "不良"}


def odds_value_score(odds: float, popularity: int) -> float:
    """人気だけに寄せすぎないための妙味スコア。"""
    if 4 <= popularity <= 8 and 5.0 <= odds <= 20.0:
        return 88
    if popularity <= 2 and odds < 4.0:
        return 70
    if odds > 30:
        return 55
    return 75


def recent_speed_score(entry: dict) -> float:
    return float(entry.get("recentSpeedScore", entry["recentFormScore"]))


def base_score_without_odds(entry: dict) -> float:
    return (
        entry["recentFormScore"] * 0.24
        + recent_speed_score(entry) * 0.10
        + entry["courseAptitude"] * 0.18
        + entry["distanceAptitude"] * 0.18
        + entry["goingAptitude"] * 0.10
        + entry["jockeyScore"] * 0.10
    )


def base_score(entry: dict) -> float:
    return base_score_without_odds(entry) + odds_value_bonus(entry)


def odds_value_bonus(entry: dict) -> float:
    return odds_value_score(entry["odds"], entry["popularity"]) * 0.10


def condition_bonus_breakdown(race: dict, entry: dict) -> tuple[dict, list[str]]:
    bonuses = {
        "courseBonus": 0.0,
        "distanceBonus": 0.0,
        "styleBonus": 0.0,
        "goingBonus": 0.0,
    }
    reasons: list[str] = []
    course_type = race.get("courseType")
    distance = int(race.get("distance", 0))
    venue = race.get("venue")
    going = race.get("going")
    style = entry.get("runningStyle")

    if venue == "東京" and course_type == "芝" and distance == 2400:
        if style in CLOSING_STYLES:
            bonuses["styleBonus"] += 4.0
            reasons.append("東京芝2400mで差し・追込の持続力を評価")
        if entry["distanceAptitude"] >= 85:
            bonuses["distanceBonus"] += 3.0
            reasons.append("東京芝2400mで距離適性が高い")
        if entry["courseAptitude"] >= 85:
            bonuses["courseBonus"] += 3.0
            reasons.append("東京コース適性が高い")

    if course_type == "芝" and distance == 1200:
        if style in FRONT_RUNNING_STYLES:
            bonuses["styleBonus"] += 4.0
            reasons.append("芝1200mで逃げ・先行力を評価")
        if recent_speed_score(entry) >= 85:
            bonuses["styleBonus"] += 4.0
            reasons.append("芝1200mで近走スピード評価が高い")

    if course_type == "ダート":
        if style in FRONT_RUNNING_STYLES:
            bonuses["styleBonus"] += 4.0
            reasons.append("ダートで前に行ける脚質を評価")
        if entry["goingAptitude"] >= 85:
            bonuses["goingBonus"] += 3.0
            reasons.append("ダートで馬場適性の高さを評価")
        if entry.get("powerScore", 0) >= 85:
            bonuses["styleBonus"] += 3.0
            reasons.append("ダートでパワー型の強みを評価")

    if going in HEAVY_GOING:
        going_bonus = max(-4.0, min(6.0, (entry["goingAptitude"] - 75) * 0.35))
        bonuses["goingBonus"] += going_bonus
        if entry["goingAptitude"] >= 82:
            reasons.append(f"{going}馬場で馬場適性を強めに評価")
        elif entry["goingAptitude"] < 70:
            reasons.append(f"{going}馬場で馬場適性に不安")

    return bonuses, reasons


def condition_adjustment(race: dict, entry: dict) -> tuple[float, list[str]]:
    bonuses, reasons = condition_bonus_breakdown(race, entry)
    adjustment = sum(bonuses.values())
    return adjustment, reasons


def score_breakdown(race: dict, entry: dict) -> tuple[dict, list[str]]:
    condition_bonuses, condition_reasons = condition_bonus_breakdown(race, entry)
    breakdown = {
        "baseScore": round(base_score_without_odds(entry), 2),
        "courseBonus": round(condition_bonuses["courseBonus"], 2),
        "distanceBonus": round(condition_bonuses["distanceBonus"], 2),
        "styleBonus": round(condition_bonuses["styleBonus"], 2),
        "goingBonus": round(condition_bonuses["goingBonus"], 2),
        "oddsValueBonus": round(odds_value_bonus(entry), 2),
    }
    final_score = sum(breakdown.values())
    breakdown["finalScore"] = round(final_score, 2)
    return breakdown, condition_reasons


def calculate_score(entry: dict, race: dict | None = None) -> float:
    if race:
        breakdown, _ = score_breakdown(race, entry)
        return breakdown["finalScore"]
    return round(base_score(entry), 2)


def build_reasons(entry: dict, race: dict, score: float, condition_reasons: list[str]) -> list[str]:
    reasons = list(condition_reasons)
    if entry["courseAptitude"] >= 85:
        reasons.append("コース適性が高い")
    if entry["distanceAptitude"] >= 85:
        reasons.append("距離適性が高い")
    if entry["recentFormScore"] >= 85:
        reasons.append("近走内容の評価が高い")
    if 4 <= entry["popularity"] <= 8:
        reasons.append("人気と能力のバランスに妙味がある")
    if entry["popularity"] >= 6 and score >= 82:
        reasons.append("人気薄だが総合評価が高く穴馬候補")
    if not reasons:
        reasons.append("総合的なバランスが安定している")
    return reasons


def suitability_score(item: dict) -> float:
    return round(
        (
            item["raw"]["courseAptitude"]
            + item["raw"]["distanceAptitude"]
            + item["raw"]["goingAptitude"]
        )
        / 3,
        2,
    )


def generate_explanation(picks: list[dict], dangerous: dict | None, value_pick: dict | None) -> str:
    top = picks[0]
    reason_text = "、".join(top["reasons"][:2])
    text = (
        f"本命の{top['horseName']}は、{reason_text}点を評価しています。"
        "レース条件、脚質、適性、近走内容、オッズの妙味を合わせて判断しています。"
    )
    if value_pick:
        text += (
            f" 穴馬候補の{value_pick['horseName']}は人気以上に総合評価が高く、"
            "相手候補として注意したい一頭です。"
        )
    if dangerous:
        text += (
            f" 一方で、{dangerous['horseName']}は人気上位ですが条件適性が伸びきらないため、"
            "買い目に入れる場合も過信しすぎない設計にしています。"
        )
    text += " この予想は参考情報であり、的中や利益を保証するものではありません。"
    return text


def _public_item(item: dict, mark: str) -> dict:
    return {key: value for key, value in {**item, "mark": mark}.items() if key != "raw"}


def generate_prediction(race: dict, entries: list[dict]) -> dict:
    scored = []
    for entry in entries:
        breakdown, condition_reasons = score_breakdown(race, entry)
        score = breakdown["finalScore"]
        condition_adjustment_value = (
            breakdown["courseBonus"]
            + breakdown["distanceBonus"]
            + breakdown["styleBonus"]
            + breakdown["goingBonus"]
        )
        scored.append(
            {
                "entryId": entry["id"],
                "horseNumber": entry["horseNumber"],
                "horseName": entry["horseName"],
                "score": score,
                "confidence": min(95, max(50, round(score))),
                "reasons": build_reasons(entry, race, score, condition_reasons),
                "popularity": entry["popularity"],
                "odds": entry["odds"],
                "conditionAdjustment": round(condition_adjustment_value, 2),
                "scoreBreakdown": breakdown,
                "raw": entry,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    picks = [_public_item(item, MARKS[index]) for index, item in enumerate(scored[:3])]

    value_candidate = next(
        (
            item
            for item in scored
            if item["popularity"] >= 6 and item["score"] >= 82
        ),
        None,
    )
    value_pick = None
    if value_candidate:
        value_pick = _public_item(value_candidate, "☆")
        if all(pick["horseNumber"] != value_pick["horseNumber"] for pick in picks):
            picks.append(value_pick)

    dangerous_candidate = next(
        (
            item
            for item in scored
            if item["popularity"] <= 3
            and (item["score"] < 78 or suitability_score(item) < 78)
        ),
        None,
    )
    dangerous = None
    if dangerous_candidate:
        dangerous = _public_item(
            {
                **dangerous_candidate,
                "reasons": [
                    *dangerous_candidate["reasons"],
                    "人気上位だが条件適性または総合評価が低い",
                ],
            },
            "危険人気馬",
        )

    return {
        "raceId": race["id"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "picks": picks,
        "valuePick": value_pick,
        "dangerousFavorite": dangerous,
        "explanation": generate_explanation(picks, dangerous, value_pick),
    }