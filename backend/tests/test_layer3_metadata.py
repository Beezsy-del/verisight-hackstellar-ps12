import io

from app.services.forensic.metadata.domain_rules import (
    check_whatsapp_recompression,
    validate_temporal_and_upi_rules,
)
from app.services.forensic.metadata.exif_inspector import inspect_image_metadata
from app.services.forensic.metadata.viewport_db import check_viewport_geometry
from app.services.forensic.typography.ocr_engine import TextToken
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def test_viewport_analysis():
    # Standard modern mobile screen (Samsung / OnePlus / GPay default: 720x1560)
    best_name, is_non_native, details = check_viewport_geometry(720, 1560)
    assert not is_non_native
    assert "Mobile" in best_name

    # Irregularly cropped screenshot (e.g. 512 x 341)
    best_name_crop, is_non_native_crop, details_crop = check_viewport_geometry(512, 341)
    assert is_non_native_crop


def test_upi_utr_validation():
    # Valid 12-digit Indian banking reference
    tokens_valid = [
        TextToken(text="UPI Ref: 631618492041", bbox=[50, 400, 200, 30])
    ]
    paradox, sb_c, rc_t, utr_valid, utr_val, boxes, details = validate_temporal_and_upi_rules(tokens_valid, 1560, 720)
    assert utr_valid is True
    assert utr_val == "631618492041"

    # Invalid: 10-digit dummy reference
    tokens_invalid = [
        TextToken(text="UPI Ref: 1234567890", bbox=[50, 400, 200, 30])
    ]
    paradox2, sb_c2, rc_t2, utr_valid2, utr_val2, boxes2, details2 = validate_temporal_and_upi_rules(tokens_invalid, 1560, 720)
    assert utr_valid2 is False


def test_temporal_paradox():
    # Status bar clock says 11:12, but transaction receipt says 11:45 AM (Temporal paradox!)
    tokens = [
        TextToken(text="11:12", bbox=[20, 10, 60, 25]),   # In status bar (y < 0.08 * 1560 = 124)
        TextToken(text="11:45 AM", bbox=[100, 500, 80, 30])  # In receipt body
    ]
    paradox, sb_c, rc_t, utr_v, utr_val, boxes, details = validate_temporal_and_upi_rules(tokens, 1560, 720)
    assert paradox is True
    assert sb_c == "11:12"
    assert "11:45" in rc_t


def test_whatsapp_laundering_detection():
    # JPEG with stripped EXIF and matching 1600 dimension
    is_laundered, desc = check_whatsapp_recompression(
        image_format="JPEG",
        has_exif=False,
        width=738,
        height=1600
    )
    assert not is_laundered
    assert "channel unknown" in desc


def test_exif_metadata_inspection():
    img = Image.new("RGB", (200, 200), (255, 255, 255))
    info = PngInfo()
    info.add_text("Software", "Adobe Photoshop 2025")
    buf = io.BytesIO()
    img.save(buf, format="PNG", pnginfo=info)
    raw_bytes = buf.getvalue()

    meta = inspect_image_metadata(raw_bytes, "test.png")
    assert meta["software"] is not None
    assert "Photoshop" in meta["software"]
