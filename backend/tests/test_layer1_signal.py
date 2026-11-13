import cv2
import numpy as np
from app.services.forensic.pixel_analysis.copy_move import run_copy_move_analysis
from app.services.forensic.pixel_analysis.ela import run_ela_analysis
from app.services.forensic.pixel_analysis.jpeg_ghosts import run_jpeg_ghost_analysis
from app.services.forensic.pixel_analysis.wavelet_noise import (
    run_wavelet_noise_analysis,
)


def create_test_image(tampered: bool = False) -> np.ndarray:
    """Generates an in-memory BGR image with optional spliced block."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 220
    cv2.putText(img, "TEST VERISIGHT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2)
    cv2.putText(img, "INR 500.00", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (10, 80, 20), 2)

    _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    img_decompressed = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    if tampered:
        patch = np.random.randint(150, 200, (80, 120, 3), dtype=np.uint8)
        cv2.putText(patch, "9999", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 180), 2)
        img_decompressed[180:260, 200:320] = patch

    return img_decompressed


def test_ela_computation():
    img_clean = create_test_image(tampered=False)
    score_clean, ela_b64, anom_clean, boxes_clean, details = run_ela_analysis(img_clean)
    assert ela_b64.startswith("data:image/png;base64,")
    assert isinstance(score_clean, float)

    img_tamp = create_test_image(tampered=True)
    score_tamp, ela_b64_tamp, anom_tamp, boxes_tamp, details_tamp = run_ela_analysis(img_tamp)
    assert score_tamp >= score_clean or anom_tamp >= anom_clean


def test_wavelet_noise_analysis():
    img_clean = create_test_image(tampered=False)
    score, wavelet_b64, boxes, details = run_wavelet_noise_analysis(img_clean)
    assert wavelet_b64.startswith("data:image/webp;base64,") or wavelet_b64.startswith("data:image/png;base64,")
    assert "mean_noise_variance" in details
    assert isinstance(score, float)


def test_copy_move_detection():
    # Construct an image with a duplicated stamp
    img = np.ones((500, 500, 3), dtype=np.uint8) * 230
    stamp = np.zeros((60, 60, 3), dtype=np.uint8)
    cv2.circle(stamp, (30, 30), 20, (0, 150, 0), -1)
    cv2.putText(stamp, "OK", (15, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    img[50:110, 50:110] = stamp
    img[250:310, 300:360] = stamp

    cloned, count, clone_b64, boxes, details = run_copy_move_analysis(img)
    assert clone_b64.startswith("data:image/png;base64,")
    assert isinstance(cloned, bool)
    assert isinstance(count, int)


def test_jpeg_ghost_analysis():
    img_clean = create_test_image(tampered=False)
    ghost_res = run_jpeg_ghost_analysis(img_clean)
    assert 60 <= ghost_res["estimated_carrier_quality"] <= 95
    assert "carrier_min_error" in ghost_res
