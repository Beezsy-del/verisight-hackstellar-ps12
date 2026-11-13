from io import BytesIO

import cv2
import numpy as np
import qrcode

from app.services.forensic.qr_inspector import inspect_qr_codes
from app.services.forensic.pipeline import analyze_screenshot
from app.services.forensic.intelligence.syndicate import (
    extract_financial_entities,
    evaluate_syndicate_threat,
    generate_section91_subpoena,
)


def test_qr_inspector_decodes_upi_fields_without_claiming_authenticity():
    payload = "upi://pay?pa=merchant%40bank&pn=Example%20Store&am=125.00&cu=INR&tr=REF123"
    image = cv2.QRCodeEncoder_create().encode(payload)
    canvas = np.full((image.shape[0] + 80, image.shape[1] + 80), 255, dtype=np.uint8)
    canvas[40:-40, 40:-40] = image
    report = inspect_qr_codes(cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR))

    assert report["decoded_count"] == 1
    decoded = report["results"][0]
    assert decoded["kind"] == "UPI_PAYMENT_INTENT"
    assert decoded["payee_vpa"] == "merchant@bank"
    assert decoded["amount"] == "125.00"
    assert decoded["authenticity_verified"] is False
    assert report["authenticity_verified"] is False
    assert len(report["regions"]) == 1


def test_qr_inspector_does_not_report_qr_when_none_is_present():
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    report = inspect_qr_codes(image)
    assert report["decoded_count"] == 0
    assert report["results"] == []


def test_syndicate_intelligence_extraction_and_section91():
    fake_tokens = [
        {"text": "Paid", "box": [10, 10, 30, 15]},
        {"text": "to", "box": [45, 10, 20, 15]},
        {"text": "Rajesh", "box": [70, 10, 50, 15]},
        {"text": "Kumar", "box": [125, 10, 50, 15]},
        {"text": "rajesh@okhdfcbank", "box": [10, 35, 120, 15]},
        {"text": "₹95,250.00", "box": [10, 60, 90, 25]},
        {"text": "UPI Ref No: 1234567890", "box": [10, 95, 160, 15]},
    ]
    entities = extract_financial_entities(fake_tokens)
    assert entities["payee_vpa"] == "rajesh@okhdfcbank"
    assert entities["amount"] == "95,250.00"
    assert entities["utr_number"] == "1234567890"

    threat = evaluate_syndicate_threat(
        entities=entities,
        tamper_score=92.0,
        verdict="CORROBORATED_ANOMALIES",
        clock_paradox=True,
    )
    assert threat["syndicate_risk_level"] == "UNVERIFIED"
    assert threat["threat_indicators"] == []

    notice = generate_section91_subpoena(
        report_sha256="abc123def4567890abcdef1234567890",
        filename="test_evidence.png",
        timestamp="2026-11-10T12:00:00",
        entities=entities,
        tamper_score=92.0,
        verdict="CORROBORATED_ANOMALIES",
        findings=[{"severity": "CRITICAL", "layer": 2, "title": "Baseline Drift", "description": "Spliced text"}],
    )
    assert "PERSONAL DRAFT" in notice
    assert "Not a subpoena" in notice
    assert "rajesh@okhdfcbank" in notice
    assert "95,250.00" in notice
