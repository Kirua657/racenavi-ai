from datetime import datetime, timezone
from uuid import uuid4

DISCLAIMER = (
    "この提案は予想情報と買い目シミュレーションであり、的中や利益を保証するものではありません。"
    "馬券の購入は必ずご自身の判断と責任の範囲で行ってください。"
)


def _ticket(bet_type: str, combination: str, stake: int) -> dict:
    return {"betType": bet_type, "combination": combination, "stake": stake}


def _round_to_100(amount: float) -> int:
    return int(amount // 100 * 100)


def _horse_number(pick: dict) -> str:
    return str(pick["horseNumber"])


def _combo(picks: list[dict], count: int = 2) -> str:
    return "-".join(_horse_number(pick) for pick in picks[:count])


def _without_dangerous(picks: list[dict], dangerous: dict | None) -> list[dict]:
    if not dangerous:
        return picks
    return [pick for pick in picks if pick["horseNumber"] != dangerous["horseNumber"]]


def _unique_picks(*pick_groups: dict | list[dict] | None) -> list[dict]:
    seen = set()
    picks: list[dict] = []
    for group in pick_groups:
        if not group:
            continue
        items = group if isinstance(group, list) else [group]
        for pick in items:
            horse_number = pick["horseNumber"]
            if horse_number in seen:
                continue
            seen.add(horse_number)
            picks.append(pick)
    return picks


def _ensure_budget(tickets: list[dict], budget: int) -> list[dict]:
    tickets = [ticket for ticket in tickets if ticket["stake"] >= 100]
    total = sum(ticket["stake"] for ticket in tickets)
    if total > budget and tickets:
        overflow = total - budget
        tickets[-1]["stake"] = max(100, tickets[-1]["stake"] - overflow)
    return [ticket for ticket in tickets if ticket["stake"] >= 100]


def generate_bet_plan(request: dict, prediction: dict) -> dict:
    budget = request["budget"]
    objective = request["objective"]
    risk = request["riskLevel"]
    allow_trifecta = request["allowTrifecta"]
    picks = prediction["picks"]
    value_pick = prediction.get("valuePick")
    dangerous = prediction.get("dangerousFavorite")

    if len(picks) < 3:
        raise ValueError("At least 3 picks are required")

    safer_picks = _without_dangerous(picks, dangerous)
    main_picks = _unique_picks(safer_picks, picks)
    top = main_picks[0]
    second = main_picks[1]
    third = main_picks[2]
    value_pick_number = value_pick["horseNumber"] if value_pick else None
    value_enabled = (
        value_pick is not None
        and objective != "hit_rate"
        and value_pick_number not in {top["horseNumber"], second["horseNumber"]}
    )
    value_partner = value_pick if value_enabled else third
    core_three = _unique_picks([top, second], value_partner, third)[:3]

    tickets = []
    notes = []

    if dangerous and any(pick["horseNumber"] == dangerous["horseNumber"] for pick in picks[:3]):
        notes.append("危険人気馬は人気だけで厚く買わず、中心候補からは控えめにしました。")
    if value_enabled:
        notes.append("穴馬候補を相手候補に入れ、ワイドや3連複で拾える形にしました。")

    if objective == "hit_rate":
        tickets.append(_ticket("複勝", _horse_number(top), _round_to_100(budget * 0.45)))
        tickets.append(_ticket("ワイド", _combo([top, second]), _round_to_100(budget * 0.35)))
        tickets.append(_ticket("ワイド", _combo([top, third]), _round_to_100(budget * 0.20)))
        notes.append("的中重視のため、複勝とワイドを中心に点数を絞りました。")
        rationale = "的中しやすさを重視し、中心馬から複勝とワイドへ配分しています。"
    elif objective == "return":
        tickets.append(_ticket("馬連", _combo([top, second]), _round_to_100(budget * 0.25)))
        tickets.append(_ticket("3連複", _combo(core_three, 3), _round_to_100(budget * 0.35)))
        tickets.append(_ticket("ワイド", _combo([top, value_partner]), _round_to_100(budget * 0.20)))
        remaining = budget - sum(ticket["stake"] for ticket in tickets)
        if (allow_trifecta or risk == "high") and remaining >= 100:
            trifecta_stake = min(remaining, max(100, _round_to_100(budget * 0.20)))
            tickets.append(
                _ticket(
                    "3連単",
                    f"{_horse_number(top)}→{_horse_number(second)}→{_horse_number(core_three[2])}",
                    trifecta_stake,
                )
            )
            remaining -= trifecta_stake
            if remaining >= 100:
                tickets.append(_ticket("ワイド", _combo([second, value_partner]), remaining))
            notes.append("3連単はリスクが高いため、残り予算の範囲で少額にしています。")
        elif remaining >= 100:
            tickets.append(_ticket("ワイド", _combo([second, value_partner]), remaining))
        rationale = "リターンを狙いつつ、穴馬候補を相手に入れた連系の買い目に配分しています。"
    else:
        tickets.append(_ticket("ワイド", _combo([top, second]), _round_to_100(budget * 0.30)))
        tickets.append(_ticket("馬連", _combo([top, second]), _round_to_100(budget * 0.25)))
        tickets.append(_ticket("3連複", _combo(core_three, 3), _round_to_100(budget * 0.25)))
        if value_enabled:
            tickets.append(_ticket("ワイド", _combo([top, value_partner]), _round_to_100(budget * 0.15)))
        remaining = budget - sum(ticket["stake"] for ticket in tickets)
        if allow_trifecta and risk == "high" and remaining >= 100:
            tickets.append(
                _ticket(
                    "3連単",
                    f"{_horse_number(top)}→{_horse_number(second)}→{_horse_number(core_three[2])}",
                    remaining,
                )
            )
        elif remaining >= 100:
            tickets.append(_ticket("複勝", _horse_number(top), remaining))
        rationale = "的中しやすさとリターンのバランスを取り、ワイド、馬連、3連複を中心にしています。"

    tickets = _ensure_budget(tickets, budget)
    total = sum(ticket["stake"] for ticket in tickets)

    return {
        "id": f"plan_{uuid4().hex[:8]}",
        "raceId": request["raceId"],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "budget": budget,
        "objective": objective,
        "riskLevel": risk,
        "allowTrifecta": allow_trifecta,
        "tickets": tickets,
        "totalStake": total,
        "rationale": rationale,
        "strategyNotes": notes,
        "disclaimer": DISCLAIMER,
    }
