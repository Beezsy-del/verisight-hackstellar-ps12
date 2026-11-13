"""
VeriSight Forensic Baselines:
1. Deterministic Multi-Layer Heuristic Baseline.
2. Learned Feature Fusion Classifier (L2 Logistic Regression / Gradient Boosting).
3. Calibrated Probabilistic Predictor.
"""
from __future__ import annotations

from typing import Any

import numpy as np


class DeterministicHeuristicBaseline:
    """
    Standard Production 4-Layer Deterministic Baseline.
    Applies domain weights and cross-layer spatial IoU synergy multiplier.
    """
    def __init__(self, synergy_multiplier: float = 1.35, critical_threshold: float = 87.0):
        self.synergy_multiplier = synergy_multiplier
        self.critical_threshold = critical_threshold

    def predict(self, feature_vector: np.ndarray) -> dict[str, Any]:
        """
        Ingests feature vector:
        [0] ela_score (0-100)
        [1] ela_z_macroblocks
        [2] wavelet_void_score (0-100)
        [3] wavelet_min_var
        [4] copy_move_vectors
        [5] baseline_drift_px
        [6] cielab_delta_e
        [7] cross_layer_iou
        [8] temporal_clock_paradox (0/1)
        [9] upi_utr_invalid (0/1)
        [10] whatsapp_transcoded (0/1)
        """
        ela_s = feature_vector[0]
        wav_s = feature_vector[2]
        clone_cnt = feature_vector[4]
        drift_px = feature_vector[5]
        delta_e = feature_vector[6]
        iou = feature_vector[7]
        temporal = feature_vector[8]
        upi_inv = feature_vector[9]
        is_wa = bool(feature_vector[10])

        # Layer 1 Signal Score
        l1_score = min(100.0, (ela_s * 0.40) + (wav_s * 0.35) + (70.0 if clone_cnt >= 4 else 0.0))

        # Layer 2 Typography Score
        drift_s = min(100.0, drift_px * 25.0) if drift_px >= 2.5 else min(20.0, drift_px * 5.0)
        patch_s = 50.0 if delta_e > 4.5 else 0.0
        l2_score = min(100.0, (drift_s * 0.50) + patch_s)

        # Layer 3 Protocol Score
        l3_score = 0.0
        if temporal > 0.5:
            l3_score += 65.0
        if upi_inv > 0.5:
            l3_score += 35.0
        l3_score = min(100.0, l3_score)

        # Weight assignment
        if is_wa:
            w1, w2, w3 = 0.35, 0.45, 0.20
        else:
            w1, w2, w3 = 0.40, 0.35, 0.25

        raw_composite = (w1 * l1_score) + (w2 * l2_score) + (w3 * l3_score)

        # Synergy multiplier
        synergy_applied = (iou > 0.15) or (clone_cnt >= 4 and drift_px >= 2.5)
        if synergy_applied:
            composite_score = min(99.0, max(88.0, raw_composite * self.synergy_multiplier))
        else:
            composite_score = min(100.0, raw_composite)

        # Low genuine score calibration
        if raw_composite < 12.0 and not synergy_applied and temporal < 0.5 and clone_cnt < 4:
            composite_score = round(min(8.5, raw_composite * 0.7), 1)
        else:
            composite_score = round(composite_score, 1)

        # Operational Triage Status (87 threshold)
        is_triage_alert = composite_score >= self.critical_threshold

        # Categorical Verdict
        if composite_score < 25.0:
            verdict = "AUTHENTIC_VERIFIED"
        elif composite_score < 70.0:
            verdict = "SUSPICIOUS_ANOMALIES"
        else:
            verdict = "MANIPULATED_FORGERY"

        return {
            "overall_tamper_score": composite_score,
            "verdict": verdict,
            "is_triage_alert": is_triage_alert,
            "synergy_applied": synergy_applied,
            "layer_scores": {
                "layer1_signal": round(float(l1_score), 1),
                "layer2_typography": round(float(l2_score), 1),
                "layer3_protocol": round(float(l3_score), 1),
            }
        }
