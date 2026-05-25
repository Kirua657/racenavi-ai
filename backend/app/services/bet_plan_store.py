import json
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "racenavi.db"


def _db_path() -> Path:
    return Path(os.environ.get("RACENAVI_DB_PATH", DEFAULT_DB_PATH))


def _connect() -> sqlite3.Connection:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bet_plans (
            id TEXT PRIMARY KEY,
            race_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            plan_json TEXT NOT NULL
        )
        """
    )
    return connection


def build_race_summary(race: dict) -> dict:
    return {
        "id": race["id"],
        "date": race.get("date"),
        "venue": race.get("venue"),
        "meeting": race.get("meeting"),
        "raceNumber": race.get("raceNumber"),
        "name": race.get("name"),
        "grade": race.get("grade"),
        "courseType": race.get("courseType"),
        "distance": race.get("distance"),
        "going": race.get("going"),
        "startTime": race.get("startTime"),
    }


def save_plan(plan: dict, race: dict) -> dict:
    stored_plan = {**plan, "race": build_race_summary(race)}
    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO bet_plans (id, race_id, created_at, plan_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                stored_plan["id"],
                stored_plan["raceId"],
                stored_plan["createdAt"],
                json.dumps(stored_plan, ensure_ascii=False),
            ),
        )
    return stored_plan


def list_plans() -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT plan_json FROM bet_plans ORDER BY created_at DESC"
        ).fetchall()
    return [json.loads(row["plan_json"]) for row in rows]


def get_plan(plan_id: str) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT plan_json FROM bet_plans WHERE id = ?",
            (plan_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["plan_json"])


def update_result(plan_id: str, result: dict) -> dict | None:
    plan = get_plan(plan_id)
    if not plan:
        return None
    plan["result"] = result
    with _connect() as connection:
        connection.execute(
            "UPDATE bet_plans SET plan_json = ? WHERE id = ?",
            (json.dumps(plan, ensure_ascii=False), plan_id),
        )
    return plan
