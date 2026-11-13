from typing import Any

import cv2
import numpy as np


def run_jpeg_ghost_analysis(
    img_bgr: np.ndarray
) -> dict[str, Any]:
    """
    JPEG Ghost & Quantization Inconsistency Analysis.
    Sweeps candidate qualities q in [55, 95] to measure local error minimas,
    detecting regions compressed at an earlier, different JPEG quality than the carrier.
    """
    h, w = img_bgr.shape[:2]
    # Resize thumbnail for fast sweep
    scale = min(1.0, 600.0 / max(h, w))
    if scale < 1.0:
        small = cv2.resize(img_bgr, (int(w * scale), int(h * scale)))
    else:
        small = img_bgr

    qualities = [60, 70, 75, 80, 85, 90, 95]
    errors = []

    for q in qualities:
        _, enc = cv2.imencode('.jpg', small, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        rec = cv2.imdecode(enc, cv2.IMREAD_COLOR)
        diff = cv2.absdiff(small, rec)
        mean_err = float(np.mean(diff))
        errors.append((q, mean_err))

    # Find minimum error quality
    min_q, min_err = min(errors, key=lambda x: x[1])

    return {
        "candidate_sweep": errors,
        "estimated_carrier_quality": min_q,
        "carrier_min_error": round(min_err, 3)
    }
