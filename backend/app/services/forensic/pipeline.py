import base64
import hashlib
from datetime import datetime

import cv2
import numpy as np

from app.core.schemas import (
    ForensicAnalysisReport,
    Layer1SignalResult,
    Layer2GeometryResult,
    Layer3MetadataResult,
    Layer4SemanticResult,
)
from app.services.forensic.ensemble.calibrator import calibrate_ensemble
from app.services.forensic.metadata.domain_rules import (
    check_whatsapp_recompression,
    validate_temporal_and_upi_rules,
)
from app.services.forensic.metadata.exif_inspector import inspect_image_metadata
from app.services.forensic.metadata.viewport_db import check_viewport_geometry
from app.services.forensic.pixel_analysis.copy_move import run_copy_move_analysis
from app.services.forensic.pixel_analysis.ela import run_ela_analysis
from app.services.forensic.pixel_analysis.jpeg_ghosts import run_jpeg_ghost_analysis
from app.services.forensic.pixel_analysis.wavelet_noise import (
    run_wavelet_noise_analysis,
)
from app.services.forensic.provenance.c2pa_inspector import inspect_c2pa_provenance
from app.services.forensic.qr_inspector import inspect_qr_codes
from app.services.forensic.typography.baseline_laser import run_baseline_laser_audit
from app.services.forensic.typography.cielab_patch import (
    run_cielab_patch_and_sharpness_audit,
)
from app.services.forensic.typography.ocr_engine import extract_text_tokens


def analyze_screenshot(
    image_bytes: bytes,
    filename: str = "screenshot.png",
    is_whatsapp_simulated: bool = False
) -> ForensicAnalysisReport:
    """
    Master 4-Layer Forensic Investigation Pipeline Orchestrator.
    Runs image residual cues, text-like component geometry, metadata rules,
    QR decoding, and rule-based review scoring.
    """
    # 1. Cryptographic SHA-256 Hash & Timestamp
    sha256_hash = hashlib.sha256(image_bytes).hexdigest()
    timestamp_iso = datetime.now().isoformat()

    # 2. Decode Image
    from app.services.image_validation import decode_image
    img_bgr = decode_image(image_bytes)

    h, w = img_bgr.shape[:2]

    # 3. Layer 3 Initial: Metadata, container chunks, and weak image-profile cues
    metadata_info = inspect_image_metadata(image_bytes, filename)
    is_whatsapp, channel_name = check_whatsapp_recompression(
        image_format=metadata_info["format"],
        has_exif=metadata_info["has_exif"],
        width=w,
        height=h,
        is_simulated=is_whatsapp_simulated
    )
    viewport_name, is_cropped, viewport_details = check_viewport_geometry(w, h)
    has_c2pa, c2pa_status, c2pa_details = inspect_c2pa_provenance(image_bytes)
    qr_details = inspect_qr_codes(img_bgr)

    # 4. Layer 1: Pixel & Frequency Signal Forensics
    ela_score, ela_b64, ela_blocks, ela_boxes, ela_details = run_ela_analysis(
        img_bgr, is_whatsapp=is_whatsapp, source_format=metadata_info["format"]
    )
    noise_score, noise_b64, noise_boxes, noise_details = run_wavelet_noise_analysis(
        img_bgr
    )
    clone_detected, clone_count, clone_b64, clone_boxes, clone_details = run_copy_move_analysis(
        img_bgr
    )
    ghost_details = run_jpeg_ghost_analysis(img_bgr)

    l1_boxes = ela_boxes + noise_boxes + clone_boxes
    l1_score = round(min(100.0, (ela_score * 0.40) + (noise_score * 0.35) + (70.0 if clone_detected else 0.0)), 1)

    layer1_result = Layer1SignalResult(
        ela_score=ela_score,
        ela_b64=ela_b64,
        wavelet_noise_score=noise_score,
        wavelet_noise_b64=noise_b64,
        clone_detected=clone_detected,
        clone_count=clone_count,
        clone_b64=clone_b64,
        anomalous_blocks_count=ela_blocks,
        layer_score=l1_score,
        bounding_boxes=l1_boxes,
        details={
            "ela": ela_details,
            "wavelet": noise_details,
            "copy_move": clone_details,
            "jpeg_ghosts": ghost_details
        }
    )

    # 5. Layer 2: Typographic Geometry & OCR Forensic Audit
    tokens = extract_text_tokens(img_bgr, use_neural=False)
    tokens_before_qr_exclusion = len(tokens)
    qr_regions = qr_details.get("regions", [])
    if qr_regions:
        def inside_qr(token):
            cx, cy = token.center_x, token.center_y
            return any(
                region["x"] - 4 <= cx <= region["x"] + region["width"] + 4
                and region["y"] - 4 <= cy <= region["y"] + region["height"] + 4
                for region in qr_regions
            )
        tokens = [token for token in tokens if not inside_qr(token)]
    drift_score, max_drift_px, lasers, baseline_boxes, baseline_details = run_baseline_laser_audit(
        tokens, img_width=w, img_height=h
    )
    max_delta_e, patch_anomaly, sharpness_anomaly, patch_boxes, patch_details = run_cielab_patch_and_sharpness_audit(
        img_bgr, tokens
    )

    l2_boxes = baseline_boxes + patch_boxes
    l2_score = round(min(100.0, (drift_score * 0.50) + (50.0 if patch_anomaly else 0.0) + (25.0 if sharpness_anomaly else 0.0)), 1)

    layer2_result = Layer2GeometryResult(
        baseline_drift_score=drift_score,
        max_baseline_drift_px=max_drift_px,
        max_delta_e=max_delta_e,
        cielab_patch_anomaly=patch_anomaly,
        sharpness_z_anomaly=sharpness_anomaly,
        layer_score=l2_score,
        lasers=lasers,
        bounding_boxes=l2_boxes,
        details={
            "baseline": baseline_details,
            "patch_sharpness": patch_details,
            "tokens_extracted": len(tokens),
            "tokens_in_qr_regions_excluded": tokens_before_qr_exclusion - len(tokens),
            "ocr_mode": "OFFLINE_COMPONENTS_ONLY",
            "ocr_note": "Offline mode identifies text-like image components but does not recognize their text. Pixel-based transaction text rules are unavailable in this mode.",
        }
    )

    # 6. Layer 3 Full: Temporal Paradox & UPI Rules
    clock_paradox, sb_clock, rc_time, utr_valid, utr_val, rule_boxes, rule_details = validate_temporal_and_upi_rules(
        tokens=tokens,
        img_height=h,
        img_width=w,
        png_chunks=metadata_info.get("png_chunks", [])
    )

    l3_score = 0.0
    if clock_paradox:
        l3_score += 65.0
    if utr_valid is False:
        l3_score += 35.0
    software_sig = metadata_info.get("software")
    if software_sig:
        l3_score += 45.0
    l3_score = round(min(100.0, l3_score), 1)

    layer3_result = Layer3MetadataResult(
        channel_detected=channel_name,
        is_whatsapp_laundered=is_whatsapp,
        exif_stripped=not metadata_info["has_exif"],
        software_signature=software_sig,
        c2pa_present=has_c2pa,
        c2pa_status=c2pa_status,
        viewport_aspect_ratio=viewport_name,
        is_non_native_viewport=is_cropped,
        clock_paradox_detected=clock_paradox,
        status_bar_clock=sb_clock,
        transaction_time=rc_time,
        upi_utr_valid=utr_valid,
        upi_utr_value=utr_val,
        layer_score=l3_score,
        bounding_boxes=rule_boxes,
        details={
            "metadata": metadata_info,
            "viewport": viewport_details,
            "rules": rule_details,
            "c2pa": c2pa_details,
            "qr_inspection": qr_details,
        }
    )

    # 7. Layer 4: Semantic / VLM Telemetry
    layer4_result = Layer4SemanticResult(
        vlm_used=False,
        vlm_provider=None,
        semantic_inconsistency=clock_paradox,
        layer_score=l3_score * 0.5,
        findings=[f"Detected clock: {sb_clock}", f"Detected receipt time: {rc_time}"] if sb_clock else [],
        details={"heuristic_mode": "Strict Deterministic Evaluation"}
    )

    # 8. Layer 4: Ensemble Calibration & Cross-Layer Spatial IoU Synergy
    overall_score, confidence, verdict, synergy, findings, all_boxes = calibrate_ensemble(
        layer1=layer1_result,
        layer2=layer2_result,
        layer3=layer3_result,
        layer4=layer4_result,
        is_whatsapp=is_whatsapp
    )

    # Read visible text independently of the component boxes used for geometry.
    from app.services.forensic.typography.receipt_text import inspect_receipt_text
    text_findings, text_status = inspect_receipt_text(img_bgr)
    layer3_result.details["receipt_text"] = text_status
    if text_findings:
        findings = text_findings + findings
        all_boxes.extend(f.bounding_box for f in text_findings if f.bounding_box)
        overall_score = max(overall_score, 55.0)
        if verdict == "INCONCLUSIVE":
            verdict = "REVIEW_REQUIRED"
        findings = [f for f in findings if f.id != "f-inconclusive"]
    elif text_status["status"] != "AVAILABLE" and verdict == "INCONCLUSIVE":
        # An unavailable scanner must not silently turn into a favorable result.
        from app.core.schemas import ForensicFinding
        verdict = "REVIEW_REQUIRED"
        findings = [f for f in findings if f.id != "f-inconclusive"]
        findings.append(ForensicFinding(id="f-text-coverage", layer=3, severity="LOW",
            title="Receipt text could not be assessed",
            description="No reliable text assessment is available. The warning reflects incomplete coverage, not detected forgery.",
            metric_name="Text assessment", metric_value=text_status["status"]))

    # 9. Send lossless WebP viewer assets to reduce the report payload. The
    # original uploaded bytes above remain the source for all forensic checks.
    _, orig_webp = cv2.imencode('.webp', img_bgr, [cv2.IMWRITE_WEBP_QUALITY, 101])
    orig_b64 = f"data:image/webp;base64,{base64.b64encode(orig_webp.tobytes()).decode('utf-8')}"

    return ForensicAnalysisReport(
        file_sha256=sha256_hash,
        filename=filename,
        timestamp=timestamp_iso,
        image_width=w,
        image_height=h,
        overall_tamper_score=overall_score,
        confidence_score=confidence,
        verdict=verdict,
        channel_detected=channel_name,
        layer1=layer1_result,
        layer2=layer2_result,
        layer3=layer3_result,
        layer4=layer4_result,
        synergy=synergy,
        findings=findings,
        all_bounding_boxes=all_boxes,
        original_image_b64=orig_b64
    )
