import asyncio
import threading
import socket
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.schemas import (
    BenchmarkRunResponse,
    DemoSampleMeta,
    ForensicAnalysisReport,
    ModelStatusResponse,
    WhatsAppSimulationResponse,
)
from app.services.forensic.ensemble.ml_calibrated_service import ml_calibrated_service
from app.services.forensic.pipeline import analyze_screenshot
from app.simulation.whatsapp_pipeline import run_whatsapp_simulation

router = APIRouter()
_WORKERS = threading.BoundedSemaphore(2)

def run_bounded(function, *args, **kwargs):
    if not _WORKERS.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Analysis capacity is busy. Retry shortly.")
    try:
        return function(*args, **kwargs)
    finally:
        _WORKERS.release()


CASE_CATALOG = {
 "sample_clean": ("sample_1_synthetic_backup.png", "Clean synthetic base", "Project-generated reference receipt; not a real payment."),
 "sample_1": ("sample_1_authentic_gpay.png", "Imported receipt — unverified", "Imported file with undocumented provenance and consent. Not an authenticity ground truth."),
 "sample_2": ("sample_2_spliced_amount.jpg", "Synthetic amount edit", "Controlled patch and baseline edit for inspection; not a measured detector accuracy test."),
 "sample_3": ("sample_3_fake_generator_paradox.png", "Synthetic metadata conflict", "User-controlled timestamp and reference fields; geometry does not recognize visible text."),
 "sample_4": ("sample_4_whatsapp_laundered.jpg", "Recompressed synthetic edit", "Messaging-style JPEG transformation of the edited fixture."),
 "sample_5": ("sample_5_cloned_chat_receipt.jpg", "Synthetic copy-move", "Repeated regions and crop for reviewing ORB candidates."),
}

async def read_image(file):
    content = await file.read(settings.MAX_FILE_SIZE_BYTES + 1)
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 20 MB limit.")
    if not content:
        raise HTTPException(status_code=400, detail="Image is empty.")
    if Path(file.filename or "").suffix.lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Supported images: PNG, JPEG, WebP, BMP.")
    return content



@router.get("/health")
async def health_check():
    """Health and readiness endpoint."""
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "database": "NOT_CONFIGURED",
        "capabilities": {"heuristic_analysis": True, "ocr": False, "ai_origin": False, "payment_status": False, "server_transcription": False, "secure_mobile_intake": False},
        "active_layers": ["L1_Signal", "L2_Typography_Geometry", "L3_Metadata_Protocol", "L4_Ensemble_Synergy"]
    }

@router.get("/model/status", response_model=ModelStatusResponse)
async def get_model_status():
    return ModelStatusResponse(active_model_id="heuristic-review-v2", active_model_version="2.0.0",
        architecture="Deterministic image and metadata cues", calibration_status="UNAVAILABLE",
        promotion_status="RESEARCH_ONLY", available_models=[], ml_environment_ready=False)

@router.get("/model/evaluation")
async def get_model_evaluation():
    return {"status": "UNAVAILABLE", "message": "No authorized representative evaluation corpus with verified source-group isolation is available. Historical synthetic results are not real-world accuracy.",
            "models": {}, "roc_evaluation": {}, "confidence_available": False,
            "release_gate": "BLOCK", "block_reasons": ["Representative validation unavailable", "Group leakage not ruled out", "Threshold and calibration not validated"]}

@router.post("/benchmark/run")
async def run_benchmark():
    raise HTTPException(status_code=409, detail="No validated benchmark is configured. Stored JSON is not a new benchmark run.")

@router.get("/benchmark/results")
async def get_benchmark_results():
    return await get_model_evaluation()

@router.get("/network-info")
async def get_network_info():
    raise HTTPException(status_code=503, detail="Remote mobile intake is not configured.")

@router.get("/demo-samples", response_model=list[DemoSampleMeta])
async def get_demo_samples():
    return [DemoSampleMeta(id=k, filename=v[0], title=v[1], scenario=v[2],
        expected_verdict="UNSPECIFIED", target_score_range="Not an accuracy benchmark",
        description=v[2], tags=["Unverified source" if k == "sample_1" else "Synthetic fixture"], url=f"/samples/{v[0]}") for k,v in CASE_CATALOG.items()]

@lru_cache(maxsize=10)
def _cached_demo_analysis(filename: str, mtime_ns: int, path_str: str) -> ForensicAnalysisReport:
    """Caches forensic analysis of static demo fixtures so CPU isn't thrashing on repeated clicks."""
    with open(path_str, "rb") as f:
        content = f.read()
    return analyze_screenshot(content, filename=filename)


@router.post("/analyze", response_model=ForensicAnalysisReport)
async def analyze_upload(file: UploadFile = File(...)):
    """Upload and run full 4-layer forensic investigation on any screenshot (non-blocking threadpool execution)."""
    content = await read_image(file)

    try:
        report = await asyncio.to_thread(run_bounded, analyze_screenshot, content, filename=file.filename or "upload.png")
        return report
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/analyze-sample", response_model=ForensicAnalysisReport)
async def analyze_sample(sample_id: str = Form(...)):
    """Instantly executes the 4-layer pipeline against a golden demo sample via form body."""
    return await execute_sample_analysis(sample_id)

@router.post("/analyze-sample/{sample_id}", response_model=ForensicAnalysisReport)
async def analyze_sample_path(sample_id: str):
    """Instantly executes the 4-layer pipeline against a golden demo sample via path parameter."""
    return await execute_sample_analysis(sample_id)

async def execute_sample_analysis(sample_id: str) -> ForensicAnalysisReport:
    record = CASE_CATALOG.get(sample_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Unknown sample ID.")
    filename = record[0]
    sample_path = settings.SAMPLES_DIR / filename
    if not sample_path.is_file():
        raise HTTPException(status_code=404, detail="Fixture image is missing; no substitute was loaded.")

    mtime_ns = sample_path.stat().st_mtime_ns
    report = await asyncio.to_thread(run_bounded, _cached_demo_analysis, filename, mtime_ns, str(sample_path))
    return report.model_copy(update={"timestamp": datetime.now().isoformat(), "case_id": sample_id, "sample_id": sample_id, "source_kind": "IMPORTED_UNVERIFIED" if sample_id == "sample_1" else "SYNTHETIC_FIXTURE"})

@router.post("/simulate-whatsapp", response_model=WhatsAppSimulationResponse)
async def simulate_whatsapp(file: UploadFile = File(...)):
    """Simulates WhatsApp laundering on an uploaded image and returns before vs after comparison."""
    content = await read_image(file)
    try:
        sim_response = await asyncio.to_thread(run_bounded, run_whatsapp_simulation, content, filename=file.filename or "image.png")
        return sim_response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/mobile-upload")
@router.post("/upload-session")
@router.get("/latest-mobile-upload")
async def unavailable_mobile_intake():
    raise HTTPException(status_code=503, detail="Secure mobile intake requires configured private storage and isolated sessions. Upload directly in the workbench.")
