"""
VeriSight Canonical Forensic Feature Schema (v1.0.0).
Defines standard feature definitions, units, expected ranges,
missing value handling, and runtime validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np


FEATURE_SCHEMA_VERSION = "1.0.0"

CANONICAL_FEATURE_NAMES: list[str] = [
    "ela_score",
    "ela_z_macroblocks",
    "wavelet_void_score",
    "wavelet_min_variance",
    "copy_move_vectors",
    "baseline_drift_px",
    "cielab_patch_delta_e",
    "cross_layer_iou",
    "temporal_clock_paradox",
    "upi_utr_invalid",
    "whatsapp_transcoded",
]


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    index: int
    units: str
    expected_min: float
    expected_max: float
    default_missing: float
    description: str


FEATURE_DEFINITIONS: dict[str, FeatureDefinition] = {
    "ela_score": FeatureDefinition(
        name="ela_score",
        index=0,
        units="normalized_loss (0-100)",
        expected_min=0.0,
        expected_max=100.0,
        default_missing=0.0,
        description="Global Error Level Analysis resave residual score under JPEG Q=90 (or Q=75 if WhatsApp)."
    ),
    "ela_z_macroblocks": FeatureDefinition(
        name="ela_z_macroblocks",
        index=1,
        units="macroblock_count",
        expected_min=0.0,
        expected_max=500.0,
        default_missing=0.0,
        description="Count of contiguous 16x16 macroblocks with ELA difference z-score > 2.6."
    ),
    "wavelet_void_score": FeatureDefinition(
        name="wavelet_void_score",
        index=2,
        units="normalized_anomaly (0-100)",
        expected_min=0.0,
        expected_max=100.0,
        default_missing=0.0,
        description="Daubechies-4 2D DWT diagonal high-frequency detail residual anomaly score."
    ),
    "wavelet_min_variance": FeatureDefinition(
        name="wavelet_min_variance",
        index=3,
        units="variance_units",
        expected_min=0.0,
        expected_max=50.0,
        default_missing=0.5,
        description="Minimum local-window wavelet noise variance (low values indicate unnatural smoothing/voids)."
    ),
    "copy_move_vectors": FeatureDefinition(
        name="copy_move_vectors",
        index=4,
        units="vector_count",
        expected_min=0.0,
        expected_max=500.0,
        default_missing=0.0,
        description="Clustered parallel translation vectors from ORB keypoint matching."
    ),
    "baseline_drift_px": FeatureDefinition(
        name="baseline_drift_px",
        index=5,
        units="pixels",
        expected_min=0.0,
        expected_max=50.0,
        default_missing=0.0,
        description="Maximum sub-pixel OLS baseline linear regression residual offset across text rows."
    ),
    "cielab_patch_delta_e": FeatureDefinition(
        name="cielab_patch_delta_e",
        index=6,
        units="delta_e_ab",
        expected_min=0.0,
        expected_max=50.0,
        default_missing=0.0,
        description="Maximum perceptual CIELAB Delta-E color difference between local background margin around tokens and reference card background."
    ),
    "cross_layer_iou": FeatureDefinition(
        name="cross_layer_iou",
        index=7,
        units="iou_ratio (0.0-1.0)",
        expected_min=0.0,
        expected_max=1.0,
        default_missing=0.0,
        description="Maximum geometric Intersection-over-Union between Layer 1 physical signal boxes and Layer 2 typographic boxes."
    ),
    "temporal_clock_paradox": FeatureDefinition(
        name="temporal_clock_paradox",
        index=8,
        units="binary_flag (0.0 or 1.0)",
        expected_min=0.0,
        expected_max=1.0,
        default_missing=0.0,
        description="Binary indicator: 1.0 if OS status bar clock is earlier than transaction receipt timestamp."
    ),
    "upi_utr_invalid": FeatureDefinition(
        name="upi_utr_invalid",
        index=9,
        units="binary_flag (0.0 or 1.0)",
        expected_min=0.0,
        expected_max=1.0,
        default_missing=0.0,
        description="Binary indicator: 1.0 if NPCI UPI 12-digit reference syntax/checksum is violated."
    ),
    "whatsapp_transcoded": FeatureDefinition(
        name="whatsapp_transcoded",
        index=10,
        units="binary_flag (0.0 or 1.0)",
        expected_min=0.0,
        expected_max=1.0,
        default_missing=0.0,
        description="Binary indicator: 1.0 if lossy social media messaging container fingerprint is detected."
    ),
}


def validate_and_format_feature_vector(
    features: dict[str, float] | list[float] | np.ndarray
) -> np.ndarray:
    """
    Validates and formats an input vector against CanonicalFeatureSchema v1.0.0.
    Ensures correct dimension, order, NaN/Inf imputation, and range sanity.
    """
    vec = np.zeros(len(CANONICAL_FEATURE_NAMES), dtype=np.float32)

    if isinstance(features, dict):
        for idx, name in enumerate(CANONICAL_FEATURE_NAMES):
            defn = FEATURE_DEFINITIONS[name]
            raw_val = features.get(name, defn.default_missing)
            if raw_val is None or np.isnan(raw_val) or np.isinf(raw_val):
                val = defn.default_missing
            else:
                val = float(raw_val)
            # Bound clamp
            val = max(defn.expected_min, min(defn.expected_max, val))
            vec[idx] = val
    elif isinstance(features, (list, np.ndarray)):
        arr = np.asarray(features, dtype=np.float32).flatten()
        if len(arr) != len(CANONICAL_FEATURE_NAMES):
            raise ValueError(
                f"Feature vector dimension mismatch: expected {len(CANONICAL_FEATURE_NAMES)} features, "
                f"got {len(arr)}. Canonical schema: {CANONICAL_FEATURE_NAMES}"
            )
        for idx, name in enumerate(CANONICAL_FEATURE_NAMES):
            defn = FEATURE_DEFINITIONS[name]
            raw_val = arr[idx]
            if raw_val is None or np.isnan(raw_val) or np.isinf(raw_val):
                val = defn.default_missing
            else:
                val = float(raw_val)
            val = max(defn.expected_min, min(defn.expected_max, val))
            vec[idx] = val
    else:
        raise TypeError(f"Unsupported features type: {type(features)}")

    return vec
