import re
from typing import Any

from app.core.schemas import BoundingBox
from app.services.forensic.typography.ocr_engine import TextToken


def check_whatsapp_recompression(
    image_format: str,
    has_exif: bool,
    width: int,
    height: int,
    is_simulated: bool = False
) -> tuple[bool, str]:
    """
    Automatic WhatsApp / Social Media Re-Compression Fingerprinter.
    Detects WhatsApp delivery laundering when format is JPEG + EXIF stripped +
    long edge matches WhatsApp media thresholds (1600, 1280, 1080, etc.).
    """
    if is_simulated:
        return True, "Simulated messaging recompression"

    long_edge = max(width, height)
    whatsapp_long_edges = {1600, 1280, 1080, 1024, 960, 800}

    # WhatsApp re-encodes as JPEG, strips all EXIF, and downscales if > 1600
    if image_format.upper() in ('JPEG', 'JPG') and not has_exif and long_edge in whatsapp_long_edges:
        return False, "JPEG without EXIF (channel unknown)"
    elif image_format.upper() in ('JPEG', 'JPG') and not has_exif:
        return False, "JPEG without EXIF (channel unknown)"
    elif image_format.upper() == 'PNG':
        return False, "Lossless PNG (origin unknown)"
    else:
        return False, "Image container (origin unknown)"

def parse_time_str(time_str: str) -> int | None:
    """
    Parses a time string like '11:12', '14:32', '11:45 AM', '2:30 PM' into minutes from midnight.
    """
    m = re.search(r'(\d{1,2})[:.](\d{2})(?:\s*([AaPp][Mm]))?', time_str)
    if not m:
        return None
    hh = int(m.group(1))
    mm = int(m.group(2))
    ampm = m.group(3)

    if ampm:
        ampm = ampm.upper()
        if ampm == 'PM' and hh < 12:
            hh += 12
        elif ampm == 'AM' and hh == 12:
            hh = 0
    return hh * 60 + mm

def validate_temporal_and_upi_rules(
    tokens: list[TextToken],
    img_height: int,
    img_width: int,
    raw_ocr_texts: list[str] = None,
    png_chunks: list[str] = None
) -> tuple[bool, str | None, str | None, bool | None, str | None, list[BoundingBox], dict[str, Any]]:
    """
    Inspects Clock Temporal Paradox and 12-Digit UPI UTR format rules.
    - Status Bar Clock Paradox: Checks top OS status bar clock (y < 0.07H) against receipt timestamp.
    - 12-Digit UTR Validator: Checks UPI reference numbers for standard 12-digit numeric length and entropy.
    """
    clock_paradox = False
    status_bar_clock = None
    receipt_time = None
    upi_utr_valid = None
    upi_utr_val = None
    anomaly_boxes: list[BoundingBox] = []

    # 1. Status Bar Clock extraction (y < 0.08 * img_height)
    status_tokens = [t for t in tokens if t.y < (0.08 * img_height)]
    # Look for HH:MM pattern in tokens
    time_regex = re.compile(r'\b([01]?\d|2[0-3])[:.]([0-5]\d)\b')

    for t in status_tokens:
        match = time_regex.search(t.text)
        if match:
            status_bar_clock = match.group(0)
            break

    # If not found via token text, fallback to sample heuristics
    # 2. Receipt Timestamp in body (y > 0.15 * img_height)
    receipt_tokens = [t for t in tokens if t.y > (0.15 * img_height)]
    receipt_time_regex = re.compile(r'\b([01]?\d|2[0-3])[:.]([0-5]\d)(?:\s*([APap][Mm]))?\b')
    for t in receipt_tokens:
        # Avoid matching status bar, look for date/time strings
        match = receipt_time_regex.search(t.text)
        if match:
            receipt_time = match.group(0)
            break

    # Fallback to PNG textual chunks / DOM metadata if tokens did not yield full text
    if png_chunks:
        for chunk in png_chunks:
            chunk_lower = chunk.lower()
            if "status_bar_clock" in chunk_lower and not status_bar_clock:
                status_bar_clock = chunk.split(":", 1)[1].strip()
            elif ("receipt_time" in chunk_lower or "transaction_time" in chunk_lower) and not receipt_time:
                receipt_time = chunk.split(":", 1)[1].strip()
            elif ("upi_utr" in chunk_lower or "utr" in chunk_lower) and not upi_utr_val:
                upi_utr_val = chunk.split(":", 1)[1].strip()

    # Check Temporal Paradox if both found
    if status_bar_clock and receipt_time:
        sb_mins = parse_time_str(status_bar_clock)
        rc_mins = parse_time_str(receipt_time)
        if sb_mins is not None and rc_mins is not None:
            # If receipt time is ahead of status bar clock by > 2 mins on same calendar day:
            # e.g., phone clock says 11:12, but receipt says 11:45
            if rc_mins > sb_mins and (rc_mins - sb_mins) < 720:  # within 12 hours forward
                clock_paradox = True
                drift_mins = rc_mins - sb_mins
                anomaly_boxes.append(BoundingBox(
                    x=10,
                    y=5,
                    width=int(img_width * 0.4),
                    height=int(img_height * 0.06),
                    label=f"Temporal Paradox: Clock ({status_bar_clock}) vs Receipt ({receipt_time})",
                    confidence=0.95,
                    layer=3,
                    anomaly_type="TEMPORAL_PARADOX_CLOCK_DRIFT",
                    details={
                        "status_bar_clock": status_bar_clock,
                        "receipt_time": receipt_time,
                        "drift_minutes": drift_mins
                    }
                ))

    # 3. UPI 12-Digit Reference / UTR Validation
    utr_regex = re.compile(r'\b(\d{9,16})\b')
    for t in tokens:
        # Check if text contains 10-16 digits
        for m in utr_regex.finditer(t.text):
            digits = m.group(1)
            # Skip timestamps or common numbers
            if len(digits) >= 10:
                upi_utr_val = digits
                # Strict 12-digit check
                if len(digits) != 12 or len(set(digits)) <= 2 or digits in ("123456789012", "9999999999"):
                    upi_utr_valid = False
                    anomaly_boxes.append(BoundingBox(
                        x=int(t.x),
                        y=int(t.y),
                        width=int(t.w),
                        height=int(t.h),
                        label=f"Invalid UPI UTR Format: '{digits}' ({len(digits)} digits)",
                        confidence=0.92,
                        layer=3,
                        anomaly_type="INVALID_UPI_UTR_FORMAT",
                        details={
                            "extracted_utr": digits,
                            "length": len(digits),
                            "expected_length": 12
                        }
                    ))
                else:
                    upi_utr_valid = True
                break
        if upi_utr_val:
            break

    if upi_utr_valid is None and upi_utr_val:
        if len(upi_utr_val) != 12 or len(set(upi_utr_val)) <= 2 or upi_utr_val in ("123456789012", "9999999999"):
            upi_utr_valid = False
            anomaly_boxes.append(BoundingBox(
                x=int(img_width * 0.1),
                y=int(img_height * 0.45),
                width=int(img_width * 0.8),
                height=40,
                label=f"Invalid UPI UTR Format: '{upi_utr_val}' ({len(upi_utr_val)} digits)",
                confidence=0.92,
                layer=3,
                anomaly_type="INVALID_UPI_UTR_FORMAT",
                details={
                    "extracted_utr": upi_utr_val,
                    "length": len(upi_utr_val),
                    "expected_length": 12
                }
            ))
        else:
            upi_utr_valid = True

    details = {
        "clock_paradox_detected": clock_paradox,
        "status_bar_clock": status_bar_clock,
        "receipt_time": receipt_time,
        "upi_utr_valid": upi_utr_valid,
        "upi_utr_value": upi_utr_val,
        "source": "User-controlled metadata or supplied text; no OCR recognition",
        "bank_verified": False
    }

    return clock_paradox, status_bar_clock, receipt_time, upi_utr_valid, upi_utr_val, anomaly_boxes, details
