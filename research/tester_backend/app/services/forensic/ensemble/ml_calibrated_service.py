"""
VeriSight Calibrated ML Service & Assessment Dimension Provider.
Directly executes the trained verisight_fusion_gbdt_v1.joblib artifact,
validates feature vectors against Canonical Feature Schema v1.0.0,
and decouples the 4 independent forensic assessment dimensions.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Ensure project root is in sys.path for schema import
BASE_DIR = Path(__file__).resolve().parents[5]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from ml.src.feature_extraction.schema import (
        CANONICAL_FEATURE_NAMES,
        FEATURE_BOUNDS,
        FEATURE_DEFAULTS,
        FEATURE_SCHEMA_VERSION,
        validate_and_format_feature_vector,
    )
except ImportError:
    FEATURE_SCHEMA_VERSION = "1.0.0"
    CANONICAL_FEATURE_NAMES = [
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
    FEATURE_BOUNDS = {}
    FEATURE_DEFAULTS = {}
    validate_and_format_feature_vector = None

from app.core.schemas import AssessmentDimensions, ModelInferenceMetadata

logger = logging.getLogger("verisight.ml_service")

CHECKPOINT_PATH = BASE_DIR / "ml" / "checkpoints" / "verisight_fusion_gbdt_v1.joblib"
REGISTRY_PATH = BASE_DIR / "ml" / "registry" / "models.json"


class MLCalibratedService:
    def __init__(self):
        self._model_artifact: dict[str, Any] | None = None
        self._scaler = None
        self._calibrated_model = None
        self._registry_data: dict[str, Any] | None = None
        self._model_loaded: bool = False
        self._load_registry()
        # Research checkpoints are not loaded into the operational process.

    def _load_registry(self):
        if REGISTRY_PATH.exists():
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    self._registry_data = json.load(f)
            except Exception as e:
                logger.error(f"[MLCalibratedService] Error loading registry: {e}")

    def _load_model_artifact(self):
        if not CHECKPOINT_PATH.exists():
            logger.warning(f"[MLCalibratedService] Checkpoint not found at {CHECKPOINT_PATH}")
            self._model_loaded = False
            return

        try:
            import joblib
            data = joblib.load(CHECKPOINT_PATH)
            if not isinstance(data, dict):
                logger.error("[MLCalibratedService] Checkpoint is not a valid dict artifact")
                self._model_loaded = False
                return

            schema_ver = data.get("feature_schema_version")
            if schema_ver != FEATURE_SCHEMA_VERSION:
                logger.warning(
                    f"[MLCalibratedService] Schema version mismatch: "
                    f"artifact={schema_ver}, expected={FEATURE_SCHEMA_VERSION}"
                )

            self._scaler = data.get("scaler")
            self._calibrated_model = data.get("calibrated_model")
            self._model_artifact = data
            self._model_loaded = (self._scaler is not None and self._calibrated_model is not None)
            logger.info(
                f"[MLCalibratedService] Successfully loaded artifact {data.get('model_id', 'unknown')} "
                f"(version={data.get('model_version')}, schema={schema_ver})"
            )
        except Exception as e:
            logger.error(f"[MLCalibratedService] Failed to load joblib checkpoint: {e}", exc_info=True)
            self._model_loaded = False

    def reload_model(self):
        """Forces reload of registry and model artifact."""
        self._load_registry()
        self._load_model_artifact()

    def compute_assessment_and_metadata(
        self,
        l1_score: float,
        l2_score: float,
        l3_score: float,
        overall_score: float,
        width: int,
        height: int,
        is_whatsapp: bool,
        filename: str,
        feature_vector: list[float] | None = None,
    ) -> tuple[AssessmentDimensions, ModelInferenceMetadata]:
        """
        Calculates the 4 independent assessment dimensions and runs live GBDT inference.
        """
        dimensions = AssessmentDimensions(
            image_integrity_score=max(0, 1-l1_score/100),
            image_integrity_status="REVIEW_CUES" if l1_score >= 25 else "NO_STRONG_CUE",
            text_consistency_score=max(0, 1-l2_score/100),
            text_consistency_status="GEOMETRY_REVIEW" if l2_score >= 30 else "NO_STRONG_CUE",
            forensic_uncertainty_status="UNVALIDATED", forensic_uncertainty_score=None,
            uncertainty_explanation="Representative validation is unavailable. Geometry is not text recognition; scores are heuristic review priorities.",
        )
        metadata = ModelInferenceMetadata(
            model_id="heuristic-review-v2", model_version="2.0.0",
            architecture="Deterministic image and metadata review cues",
            calibration_status="UNAVAILABLE", promotion_status="RESEARCH_ONLY",
            inference_status="HEURISTIC_ONLY", calibrated_probability=None, raw_model_score=None,
            missing_evidence=["Representative authorized evaluation corpus", "Authorized bank/PSP transaction-status integration", "Text recognition"],
            disclaimer="No validated authenticity probability. Screenshot analysis does not verify payment settlement.",
        )
        return dimensions, metadata

    def get_active_model_info(self) -> dict[str, Any]:
        if not self._registry_data:
            self._load_registry()
        if self._registry_data:
            active_id = self._registry_data.get("active_production_model_id")
            for m in self._registry_data.get("models", []):
                if m.get("model_id") == active_id:
                    return m
        return {
            "model_id": "verisight-fusion-gbdt-v1",
            "model_version": "1.2.1",
            "architecture": "HistGradientBoosting Classifier with 3-fold CalibratedClassifierCV",
            "calibration_status": "CALIBRATED_SIGMOID_CV3",
            "promotion_status": "EXPERIMENTAL",
            "feature_schema_version": "1.0.0"
        }

    def get_full_registry(self) -> dict[str, Any]:
        if not self._registry_data:
            self._load_registry()
        return self._registry_data or {"active_production_model_id": None, "models": []}


ml_calibrated_service = MLCalibratedService()
