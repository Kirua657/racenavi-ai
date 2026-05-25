from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = BACKEND_DIR / "app" / "data" / "races.json"

REQUIRED_FIELDS = [
    "race_id",
    "date",
    "venue",
    "race_number",
    "race_name",
    "course_type",
    "distance",
    "going",
    "start_time",
    "horse_number",
    "gate_number",
    "horse_name",
    "sex_age",
    "jockey",
    "weight",
    "odds",
    "popularity",
    "running_style",
    "recent_form_score",
    "course_aptitude",
    "distance_aptitude",
    "going_aptitude",
    "jockey_score",
    "recent_speed_score",
    "power_score",
]

RACE_FIELD_MAP = {
    "race_id": "id",
    "date": "date",
    "venue": "venue",
    "race_number": "raceNumber",
    "race_name": "name",
    "course_type": "courseType",
    "distance": "distance",
    "going": "going",
    "start_time": "startTime",
    "meeting": "meeting",
    "grade": "grade",
    "turn": "turn",
    "weather": "weather",
    "conditions": "conditions",
}

ENTRY_FIELD_MAP = {
    "horse_number": "horseNumber",
    "gate_number": "gateNumber",
    "horse_name": "horseName",
    "sex_age": "sexAge",
    "jockey": "jockey",
    "weight": "carriedWeight",
    "odds": "odds",
    "popularity": "popularity",
    "running_style": "runningStyle",
    "recent_form_score": "recentFormScore",
    "course_aptitude": "courseAptitude",
    "distance_aptitude": "distanceAptitude",
    "going_aptitude": "goingAptitude",
    "jockey_score": "jockeyScore",
    "recent_speed_score": "recentSpeedScore",
    "power_score": "powerScore",
    "trainer": "trainer",
    "body_weight": "bodyWeight",
}

RACE_CONSISTENCY_FIELDS = [
    "date",
    "venue",
    "race_number",
    "race_name",
    "course_type",
    "distance",
    "going",
    "start_time",
]


@dataclass
class CsvError:
    row_number: int
    field: str
    message: str

    def format(self) -> str:
        return f"row {self.row_number}, field '{self.field}': {self.message}"


class RaceCsvImportError(ValueError):
    def __init__(self, errors: list[CsvError]):
        self.errors = errors
        super().__init__("Invalid race CSV:\n" + "\n".join(error.format() for error in errors))


def _clean(value: str | None) -> str:
    return "" if value is None else value.strip()


def _required(row: dict[str, str], row_number: int, field: str, errors: list[CsvError]) -> str:
    value = _clean(row.get(field))
    if value == "":
        errors.append(CsvError(row_number, field, "required value is missing"))
    return value


def _parse_int(
    row: dict[str, str],
    row_number: int,
    field: str,
    errors: list[CsvError],
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    raw = _required(row, row_number, field, errors)
    try:
        value = int(raw)
    except ValueError:
        errors.append(CsvError(row_number, field, f"expected integer, got '{raw}'"))
        return 0
    if min_value is not None and value < min_value:
        errors.append(CsvError(row_number, field, f"must be at least {min_value}"))
    if max_value is not None and value > max_value:
        errors.append(CsvError(row_number, field, f"must be at most {max_value}"))
    return value


def _parse_float(
    row: dict[str, str],
    row_number: int,
    field: str,
    errors: list[CsvError],
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    raw = _required(row, row_number, field, errors)
    try:
        value = float(raw)
    except ValueError:
        errors.append(CsvError(row_number, field, f"expected number, got '{raw}'"))
        return 0.0
    if min_value is not None and value < min_value:
        errors.append(CsvError(row_number, field, f"must be at least {min_value:g}"))
    if max_value is not None and value > max_value:
        errors.append(CsvError(row_number, field, f"must be at most {max_value:g}"))
    return value


def _parse_score(row: dict[str, str], row_number: int, field: str, errors: list[CsvError]) -> int:
    return _parse_int(row, row_number, field, errors, min_value=0, max_value=100)


def _validate_date(value: str, row_number: int, errors: list[CsvError]) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        errors.append(CsvError(row_number, "date", "expected YYYY-MM-DD"))


def _validate_start_time(value: str, row_number: int, errors: list[CsvError]) -> None:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError:
        errors.append(CsvError(row_number, "start_time", "expected HH:MM"))


def _validate_header(fieldnames: Iterable[str] | None) -> None:
    header = set(fieldnames or [])
    missing = [field for field in REQUIRED_FIELDS if field not in header]
    if missing:
        errors = [CsvError(1, field, "required column is missing") for field in missing]
        raise RaceCsvImportError(errors)


def _optional(row: dict[str, str], field: str) -> str | None:
    value = _clean(row.get(field))
    return value or None


def _build_race(row: dict[str, str], row_number: int, errors: list[CsvError]) -> dict:
    race_id = _required(row, row_number, "race_id", errors)
    date = _required(row, row_number, "date", errors)
    start_time = _required(row, row_number, "start_time", errors)
    if date:
        _validate_date(date, row_number, errors)
    if start_time:
        _validate_start_time(start_time, row_number, errors)

    course_type = _required(row, row_number, "course_type", errors)
    if course_type and course_type not in {"芝", "ダート"}:
        errors.append(CsvError(row_number, "course_type", "expected '芝' or 'ダート'"))

    race = {
        "id": race_id,
        "date": date,
        "venue": _required(row, row_number, "venue", errors),
        "raceNumber": _parse_int(row, row_number, "race_number", errors, min_value=1),
        "name": _required(row, row_number, "race_name", errors),
        "courseType": course_type,
        "distance": _parse_int(row, row_number, "distance", errors, min_value=100),
        "going": _required(row, row_number, "going", errors),
        "startTime": start_time,
        "dataSource": "local-csv",
        "sourceNote": "手元のCSVから取り込んだデータです。外部サイトから自動取得したものではありません。",
        "entries": [],
    }
    for csv_field, json_field in RACE_FIELD_MAP.items():
        if json_field in race or csv_field in REQUIRED_FIELDS:
            continue
        value = _optional(row, csv_field)
        if value is not None:
            race[json_field] = value
    return race


def _build_entry(row: dict[str, str], row_number: int, errors: list[CsvError]) -> dict:
    horse_number = _parse_int(row, row_number, "horse_number", errors, min_value=1, max_value=18)
    entry = {
        "id": _optional(row, "entry_id") or f"{_required(row, row_number, 'race_id', errors)}-{horse_number}",
        "horseNumber": horse_number,
        "gateNumber": _parse_int(row, row_number, "gate_number", errors, min_value=1, max_value=8),
        "horseName": _required(row, row_number, "horse_name", errors),
        "sexAge": _required(row, row_number, "sex_age", errors),
        "carriedWeight": _parse_float(row, row_number, "weight", errors, min_value=0),
        "jockey": _required(row, row_number, "jockey", errors),
        "odds": _parse_float(row, row_number, "odds", errors, min_value=1.0),
        "popularity": _parse_int(row, row_number, "popularity", errors, min_value=1),
        "runningStyle": _required(row, row_number, "running_style", errors),
        "recentFormScore": _parse_score(row, row_number, "recent_form_score", errors),
        "courseAptitude": _parse_score(row, row_number, "course_aptitude", errors),
        "distanceAptitude": _parse_score(row, row_number, "distance_aptitude", errors),
        "goingAptitude": _parse_score(row, row_number, "going_aptitude", errors),
        "jockeyScore": _parse_score(row, row_number, "jockey_score", errors),
        "recentSpeedScore": _parse_score(row, row_number, "recent_speed_score", errors),
        "powerScore": _parse_score(row, row_number, "power_score", errors),
    }
    for csv_field, json_field in ENTRY_FIELD_MAP.items():
        if json_field in entry or csv_field in REQUIRED_FIELDS:
            continue
        value = _optional(row, csv_field)
        if value is not None:
            entry[json_field] = value
    return entry


def _check_race_consistency(
    base_row: dict[str, str],
    row: dict[str, str],
    row_number: int,
    errors: list[CsvError],
) -> None:
    for field in RACE_CONSISTENCY_FIELDS:
        if _clean(base_row.get(field)) != _clean(row.get(field)):
            errors.append(CsvError(row_number, field, "must match other rows with the same race_id"))


def _import_reader(reader: csv.DictReader, output_path: Path) -> dict:
    errors: list[CsvError] = []
    races_by_id: dict[str, dict] = {}
    first_rows_by_race_id: dict[str, dict[str, str]] = {}
    seen_entries: set[tuple[str, int]] = set()

    _validate_header(reader.fieldnames)
    for row_number, row in enumerate(reader, start=2):
        race_id = _required(row, row_number, "race_id", errors)
        if not race_id:
            continue

        if race_id not in races_by_id:
            races_by_id[race_id] = _build_race(row, row_number, errors)
            first_rows_by_race_id[race_id] = dict(row)
        else:
            _check_race_consistency(first_rows_by_race_id[race_id], row, row_number, errors)

        entry = _build_entry(row, row_number, errors)
        entry_key = (race_id, entry["horseNumber"])
        if entry_key in seen_entries:
            errors.append(CsvError(row_number, "horse_number", "duplicate horse_number in the same race_id"))
        seen_entries.add(entry_key)
        races_by_id[race_id]["entries"].append(entry)

    if errors:
        raise RaceCsvImportError(errors)

    payload = {"races": list(races_by_id.values())}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def import_csv(input_path: Path, output_path: Path = DEFAULT_OUTPUT_PATH) -> dict:
    with input_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return _import_reader(reader, output_path)


def import_csv_text(csv_text: str, output_path: Path = DEFAULT_OUTPUT_PATH) -> dict:
    reader = csv.DictReader(io.StringIO(csv_text))
    return _import_reader(reader, output_path)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import RaceNavi race data from a local CSV file.")
    parser.add_argument("csv_path", type=Path, help="Path to the source CSV file")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output races.json path (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = import_csv(args.csv_path, args.output)
    except RaceCsvImportError as exc:
        print(exc)
        return 1
    print(f"Imported {len(payload['races'])} race(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())