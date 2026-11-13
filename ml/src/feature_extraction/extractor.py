"""
VeriSight Canonical Forensic Feature Extraction Pipeline.
Extracts the 11 canonical forensic features by directly invoking the production
forensic analysis engines, guaranteeing 100% mathematical parity (Delta = 0.0000)
between training evaluation and live production inference.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# Ensure project root and backend are in sys.path
BASE_DIR = Path(__file__).resolve().parents[3]  # C:\Users\HP\verisight-new
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "ml") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "ml"))

try:
    from ml.src.feature_extraction.schema import (
        CANONICAL_FEATURE_NAMES,
        FEATURE_DEFINITIONS,
        FEATURE_SCHEMA_VERSION,
        validate_and_format_feature_vector,
    )
except ImportError:
    from src.feature_extraction.schema import (
        CANONICAL_FEATURE_NAMES,
        FEATURE_DEFINITIONS,
        FEATURE_SCHEMA_VERSION,
        validate_and_format_feature_vector,
    )

from app.services.forensic.pixel_analysis.ela import run_ela_analysis
from app.services.forensic.pixel_analysis.wavelet_noise import run_wavelet_noise_analysis
from app.services.forensic.pixel_analysis.copy_move import run_copy_move_analysis
from app.services.forensic.typography.ocr_engine import extract_text_tokens
from app.services.forensic.typography.baseline_laser import run_baseline_laser_audit
from app.services.forensic.typography.cielab_patch import run_cielab_patch_and_sharpness_audit
from app.services.forensic.ensemble.calibrator import compute_box_iou
from app.services.forensic.qr_inspector import inspect_qr_codes

logger = logging.getLogger("verisight.extractor")


class ForensicFeatureRecord:
    def __init__(
        self,
        name: str,
        value: float,
        source_method: str,
        region: list[int] | None = None,
        reliability: float = 1.0,
        availability: bool = True,
        error: str | None = None,
        evidence_reference: str = "",
    ):
        self.name = name
        self.value = value
        self.source_method = source_method
        self.region = region or [0, 0, 0, 0]  # [x, y, w, h]
        self.reliability = reliability
        self.availability = availability
        self.error = error
        self.evidence_reference = evidence_reference

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": round(float(self.value), 4),
            "source_method": self.source_method,
            "region": self.region,
            "reliability": round(float(self.reliability), 3),
            "availability": self.availability,
            "error": self.error,
            "evidence_reference": self.evidence_reference,
        }


def extract_all_forensic_features(
    img_bgr: np.ndarray,
    metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Extracts the 11 canonical forensic features using production forensic engines.
    Guarantees exact parity between offline training and live serving.
    """
    metadata = metadata or {}
    h, w = img_bgr.shape[:2]
    is_whatsapp = bool(metadata.get("is_whatsapp", False))

    # 1. Layer 1: Pixel & Frequency Forensics
    ela_score, _, ela_blocks, ela_boxes, _ = run_ela_analysis(img_bgr, is_whatsapp=is_whatsapp)
    noise_score, _, noise_boxes, noise_details = run_wavelet_noise_analysis(img_bgr)
    min_variance = float(noise_details.get("min_variance", 0.5)) if isinstance(noise_details, dict) else 0.5
    _, clone_count, _, clone_boxes, _ = run_copy_move_analysis(img_bgr)

    # 2. Layer 2: Typographic & Baseline Geometric Audit
    tokens = extract_text_tokens(img_bgr)
    qr_details = inspect_qr_codes(img_bgr)
    if qr_details.get("qr_detected") and qr_details.get("bounding_boxes"):
        qr_boxes = qr_details["bounding_boxes"]
        def _in_any_qr(token) -> bool:
            box = token.box
            tx, ty, tw, th = box[0], box[1], box[2], box[3]
            for qb in qr_boxes:
                if not (tx + tw < qb["x"] or tx > qb["x"] + qb["width"] or ty + th < qb["y"] or ty > qb["y"] + qb["height"]):
                    return True
            return False
        tokens = [t for t in tokens if not _in_any_qr(t)]

    _, max_drift_px, _, laser_boxes, _ = run_baseline_laser_audit(tokens, img_width=w, img_height=h)
    max_delta_e, patch_anomaly, sharpness_anomaly, patch_boxes, patch_details = run_cielab_patch_and_sharpness_audit(img_bgr, tokens)
    delta_e_val = float(max_delta_e) if max_delta_e is not None else 0.0

    # 3. Layer 4 / Synergy: Cross-Layer Spatial IoU
    l1_boxes = ela_boxes + noise_boxes + clone_boxes
    l2_boxes = laser_boxes + patch_boxes

    max_iou = 0.0
    for b1 in l1_boxes:
        for b2 in l2_boxes:
            iou = compute_box_iou(b1, b2)
            if iou > max_iou:
                max_iou = iou

    # 4. Layer 3: Protocol & Temporal Metadata
    temporal_paradox = 1.0 if metadata.get("clock_paradox", False) else 0.0
    upi_invalid = 1.0 if metadata.get("upi_invalid", False) else 0.0
    whatsapp_transcoded = 1.0 if is_whatsapp else 0.0

    raw_dict = {
        "ela_score": float(ela_score),
        "ela_z_macroblocks": float(ela_blocks),
        "wavelet_void_score": float(noise_score),
        "wavelet_min_variance": float(min_variance),
        "copy_move_vectors": float(clone_count),
        "baseline_drift_px": float(max_drift_px),
        "cielab_patch_delta_e": float(delta_e_val),
        "cross_layer_iou": float(max_iou),
        "temporal_clock_paradox": float(temporal_paradox),
        "upi_utr_invalid": float(upi_invalid),
        "whatsapp_transcoded": float(whatsapp_transcoded),
    }

    feature_vector = validate_and_format_feature_vector(raw_dict)

    def _box_to_list(b):
        return [b.x, b.y, b.width, b.height] if b is not None else [0, 0, 0, 0]

    feature_records = [
        ForensicFeatureRecord("ela_score", ela_score, "Error Level Analysis Q=90", _box_to_list(ela_boxes[0]) if ela_boxes else None, 0.85, True, None, "L1_ELA"),
        ForensicFeatureRecord("ela_z_macroblocks", float(ela_blocks), "16x16 ELA Z-Score Outliers", None, 0.88, True, None, "L1_ELA_Z"),
        ForensicFeatureRecord("wavelet_void_score", noise_score, "Daubechies-4 DWT HH Residual", _box_to_list(noise_boxes[0]) if noise_boxes else None, 0.90, True, None, "L1_DWT"),
        ForensicFeatureRecord("wavelet_min_variance", min_variance, "Minimum Local Wavelet Variance", None, 0.82, True, None, "L1_DWT_VAR"),
        ForensicFeatureRecord("copy_move_vectors", float(clone_count), "ORB Vector Clustering", _box_to_list(clone_boxes[0]) if clone_boxes else None, 0.94, True, None, "L1_ORB"),
        ForensicFeatureRecord("baseline_drift_px", max_drift_px, "Sub-Pixel OLS Baseline Drift", _box_to_list(laser_boxes[0]) if laser_boxes else None, 0.96, True, None, "L2_LASER"),
        ForensicFeatureRecord("cielab_patch_delta_e", delta_e_val, "CIELAB Background Margin Delta-E", _box_to_list(patch_boxes[0]) if patch_boxes else None, 0.92, True, None, "L2_CIELAB"),
        ForensicFeatureRecord("cross_layer_iou", max_iou, "Spatial L1/L2 IoU Intersection", None, 0.98, True, None, "L4_SYNERGY"),
        ForensicFeatureRecord("temporal_clock_paradox", temporal_paradox, "Status Bar Clock vs Timestamp", None, 0.99, True, None, "L3_TEMPORAL"),
        ForensicFeatureRecord("upi_utr_invalid", upi_invalid, "NPCI 12-Digit Reference Syntax", None, 0.99, True, None, "L3_UPI"),
        ForensicFeatureRecord("whatsapp_transcoded", whatsapp_transcoded, "Channel Compression Fingerprint", None, 0.90, True, None, "L3_CONTAINER"),
    ]

    return {
        "feature_vector": feature_vector,
        "feature_names": CANONICAL_FEATURE_NAMES,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "records": [r.to_dict() for r in feature_records],
        "token_count": len(tokens),
    }
