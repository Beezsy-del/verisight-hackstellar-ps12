from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import pytest
from app.services.forensic.pipeline import analyze_screenshot


def receipt(text, fmt='PNG'):
    image = np.full((800, 720, 3), 255, np.uint8)
    cv2.putText(image, text, (35, 300), cv2.FONT_HERSHEY_SIMPLEX, .65, (0,0,0), 1, cv2.LINE_AA)
    out=BytesIO(); Image.fromarray(image).save(out,format=fmt)
    return out.getvalue()

@pytest.mark.parametrize('text', ['FAKE PAYMENT RECEIPT','FOR DEMO ONLY','NOT A REAL TRANSACTION','Payment failed','Transaction declined'])
@pytest.mark.parametrize('fmt',['PNG','JPEG'])
def test_visible_negative_receipt_text_is_not_favorable(text,fmt):
    report=analyze_screenshot(receipt(text,fmt))
    assert report.verdict == 'REVIEW_REQUIRED'
    assert any(f.id.startswith('f-receipt-text-') for f in report.findings)

@pytest.mark.parametrize('text',['Payment successful','Report fake payment receipts','Never share OTP','Payment failed? Contact support'])
def test_non_assertions_are_not_treated_as_negative_receipt_evidence(text):
    report=analyze_screenshot(receipt(text))
    assert not any(f.id.startswith('f-receipt-text-') for f in report.findings)


def test_unavailable_ocr_does_not_silently_produce_favorable_result(monkeypatch):
    monkeypatch.setattr('app.services.forensic.typography.receipt_text.inspect_receipt_text',
        lambda image: ([], {'status':'UNAVAILABLE','recognized_lines':0}))
    report=analyze_screenshot(receipt('Payment successful'))
    assert report.verdict != 'INCONCLUSIVE'
    assert any(f.id == 'f-text-coverage' for f in report.findings)


def test_low_confidence_text_does_not_create_fake_evidence():
    from app.services.forensic.typography.receipt_text import receipt_text_findings
    assert receipt_text_findings([{'text':'FAKE PAYMENT RECEIPT','confidence':.4,'bbox':[0,0,100,20]}]) == []
