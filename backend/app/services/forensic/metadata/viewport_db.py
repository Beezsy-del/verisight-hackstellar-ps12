from typing import Any

STANDARD_ASPECT_RATIOS = [
    ("9:19.5 (Modern Mobile)", 9.0 / 19.5),   # 0.4615 (e.g. 720x1560, 1080x2340)
    ("9:20 (Tall Mobile)", 9.0 / 20.0),       # 0.4500 (e.g. 1080x2400)
    ("9:16 (Standard Mobile)", 9.0 / 16.0),   # 0.5625 (e.g. 720x1280, 1080x1920)
    ("10:16 (Tablet/Mobile)", 10.0 / 16.0),   # 0.6250
    ("3:4 (iPad/Tablet)", 3.0 / 4.0),         # 0.7500
    ("16:9 (Desktop)", 16.0 / 9.0),           # 1.7778
    ("16:10 (Desktop)", 16.0 / 10.0),         # 1.6000
]

def check_viewport_geometry(
    width: int,
    height: int
) -> tuple[str, bool, dict[str, Any]]:
    """
    Evaluates image dimensions (W, H) against the native mobile & desktop viewport database.
    Flags non-standard cropped viewports as NON_NATIVE_VIEWPORT_CROP.
    """
    if width <= 0 or height <= 0:
        return "Invalid Dimensions", True, {"ratio": 0.0}

    current_ratio = float(width) / float(height)

    # Find closest standard aspect ratio
    best_match_name = "Custom / Non-Standard"
    min_deviation = 1.0

    for name, standard_ratio in STANDARD_ASPECT_RATIOS:
        dev = abs(current_ratio - standard_ratio) / standard_ratio
        if dev < min_deviation:
            min_deviation = dev
            best_match_name = name

    # Tolerance: 4.5% difference from native viewport
    is_non_native = min_deviation > 0.045

    details = {
        "width": width,
        "height": height,
        "aspect_ratio": round(current_ratio, 4),
        "closest_standard": best_match_name,
        "deviation_pct": round(min_deviation * 100, 2),
        "is_cropped": is_non_native
    }

    return best_match_name if not is_non_native else f"Non-Native Crop ({width}x{height})", is_non_native, details
