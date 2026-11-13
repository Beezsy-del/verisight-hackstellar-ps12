"""
VeriSight Learned Feature Fusion Architecture.
Trains and evaluates regularized logistic regression and gradient-boosted trees
with out-of-fold cross-validation and probability calibration.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

from src.feature_extraction.schema import (
    CANONICAL_FEATURE_NAMES,
    FEATURE_SCHEMA_VERSION,
    validate_and_format_feature_vector,
)


class LearnedFusionModel:
    def __init__(self, model_type: str = "gradient_boosting", model_version: str = "1.2.1"):
        self.model_type = model_type
        self.model_version = model_version
        self.feature_schema_version = FEATURE_SCHEMA_VERSION
        self.feature_names = list(CANONICAL_FEATURE_NAMES)
        self.scaler = StandardScaler()

        if model_type == "logistic":
            self.base_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
        elif model_type == "gradient_boosting":
            self.base_model = HistGradientBoostingClassifier(
                max_iter=100, min_samples_leaf=2, l2_regularization=1.0, random_state=42
            )
        elif model_type == "random_forest":
            self.base_model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        self.calibrated_model: CalibratedClassifierCV | None = None
        self.is_fitted = False

    def fit_and_evaluate(
        self,
        X_dev: np.ndarray,
        y_dev: np.ndarray,
        X_test: np.ndarray | None = None,
        y_test: np.ndarray | None = None,
        n_splits: int = 4
    ) -> dict[str, Any]:
        """
        Executes Stratified K-Fold cross-validation on the development set (X_dev, y_dev)
        to measure out-of-fold metrics, fits CalibratedClassifierCV on X_dev,
        and optionally evaluates on the held-out test set (X_test, y_test).
        Zero data leakage: X_test is strictly held out.
        """
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        oof_preds = np.zeros(len(y_dev), dtype=np.float32)
        oof_probs = np.zeros(len(y_dev), dtype=np.float32)

        for train_idx, val_idx in skf.split(X_dev, y_dev):
            X_tr, y_tr = X_dev[train_idx], y_dev[train_idx]
            X_va, y_va = X_dev[val_idx], y_dev[val_idx]

            fold_scaler = StandardScaler()
            X_tr_sc = fold_scaler.fit_transform(X_tr)
            X_va_sc = fold_scaler.transform(X_va)

            if self.model_type == "logistic":
                fold_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
            elif self.model_type == "gradient_boosting":
                fold_model = HistGradientBoostingClassifier(
                    max_iter=100, min_samples_leaf=2, l2_regularization=1.0, random_state=42
                )
            else:
                fold_model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42)

            fold_model.fit(X_tr_sc, y_tr)
            probs = fold_model.predict_proba(X_va_sc)[:, 1]
            oof_probs[val_idx] = probs
            oof_preds[val_idx] = (probs >= 0.5).astype(np.float32)

        # Compute Out-of-Fold Evaluation Metrics on Dev Set
        oof_auc = float(roc_auc_score(y_dev, oof_probs))
        oof_brier = float(brier_score_loss(y_dev, oof_probs))
        oof_prec = float(precision_score(y_dev, oof_preds, zero_division=0))
        oof_rec = float(recall_score(y_dev, oof_preds, zero_division=0))
        oof_f1 = float(f1_score(y_dev, oof_preds, zero_division=0))
        oof_acc = float(accuracy_score(y_dev, oof_preds))
        oof_cm = confusion_matrix(y_dev, oof_preds.astype(int)).tolist()

        # False-Positive Rate at 95% Recall (on dev set OOF)
        p_curve, r_curve, thres = precision_recall_curve(y_dev, oof_probs)
        idx_95 = np.where(r_curve >= 0.95)[0]
        th_95 = float(thres[idx_95[-1]]) if len(idx_95) > 0 and idx_95[-1] < len(thres) else 0.5
        preds_at_95 = (oof_probs >= th_95).astype(int)
        neg_mask = (y_dev == 0)
        fpr_at_95 = float(np.sum(preds_at_95[neg_mask]) / np.sum(neg_mask)) if np.sum(neg_mask) > 0 else 0.0

        # Now fit calibrated model strictly on Development Set (X_dev, y_dev)
        X_dev_scaled = self.scaler.fit_transform(X_dev)
        # Use cv=3 calibration on dev set
        self.calibrated_model = CalibratedClassifierCV(estimator=self.base_model, cv=3, method="sigmoid")
        self.calibrated_model.fit(X_dev_scaled, y_dev)
        self.is_fitted = True

        results = {
            "model_type": self.model_type,
            "model_version": self.model_version,
            "feature_schema_version": self.feature_schema_version,
            "dev_set_size": len(y_dev),
            "dev_positive": int(np.sum(y_dev)),
            "dev_negative": int(len(y_dev) - np.sum(y_dev)),
            "oof_cv_metrics": {
                "roc_auc": round(oof_auc, 4),
                "brier_score": round(oof_brier, 4),
                "accuracy": round(oof_acc, 4),
                "precision": round(oof_prec, 4),
                "recall": round(oof_rec, 4),
                "f1_score": round(oof_f1, 4),
                "fpr_at_95_recall": round(fpr_at_95, 4),
                "operating_threshold_at_95_recall": round(th_95, 4),
                "confusion_matrix": oof_cm,
            },
            "is_calibrated": True,
            "calibration_method": "Platt Sigmoid (cv=3)",
        }

        # Evaluate on Held-Out Test Set if provided
        if X_test is not None and y_test is not None and len(y_test) > 0:
            X_test_scaled = self.scaler.transform(X_test)
            test_probs = self.calibrated_model.predict_proba(X_test_scaled)[:, 1]
            test_preds = (test_probs >= 0.5).astype(int)

            test_auc = float(roc_auc_score(y_test, test_probs)) if len(np.unique(y_test)) > 1 else 0.0
            test_brier = float(brier_score_loss(y_test, test_probs))
            test_prec = float(precision_score(y_test, test_preds, zero_division=0))
            test_rec = float(recall_score(y_test, test_preds, zero_division=0))
            test_f1 = float(f1_score(y_test, test_preds, zero_division=0))
            test_acc = float(accuracy_score(y_test, test_preds))
            test_cm = confusion_matrix(y_test, test_preds).tolist()

            results["held_out_test_metrics"] = {
                "test_set_size": len(y_test),
                "test_positive": int(np.sum(y_test)),
                "test_negative": int(len(y_test) - np.sum(y_test)),
                "roc_auc": round(test_auc, 4),
                "brier_score": round(test_brier, 4),
                "accuracy": round(test_acc, 4),
                "precision": round(test_prec, 4),
                "recall": round(test_rec, 4),
                "f1_score": round(test_f1, 4),
                "confusion_matrix": test_cm,
                "test_probabilities": [round(float(p), 4) for p in test_probs],
                "ground_truth": [int(g) for g in y_test],
            }

        return results

    def predict_proba(self, feature_vector: np.ndarray | list[float]) -> float:
        """
        Returns calibrated posterior probability P(Tampered | x).
        Validates against CanonicalFeatureSchema v1.0.0.
        """
        if not self.is_fitted or self.calibrated_model is None:
            raise RuntimeError("Model is not fitted. Cannot predict.")

        validated_vec = validate_and_format_feature_vector(feature_vector)
        vec_scaled = self.scaler.transform(validated_vec.reshape(1, -1))
        prob = self.calibrated_model.predict_proba(vec_scaled)[0, 1]
        return float(prob)

    def save(self, filepath: str | Path):
        joblib.dump({
            "model_id": f"verisight-fusion-{self.model_type}-v1",
            "model_type": self.model_type,
            "model_version": self.model_version,
            "feature_schema_version": self.feature_schema_version,
            "feature_names": self.feature_names,
            "scaler": self.scaler,
            "calibrated_model": self.calibrated_model,
            "is_fitted": self.is_fitted
        }, filepath)

    @classmethod
    def load(cls, filepath: str | Path) -> LearnedFusionModel:
        data = joblib.load(filepath)
        inst = cls(model_type=data["model_type"], model_version=data.get("model_version", "1.2.1"))
        inst.feature_schema_version = data.get("feature_schema_version", FEATURE_SCHEMA_VERSION)
        inst.feature_names = data.get("feature_names", list(CANONICAL_FEATURE_NAMES))
        inst.scaler = data["scaler"]
        inst.calibrated_model = data["calibrated_model"]
        inst.is_fitted = data["is_fitted"]
        return inst
