import sys
from pathlib import Path

# Add backend directory and root verisight directory to sys.path
backend_dir = Path(__file__).resolve().parent
verisight_dir = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(verisight_dir) not in sys.path:
    sys.path.insert(0, str(verisight_dir))

# Never write test incident records to the user's local notes database.
import pytest
@pytest.fixture(autouse=True)
def isolated_case_storage(tmp_path, monkeypatch):
    from app.services.response import case_store
    monkeypatch.setattr(case_store, "STORE_FILE", tmp_path / "cases.sqlite3")
