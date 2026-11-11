import base64

import cv2
import numpy as np

from app.core.schemas import WhatsAppSimulationResponse


def run_whatsapp_simulation(
    image_bytes: bytes,
    filename: str = "screenshot.png"
) -> WhatsAppSimulationResponse:
    """
    Executes the WhatsApp Media Delivery Simulation:
    1. Strips all EXIF / metadata / ICC / PNG chunks.
    2. Resizes if longest edge exceeds 1600px.
    3. Re-quantizes as standard JPEG (Quality=77, 4:2:0 chroma subsampling).
    4. Computes before vs after difference map.
    5. Re-runs the 4-layer forensic pipeline on the laundered image to demonstrate survival of geometric/wavelet signals.
    """
    orig_size = len(image_bytes)

    # Decode, resize to 1600px maximum and JPEG re-encode (OpenCV uses 4:2:0 by default).
    from app.services.image_validation import decode_image
    orig_bgr = decode_image(image_bytes)
    h_orig, w_orig = orig_bgr.shape[:2]
    max_edge = max(w_orig, h_orig)
    if max_edge > 1600:
        scale = 1600.0 / max_edge
        new_w, new_h = int(round(w_orig * scale)), int(round(h_orig * scale))
        resized = cv2.resize(orig_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        new_w, new_h, resized = w_orig, h_orig, orig_bgr
    ok, encoded = cv2.imencode('.jpg', resized, [cv2.IMWRITE_JPEG_QUALITY, 77])
    if not ok:
        raise ValueError("JPEG recompression failed")
    simulated_bytes = encoded.tobytes()

    sim_size = len(simulated_bytes)
    comp_ratio = round(float(orig_size) / max(1, sim_size), 2)

    # Decode simulated image
    np_sim = np.frombuffer(simulated_bytes, np.uint8)
    sim_bgr = cv2.imdecode(np_sim, cv2.IMREAD_COLOR)

    # Match sizes for diff if resized
    if orig_bgr.shape[:2] != sim_bgr.shape[:2]:
        orig_resized = cv2.resize(orig_bgr, (new_w, new_h))
    else:
        orig_resized = orig_bgr

    diff = cv2.absdiff(orig_resized, sim_bgr)
    diff_amplified = np.clip(diff.astype(np.uint16) * 12, 0, 255).astype(np.uint8)
    diff_colormap = cv2.applyColorMap(cv2.cvtColor(diff_amplified, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_JET)

    _, diff_png = cv2.imencode('.png', diff_colormap)
    diff_b64 = f"data:image/png;base64,{base64.b64encode(diff_png.tobytes()).decode('utf-8')}"

    sim_b64 = f"data:image/jpeg;base64,{base64.b64encode(simulated_bytes).decode('utf-8')}"

    # Re-analyze laundered image
    from app.services.forensic.pipeline import analyze_screenshot
    reanalysis_report = analyze_screenshot(
        image_bytes=simulated_bytes,
        filename=f"whatsapp_{filename}.jpg",
        is_whatsapp_simulated=True
    )

    return WhatsAppSimulationResponse(
        original_size_bytes=orig_size,
        simulated_size_bytes=sim_size,
        compression_ratio=comp_ratio,
        original_dimensions=[w_orig, h_orig],
        simulated_dimensions=[new_w, new_h],
        simulated_image_b64=sim_b64,
        diff_heatmap_b64=diff_b64,
        reanalysis=reanalysis_report
    )
