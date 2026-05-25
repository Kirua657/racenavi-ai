import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import admin as admin_api
from app.core import mock_data
from app.main import app


client = TestClient(app)
TMP_ROOT = Path(__file__).resolve().parent / ".tmp_admin"


@pytest.fixture
def work_dir(request):
    path = TMP_ROOT / request.node.name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def valid_csv() -> str:
    return "\n".join(
        [
            "race_id,date,venue,race_number,race_name,course_type,distance,going,start_time,horse_number,gate_number,horse_name,sex_age,jockey,weight,odds,popularity,running_style,recent_form_score,course_aptitude,distance_aptitude,going_aptitude,jockey_score,recent_speed_score,power_score",
            "admin-race,2026-06-14,東京,10,管理画面テスト,芝,1600,良,15:10,1,1,アップロードスター,牡4,田中,57.0,3.5,1,先行,84,82,83,80,81,86,70",
            "admin-race,2026-06-14,東京,10,管理画面テスト,芝,1600,良,15:10,2,2,アップロードムーン,牝4,佐藤,55.0,8.2,4,差し,80,84,82,78,79,81,68",
            "",
        ]
    )


def test_admin_import_race_csv_updates_json_and_reload_data(work_dir, monkeypatch):
    output_path = work_dir / "races.json"
    original_data_path = mock_data.DATA_PATH
    monkeypatch.setattr(admin_api, "DEFAULT_OUTPUT_PATH", output_path)
    monkeypatch.setattr(mock_data, "DATA_PATH", output_path)

    try:
        response = client.post(
            "/api/admin/import-race-csv",
            content=valid_csv().encode("utf-8"),
            headers={"Content-Type": "text/csv; charset=utf-8"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["raceCount"] == 1
        assert body["entryCount"] == 2
        races = client.get("/api/races").json()
        assert races[0]["id"] == "admin-race"
        assert output_path.exists()
    finally:
        mock_data.DATA_PATH = original_data_path
        mock_data.reload_data()


def test_admin_import_race_csv_returns_row_field_errors(work_dir, monkeypatch):
    output_path = work_dir / "races.json"
    monkeypatch.setattr(admin_api, "DEFAULT_OUTPUT_PATH", output_path)
    bad_csv = valid_csv().replace("3.5", "abc", 1)

    response = client.post(
        "/api/admin/import-race-csv",
        content=bad_csv.encode("utf-8"),
        headers={"Content-Type": "text/csv; charset=utf-8"},
    )

    assert response.status_code == 400
    assert "row 2, field 'odds'" in response.json()["detail"]["errors"][0]
    assert not output_path.exists()