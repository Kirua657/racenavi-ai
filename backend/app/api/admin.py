from fastapi import APIRouter, HTTPException, Request

from app.core.mock_data import reload_data
from tools.import_race_csv import DEFAULT_OUTPUT_PATH, RaceCsvImportError, import_csv_text

router = APIRouter()


def _count_entries(payload: dict) -> int:
    return sum(len(race.get("entries", [])) for race in payload.get("races", []))


@router.post("/admin/import-race-csv")
async def import_race_csv(request: Request):
    body = await request.body()
    if not body:
        raise HTTPException(
            status_code=400,
            detail={"errors": ["row 1, field 'file': CSV file is empty"]},
        )

    try:
        csv_text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail={"errors": ["row 1, field 'file': CSV must be UTF-8 encoded"]},
        ) from None

    try:
        payload = import_csv_text(csv_text, DEFAULT_OUTPUT_PATH)
    except RaceCsvImportError as exc:
        raise HTTPException(
            status_code=400,
            detail={"errors": [error.format() for error in exc.errors]},
        ) from exc

    reload_data()
    return {
        "ok": True,
        "raceCount": len(payload.get("races", [])),
        "entryCount": _count_entries(payload),
        "message": "CSVを取り込み、races.jsonを更新しました。",
    }