from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"


def test_each_demo_endpoint_matches_its_published_verdict():
    samples = client.get("/api/demo-samples").json()
    assert len(samples) == 6
    for sample in samples:
        response = client.post(f"/api/analyze-sample/{sample['id']}")
        assert response.status_code == 200
        assert sample["expected_verdict"] == "UNSPECIFIED"
        assert response.json()["confidence_score"] is None
        assert response.json()["case_id"] == sample["id"]


def test_unknown_demo_sample_is_a_404():
    response = client.post("/api/analyze-sample/not-a-sample")
    assert response.status_code == 404


def test_model_status_does_not_claim_a_trained_classifier():
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["architecture"] == "Deterministic image and metadata cues"
    assert data["active_model_id"] == "heuristic-review-v2"
    assert data["calibration_status"] == "UNAVAILABLE"


def test_model_evaluation_reports_missing_validation_data():
    response = client.get("/api/model/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNAVAILABLE"
    assert data["release_readiness"]["training_permitted"] is False
    assert data["test_set_locked"] is False
    assert data["metrics"] is None


def test_client_side_routes_serve_the_spa_entrypoint():
    for path in ("/workbench", "/evaluation"):
        response = client.get(path)
        assert response.status_code == 200
        assert 'id="root"' in response.text


def test_upload_analysis_endpoint_accepts_an_image():
    image = (SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").read_bytes()
    response = client.post(
        "/api/analyze",
        files={"file": ("capture.png", image, "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "capture.png"


def test_whatsapp_simulation_endpoint_returns_comparison():
    image = (SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").read_bytes()
    response = client.post(
        "/api/simulate-whatsapp",
        files={"file": ("capture.png", image, "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["simulated_image_b64"].startswith("data:image/")
    assert response.json()["reanalysis"]["file_sha256"]


def test_production_mobile_upload_requires_paired_session(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VERISIGHT_ACCESS_PASSWORD", "test-password")
    image = (SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").read_bytes()
    response = client.post(
        "/api/mobile-upload",
        auth=("verisight", "test-password"),
        files={"file": ("capture.png", image, "image/png")},
    )
    assert response.status_code == 400


def test_mobile_upload_is_delivered_only_to_its_session():
    session_id = str(uuid4())
    image = (SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").read_bytes()
    uploaded = client.post(
        f"/api/mobile-upload?session_id={session_id}",
        files={"file": ("phone.png", image, "image/png")},
    )
    assert uploaded.status_code == 200
    assert uploaded.json()["status"] == "SUCCESS"

    other_session = client.get(f"/api/latest-mobile-upload?session_id={uuid4()}")
    assert other_session.status_code == 200
    assert other_session.json()["report"] is None

    paired_session = client.get(f"/api/latest-mobile-upload?session_id={session_id}")
    assert paired_session.status_code == 200
    assert paired_session.json()["report"]["filename"] == "phone.png"
