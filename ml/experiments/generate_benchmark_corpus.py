"""
VeriSight Controlled Benchmark Corpus Generator.
Generates an annotated, multi-scenario dataset with known ground truth
and full provenance tracking adhering to docs/DATASET_GOVERNANCE.md.
"""
from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

# Add ml and backend to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(ROOT_DIR / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend"))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_font(size: int, bold: bool = False):
    font_candidates = [
        "arial.ttf", "arialbd.ttf" if bold else "arial.ttf",
        "segoeui.ttf", "segoeuib.ttf" if bold else "segoeui.ttf",
        "DejaVuSans.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    ]
    for c in font_candidates:
        try:
            return ImageFont.truetype(c, size)
        except IOError:
            continue
    return ImageFont.load_default()


def render_upi_screenshot(
    amount_str: str = "₹1,250.00",
    status_time: str = "14:32",
    receipt_time: str = "12 Nov 2026, 2:30 PM",
    utr_number: str = "631618492041",
    watermark: str = "SYNTHETIC BENCHMARK — RESEARCH EVALUATION ONLY",
    card_bg: tuple = (255, 255, 255),
    patch_color: tuple | None = None,
    baseline_offset: float = 0.0,
    zero_noise_void: bool = False,
    is_whatsapp: bool = False,
    is_cloned: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Renders screenshot and binary manipulation mask (0=authentic, 255=manipulated).
    """
    w, h = 720, 1560
    img = Image.new("RGB", (w, h), (18, 24, 38))
    draw = ImageDraw.Draw(img)
    mask = np.zeros((h, w), dtype=np.uint8)

    # Status Bar
    draw.text((45, 22), status_time, fill=(240, 243, 248), font=get_font(26, bold=True))
    draw.text((w - 150, 22), "LTE  84%", fill=(220, 225, 235), font=get_font(22))

    # Watermark Banner
    draw.rectangle([0, 68, w, 102], fill=(45, 55, 75))
    draw.text((50, 74), watermark, fill=(250, 204, 21), font=get_font(16, bold=True))

    # Card
    draw.rounded_rectangle([40, 140, w - 40, 1320], radius=28, fill=card_bg)

    # Success Checkmark
    cx, cy = w // 2, 235
    draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill=(16, 185, 129))
    draw.line([cx - 20, cy + 2, cx - 5, cy + 18], fill=(255, 255, 255), width=6)
    draw.line([cx - 5, cy + 18, cx + 22, cy - 14], fill=(255, 255, 255), width=6)

    # Text
    draw.text((cx - 165, 310), "Paid to Ramesh Kirana Store", fill=(30, 41, 59), font=get_font(28, bold=True))
    draw.text((cx - 120, 355), "rameshstore@okaxis", fill=(100, 116, 139), font=get_font(22))

    # Primary Amount
    amount_y = int(450 + baseline_offset)
    draw.text((cx - 160, 456), "₹", fill=(15, 23, 42), font=get_font(56, bold=True))

    if patch_color:
        # Draw background patch box
        px1, py1, px2, py2 = cx - 110, 440, cx + 160, 525
        draw.rectangle([px1, py1, px2, py2], fill=patch_color)
        mask[py1:py2, px1:px2] = 255

    draw.text((cx - 100, amount_y), amount_str.replace("₹", "").strip(), fill=(15, 23, 42), font=get_font(62, bold=True))

    # Details
    draw.text((70, 620), "Transaction Details", fill=(71, 85, 105), font=get_font(22, bold=True))
    draw.text((70, 680), "UPI Transaction ID", fill=(100, 116, 139), font=get_font(20))
    draw.text((70, 715), utr_number, fill=(30, 41, 59), font=get_font(24, bold=True))
    draw.text((70, 780), "Date & Time", fill=(100, 116, 139), font=get_font(20))
    draw.text((70, 815), receipt_time, fill=(30, 41, 59), font=get_font(24, bold=True))

    img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    if zero_noise_void:
        # Smooth the amount patch region to zero out noise
        px1, py1, px2, py2 = cx - 110, 440, cx + 160, 525
        img_bgr[py1:py2, px1:px2] = cv2.GaussianBlur(img_bgr[py1:py2, px1:px2], (5, 5), 0)
        mask[py1:py2, px1:px2] = 255

    if is_cloned:
        # Copy-move patch simulation
        patch = img_bgr[715:745, 70:220].copy()
        img_bgr[870:900, 70:220] = patch
        mask[870:900, 70:220] = 255

    if is_whatsapp:
        # Transcode with JPEG Q=77, 4:2:0 subsampling
        _, enc = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 77])
        img_bgr = cv2.imdecode(enc, cv2.IMREAD_COLOR)

    return img_bgr, mask


def generate_benchmark_suite(output_dir: Path) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    masks_dir = output_dir / "masks"
    images_dir.mkdir(parents=True, exist_ok=True)
    masks_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, Any]] = []

    configs = [
        # 1-10 Authentic Reference
        {"id": "auth_01", "label": 0, "manip_type": "NONE", "amt": "₹500.00", "st": "10:15", "rt": "11 Nov 2026, 10:14 AM", "utr": "631618492041", "split": "TRAINING"},
        {"id": "auth_02", "label": 0, "manip_type": "NONE", "amt": "₹1,250.00", "st": "14:32", "rt": "11 Nov 2026, 2:30 PM", "utr": "631618492042", "split": "TRAINING"},
        {"id": "auth_03", "label": 0, "manip_type": "NONE", "amt": "₹3,400.00", "st": "09:05", "rt": "11 Nov 2026, 9:04 AM", "utr": "631618492043", "split": "TRAINING"},
        {"id": "auth_04", "label": 0, "manip_type": "NONE", "amt": "₹85.00", "st": "16:45", "rt": "11 Nov 2026, 4:44 PM", "utr": "631618492044", "split": "TRAINING"},
        {"id": "auth_05", "label": 0, "manip_type": "NONE", "amt": "₹12,000.00", "st": "11:20", "rt": "11 Nov 2026, 11:18 AM", "utr": "631618492045", "split": "TRAINING"},
        {"id": "auth_06", "label": 0, "manip_type": "NONE", "amt": "₹250.00", "st": "18:10", "rt": "11 Nov 2026, 6:08 PM", "utr": "631618492046", "split": "VALIDATION"},
        {"id": "auth_07", "label": 0, "manip_type": "NONE", "amt": "₹9,999.00", "st": "13:40", "rt": "11 Nov 2026, 1:38 PM", "utr": "631618492047", "split": "VALIDATION"},
        {"id": "auth_08", "label": 0, "manip_type": "NONE", "amt": "₹45.00", "st": "08:15", "rt": "11 Nov 2026, 8:14 AM", "utr": "631618492048", "split": "CALIBRATION"},
        {"id": "auth_09", "label": 0, "manip_type": "NONE", "amt": "₹750.00", "st": "20:00", "rt": "11 Nov 2026, 7:58 PM", "utr": "631618492049", "split": "FINAL_TEST"},
        {"id": "auth_10", "label": 0, "manip_type": "NONE", "amt": "₹15,400.00", "st": "21:30", "rt": "11 Nov 2026, 9:28 PM", "utr": "631618492050", "split": "FINAL_TEST"},

        # 11-15 Authentic WhatsApp Forwarded (Tests False Positive Resistance under compression)
        {"id": "auth_wa_01", "label": 0, "manip_type": "NONE", "amt": "₹1,500.00", "st": "11:00", "rt": "11 Nov 2026, 10:58 AM", "utr": "631618492051", "wa": True, "split": "TRAINING"},
        {"id": "auth_wa_02", "label": 0, "manip_type": "NONE", "amt": "₹420.00", "st": "15:20", "rt": "11 Nov 2026, 3:18 PM", "utr": "631618492052", "wa": True, "split": "VALIDATION"},
        {"id": "auth_wa_03", "label": 0, "manip_type": "NONE", "amt": "₹8,500.00", "st": "17:40", "rt": "11 Nov 2026, 5:39 PM", "utr": "631618492053", "wa": True, "split": "FINAL_TEST"},

        # 16-25 Spliced Amount Manipulations
        {"id": "manip_splice_01", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹95,250.00", "st": "14:32", "rt": "11 Nov 2026, 2:30 PM", "utr": "631618492054", "patch": (245, 247, 252), "drift": 3.8, "void": True, "split": "TRAINING"},
        {"id": "manip_splice_02", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹50,000.00", "st": "11:15", "rt": "11 Nov 2026, 11:14 AM", "utr": "631618492055", "patch": (240, 242, 248), "drift": 4.2, "void": True, "split": "TRAINING"},
        {"id": "manip_splice_03", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹1,00,000.00", "st": "16:00", "rt": "11 Nov 2026, 3:58 PM", "utr": "631618492056", "patch": (248, 250, 255), "drift": 3.2, "void": True, "split": "TRAINING"},
        {"id": "manip_splice_04", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹88,750.00", "st": "18:20", "rt": "11 Nov 2026, 6:18 PM", "utr": "631618492057", "patch": (242, 244, 250), "drift": 3.5, "void": True, "split": "VALIDATION"},
        {"id": "manip_splice_05", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹65,000.00", "st": "20:45", "rt": "11 Nov 2026, 8:44 PM", "utr": "631618492058", "patch": (244, 246, 252), "drift": 4.0, "void": True, "split": "FINAL_TEST"},

        # 26-30 Temporal Clock Paradox & Fake UTR Generator
        {"id": "manip_paradox_01", "label": 1, "manip_type": "DOM_EDIT", "amt": "₹2,500.00", "st": "11:12", "rt": "11 Nov 2026, 11:45 AM", "utr": "9876543210", "split": "TRAINING"},
        {"id": "manip_paradox_02", "label": 1, "manip_type": "DOM_EDIT", "amt": "₹15,000.00", "st": "09:30", "rt": "11 Nov 2026, 10:15 AM", "utr": "1234567890", "split": "VALIDATION"},
        {"id": "manip_paradox_03", "label": 1, "manip_type": "DOM_EDIT", "amt": "₹7,800.00", "st": "14:10", "rt": "11 Nov 2026, 3:00 PM", "utr": "5555555555", "split": "FINAL_TEST"},

        # 31-35 WhatsApp Laundered Forgery
        {"id": "manip_wa_splice_01", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹45,000.00", "st": "12:00", "rt": "11 Nov 2026, 11:58 AM", "utr": "631618492059", "patch": (244, 246, 250), "drift": 3.6, "void": True, "wa": True, "split": "TRAINING"},
        {"id": "manip_wa_splice_02", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹82,500.00", "st": "15:45", "rt": "11 Nov 2026, 3:42 PM", "utr": "631618492060", "patch": (242, 245, 251), "drift": 3.9, "void": True, "wa": True, "split": "VALIDATION"},
        {"id": "manip_wa_splice_03", "label": 1, "manip_type": "PIXEL_SPLICE", "amt": "₹99,990.00", "st": "19:15", "rt": "11 Nov 2026, 7:12 PM", "utr": "631618492061", "patch": (243, 246, 252), "drift": 3.7, "void": True, "wa": True, "split": "FINAL_TEST"},

        # 36-40 Copy-Move Cloned Digits
        {"id": "manip_clone_01", "label": 1, "manip_type": "COPY_MOVE", "amt": "₹8,888.00", "st": "13:00", "rt": "11 Nov 2026, 12:58 PM", "utr": "631618492062", "clone": True, "split": "TRAINING"},
        {"id": "manip_clone_02", "label": 1, "manip_type": "COPY_MOVE", "amt": "₹3,333.00", "st": "17:30", "rt": "11 Nov 2026, 5:28 PM", "utr": "631618492063", "clone": True, "split": "VALIDATION"},
        {"id": "manip_clone_03", "label": 1, "manip_type": "COPY_MOVE", "amt": "₹7,777.00", "st": "21:00", "rt": "11 Nov 2026, 8:58 PM", "utr": "631618492064", "clone": True, "split": "FINAL_TEST"},
    ]

    for cfg in configs:
        img_bgr, mask = render_upi_screenshot(
            amount_str=cfg["amt"],
            status_time=cfg["st"],
            receipt_time=cfg["rt"],
            utr_number=cfg["utr"],
            patch_color=cfg.get("patch"),
            baseline_offset=cfg.get("drift", 0.0),
            zero_noise_void=cfg.get("void", False),
            is_whatsapp=cfg.get("wa", False),
            is_cloned=cfg.get("clone", False),
        )

        img_path = images_dir / f"{cfg['id']}.png"
        mask_path = masks_dir / f"{cfg['id']}_mask.png"

        cv2.imwrite(str(img_path), img_bgr)
        cv2.imwrite(str(mask_path), mask)

        manifest.append({
            "sample_id": cfg["id"],
            "image_path": str(img_path.relative_to(BASE_DIR)),
            "mask_path": str(mask_path.relative_to(BASE_DIR)),
            "ground_truth_label": cfg["label"],
            "manipulation_type": cfg["manip_type"],
            "source_type": "PIL_SYNTHESIS",
            "screenshot_template": "GPAY_UPI",
            "is_whatsapp": cfg.get("wa", False),
            "clock_paradox": cfg.get("st") == "11:12" and "11:45" in cfg.get("rt", ""),
            "upi_invalid": len(cfg.get("utr", "")) != 12,
            "split_assignment": cfg["split"],
            "license_status": "PROJECT_OWNED",
        })

    manifest_path = output_dir / "manifests" / "benchmark_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {len(manifest)} benchmark samples in {output_dir}")
    return manifest


if __name__ == "__main__":
    generate_benchmark_suite(BASE_DIR / "datasets")
