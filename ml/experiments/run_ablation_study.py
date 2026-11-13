"""
VeriSight Synthetic Benchmark Ablation & Shortcut Analysis (Phase 9).
Tests sensitivity of the GBDT and heuristic pipeline to generator artifacts:
- Watermark masking / banner removal
- JPEG / WebP transcoding variations (Q=95, Q=80, Q=60)
- Aspect ratio and resolution scaling (0.8x, 1.2x)
- Background luminance perturbation
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.services.forensic.pipeline import analyze_screenshot

BENCHMARK_IMAGES = BASE_DIR / "datasets" / "images"


def run_ablation_study() -> dict:
    auth_path = BENCHMARK_IMAGES / "auth_01.png"
    splice_path = BENCHMARK_IMAGES / "manip_splice_01.png"

    if not auth_path.exists():
        raise FileNotFoundError(f"Fixture {auth_path} not found")

    auth_bytes = auth_path.read_bytes()
    splice_bytes = splice_path.read_bytes()
    auth_img = cv2.imdecode(np.frombuffer(auth_bytes, np.uint8), cv2.IMREAD_COLOR)
    splice_img = cv2.imdecode(np.frombuffer(splice_bytes, np.uint8), cv2.IMREAD_COLOR)

    results = {}

    # 1. Baseline Full Image
    rep_auth_base = analyze_screenshot(auth_bytes, "auth_01.png")
    rep_splice_base = analyze_screenshot(splice_bytes, "manip_splice_01.png")
    results["baseline"] = {
        "auth_overall_score": rep_auth_base.overall_tamper_score,
        "auth_calibrated_prob": rep_auth_base.model_metadata.calibrated_probability,
        "splice_overall_score": rep_splice_base.overall_tamper_score,
        "splice_calibrated_prob": rep_splice_base.model_metadata.calibrated_probability,
    }

    # 2. Ablation: Watermark / Header Banner Masking
    # Mask top 12% and bottom 10% with mean card background
    h, w = auth_img.shape[:2]
    auth_masked = auth_img.copy()
    bg_color = auth_img[h // 2, w // 2].tolist()
    auth_masked[: int(h * 0.12), :] = bg_color
    auth_masked[int(h * 0.90) :, :] = bg_color
    _, enc = cv2.imencode(".png", auth_masked)
    rep_auth_masked = analyze_screenshot(enc.tobytes(), "auth_masked.png")
    results["watermark_header_masked"] = {
        "auth_calibrated_prob": rep_auth_masked.model_metadata.calibrated_probability,
        "delta_from_baseline": round(
            float(rep_auth_masked.model_metadata.calibrated_probability - rep_auth_base.model_metadata.calibrated_probability), 4
        ),
    }

    # 3. Ablation: Compression Quality Perturbation (JPEG Q=95, Q=80, Q=60)
    for q in [95, 80, 60]:
        _, enc_jpg = cv2.imencode(".jpg", auth_img, [cv2.IMWRITE_JPEG_QUALITY, q])
        rep_jpg = analyze_screenshot(enc_jpg.tobytes(), f"auth_q{q}.jpg")
        results[f"jpeg_q{q}"] = {
            "auth_calibrated_prob": rep_jpg.model_metadata.calibrated_probability,
            "overall_tamper_score": rep_jpg.overall_tamper_score,
            "ela_score": rep_jpg.layer1.ela_score,
        }

    # 4. Ablation: Resolution Scaling (0.8x, 1.25x)
    for scale in [0.8, 1.25]:
        new_w, new_h = int(w * scale), int(h * scale)
        scaled_img = cv2.resize(auth_img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        _, enc_scaled = cv2.imencode(".png", scaled_img)
        rep_scaled = analyze_screenshot(enc_scaled.tobytes(), f"auth_s{scale}.png")
        results[f"scale_{scale}x"] = {
            "auth_calibrated_prob": rep_scaled.model_metadata.calibrated_probability,
            "overall_tamper_score": rep_scaled.overall_tamper_score,
            "ela_score": rep_scaled.layer1.ela_score,
        }

    # 5. Ablation: Background Luminance Perturbation (+15, -15 intensity shift)
    for shift in [15, -15]:
        shifted = np.clip(auth_img.astype(np.int16) + shift, 0, 255).astype(np.uint8)
        _, enc_shift = cv2.imencode(".png", shifted)
        rep_shift = analyze_screenshot(enc_shift.tobytes(), f"auth_lum_{shift}.png")
        results[f"lum_shift_{shift}"] = {
            "auth_calibrated_prob": rep_shift.model_metadata.calibrated_probability,
            "max_delta_e": rep_shift.layer2.max_delta_e,
        }

    ablation_out_path = BASE_DIR / "evaluation" / "ablation_study_results.json"
    with open(ablation_out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Ablation Study Completed Successfully:")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    run_ablation_study()
