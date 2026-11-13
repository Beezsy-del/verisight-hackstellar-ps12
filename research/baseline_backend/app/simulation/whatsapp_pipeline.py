import base64
import io

import cv2
import numpy as np
from PIL import Image

from app.core.schemas import WhatsAppSimulationResponse
from app.services.forensic.pipeline import analyze_screenshot


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

    # 1. Process via PIL
    with Image.open(io.BytesIO(image_bytes)) as pil_img:
        pil_img = pil_img.convert('RGB')
        w_orig, h_orig = pil_img.size

        # Clamp long edge to 1600px
        max_edge = max(w_orig, h_orig)
        if max_edge > 1600:
            scale = 1600.0 / max_edge
            new_w = int(round(w_orig * scale))
            new_h = int(round(h_orig * scale))
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            new_w, new_h = w_orig, h_orig

        out_buf = io.BytesIO()
        pil_img.save(
            out_buf,
            format='JPEG',
            quality=77,
            subsampling=2,  # 4:2:0 subsampling
            optimize=True
        )
        simulated_bytes = out_buf.getvalue()

    sim_size = len(simulated_bytes)
    comp_ratio = round(float(orig_size) / max(1, sim_size), 2)

    # Decode simulated image
    np_sim = np.frombuffer(simulated_bytes, np.uint8)
    sim_bgr = cv2.imdecode(np_sim, cv2.IMREAD_COLOR)

    # Decode original image for diff
    np_orig = np.frombuffer(image_bytes, np.uint8)
    orig_bgr = cv2.imdecode(np_orig, cv2.IMREAD_COLOR)

    # Match sizes for diff if resized
    if orig_bgr.shape[:2] != sim_bgr.shape[:2]:
        orig_resized = cv2.resize(orig_bgr, (new_w, new_h))
    else:
        orig_resized = orig_bgr

    diff = cv2.absdiff(orig_resized, sim_bgr)
    diff_amplified = np.clip(diff * 12, 0, 255).astype(np.uint8)
    diff_colormap = cv2.applyColorMap(cv2.cvtColor(diff_amplified, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_JET)

    _, diff_png = cv2.imencode('.png', diff_colormap)
    diff_b64 = f"data:image/png;base64,{base64.b64encode(diff_png.tobytes()).decode('utf-8')}"

    sim_b64 = f"data:image/jpeg;base64,{base64.b64encode(simulated_bytes).decode('utf-8')}"

    # Re-analyze laundered image
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
