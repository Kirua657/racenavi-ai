from app.core.mock_data import ENTRIES, RACES
from app.services.prediction_service import generate_prediction


def make_entry(
    entry_id: str,
    horse_name: str,
    horse_number: int,
    popularity: int,
    running_style: str,
    *,
    recent_form: int = 80,
    recent_speed: int | None = None,
    course: int = 80,
    distance: int = 80,
    going: int = 80,
    jockey: int = 80,
    odds: float = 8.0,
    power: int | None = None,
) -> dict:
    entry = {
        "id": entry_id,
        "horseNumber": horse_number,
        "horseName": horse_name,
        "popularity": popularity,
        "odds": odds,
        "runningStyle": running_style,
        "recentFormScore": recent_form,
        "courseAptitude": course,
        "distanceAptitude": distance,
        "goingAptitude": going,
        "jockeyScore": jockey,
    }
    if recent_speed is not None:
        entry["recentSpeedScore"] = recent_speed
    if power is not None:
        entry["powerScore"] = power
    return entry


def test_prediction_has_main_pick():
    race = RACES[0]
    entries = [entry for entry in ENTRIES if entry["raceId"] == race["id"]]
    prediction = generate_prediction(race, entries)
    assert prediction["picks"][0]["mark"] == "◎"
    assert prediction["explanation"]


def test_tokyo_turf_2400_boosts_closing_and_aptitude_reasons():
    race = {"id": "r1", "venue": "東京", "courseType": "芝", "distance": 2400, "going": "良"}
    entries = [
        make_entry("a", "ロングアクセル", 1, 5, "差し", course=88, distance=90),
        make_entry("b", "スピードリード", 2, 1, "逃げ", course=80, distance=80),
    ]

    prediction = generate_prediction(race, entries)
    top = prediction["picks"][0]

    assert top["horseName"] == "ロングアクセル"
    assert any("東京芝2400m" in reason for reason in top["reasons"])
    assert top["conditionAdjustment"] > 0
    assert top["scoreBreakdown"]["styleBonus"] > 0
    assert top["scoreBreakdown"]["courseBonus"] > 0
    assert top["scoreBreakdown"]["distanceBonus"] > 0
    assert top["scoreBreakdown"]["finalScore"] == top["score"]


def test_turf_1200_boosts_front_runner_and_speed():
    race = {"id": "r2", "venue": "中山", "courseType": "芝", "distance": 1200, "going": "良"}
    entries = [
        make_entry("a", "スプリントリード", 3, 4, "先行", recent_speed=90),
        make_entry("b", "ラストチャージ", 8, 3, "追込", recent_speed=78),
    ]

    prediction = generate_prediction(race, entries)
    top = prediction["picks"][0]

    assert top["horseName"] == "スプリントリード"
    assert any("芝1200m" in reason for reason in top["reasons"])


def test_dirt_boosts_front_runner_and_power_going():
    race = {"id": "r3", "venue": "阪神", "courseType": "ダート", "distance": 1800, "going": "良"}
    entries = [
        make_entry("a", "ダートパワー", 5, 4, "逃げ", going=88, power=90),
        make_entry("b", "ターフタイプ", 9, 2, "差し", going=75, power=70),
    ]

    prediction = generate_prediction(race, entries)
    top = prediction["picks"][0]

    assert top["horseName"] == "ダートパワー"
    assert any("ダート" in reason for reason in top["reasons"])


def test_heavy_going_weights_going_aptitude_more_strongly():
    race = {"id": "r4", "venue": "京都", "courseType": "芝", "distance": 2000, "going": "不良"}
    entries = [
        make_entry("a", "タフコンディション", 6, 5, "差し", going=92),
        make_entry("b", "パンパンリード", 2, 2, "先行", going=62),
    ]

    prediction = generate_prediction(race, entries)
    top = prediction["picks"][0]

    assert top["horseName"] == "タフコンディション"
    assert any("不良馬場" in reason for reason in top["reasons"])


def test_value_pick_and_dangerous_favorite_are_detected():
    race = {"id": "r5", "venue": "東京", "courseType": "芝", "distance": 2400, "going": "良"}
    entries = [
        make_entry(
            "a",
            "人気薄ハイバランス",
            11,
            8,
            "差し",
            course=90,
            distance=90,
            recent_form=88,
            odds=20.0,
        ),
        make_entry(
            "b",
            "過信禁物リード",
            1,
            1,
            "逃げ",
            course=68,
            distance=67,
            going=70,
            recent_form=72,
            odds=2.8,
        ),
    ]

    prediction = generate_prediction(race, entries)

    assert prediction["valuePick"]["horseName"] == "人気薄ハイバランス"
    assert prediction["dangerousFavorite"]["horseName"] == "過信禁物リード"
    assert prediction["valuePick"]["scoreBreakdown"]["finalScore"] == prediction["valuePick"]["score"]
    assert prediction["dangerousFavorite"]["scoreBreakdown"]["finalScore"] == prediction["dangerousFavorite"]["score"]
