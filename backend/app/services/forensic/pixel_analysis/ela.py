import base64
from typing import Any

import cv2
import numpy as np

from app.core.config import settings
from app.core.schemas import BoundingBox


def run_ela_analysis(
    img_bgr: np.ndarray,
    is_whatsapp: bool = False,
    override_quality: int = None
) -> tuple[float, str, int, list[BoundingBox], dict[str, Any]]:
    """
    Multi-Scale Error Level Analysis (ELA) with Macroblock Z-Score Splicing Localization.
    Re-compresses in memory as JPEG at Q_ref (75 if WhatsApp/Telegram, otherwise 90).
    Amplifies absolute pixel difference by dynamic gain (x18), renders Inferno colormap,
    and isolates contiguous 16x16 macroblock clusters exceeding mu + 2.6*sigma.
    """
    h, w = img_bgr.shape[:2]

    # 1. Select reference JPEG quality
    if override_quality is not None:
        q_ref = override_quality
    elif is_whatsapp:
        q_ref = 75
    else:
        q_ref = 90

    # 2. Re-compress in memory via Pillow / OpenCV
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q_ref]
    _, enc_buf = cv2.imencode('.jpg', img_bgr, encode_param)
    recompressed_bgr = cv2.imdecode(enc_buf, cv2.IMREAD_COLOR)

    # 3. Compute absolute difference and amplify
    diff = cv2.absdiff(img_bgr, recompressed_bgr)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Dynamic gain
    amplified = np.clip(diff_gray * settings.ELA_DYNAMIC_GAIN, 0, 255).astype(np.uint8)

    # 4. Generate Colormap (INFERNO)
    colormap_img = cv2.applyColorMap(amplified, cv2.COLORMAP_INFERNO)
    _, ela_png = cv2.imencode('.png', colormap_img)
    ela_b64 = f"data:image/png;base64,{base64.b64encode(ela_png.tobytes()).decode('utf-8')}"

    # 5. Macroblock Z-Score Splicing Localization (16x16 blocks)
    block_size = 16
    n_blocks_y = h // block_size
    n_blocks_x = w // block_size

    if n_blocks_y == 0 or n_blocks_x == 0:
        return 0.0, ela_b64, 0, [], {"q_ref": q_ref, "global_mean": 0.0}

    block_means = np.zeros((n_blocks_y, n_blocks_x), dtype=np.float32)
    for by in range(n_blocks_y):
        for bx in range(n_blocks_x):
            block = diff_gray[by*block_size:(by+1)*block_size, bx*block_size:(bx+1)*block_size]
            block_means[by, bx] = np.mean(block)

    mu_ela = float(np.mean(block_means))
    sigma_ela = float(np.std(block_means))
    threshold = max(8.0, mu_ela + (settings.ELA_Z_SCORE_THRESHOLD * sigma_ela))

    # Outlier mask: requires both statistical z-score outlier and minimum absolute error
    outlier_mask = ((block_means >= threshold) & (block_means >= 8.0)).astype(np.uint8) * 255
    anomalous_blocks_count = int(np.sum(outlier_mask > 0))

    # Cluster contiguous blocks into bounding boxes
    contours, _ = cv2.findContours(outlier_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes: list[BoundingBox] = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= 1:  # At least 1-2 blocks
            bx, by, bw, bh = cv2.boundingRect(cnt)
            # Map back to pixel coordinates
            px = int(bx * block_size)
            py = int(by * block_size)
            pw = int(min(bw * block_size, w - px))
            ph = int(min(bh * block_size, h - py))

            # Confidence based on max block z-score in this region
            region_means = block_means[by:by+bh, bx:bx+bw]
            max_val = np.max(region_means) if region_means.size > 0 else threshold
            z_score = float((max_val - mu_ela) / (sigma_ela + 1e-6))
            conf = min(1.0, max(0.5, 0.5 + (z_score - settings.ELA_Z_SCORE_THRESHOLD) * 0.15))

            bounding_boxes.append(BoundingBox(
                x=px,
                y=py,
                width=pw,
                height=ph,
                points=[[px, py], [px + pw, py], [px + pw, py + ph], [px, py + ph]],
                label=f"ELA Compression Anomaly (Z={z_score:.2f})",
                confidence=round(conf, 2),
                layer=1,
                anomaly_type="ELA_MACROBLOCK_OUTLIER",
                details={
                    "z_score": round(z_score, 2),
                    "block_mean": round(float(max_val), 2),
                    "threshold": round(threshold, 2)
                }
            ))

    # 6. Normalized ELA score (0-100)
    # Calibrated based on anomalous block density and max z-score
    max_z = 0.0
    if mu_ela < 3.0 and sigma_ela < 2.0 and anomalous_blocks_count == 0:
        ela_score = round(min(8.0, mu_ela * 1.5), 1)
    else:
        if sigma_ela > 0.1:
            max_z = float((np.max(block_means) - mu_ela) / sigma_ela)

        score_from_blocks = min(60.0, (anomalous_blocks_count / max(1, n_blocks_y * n_blocks_x)) * 500.0)
        score_from_z = min(40.0, max(0.0, (max_z - 2.5) * 12.0))
        ela_score = round(min(100.0, score_from_blocks + score_from_z), 1)

    details = {
        "q_ref": q_ref,
        "global_mean_diff": round(mu_ela, 3),
        "global_std_diff": round(sigma_ela, 3),
        "threshold_value": round(threshold, 3),
        "total_macroblocks": int(n_blocks_y * n_blocks_x),
        "anomalous_blocks": anomalous_blocks_count,
        "max_z_score": round(max_z, 2)
    }

    return ela_score, ela_b64, anomalous_blocks_count, bounding_boxes, details
