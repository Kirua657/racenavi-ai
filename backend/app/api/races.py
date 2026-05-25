from fastapi import APIRouter, HTTPException

from app.core.mock_data import RACES, ENTRIES
from app.services.prediction_service import generate_prediction

router = APIRouter()


@router.get("/races")
def list_races():
    return RACES


@router.get("/races/{race_id}")
def get_race(race_id: str):
    race = next((race for race in RACES if race["id"] == race_id), None)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    entries = [entry for entry in ENTRIES if entry["raceId"] == race_id]
    return {"race": race, "entries": entries}


@router.get("/races/{race_id}/predictions")
def get_predictions(race_id: str):
    race = next((race for race in RACES if race["id"] == race_id), None)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    entries = [entry for entry in ENTRIES if entry["raceId"] == race_id]
    return generate_prediction(race, entries)
