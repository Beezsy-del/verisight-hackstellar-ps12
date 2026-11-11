from pathlib import Path
from io import BytesIO

from PIL import Image

from app.main import app
from app.services.forensic.pipeline import analyze_screenshot
from fastapi.testclient import TestClient

client = TestClient(app)
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "HEALTHY")
    assert "VeriSight" in data["service"]


def test_api_demo_samples_list():
    response = client.get("/api/demo-samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) == 5
    sample_ids = [s["id"] for s in samples]
    assert "sample_1" in sample_ids
    assert "sample_2" in sample_ids


def test_sample_1_clean_synthetic_fixture():
    sample_path = SAMPLES_DIR / "sample_1_clean_synthetic_ui.png"
    assert sample_path.exists()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    report = analyze_screenshot(file_bytes, sample_path.name)
    assert report.verdict == "REVIEW_REQUIRED"
    assert any(f.id.startswith("f-receipt-text-") for f in report.findings)
    assert report.confidence_score is None
    assert all(box.confidence is None for box in report.all_bounding_boxes)
    assert not any(f.id == "f-l2-laser" for f in report.findings)


def test_authentic_screenshot_transforms_do_not_escalate_to_manipulated():
    source = Image.open(SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").convert("RGB")
    variants = []
    for quality in (95, 80):
        output = BytesIO()
        source.save(output, format="JPEG", quality=quality)
        variants.append((f"jpeg-{quality}", output.getvalue()))

    resized = BytesIO()
    source.resize((360, 780)).save(resized, format="PNG")
    variants.append(("resized-png", resized.getvalue()))

    cropped = BytesIO()
    source.crop((20, 20, source.width - 20, source.height - 20)).save(cropped, format="PNG")
    variants.append(("cropped-png", cropped.getvalue()))

    for name, data in variants:
        report = analyze_screenshot(data, name)
        assert report.verdict != "CORROBORATED_ANOMALIES", name


def test_png_ela_is_not_scored_as_manipulation_evidence():
    report = analyze_screenshot((SAMPLES_DIR / "sample_1_clean_synthetic_ui.png").read_bytes(), "clean.png")
    assert report.layer1.ela_score == 0
    assert report.layer1.details["ela"]["scoring_eligible"] is False


def test_sample_2_spliced_amount():
    sample_path = SAMPLES_DIR / "sample_2_spliced_amount.jpg"
    assert sample_path.exists()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    report = analyze_screenshot(file_bytes, sample_path.name)
    # This labeled synthetic fixture combines a baseline anomaly with independent cues.
    assert report.verdict == "REVIEW_REQUIRED"


def test_sample_3_temporal_paradox():
    sample_path = SAMPLES_DIR / "sample_3_fake_generator_paradox.png"
    assert sample_path.exists()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    report = analyze_screenshot(file_bytes, sample_path.name)
    assert report.verdict == "REVIEW_REQUIRED"
    assert report.layer3.clock_paradox_detected or report.layer3.upi_utr_valid is False


def test_sample_4_synthetic_jpeg_reencode():
    sample_path = SAMPLES_DIR / "sample_4_synthetic_jpeg_reencode.jpg"
    assert sample_path.exists()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    report = analyze_screenshot(file_bytes, sample_path.name)
    assert not report.layer3.is_whatsapp_laundered
    assert "source unknown" in report.layer3.channel_detected


def test_sample_5_cloned_receipt():
    sample_path = SAMPLES_DIR / "sample_5_cloned_chat_receipt.jpg"
    assert sample_path.exists()
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    report = analyze_screenshot(file_bytes, sample_path.name)
    assert report.overall_tamper_score >= 35.0


def test_api_analyze_sample_endpoint():
    response = client.post("/api/analyze-sample/sample_1")
    assert response.status_code == 200
    data = response.json()
    assert "overall_tamper_score" in data
    assert "verdict" in data
    assert "layer1" in data
    assert "layer2" in data
    assert "layer3" in data
    assert "synergy" in data
