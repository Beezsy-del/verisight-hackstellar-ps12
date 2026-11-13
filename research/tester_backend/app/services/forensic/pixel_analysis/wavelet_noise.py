import base64
from typing import Any

import cv2
import numpy as np

from app.core.schemas import BoundingBox


def run_wavelet_noise_analysis(
    img_bgr: np.ndarray
) -> tuple[float, str, list[BoundingBox], dict[str, Any]]:
    """
    2D Daubechies Wavelet (db4) High-Pass Noise Residual & Local Variance Mapping.
    Decomposes luminance Y into sub-bands, extracts diagonal high-pass details (cD / HH),
    computes local 9x9 sliding variance, identifies Zero-Noise Voids and High-Variance Halos,
    and outputs a high-contrast Cyan/Magenta forensic map.
    """
    h_orig, w_orig = img_bgr.shape[:2]

    # 1. Convert to YCbCr Luminance Y
    ycbcr = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    Y = ycbcr[:, :, 0].astype(np.float32)

    # 2. 2D Daubechies db4 decomposition
    # cA: approximation, (cH, cV, cD): horizontal, vertical, diagonal details
    # Separable orthonormal Daubechies-4 analysis filters (periodic symmetric border).
    low = np.array([-0.010597401785069032, 0.0328830116668852, 0.030841381835560764,
                    -0.18703481171909309, -0.027983769416859854, 0.6308807679298587,
                    0.7148465705529154, 0.2303778133088964], dtype=np.float32)
    high = low[::-1].copy(); high[::2] *= -1
    # Filter rows then columns; critically sampled detail coefficients approximate PyWavelets dwt2.
    lo_x = cv2.filter2D(Y, cv2.CV_32F, low.reshape(1, -1), borderType=cv2.BORDER_REFLECT)
    hi_x = cv2.filter2D(Y, cv2.CV_32F, high.reshape(1, -1), borderType=cv2.BORDER_REFLECT)
    cD = cv2.filter2D(hi_x, cv2.CV_32F, high.reshape(-1, 1), borderType=cv2.BORDER_REFLECT)[::2, ::2]

    # cD represents the high-frequency diagonal noise sub-band
    cD_abs = np.abs(cD)

    # 3. Local sliding-window 9x9 variance estimation
    # Var(X) = E[X^2] - (E[X])^2
    kernel_size = 9
    kernel = np.ones((kernel_size, kernel_size), dtype=np.float32) / (kernel_size * kernel_size)
    
    mean_cD = cv2.filter2D(cD, -1, kernel)
    mean_cD_sq = cv2.filter2D(cD * cD, -1, kernel)
    var_cD = np.maximum(0.0, mean_cD_sq - (mean_cD * mean_cD))
    std_cD = np.sqrt(var_cD)

    # Resize back to original dimensions for visualization & bounding boxes
    std_map_full = cv2.resize(std_cD, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)

    # 4. Global noise statistics (robust median estimator)
    global_median_sigma = float(np.median(cD_abs) / 0.6745)
    mean_noise = float(np.mean(std_map_full))
    std_noise = float(np.std(std_map_full))

    # 5. Detect Zero-Noise Voids (spliced/brush patches where noise drops to ~0)
    # and High-Frequency Splicing Boundaries
    # In natural captures, noise variance is relatively homogeneous.
    # A flat patched area has local std < 0.15 * mean_noise.
    void_threshold = max(0.05, mean_noise * 0.18)
    void_mask = (std_map_full < void_threshold).astype(np.uint8)

    # Eliminate tiny isolated noise pixels using morphology
    kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    void_clean = cv2.morphologyEx(void_mask, cv2.MORPH_OPEN, kernel_morph)

    bounding_boxes: list[BoundingBox] = []
    contours, _ = cv2.findContours(void_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Detect notable void regions (area >= 800 px, aspect ratio reasonable)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= 1200:
            bx, by, bw, bh = cv2.boundingRect(cnt)
            # Avoid full screen white backgrounds (e.g. huge background card)
            if bw < w_orig * 0.90 and bh < h_orig * 0.50:
                # Calculate noise deficit
                patch_std = float(np.mean(std_map_full[by:by+bh, bx:bx+bw]))
                confidence = min(1.0, max(0.6, 1.0 - (patch_std / (mean_noise + 1e-6))))
                
                bounding_boxes.append(BoundingBox(
                    x=int(bx),
                    y=int(by),
                    width=int(bw),
                    height=int(bh),
                    points=[[bx, by], [bx + bw, by], [bx + bw, by + bh], [bx, by + bh]],
                    label=f"Zero-Noise Splicing Void (σ={patch_std:.2f})",
                    confidence=round(confidence, 2),
                    layer=1,
                    anomaly_type="WAVELET_NOISE_VOID",
                    details={
                        "local_std": round(patch_std, 3),
                        "global_mean_noise": round(mean_noise, 3),
                        "void_area_px": int(area)
                    }
                ))

    # 6. Render High-Contrast Forensic Noise Map (Cyan / Magenta colormap)
    # Normalize noise std to 0-255
    norm_noise = cv2.normalize(std_map_full, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Custom forensic colormap (Cyan to Magenta: Cyan [255, 255, 0] to Magenta [255, 0, 255] in BGR)
    # Using COLORMAP_COOL (Cyan to Magenta) or COLORMAP_JET
    heatmap_colored = cv2.applyColorMap(norm_noise, cv2.COLORMAP_COOL)
    
    # Invert so voids show dark/black and edges glow brightly
    _, noise_webp = cv2.imencode('.webp', heatmap_colored, [cv2.IMWRITE_WEBP_QUALITY, 101])
    wavelet_noise_b64 = f"data:image/webp;base64,{base64.b64encode(noise_webp.tobytes()).decode('utf-8')}"

    # 7. Compute noise inconsistency score (0-100)
    # Calibrated primarily by localized zero-noise voids and splicing boundaries
    coef_var = (std_noise / (mean_noise + 1e-6)) * 100.0
    void_penalty = min(75.0, len(bounding_boxes) * 35.0)
    base_variation = min(12.0, max(0.0, (coef_var - 70.0) * 0.2))
    noise_inconsistency_score = round(min(100.0, base_variation + void_penalty), 1)

    details = {
        "wavelet_basis": "Daubechies db4",
        "subband": "cD (High-Frequency Diagonal)",
        "kernel_size": f"{kernel_size}x{kernel_size}",
        "global_median_sigma": round(global_median_sigma, 3),
        "mean_noise_variance": round(mean_noise, 3),
        "noise_heterogeneity_cv": round(coef_var, 2),
        "void_regions_detected": len(bounding_boxes)
    }

    return noise_inconsistency_score, wavelet_noise_b64, bounding_boxes, details
