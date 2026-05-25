import csv
import shutil
from pathlib import Path

import pytest

from tools.import_race_csv import RaceCsvImportError, import_csv


TMP_ROOT = Path(__file__).resolve().parent / ".tmp_import"


@pytest.fixture
def work_dir(request):
    path = TMP_ROOT / request.node.name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


HEADER = [
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


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


def base_row(**overrides):
    row = {
        "race_id": "race-1",
        "date": "2026-06-07",
        "venue": "東京",
        "race_number": "11",
        "race_name": "テストステークス",
        "course_type": "芝",
        "distance": "1600",
        "going": "良",
        "start_time": "15:45",
        "horse_number": "1",
        "gate_number": "1",
        "horse_name": "テストホース",
        "sex_age": "牡4",
        "jockey": "田中",
        "weight": "57.0",
        "odds": "3.4",
        "popularity": "1",
        "running_style": "差し",
        "recent_form_score": "82",
        "course_aptitude": "83",
        "distance_aptitude": "84",
        "going_aptitude": "80",
        "jockey_score": "81",
        "recent_speed_score": "85",
        "power_score": "70",
    }
    row.update(overrides)
    return row


def test_import_csv_groups_rows_by_race_id(work_dir):
    csv_path = work_dir / "races.csv"
    output_path = work_dir / "races.json"
    write_csv(
        csv_path,
        [
            base_row(horse_number="1", horse_name="テストホース"),
            base_row(horse_number="2", gate_number="2", horse_name="セカンドホース"),
            base_row(race_id="race-2", race_number="12", race_name="次走", horse_number="5", gate_number="3"),
        ],
    )

    payload = import_csv(csv_path, output_path)

    assert output_path.exists()
    assert len(payload["races"]) == 2
    assert payload["races"][0]["id"] == "race-1"
    assert payload["races"][0]["raceNumber"] == 11
    assert len(payload["races"][0]["entries"]) == 2
    entry = payload["races"][0]["entries"][0]
    assert entry["horseNumber"] == 1
    assert entry["carriedWeight"] == 57.0
    assert entry["recentSpeedScore"] == 85
    assert entry["powerScore"] == 70


def test_import_csv_reports_row_and_field_errors(work_dir):
    csv_path = work_dir / "bad.csv"
    output_path = work_dir / "races.json"
    write_csv(
        csv_path,
        [
            base_row(odds="abc", horse_number="1"),
            base_row(horse_number="1", horse_name="重複ホース"),
        ],
    )

    with pytest.raises(RaceCsvImportError) as exc_info:
        import_csv(csv_path, output_path)

    message = str(exc_info.value)
    assert "row 2, field 'odds'" in message
    assert "row 3, field 'horse_number'" in message
    assert not output_path.exists()


def test_import_csv_rejects_missing_required_header(work_dir):
    csv_path = work_dir / "missing_header.csv"
    csv_path.write_text("race_id,date\nrace-1,2026-06-07\n", encoding="utf-8")

    with pytest.raises(RaceCsvImportError) as exc_info:
        import_csv(csv_path, work_dir / "races.json")

    assert "row 1, field 'venue'" in str(exc_info.value)