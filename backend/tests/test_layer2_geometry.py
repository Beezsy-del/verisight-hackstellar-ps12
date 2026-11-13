import cv2
import numpy as np
from app.services.forensic.typography.baseline_laser import run_baseline_laser_audit
from app.services.forensic.typography.cielab_patch import (
    run_cielab_patch_and_sharpness_audit,
)
from app.services.forensic.typography.ocr_engine import (
    TextToken,
    extract_text_tokens_offline,
)


def create_receipt_text_image(skew_amount: bool = False) -> np.ndarray:
    """Creates a high-contrast receipt text banner."""
    img = np.ones((200, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img, "Paid to Merchant", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    y_amount = 140
    if skew_amount:
        patch = np.ones((50, 150, 3), dtype=np.uint8) * 250
        cv2.putText(patch, "9,999", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2)
        img[y_amount + 6:y_amount + 56, 120:270] = patch
        cv2.putText(img, "INR", (50, y_amount), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    else:
        cv2.putText(img, "INR 1,250.00", (50, y_amount), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    return img


def test_ocr_engine_token_extraction():
    img = create_receipt_text_image(skew_amount=False)
    tokens = extract_text_tokens_offline(img)
    assert len(tokens) > 0
    first = tokens[0]
    assert isinstance(first, TextToken)
    assert first.w > 0 and first.h > 0
    assert first.baseline_y >= first.y


def test_baseline_laser_clean():
    # Construct artificial text tokens on perfectly aligned baseline
    tokens = [
        TextToken(text="Paid", bbox=[50, 50, 60, 30], confidence=0.99),
        TextToken(text="to", bbox=[120, 55, 30, 25], confidence=0.99),
        TextToken(text="Merchant", bbox=[160, 48, 100, 32], confidence=0.99),
    ]
    # Override baseline_y
    tokens[0].baseline_y = 80.0
    tokens[1].baseline_y = 80.1
    tokens[2].baseline_y = 79.9

    score, max_drift, lasers, boxes, details = run_baseline_laser_audit(tokens, 600, 200)
    assert max_drift < 0.5
    assert not any(l.is_tampered for l in lasers)


def test_baseline_laser_spliced():
    # Construct artificial text tokens where the amount phrase is spliced with a 6.0px drop
    tokens = [
        TextToken(text="Paid", bbox=[50, 100, 50, 30], confidence=0.99),
        TextToken(text="to", bbox=[110, 100, 30, 30], confidence=0.99),
        TextToken(text="Store", bbox=[150, 100, 60, 30], confidence=0.99),
        TextToken(text="INR", bbox=[220, 106, 40, 30], confidence=0.99),
        TextToken(text="99,000", bbox=[270, 106, 80, 30], confidence=0.99),
    ]
    tokens[0].baseline_y = 130.0
    tokens[1].baseline_y = 130.0
    tokens[2].baseline_y = 130.0
    tokens[3].baseline_y = 136.0  # Spliced!
    tokens[4].baseline_y = 136.0  # Spliced!

    score, max_drift, lasers, boxes, details = run_baseline_laser_audit(tokens, 600, 200)
    assert max_drift >= 3.0
    assert any(l.is_tampered for l in lasers)


def test_cielab_patch_analysis():
    # Clean uniform card
    img_clean = np.ones((300, 300, 3), dtype=np.uint8) * 245
    cv2.rectangle(img_clean, (20, 20), (280, 280), (255, 255, 255), -1)
    tokens_clean = [
        TextToken(text="INR", bbox=[50, 50, 40, 20]),
        TextToken(text="500", bbox=[100, 50, 40, 20]),
    ]
    max_d_e_clean, patch_anom, sharp_anom, boxes, details = run_cielab_patch_and_sharpness_audit(img_clean, tokens_clean)
    assert max_d_e_clean < 2.5

    # Tampered card with a spliced off-color patch
    img_tamp = np.ones((300, 300, 3), dtype=np.uint8) * 245
    cv2.rectangle(img_tamp, (20, 20), (280, 280), (255, 255, 255), -1)
    cv2.rectangle(img_tamp, (90, 40), (160, 80), (220, 230, 220), -1)
    tokens_tamp = [
        TextToken(text="INR", bbox=[50, 50, 40, 20]),
        TextToken(text="9999", bbox=[100, 50, 40, 20]),
    ]
    max_d_e_tamp, patch_anom_tamp, sharp_anom_tamp, boxes_tamp, details_tamp = run_cielab_patch_and_sharpness_audit(img_tamp, tokens_tamp)
    assert max_d_e_tamp > max_d_e_clean
