import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "races.json"


def _load_data() -> tuple[list[dict], list[dict]]:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    races = []
    entries = []
    for race in payload["races"]:
        race_entries = race.get("entries", [])
        race_without_entries = {key: value for key, value in race.items() if key != "entries"}
        races.append(race_without_entries)
        for entry in race_entries:
            entries.append({**entry, "raceId": race["id"]})
    return races, entries


RACES, ENTRIES = _load_data()


def reload_data() -> tuple[list[dict], list[dict]]:
    races, entries = _load_data()
    RACES.clear()
    RACES.extend(races)
    ENTRIES.clear()
    ENTRIES.extend(entries)
    return RACES, ENTRIES