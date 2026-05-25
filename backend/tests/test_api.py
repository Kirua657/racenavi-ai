from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_race_and_prediction_endpoints():
    races = client.get("/api/races")
    assert races.status_code == 200
    race_id = races.json()[0]["id"]

    detail = client.get(f"/api/races/{race_id}")
    assert detail.status_code == 200
    assert detail.json()["entries"]

    prediction = client.get(f"/api/races/{race_id}/predictions")
    assert prediction.status_code == 200
    assert prediction.json()["picks"][0]["mark"] == "◎"


def test_create_bet_plan_endpoint_persists_plan():
    response = client.post(
        "/api/bet-plans",
        json={
            "raceId": "tokyo-2026-05-31-11",
            "budget": 3000,
            "objective": "balanced",
            "riskLevel": "medium",
            "allowTrifecta": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["race"]["name"] == "日本ダービー"
    assert body["totalStake"] <= 3000
    assert body["tickets"]
    assert body["predictionSnapshot"]["picks"]

    plans = client.get("/api/bet-plans")
    assert plans.status_code == 200
    assert any(plan["id"] == body["id"] for plan in plans.json())


def test_update_bet_plan_result_persists_result():
    created = client.post(
        "/api/bet-plans",
        json={
            "raceId": "tokyo-2026-05-31-11",
            "budget": 2000,
            "objective": "hit_rate",
            "riskLevel": "low",
            "allowTrifecta": False,
        },
    ).json()
    response = client.post(
        f"/api/bet-plans/{created['id']}/result",
        json={
            "payout": 1200,
            "hit": True,
            "first": 4,
            "second": 7,
            "third": 1,
            "mainPickFinish": 2,
            "memo": "ワイド的中",
        },
    )
    assert response.status_code == 200
    result = response.json()["plan"]["result"]
    assert result["payout"] == 1200
    assert result["first"] == 4
    assert result["mainPickFinish"] == 2

def test_preview_bet_plan_endpoint_does_not_persist_plan():
    before = client.get("/api/bet-plans").json()
    response = client.post(
        "/api/bet-plans/preview",
        json={
            "raceId": "tokyo-2026-05-31-11",
            "budget": 3000,
            "objective": "balanced",
            "riskLevel": "medium",
            "allowTrifecta": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["race"]["id"] == "tokyo-2026-05-31-11"
    assert body["totalStake"] <= 3000
    assert body["tickets"]

    after = client.get("/api/bet-plans").json()
    assert len(after) == len(before)
    assert not any(plan["id"] == body["id"] for plan in after)
