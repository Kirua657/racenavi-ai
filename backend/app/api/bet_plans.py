from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.mock_data import ENTRIES, RACES
from app.services.bet_optimizer import generate_bet_plan
from app.services.bet_plan_store import build_race_summary, list_plans, save_plan, update_result
from app.services.history_summary import summarize_plans
from app.services.prediction_service import generate_prediction

router = APIRouter()


def _compact_pick(pick: dict | None) -> dict | None:
    if not pick:
        return None
    keys = ("mark", "horseNumber", "horseName", "score", "confidence", "popularity", "odds")
    return {key: pick[key] for key in keys if key in pick}


def _prediction_snapshot(prediction: dict) -> dict:
    return {
        "picks": [_compact_pick(pick) for pick in prediction.get("picks", [])],
        "valuePick": _compact_pick(prediction.get("valuePick")),
        "dangerousFavorite": _compact_pick(prediction.get("dangerousFavorite")),
    }


def _find_race(race_id: str) -> dict | None:
    return next((race for race in RACES if race["id"] == race_id), None)


def _build_bet_plan(request: "BetPlanRequest") -> tuple[dict, dict]:
    race = _find_race(request.raceId)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    entries = [entry for entry in ENTRIES if entry["raceId"] == request.raceId]
    prediction = generate_prediction(race, entries)
    plan = generate_bet_plan(request.model_dump(), prediction)
    plan["predictionSnapshot"] = _prediction_snapshot(prediction)
    return plan, race


def _with_prediction_snapshot(plan: dict) -> dict:
    if plan.get("predictionSnapshot"):
        return plan
    race = _find_race(plan["raceId"])
    if not race:
        return plan
    entries = [entry for entry in ENTRIES if entry["raceId"] == plan["raceId"]]
    prediction = generate_prediction(race, entries)
    return {**plan, "predictionSnapshot": _prediction_snapshot(prediction)}


class BetPlanRequest(BaseModel):
    raceId: str
    budget: int = Field(ge=100, le=100000)
    objective: Literal["hit_rate", "balanced", "return"] = "balanced"
    riskLevel: Literal["low", "medium", "high"] = "medium"
    allowTrifecta: bool = False


class ResultRequest(BaseModel):
    payout: int = Field(ge=0)
    hit: bool
    first: int | None = Field(default=None, ge=1, le=18)
    second: int | None = Field(default=None, ge=1, le=18)
    third: int | None = Field(default=None, ge=1, le=18)
    mainPickFinish: int | None = Field(default=None, ge=1)
    memo: str | None = None


@router.post("/bet-plans/preview")
def preview_bet_plan(request: BetPlanRequest):
    plan, race = _build_bet_plan(request)
    return {**plan, "race": build_race_summary(race)}


@router.post("/bet-plans")
def create_bet_plan(request: BetPlanRequest):
    plan, race = _build_bet_plan(request)
    return save_plan(plan, race)


@router.get("/bet-plans")
def get_bet_plans():
    return [_with_prediction_snapshot(plan) for plan in list_plans()]


@router.get("/bet-plans/summary")
def get_bet_plan_summary():
    plans = [_with_prediction_snapshot(plan) for plan in list_plans()]
    return summarize_plans(plans)


@router.post("/bet-plans/{plan_id}/result")
def set_result(plan_id: str, request: ResultRequest):
    plan = update_result(plan_id, request.model_dump())
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"ok": True, "plan": plan}