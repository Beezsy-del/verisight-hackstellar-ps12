import socket
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from uuid import UUID, uuid4
from urllib.parse import quote, urlsplit
from typing import Any
from time import monotonic
from starlette.concurrency import run_in_threadpool
from app.services.image_validation import decode_image, InvalidImage, ImageTooLarge

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.evaluation.readiness import release_readiness, evidence_sources
from app.core.schemas import (
    DemoSampleMeta,
    ForensicAnalysisReport,
    WhatsAppSimulationResponse,
)
from app.services.supabase_store import database_status, save_case
from app.services.mobile_upload_store import (
    ALLOWED_UPLOAD_TYPES,
    consume_mobile_upload,
    create_signed_upload,
    save_mobile_image,
)

router = APIRouter()

# In-memory storage for latest mobile upload (for stage judge real-time sync)
_MOBILE_UPLOADS: dict[str, dict[str, Any]] = {}

async def read_image_upload(file: UploadFile) -> bytes:
    content = await file.read(settings.MAX_FILE_SIZE_BYTES + 1)
    await run_in_threadpool(decode_image, content)
    return content



class UploadSessionRequest(BaseModel):
    filename: str
    content_type: str
    size: int
    session_id: UUID | None = None


@router.post("/upload-session")
async def create_upload_session(payload: UploadSessionRequest):
    """Issue a one-file, signed Storage upload so large phone files avoid function body limits."""
    if payload.size < 1 or payload.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Choose an image smaller than 20 MB.")
    content_type = payload.content_type.split(";", 1)[0].strip().lower()
    if content_type not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(status_code=415, detail="Use a PNG, JPG, WebP, or BMP screenshot.")

    session_id = payload.session_id or uuid4()
    try:
        upload = await create_signed_upload(session_id, payload.filename)
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        if not supabase_url:
            raise RuntimeError("Supabase Storage is not configured")
        upload_url = (
            f"{supabase_url}/storage/v1/object/upload/sign/mobile-evidence/"
            f"{quote(upload['path'], safe='/')}?token={quote(upload['token'])}"
        )
        public_storage_key = os.getenv("SUPABASE_ANON_KEY", "")
        if not public_storage_key:
            raise RuntimeError("Supabase public storage key is not configured")
        return {
            "session_id": str(session_id),
            "upload_url": upload_url,
            "storage_key": public_storage_key,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Secure screenshot upload is temporarily unavailable. Please try again.",
        ) from exc


@router.post("/analyze-upload-session/{session_id}", response_model=ForensicAnalysisReport)
async def analyze_upload_session(session_id: UUID):
    """Analyze a screenshot already placed in private Storage, then consume and delete it."""
    try:
        report = await consume_mobile_upload(session_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Screenshot upload was not found or was already used.")
        return report
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="The uploaded screenshot could not be retrieved or analyzed. Please try again with a PNG, JPG, WebP, or BMP file.",
        ) from exc

@router.get("/health")
async def health_check():
    """Health and readiness endpoint."""
    return {
        "status": "HEALTHY",
        "database": await database_status(),
        "upload_mode": "signed" if os.getenv("VERCEL") else "direct",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "active_layers": ["L1_Signal_Heuristics", "L2_Geometry_Heuristics", "L3_Metadata_QR", "L4_Evidence_Review"]
    }


@router.get("/model/status")
async def model_status():
    """Describe the deployed analyzer without implying a trained model is active."""
    return {
        "status": "HEURISTIC_ONLY",
        "active_model_id": None,
        "active_model_version": None,
        "architecture": "Deterministic four-layer forensic heuristics",
        "calibration_status": "NOT_CALIBRATED",
        "promotion_status": "NO_TRAINED_MODEL",
        "available_models": [],
        "ml_environment_ready": False,
        "release_gate": release_readiness(),
        "evidence_sources": evidence_sources(),
        "message": "No trained or calibrated classifier is deployed. Results are review cues, not authenticity probabilities.",
    }


@router.get("/model/evaluation")
async def model_evaluation():
    """Return only evaluation facts supported by the bundled synthetic fixtures."""
    return {
        "status": "NOT_EVALUATED",
        "dataset_summary": {
            "total_samples": 5,
            "synthetic_fixtures": 5,
            "independent_authentic_references": 0,
            "independent_manipulated_references": 0,
            "held_out_test_samples": 0,
        },
        "metrics": None,
        "release_gate": release_readiness(),
        "test_set_locked": False,
        "baseline_comparison": None,
        "message": "No representative labeled dataset or held-out evaluation is configured. Accuracy, ROC-AUC, and calibrated confidence are unavailable.",
    }

@router.get("/network-info")
async def get_network_info(request: Request):
    """
    Auto-detects the host machine's local LAN IP address for the Stage Judge Mobile Upload QR code.
    """
    local_ip = "127.0.0.1"
    try:
        # Create a UDP socket to discover the primary outbound interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            local_ip = "127.0.0.1"

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    if not origin and referer:
        parsed = urlsplit(referer)
        if parsed.scheme and parsed.netloc:
            origin = f"{parsed.scheme}://{parsed.netloc}"
    if not origin:
        forwarded_host = request.headers.get("x-forwarded-host")
        forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = forwarded_host or request.headers.get("host", f"{local_ip}:5174")
        origin = f"{forwarded_proto}://{host}"

    parsed_origin = urlsplit(origin)
    if not os.getenv("VERCEL") and parsed_origin.hostname in {"localhost", "127.0.0.1", "::1"}:
        port = parsed_origin.port or 8101
        origin = f"http://{local_ip}:{port}"
    qr_url = f"{origin}/?mode=mobile"

    return {
        "local_ip": local_ip,
        "frontend_port": 5174,
        "backend_port": 8101,
        "mobile_upload_url": qr_url
    }

@router.get("/demo-samples", response_model=list[DemoSampleMeta])
async def get_demo_samples():
    """Returns the 5 synthetic regression fixtures and metadata."""
    samples = [
        DemoSampleMeta(
            id="sample_1",
            filename="sample_1_clean_synthetic_ui.png",
            title="Sample 1 — Clean Synthetic Payment UI (₹1,250.00)",
            scenario="Synthetic clean baseline used to demonstrate low anomaly indicators; it is not a genuine bank or payment receipt.",
            expected_verdict="REVIEW_REQUIRED",
            target_score_range="Variable heuristic points",
            description="Clean synthetic fixture with no corroborated manipulation indicators. The result does not verify a real payment or origin.",
            tags=["Clean Baseline", "Synthetic", "UPI-style", "Aligned"],
            url="/samples/sample_1_clean_synthetic_ui.png"
        ),
        DemoSampleMeta(
            id="sample_2",
            filename="sample_2_spliced_amount.jpg",
            title="Sample 2 — Synthetic Edited Amount (₹95,250.00)",
            scenario="A known amount alteration in a synthetic fixture. The geometry and residual cues are heuristic; no localized overlap is produced.",
            expected_verdict="REVIEW_REQUIRED",
            target_score_range="Variable heuristic points",
            description="Synthetic fixture with an edited amount. The review score is a heuristic and does not prove the alteration was detected.",
            tags=["Synthetic edit", "Review cue", "Baseline geometry"],
            url="/samples/sample_2_spliced_amount.jpg"
        ),
        DemoSampleMeta(
            id="sample_3",
            filename="sample_3_fake_generator_paradox.png",
            title="Sample 3 — Synthetic Metadata Conflict Fixture",
            scenario="Generated PNG metadata contains a clock mismatch (11:12 vs 11:45 AM) and a short reference example.",
            expected_verdict="REVIEW_REQUIRED",
            target_score_range="Variable heuristic points",
            description="Synthetic fixture with embedded metadata rule cues. These values are not OCR-verified or checked against a bank.",
            tags=["Synthetic", "Metadata Rule Cues", "Not OCR-Verified"],
            url="/samples/sample_3_fake_generator_paradox.png"
        ),
        DemoSampleMeta(
            id="sample_4",
            filename="sample_4_synthetic_jpeg_reencode.jpg",
            title="Sample 4 — Synthetic JPEG Re-encode",
            scenario="Synthetic edited fixture re-encoded as JPEG (Q=77); its file profile does not identify an app or source.",
            expected_verdict="REVIEW_REQUIRED",
            target_score_range="Variable heuristic points",
            description="Synthetic edited fixture re-encoded as JPEG. The source app cannot be identified from its file profile.",
            tags=["Synthetic", "JPEG re-encode", "Source unknown"],
            url="/samples/sample_4_synthetic_jpeg_reencode.jpg"
        ),
        DemoSampleMeta(
            id="sample_5",
            filename="sample_5_cloned_chat_receipt.jpg",
            title="Sample 5 — Synthetic Repeated-Region Fixture",
            scenario="Digit sequence cloned to inflate balance; non-native cropped viewport (680x1120).",
            expected_verdict="REVIEW_REQUIRED",
            target_score_range="Variable heuristic points",
            description="Synthetic cloned-region fixture. Copy-move matching is a review cue and can match repeated interface elements.",
            tags=["Repeated regions", "ORB candidate matches", "Unlisted aspect ratio"],
            url="/samples/sample_5_cloned_chat_receipt.jpg"
        )
    ]
    return samples

@router.post("/analyze", response_model=ForensicAnalysisReport)
async def analyze_upload(file: UploadFile = File(...)):
    """Upload and run full 4-layer forensic investigation on any screenshot."""
    content = await read_image_upload(file)
    
    try:
        from app.services.forensic.pipeline import analyze_screenshot
        report = await run_in_threadpool(analyze_screenshot, content, filename=file.filename or "upload.png")
        await save_case(report, "upload")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail="Screenshot analysis failed. Please try another image.")

@router.post("/analyze-sample", response_model=ForensicAnalysisReport)
async def analyze_sample(background_tasks: BackgroundTasks, sample_id: str = Form(...)):
    """Run the heuristic pipeline against a synthetic fixture via form body."""
    return await execute_sample_analysis(sample_id, background_tasks)

@router.post("/analyze-sample/{sample_id}", response_model=ForensicAnalysisReport)
async def analyze_sample_path(sample_id: str, background_tasks: BackgroundTasks):
    """Run the heuristic pipeline against a synthetic fixture via path parameter."""
    return await execute_sample_analysis(sample_id, background_tasks)

async def execute_sample_analysis(
    sample_id: str,
    background_tasks: BackgroundTasks | None = None,
) -> ForensicAnalysisReport:
    sample_files = {
        "sample_1": "sample_1_clean_synthetic_ui.png",
        "sample_2": "sample_2_spliced_amount.jpg",
        "sample_3": "sample_3_fake_generator_paradox.png",
        "sample_4": "sample_4_synthetic_jpeg_reencode.jpg",
        "sample_5": "sample_5_cloned_chat_receipt.jpg"
    }
    filename = sample_files.get(sample_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Unknown sample ID.")

    sample_path = settings.SAMPLES_DIR / filename
    if not sample_path.exists():
        from samples.generator import generate_all_samples
        generate_all_samples()

    from app.services.forensic.pipeline import analyze_screenshot
    report = await run_in_threadpool(_cached_demo_analysis, filename, sample_path.stat().st_mtime_ns, str(sample_path))
    report = report.model_copy(update={"timestamp": datetime.now().isoformat()})
    if background_tasks is not None:
        background_tasks.add_task(save_case, report, "synthetic_sample")
    else:
        await save_case(report, "synthetic_sample")
    return report


@lru_cache(maxsize=5)
def _cached_demo_analysis(filename: str, modified_ns: int, path: str) -> ForensicAnalysisReport:
    """Keep demo analyses warm in a reused serverless instance."""
    from app.services.forensic.pipeline import analyze_screenshot
    return analyze_screenshot(Path(path).read_bytes(), filename=filename)

@router.post("/simulate-whatsapp", response_model=WhatsAppSimulationResponse)
async def simulate_whatsapp(file: UploadFile = File(...)):
    """Simulates WhatsApp laundering on an uploaded image and returns before vs after comparison."""
    content = await read_image_upload(file)
    try:
        from app.simulation.whatsapp_pipeline import run_whatsapp_simulation
        sim_response = await run_in_threadpool(run_whatsapp_simulation, content, filename=file.filename or "image.png")
        return sim_response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Image simulation failed. Please try another image.")

@router.post("/mobile-upload")
async def mobile_upload(request: Request, file: UploadFile = File(...)):
    """
    Mobile upload route accessed by stage judges scanning the QR code on their phones.
    Pairs the upload to the desktop session; Vercel uses private Supabase Storage
    because serverless instances do not share in-memory state.
    """
    content = await read_image_upload(file)
    session_text = request.query_params.get("session_id")
    session_id: UUID | None = None
    if session_text:
        try:
            session_id = UUID(session_text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid mobile session.") from exc
    if session_id is None:
        raise HTTPException(status_code=400, detail="Open this upload page from the desktop QR code.")

    # Local development keeps the existing in-memory handoff. Production
    # stores the image privately until the paired desktop retrieves it.
    if os.getenv("VERCEL"):
        stored = await save_mobile_image(session_id, file.filename or "mobile_upload.jpg", content)
        if not stored:
            raise HTTPException(status_code=503, detail="Could not queue the upload for the desktop session.")
        return {"status": "SUCCESS", "message": "Screenshot queued for the paired desktop workbench."}

    from app.services.forensic.pipeline import analyze_screenshot
    report = await run_in_threadpool(analyze_screenshot, content, filename=file.filename or "mobile_upload.jpg")

    for key, item in list(_MOBILE_UPLOADS.items()):
        if monotonic() - item["received_at"] > 600:
            _MOBILE_UPLOADS.pop(key, None)
    if len(_MOBILE_UPLOADS) >= 32:
        _MOBILE_UPLOADS.pop(next(iter(_MOBILE_UPLOADS)))
    _MOBILE_UPLOADS[str(session_id)] = {
        "received_at": monotonic(),
        "session_id": str(session_id) if session_id else None,
        "filename": file.filename or "mobile_upload.jpg",
        "timestamp": report.timestamp,
        "report": report.model_dump()
    }
    await save_case(report, "mobile_upload")

    return {"status": "SUCCESS", "message": "Screenshot uploaded and analyzed.", "verdict": report.verdict}

@router.get("/latest-mobile-upload")
async def get_latest_mobile_upload(clear: bool = False, session_id: UUID | None = None):
    """
    Desktop workbench polling endpoint. Returns the upload paired to this session.
    """
    if os.getenv("VERCEL"):
        if session_id is None:
            return {"report": None}
        try:
            report = await consume_mobile_upload(session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Could not retrieve the mobile upload.") from e
        return {"report": report}

    if session_id is None:
        return {"report": None}
    data = _MOBILE_UPLOADS.pop(str(session_id), None)
    if data and monotonic() - data["received_at"] > 600:
        data = None
    return {"report": data.get("report") if data else None}
