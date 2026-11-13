import os
import io
import sys
import base64
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.simulation.whatsapp_pipeline import run_whatsapp_simulation

SAMPLES_DIR = Path(__file__).resolve().parent

def get_font(size: int, bold: bool = False):
    """Fallback font loader using default or Arial / DejaVu / Tahoma."""
    font_candidates = [
        "arial.ttf", "arialbd.ttf" if bold else "arial.ttf",
        "segoeui.ttf", "segoeuib.ttf" if bold else "segoeui.ttf",
        "DejaVuSans.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except IOError:
            continue
    return ImageFont.load_default()

def draw_rounded_rect(draw: ImageDraw.Draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def generate_base_gpay_screenshot(
    amount_str: str = "₹1,250.00",
    status_time: str = "14:32",
    receipt_time: str = "12 Nov 2026, 2:30 PM",
    utr_number: str = "631618492041",
    watermark_text: str = "SYNTHETIC DEMONSTRATION — NOT A REAL TRANSACTION",
    card_bg_color: tuple = (255, 255, 255),
    baseline_offset_px: float = 0.0,
    patch_color: tuple = None,
    zero_noise_patch: bool = False,
    software_tag: str = None
) -> Image.Image:
    """
    Renders a realistic mobile UPI Payment receipt (720 x 1560).
    """
    width, height = 720, 1560
    # Background: modern dark/slate canvas for mobile UI
    canvas_bg = (18, 24, 38)
    image = Image.new("RGB", (width, height), canvas_bg)
    draw = ImageDraw.Draw(image)

    # 1. Top OS Status Bar (y: 0 to 65)
    # Clock (left), Icons (right: Wi-Fi, 4G, Battery 84%)
    font_status = get_font(26, bold=True)
    draw.text((45, 22), status_time, fill=(240, 243, 248), font=font_status)
    draw.text((width - 150, 22), "LTE  84%", fill=(220, 225, 235), font=get_font(22, bold=False))

    # 2. Top Watermark Banner
    font_wm = get_font(18, bold=True)
    draw.rectangle([0, 68, width, 102], fill=(45, 55, 75))
    draw.text((60, 74), watermark_text, fill=(250, 204, 21), font=font_wm)

    # 3. White Central Transaction Card (x: 40 to 680, y: 140 to 1320)
    card_box = [40, 140, width - 40, 1320]
    draw_rounded_rect(draw, card_box, radius=28, fill=card_bg_color)

    # 4. Success Green Checkmark Circle
    circle_center = (width // 2, 235)
    circle_radius = 48
    draw.ellipse([
        circle_center[0] - circle_radius, circle_center[1] - circle_radius,
        circle_center[0] + circle_radius, circle_center[1] + circle_radius
    ], fill=(16, 185, 129))  # Emerald #10B981

    # Checkmark white icon
    draw.line([circle_center[0] - 20, circle_center[1] + 2, circle_center[0] - 5, circle_center[1] + 18], fill=(255, 255, 255), width=6)
    draw.line([circle_center[0] - 5, circle_center[1] + 18, circle_center[0] + 22, circle_center[1] - 14], fill=(255, 255, 255), width=6)

    # 5. Paid To Details
    font_paid_to = get_font(28, bold=True)
    draw.text((width // 2 - 165, 310), "Paid to Ramesh Kirana Store", fill=(30, 41, 59), font=font_paid_to)

    font_upi_id = get_font(22, bold=False)
    draw.text((width // 2 - 120, 355), "rameshstore@okaxis", fill=(100, 116, 139), font=font_upi_id)

    # 6. Primary Amount Display (e.g. ₹1,250.00)
    font_currency = get_font(56, bold=True)
    font_amount = get_font(62, bold=True)

    amount_y_base = 450
    # Currency symbol "₹" (baseline aligned to digits)
    draw.text((width // 2 - 160, amount_y_base + 6), "₹", fill=(15, 23, 42), font=font_currency)

    # Amount digits: e.g. "1,250.00" or "95,250.00"
    digits_text = amount_str.replace("₹", "").strip()
    digits_x = width // 2 - 105
    digits_y = amount_y_base + int(baseline_offset_px)

    # If patch color provided, draw the background patch under digits
    if patch_color:
        patch_rect = [digits_x - 10, digits_y - 6, digits_x + 310, digits_y + 76]
        draw.rectangle(patch_rect, fill=patch_color)

    draw.text((digits_x, digits_y), digits_text, fill=(15, 23, 42), font=font_amount)

    # 7. Divider Line
    draw.line([80, 580, width - 80, 580], fill=(226, 232, 240), width=2)

    # 8. Transaction Details Rows
    font_label = get_font(24, bold=False)
    font_val = get_font(24, bold=True)

    # Date & Time Row
    draw.text((80, 630), "Date & Time", fill=(100, 116, 139), font=font_label)
    draw.text((width - 360, 630), receipt_time, fill=(30, 41, 59), font=font_val)

    # UPI Reference (UTR) Row
    draw.text((80, 720), "UPI Reference ID", fill=(100, 116, 139), font=font_label)
    draw.text((width - 290, 720), utr_number, fill=(30, 41, 59), font=font_val)

    # Payment Status Row
    draw.text((80, 810), "Payment Status", fill=(100, 116, 139), font=font_label)
    draw.text((width - 240, 810), "COMPLETED", fill=(16, 185, 129), font=font_val)

    # 9. Bottom Security Badge
    draw.rounded_rectangle([width // 2 - 180, 1050, width // 2 + 180, 1110], radius=16, fill=(241, 245, 249))
    draw.text((width // 2 - 145, 1068), "🛡️ Verified by NPCI UPI Security", fill=(71, 85, 105), font=get_font(20, bold=True))

    # Add subtle realistic raster render noise (sigma = 1.8)
    img_np = np.array(image).astype(np.float32)
    noise = np.random.normal(0, 1.8, img_np.shape).astype(np.float32)

    # If zero-noise patch specified, suppress noise in the spliced patch area
    if zero_noise_patch and patch_color:
        px1, py1, px2, py2 = patch_rect
        noise[py1:py2, px1:px2] = 0.0

    img_with_noise = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    final_pil = Image.fromarray(img_with_noise)

    # If software tag specified, attach PNG metadata
    if software_tag:
        final_pil.info["Software"] = software_tag

    return final_pil

def generate_all_samples():
    """Generates all 5 golden demo samples on startup."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # Sample 1: Authentic GPay UPI Receipt (₹1,250.00)
    # Target Score: 4% - 9% (AUTHENTIC_VERIFIED)
    # -------------------------------------------------------------
    s1_path = SAMPLES_DIR / "sample_1_authentic_gpay.png"
    if not s1_path.exists():
        s1_img = generate_base_gpay_screenshot(
            amount_str="₹1,250.00",
            status_time="14:32",
            receipt_time="12 Nov 2026, 2:30 PM",
            utr_number="631618492041",
            card_bg_color=(255, 255, 255),
            baseline_offset_px=0.0
        )
        s1_img.save(s1_path, format="PNG")
        print(f"[SampleGenerator] Generated: {s1_path.name}")

    # -------------------------------------------------------------
    # Sample 2: Pixel-Spliced Amount (₹95,250.00)
    # Spliced with Delta-E = 5.2, baseline offset +3.5px, zero wavelet noise patch, JPEG Q=82
    # Target Score: 91% - 97% (MANIPULATED_FORGERY)
    # -------------------------------------------------------------
    s2_path = SAMPLES_DIR / "sample_2_spliced_amount.jpg"
    if not s2_path.exists():
        # Patch color: #F4F6F9 (244, 246, 249) vs Card White #FFFFFF (255, 255, 255)
        # CIELAB Delta-E ~ 5.2!
        s2_img = generate_base_gpay_screenshot(
            amount_str="₹95,250.00",
            status_time="14:32",
            receipt_time="12 Nov 2026, 2:30 PM",
            utr_number="631618492041",
            card_bg_color=(255, 255, 255),
            baseline_offset_px=4.2,  # 4.2 px downward shift
            patch_color=(240, 243, 248),
            zero_noise_patch=True
        )
        s2_img.save(s2_path, format="JPEG", quality=82)
        print(f"[SampleGenerator] Generated: {s2_path.name}")

    # -------------------------------------------------------------
    # Sample 3: Fake Receipt Generator / DOM Edit
    # Temporal Paradox (11:12 vs 11:45 AM) + 10-digit dummy UTR 9999999999 + FakeGen-UI tag
    # Target Score: 86% - 93% (MANIPULATED_FORGERY)
    # -------------------------------------------------------------
    s3_path = SAMPLES_DIR / "sample_3_fake_generator_paradox.png"
    if not s3_path.exists():
        s3_img = generate_base_gpay_screenshot(
            amount_str="₹35,000.00",
            status_time="11:12",  # Phone clock 11:12
            receipt_time="12 Nov 2026, 11:45 AM",  # Future receipt timestamp!
            utr_number="9999999999",  # Invalid 10-digit dummy UTR
            software_tag="FakeGen-UI v2.4 (CanvasCapture)"
        )
        from PIL.PngImagePlugin import PngInfo
        pnginfo = PngInfo()
        pnginfo.add_text("Software", "FakeGen-UI v2.4 (CanvasCapture)")
        pnginfo.add_text("Status_Bar_Clock", "11:12")
        pnginfo.add_text("Receipt_Time", "11:45 AM")
        pnginfo.add_text("UPI_UTR", "9999999999")
        s3_img.save(s3_path, format="PNG", pnginfo=pnginfo)
        print(f"[SampleGenerator] Generated: {s3_path.name}")

    # -------------------------------------------------------------
    # Sample 4: WhatsApp-Forwarded Forgery
    # Generated by passing sample 2 through whatsapp_pipeline (EXIF stripped, Q=77, 4:2:0)
    # Target Score: 82% - 89% (MANIPULATED_FORGERY with WhatsApp pill)
    # -------------------------------------------------------------
    s4_path = SAMPLES_DIR / "sample_4_whatsapp_laundered.jpg"
    if not s4_path.exists():
        with open(s2_path, "rb") as f:
            s2_bytes = f.read()
        sim_res = run_whatsapp_simulation(s2_bytes, "sample_4.jpg")
        # Save simulated output
        sim_bytes = base64.b64decode(sim_res.simulated_image_b64.split(",")[1])
        with open(s4_path, "wb") as f:
            f.write(sim_bytes)
        print(f"[SampleGenerator] Generated: {s4_path.name}")

    # -------------------------------------------------------------
    # Sample 5: Copy-Move Cloned Digits & Cropped Viewport (680 x 1120)
    # Digit sequence cloned via ORB matching, non-native viewport crop
    # Target Score: 85% - 92% (MANIPULATED_FORGERY)
    # -------------------------------------------------------------
    s5_path = SAMPLES_DIR / "sample_5_cloned_chat_receipt.jpg"
    if not s5_path.exists():
        # Non-native cropped viewport: 680 x 1120
        crop_w, crop_h = 680, 1120
        base_img = generate_base_gpay_screenshot(
            amount_str="₹50,000.00",
            status_time="16:45",
            receipt_time="12 Nov 2026, 4:40 PM",
            utr_number="411982736184"
        )
        cropped = base_img.crop((20, 100, 20 + crop_w, 100 + crop_h))

        # Clone "000" digits block onto another area to create copy-move clusters
        np_crop = np.array(cropped)
        # Clone a 40x80 block containing the zeros and paste it at another location
        src_block = np_crop[350:410, 310:390].copy()
        np_crop[550:610, 310:390] = src_block

        cloned_pil = Image.fromarray(np_crop)
        cloned_pil.save(s5_path, format="JPEG", quality=85)
        print(f"[SampleGenerator] Generated: {s5_path.name}")

if __name__ == "__main__":
    generate_all_samples()
