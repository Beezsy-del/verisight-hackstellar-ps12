from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_registry_truthful():
    d=client.get("/api/model/status").json()
    assert d["active_model_id"] == "heuristic-review-v2"
    assert d["calibration_status"] == "UNAVAILABLE"
    assert not d["ml_environment_ready"]

def test_evaluation_and_run_fail_closed():
    for route in ("/api/model/evaluation", "/api/benchmark/results"):
        d=client.get(route).json()
        assert d["status"] == "UNAVAILABLE"
        assert d["roc_evaluation"] == {}
        assert d["release_gate"] == "BLOCK"
    assert client.post("/api/benchmark/run").status_code == 409

def test_analysis_no_probability_or_settlement():
    d=client.post("/api/analyze-sample/sample_clean").json()
    assert d["source_kind"] == "SYNTHETIC_FIXTURE"
    assert d["case_id"] == "sample_clean"
    assert d["confidence_score"] is None
    assert d["model_metadata"]["calibrated_probability"] is None
    assert d["payment_status"] == "NOT_VERIFIED"
    assert d["assessment_dimensions"]["forensic_uncertainty_score"] is None
