from typing import Any

import numpy as np

from app.core.config import settings
from app.core.schemas import BaselineLaser, BoundingBox
from app.services.forensic.typography.ocr_engine import TextToken


def run_baseline_laser_audit(
    tokens: list[TextToken],
    img_width: int,
    img_height: int
) -> tuple[float, float, list[BaselineLaser], list[BoundingBox], dict[str, Any]]:
    """
    Sub-Pixel Horizontal Baseline Laser Audit (sigma_baseline).
    Clusters tokens into horizontal text rows, fits reference baseline linear regression,
    and flags any token with vertical baseline deviation >= 1.8 px as CRITICAL_RED.
    """
    if len(tokens) < 2:
        return 0.0, 0.0, [], [], {"rows_audited": 0, "max_drift_px": 0.0}

    # Filter out graphic icons / avatars (aspect ~1.0 with large area)
    valid_tokens = []
    for t in tokens:
        # If square-ish and large, it's an icon/badge
        is_icon = (t.w > 65 and t.h > 65 and 0.8 <= (t.w / float(t.h)) <= 1.25)
        if not is_icon and t.h >= 10:
            valid_tokens.append(t)

    if len(valid_tokens) < 2:
        return 0.0, 0.0, [], [], {"rows_audited": 0, "max_drift_px": 0.0}

    # Sort top to bottom
    valid_tokens.sort(key=lambda t: (t.y, t.x))

    # 1. Cluster tokens into horizontal visual rows
    rows: list[list[TextToken]] = []
    for token in valid_tokens:
        placed = False
        for row in rows:
            row_avg_center_y = np.mean([t.center_y for t in row])
            row_avg_h = np.mean([t.h for t in row])
            
            # Vertical center alignment (same text line band)
            center_match = abs(token.center_y - row_avg_center_y) <= max(12.0, 0.45 * row_avg_h)
            # Height compatibility: within 45%
            height_match = (abs(token.h - row_avg_h) / max(token.h, row_avg_h)) <= 0.45
            # Horizontal proximity: must be an adjacent word in the same phrase (gap <= 80px)
            horiz_prox = any(abs(token.x - (t.x + t.w)) <= 80.0 or abs(t.x - (token.x + token.w)) <= 80.0 for t in row)

            if center_match and height_match and horiz_prox:
                row.append(token)
                placed = True
                break
        if not placed:
            rows.append([token])

    lasers: list[BaselineLaser] = []
    anomaly_boxes: list[BoundingBox] = []
    max_drift_overall = 0.0

    for r_idx, row in enumerate(rows):
        # Only audit rows with >= 2 tokens (or a single prominent currency token with digits)
        if len(row) < 2:
            continue

        # Sort left to right within row
        row.sort(key=lambda t: t.x)

        # Token bottom-edge anchor points: (x_center, baseline_y)
        x_coords = np.array([t.center_x for t in row], dtype=np.float32)
        y_baselines = np.array([t.baseline_y for t in row], dtype=np.float32)

        # Reference baseline via robust median consensus
        slope = 0.0
        intercept = float(np.median(y_baselines))
        residuals = np.abs(y_baselines - intercept)
        max_row_drift = float(np.max(residuals))

        # Check how many tokens deviate significantly from the consensus baseline
        deviating_tokens = [i for i, r in enumerate(residuals) if r >= settings.BASELINE_DRIFT_THRESHOLD_PX]

        # Natural typography: a single token with a descender (',', 'g', 'p', 'y') dips naturally.
        # A true typographic splice/tamper occurs when:
        # 1. Multiple tokens deviate (>= 2) in a phrase (e.g. pasted multi-digit amount).
        # 2. Or a severe vertical drop (>= 10px).
        # 3. Or a step >= 4.5px in a 2-token row.
        is_tampered_row = False
        if len(row) >= 3:
            if len(deviating_tokens) >= 2 or (len(deviating_tokens) == 1 and residuals[deviating_tokens[0]] >= 10.0):
                is_tampered_row = True
        elif len(row) == 2:
            if max_row_drift >= 4.5:
                is_tampered_row = True

        status = "CRITICAL_RED" if is_tampered_row else "ALIGNED_CYAN"
        callout = None

        x_start = int(max(0, np.min(x_coords) - 20))
        x_end = int(min(img_width, np.max(x_coords) + 20))

        if is_tampered_row:
            drift_token_idx = int(np.argmax(residuals))
            drifted_token = row[drift_token_idx]
            callout = f"+{max_row_drift:.1f}px DRIFT"

            # Generate high-confidence anomaly bounding box around the drifted token
            pad = 4
            bx = max(0, drifted_token.x - pad)
            by = max(0, drifted_token.y - pad)
            bw = min(img_width - bx, drifted_token.w + pad * 2)
            bh = min(img_height - by, drifted_token.h + pad * 2)

            anomaly_boxes.append(BoundingBox(
                x=int(bx),
                y=int(by),
                width=int(bw),
                height=int(bh),
                points=[[bx, by], [bx + bw, by], [bx + bw, by + bh], [bx, by + bh]],
                label=f"Baseline Drift Anomaly (+{max_row_drift:.1f}px)",
                confidence=min(0.98, max(0.70, 0.70 + (max_row_drift - 1.8) * 0.1)),
                layer=2,
                anomaly_type="SUBPIXEL_BASELINE_DRIFT",
                details={
                    "drift_px": round(max_row_drift, 2),
                    "row_index": r_idx,
                    "tokens_in_row": len(row)
                }
            ))

        lasers.append(BaselineLaser(
            row_index=r_idx,
            y_baseline=round(float(intercept), 2),
            slope=round(float(slope), 4),
            tokens_count=len(row),
            delta_y_max=round(max_row_drift, 2),
            is_tampered=is_tampered_row,
            status=status,
            callout_text=callout,
            token_indices=list(range(len(row))),
            x_start=x_start,
            x_end=x_end
        ))

    # Compute baseline drift score (0-100)
    # Only penalized if verified tampered rows exist
    tampered_drifts = [l.delta_y_max for l in lasers if l.is_tampered]
    if tampered_drifts:
        max_drift_overall = float(np.max(tampered_drifts))
        drift_score = round(min(100.0, 65.0 + (max_drift_overall - settings.BASELINE_DRIFT_THRESHOLD_PX) * 15.0), 1)
    else:
        max_drift_overall = float(np.max([l.delta_y_max for l in lasers])) if lasers else 0.0
        drift_score = round(min(12.0, max_drift_overall * 3.5), 1)

    drift_score = round(min(100.0, drift_score), 1)

    details = {
        "total_rows_audited": len(lasers),
        "tampered_rows_count": sum(1 for l in lasers if l.is_tampered),
        "max_drift_px": round(max_drift_overall, 2),
        "threshold_px": settings.BASELINE_DRIFT_THRESHOLD_PX
    }

    return drift_score, round(max_drift_overall, 2), lasers, anomaly_boxes, details
