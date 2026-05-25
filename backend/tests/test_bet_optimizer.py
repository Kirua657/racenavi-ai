import re
from app.core.mock_data import ENTRIES, RACES
from app.services.bet_optimizer import generate_bet_plan
from app.services.prediction_service import generate_prediction


def make_pick(horse_number: int, horse_name: str, popularity: int = 4) -> dict:
    return {
        "horseNumber": horse_number,
        "horseName": horse_name,
        "score": 82,
        "popularity": popularity,
        "odds": 8.0,
        "reasons": ["テスト用"],
    }


def test_bet_plan_does_not_exceed_budget():
    race = RACES[0]
    entries = [entry for entry in ENTRIES if entry["raceId"] == race["id"]]
    prediction = generate_prediction(race, entries)
    request = {
        "raceId": race["id"],
        "budget": 3000,
        "objective": "balanced",
        "riskLevel": "medium",
        "allowTrifecta": True,
    }
    plan = generate_bet_plan(request, prediction)
    assert plan["totalStake"] <= 3000
    assert "保証" in plan["disclaimer"]


def test_balanced_plan_uses_value_pick_and_avoids_dangerous_favorite_as_core():
    dangerous = make_pick(1, "人気先行", popularity=1)
    value_pick = make_pick(7, "穴馬候補", popularity=8)
    prediction = {
        "picks": [
            dangerous,
            make_pick(2, "軸候補"),
            make_pick(3, "相手候補"),
            value_pick,
        ],
        "valuePick": value_pick,
        "dangerousFavorite": dangerous,
    }
    request = {
        "raceId": "race-1",
        "budget": 3000,
        "objective": "balanced",
        "riskLevel": "medium",
        "allowTrifecta": False,
    }

    plan = generate_bet_plan(request, prediction)
    combinations = [ticket["combination"] for ticket in plan["tickets"]]

    assert any("7" in combination for combination in combinations)
    assert all("1" not in combination for combination in combinations)
    assert any("穴馬候補" in note for note in plan["strategyNotes"])
    assert any("危険人気馬" in note for note in plan["strategyNotes"])
    assert plan["totalStake"] <= 3000


def test_return_plan_keeps_trifecta_small_when_allowed():
    value_pick = make_pick(8, "リターン穴馬", popularity=7)
    prediction = {
        "picks": [
            make_pick(2, "本命"),
            make_pick(5, "対抗"),
            make_pick(6, "単穴"),
            value_pick,
        ],
        "valuePick": value_pick,
        "dangerousFavorite": None,
    }
    request = {
        "raceId": "race-2",
        "budget": 5000,
        "objective": "return",
        "riskLevel": "high",
        "allowTrifecta": True,
    }

    plan = generate_bet_plan(request, prediction)
    trifecta = next(ticket for ticket in plan["tickets"] if ticket["betType"] == "3連単")

    assert trifecta["stake"] <= 1000
    assert any("8" in ticket["combination"] for ticket in plan["tickets"])
    assert plan["totalStake"] <= 5000

def test_plan_does_not_create_same_horse_combination_when_value_pick_is_top():
    top = make_pick(12, "Top Value", popularity=8)
    prediction = {
        "picks": [
            top,
            make_pick(5, "Second"),
            make_pick(3, "Third"),
            make_pick(8, "Fourth"),
        ],
        "valuePick": top,
        "dangerousFavorite": None,
    }
    request = {
        "raceId": "race-3",
        "budget": 3000,
        "objective": "balanced",
        "riskLevel": "medium",
        "allowTrifecta": False,
    }

    plan = generate_bet_plan(request, prediction)

    for ticket in plan["tickets"]:
        numbers = re.split(r"-|→", ticket["combination"])
        assert len(numbers) == len(set(numbers))
