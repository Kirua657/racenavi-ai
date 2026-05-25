import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).resolve().parents[1] / "test-racenavi.db"
os.environ["RACENAVI_DB_PATH"] = str(TEST_DB_PATH)

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
