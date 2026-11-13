from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import cv2
import numpy as np


def inspect_qr_codes(img_bgr: np.ndarray) -> dict[str, object]:
    """Decode QR payloads locally and describe their type; never trust/execute them."""
    detector = cv2.QRCodeDetector()
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    candidates = [gray]
    if min(gray.shape[:2]) < 900:
        candidates.append(cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))

    decoded: list[str] = []
    regions: list[dict[str, int]] = []
    for candidate in candidates:
        try:
            ok, values, points, _straight = detector.detectAndDecodeMulti(candidate)
            if ok:
                decoded.extend(value for value in values if value)
                if points is not None:
                    scale_x = gray.shape[1] / candidate.shape[1]
                    scale_y = gray.shape[0] / candidate.shape[0]
                    regions.extend(_regions_from_points(points, scale_x, scale_y))
        except (cv2.error, ValueError):
            pass
        if not decoded:
            try:
                value, points, _straight = detector.detectAndDecode(candidate)
                if value:
                    decoded.append(value)
                    if points is not None:
                        scale_x = gray.shape[1] / candidate.shape[1]
                        scale_y = gray.shape[0] / candidate.shape[0]
                        regions.extend(_regions_from_points(points, scale_x, scale_y))
            except (cv2.error, ValueError):
                pass
        if decoded:
            break

    # Remove duplicates while retaining order and bound response size.
    payloads = list(dict.fromkeys(value[:2048] for value in decoded))[:8]
    results = [_describe_payload(value) for value in payloads]
    return {
        "scanner": "OpenCV QR decoder",
        "decoded_count": len(results),
        "results": results,
        "regions": regions,
        "authenticity_verified": False,
        "note": "Decoded QR content only. This does not verify the recipient, destination website, or whether a payment was made. Do not open links or pay based only on this result.",
    }


def _regions_from_points(points: np.ndarray, scale_x: float, scale_y: float) -> list[dict[str, int]]:
    regions = []
    for polygon in np.asarray(points):
        xs = polygon[:, 0] * scale_x
        ys = polygon[:, 1] * scale_y
        left, top = max(0, int(xs.min())), max(0, int(ys.min()))
        right, bottom = int(xs.max()), int(ys.max())
        if right > left and bottom > top:
            regions.append({"x": left, "y": top, "width": right - left, "height": bottom - top})
    return regions


def _describe_payload(payload: str) -> dict[str, object]:
    parsed = urlsplit(payload)
    scheme = parsed.scheme.lower()
    result: dict[str, object] = {
        "payload": payload,
        "kind": "TEXT",
        "scheme": scheme or None,
        "host": parsed.hostname,
        "authenticity_verified": False,
        "review_cue": None,
    }
    if scheme == "upi":
        result["kind"] = "UPI_PAYMENT_INTENT"
        params = parse_qs(parsed.query, keep_blank_values=False)
        for source, target in (("pa", "payee_vpa"), ("pn", "payee_name"), ("am", "amount"), ("cu", "currency"), ("tr", "reference")):
            values = params.get(source)
            if values:
                result[target] = values[0][:256]
        result["review_cue"] = "Compare the displayed payee and amount with what you intended. A QR payload cannot prove the recipient is trustworthy or payment succeeded."
    elif scheme in {"http", "https"} and parsed.hostname:
        result["kind"] = "WEB_LINK"
        if scheme == "http":
            result["review_cue"] = "This link does not use HTTPS. Do not enter payment credentials unless you independently trust the destination."
        else:
            result["review_cue"] = "Check the full domain carefully before opening. HTTPS does not establish that the site or QR is trustworthy."
    elif scheme:
        result["kind"] = "OTHER_URI"
        result["review_cue"] = "This QR contains an application URI. Inspect it before opening; it has not been validated."
    return result
