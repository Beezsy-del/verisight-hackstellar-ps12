from typing import Any

import cv2
import numpy as np

from app.core.config import settings
from app.core.schemas import BoundingBox
from app.services.forensic.typography.ocr_engine import TextToken


def run_cielab_patch_and_sharpness_audit(
    img_bgr: np.ndarray,
    tokens: list[TextToken]
) -> tuple[float, bool, bool, list[BoundingBox], dict[str, Any]]:
    """
    CIELAB Perceptual Background Patch / Halo Detector (Delta-E_ab) & Edge Gradient Sharpness Z-score.
    Samples inner background ring (2-5px) vs outer reference card background (10-18px).
    Computes Delta-E_ab in CIELAB space and flags patches exceeding Delta-E > 2.4.
    Computes Laplacian sharpness variance per token and flags tokens with |Z_sharpness| > 2.1.
    """
    h_img, w_img = img_bgr.shape[:2]
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab).astype(np.float32)
    # OpenCV maps L: 0..255 (0..100 in standard CIE), a: 0..255 (-128..127), b: 0..255 (-128..127)
    # Rescale to standard CIE units: L* = L * 100 / 255, a* = a - 128, b* = b - 128
    L = lab[:, :, 0] * (100.0 / 255.0)
    A = lab[:, :, 1] - 128.0
    B = lab[:, :, 2] - 128.0

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_32F)

    patch_bounding_boxes: list[BoundingBox] = []
    max_delta_e = 0.0
    sharpness_values = []
    token_delta_es = []

    for t_idx, token in enumerate(tokens):
        x, y, w, h = token.bbox

        # 1. Edge Sharpness Variance (Laplacian variance inside token)
        token_lap = laplacian[max(0, y):min(h_img, y+h), max(0, x):min(w_img, x+w)]
        token_sharpness = float(np.var(token_lap)) if token_lap.size > 0 else 0.0
        sharpness_values.append(token_sharpness)

        # 2. CIELAB Background Patch Sampling (Sampling margins around token to avoid text strokes)
        # Immediate local background: sample 2px to 12px directly left or right of the token
        margin_samples_L = []
        margin_samples_A = []
        margin_samples_B = []

        # Left margin
        mx1 = max(0, x - 12)
        mx2 = max(0, x - 2)
        my1 = max(0, y + 2)
        my2 = min(h_img, y + h - 2)
        if mx2 > mx1 and my2 > my1:
            margin_samples_L.extend(L[my1:my2, mx1:mx2].flatten())
            margin_samples_A.extend(A[my1:my2, mx1:mx2].flatten())
            margin_samples_B.extend(B[my1:my2, mx1:mx2].flatten())

        # Right margin
        rx1 = min(w_img, x + w + 2)
        rx2 = min(w_img, x + w + 12)
        if rx2 > rx1 and my2 > my1:
            margin_samples_L.extend(L[my1:my2, rx1:rx2].flatten())
            margin_samples_A.extend(A[my1:my2, rx1:rx2].flatten())
            margin_samples_B.extend(B[my1:my2, rx1:rx2].flatten())

        if len(margin_samples_L) >= 8:
            local_L = float(np.median(margin_samples_L))
            local_A = float(np.median(margin_samples_A))
            local_B = float(np.median(margin_samples_B))
        else:
            local_L, local_A, local_B = None, None, None

        # Reference Background Card: sample 10px to 22px vertically above the token
        out_y1 = max(0, y - 22)
        out_y2 = max(out_y1 + 1, y - 8)
        out_x1 = max(0, x)
        out_x2 = min(w_img, x + w)

        # If top is out of bounds (status bar), sample below
        if out_y2 - out_y1 < 4 or y < 30:
            out_y1 = min(h_img - 4, y + h + 8)
            out_y2 = min(h_img, y + h + 22)

        if out_y2 > out_y1 and out_x2 > out_x1 and local_L is not None:
            ref_L = float(np.median(L[out_y1:out_y2, out_x1:out_x2]))
            ref_A = float(np.median(A[out_y1:out_y2, out_x1:out_x2]))
            ref_B = float(np.median(B[out_y1:out_y2, out_x1:out_x2]))

            # Only compare if both are on a card background (i.e. not dark UI border)
            if local_L > 45.0 and ref_L > 45.0:
                delta_e = float(np.sqrt((local_L - ref_L)**2 + (local_A - ref_A)**2 + (local_B - ref_B)**2))
            else:
                delta_e = 0.0
        else:
            delta_e = 0.0

        token_delta_es.append(delta_e)
        max_delta_e = max(max_delta_e, delta_e)

        # Flag patch anomaly if Delta-E exceeds threshold (2.4)
        if delta_e >= settings.CIELAB_DELTA_E_THRESHOLD:
            conf = min(0.99, max(0.65, 0.65 + (delta_e - 2.4) * 0.08))
            patch_bounding_boxes.append(BoundingBox(
                x=int(x),
                y=int(y),
                width=int(w),
                height=int(h),
                points=[[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                label=f"Color Patch Mismatch (ΔE={delta_e:.1f})",
                confidence=round(conf, 2),
                layer=2,
                anomaly_type="LOCAL_BACKGROUND_PATCH_MISMATCH",
                details={
                    "delta_e": round(delta_e, 2),
                    "inner_lab": [round(local_L, 1), round(local_A, 1), round(local_B, 1)] if local_L is not None else [0.0, 0.0, 0.0],
                    "outer_lab": [round(ref_L, 1), round(ref_A, 1), round(ref_B, 1)] if local_L is not None else [0.0, 0.0, 0.0]
                }
            ))

    # 3. Compute Sharpness Z-Scores across all tokens
    sharpness_anomaly = False
    if len(sharpness_values) >= 4:
        sharp_arr = np.array(sharpness_values, dtype=np.float32)
        mu_sharp = float(np.mean(sharp_arr))
        sigma_sharp = float(np.std(sharp_arr))

        if sigma_sharp > 1e-4:
            for t_idx, sharp_val in enumerate(sharpness_values):
                z_sharp = float((sharp_val - mu_sharp) / sigma_sharp)
                if abs(z_sharp) >= settings.SHARPNESS_Z_THRESHOLD:
                    sharpness_anomaly = True
                    token = tokens[t_idx]
                    # Check if already in bounding boxes to prevent duplicates
                    existing = any(b.x == token.x and b.y == token.y for b in patch_bounding_boxes)
                    if not existing:
                        patch_bounding_boxes.append(BoundingBox(
                            x=int(token.x),
                            y=int(token.y),
                            width=int(token.w),
                            height=int(token.h),
                            points=[[token.x, token.y], [token.x + token.w, token.y], [token.x + token.w, token.y + token.h], [token.x, token.y + token.h]],
                            label=f"Anti-Aliasing Sharpness Inconsistency (Z={z_sharp:.2f})",
                            confidence=min(0.95, 0.60 + abs(z_sharp - 2.1) * 0.1),
                            layer=2,
                            anomaly_type="SHARPNESS_Z_ANOMALY",
                            details={"sharpness_z_score": round(z_sharp, 2)}
                        ))

    cielab_anomaly = (max_delta_e >= settings.CIELAB_DELTA_E_THRESHOLD)

    details = {
        "max_delta_e": round(max_delta_e, 2),
        "threshold_delta_e": settings.CIELAB_DELTA_E_THRESHOLD,
        "cielab_patch_detected": cielab_anomaly,
        "sharpness_anomaly_detected": sharpness_anomaly,
        "total_tokens_tested": len(tokens)
    }

    return round(max_delta_e, 2), cielab_anomaly, sharpness_anomaly, patch_bounding_boxes, details
