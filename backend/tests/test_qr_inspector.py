from io import BytesIO

import cv2
import numpy as np
import qrcode

from app.services.forensic.qr_inspector import inspect_qr_codes
from app.services.forensic.pipeline import analyze_screenshot


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
    assert "pixel_integrity" not in decoded
    assert report["authenticity_verified"] is False
    assert len(report["regions"]) == 1


def test_qr_inspector_does_not_report_qr_when_none_is_present():
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    report = inspect_qr_codes(image)
    assert report["decoded_count"] == 0
    assert report["results"] == []


def test_qr_pattern_is_not_mistaken_for_tampered_text_geometry():
    payload = "upi://pay?pa=merchant%40bank&pn=Example%20Store&am=125.00&cu=INR"
    image = qrcode.make(payload).convert("RGB")
    stream = BytesIO()
    image.save(stream, format="PNG")

    report = analyze_screenshot(stream.getvalue(), "qr-only.png")
    assert report.layer3.details["qr_inspection"]["decoded_count"] == 1
    assert report.layer2.details["tokens_in_qr_regions_excluded"] > 0
    assert not any(row.is_alignment_outlier for row in report.layer2.lasers)
    assert report.verdict == "REVIEW_REQUIRED"
    assert any(f.id == "f-text-coverage" for f in report.findings)
    assert not any(f.id == "f-l2-laser" for f in report.findings)
