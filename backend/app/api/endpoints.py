from app.evaluation.readiness import release_readiness, evidence_sources
import os
from app.services.supabase_store import database_status, save_case
from app.services.forensic.intelligence.media_cache import compact_report, get_media, store_extra_media
import asyncio
import threading
import socket
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request

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
from app.services.forensic.intelligence.robust_review import ocr_available
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
 "sample_1": ("sample_1_clean_synthetic_ui.png", "Original synthetic base", "Repository-generated reference receipt, not a real payment."),
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
        raise HTTPException(status_code=422, detail="Image is empty.")
    if Path(file.filename or "").suffix.lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Supported images: PNG, JPEG, WebP, BMP.")
    from app.services.image_validation import decode_image
    await asyncio.to_thread(decode_image, content)
    return content



@router.get("/health")
async def health_check():
    """Health and readiness endpoint."""
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "upload_mode": "signed" if os.getenv("VERCEL") else "direct",
        "database": await database_status(),
        "capabilities": {"heuristic_analysis": True, "ocr": ocr_available(), "ai_origin": False, "payment_status": False, "server_transcription": False, "secure_mobile_intake": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))},
        "active_layers": ["L1_Signal", "L2_Typography_Geometry", "L3_Metadata_Protocol", "L4_Ensemble_Synergy"]
    }

@router.get("/model/status", response_model=ModelStatusResponse)
async def get_model_status():
    return ModelStatusResponse(release_readiness=release_readiness(), evidence_sources=evidence_sources(), active_model_id="heuristic-review-v2", active_model_version="2.0.0",
        architecture="Deterministic image and metadata cues", calibration_status="UNAVAILABLE",
        promotion_status="RESEARCH_ONLY", available_models=[], ml_environment_ready=False)

@router.get("/model/evaluation")
async def get_model_evaluation():
    return {"release_readiness": release_readiness(), "metrics": None, "test_set_locked": False, "status": "UNAVAILABLE", "message": "No authorized representative evaluation corpus with verified source-group isolation is available. Historical synthetic results are not real-world accuracy.",
            "models": {}, "roc_evaluation": {}, "confidence_available": False,
            "release_gate": "BLOCK", "block_reasons": ["Representative validation unavailable", "Group leakage not ruled out", "Threshold and calibration not validated"]}

@router.post("/benchmark/run")
async def run_benchmark():
    raise HTTPException(status_code=409, detail="No validated benchmark is configured. Stored JSON is not a new benchmark run.")

@router.get("/benchmark/results")
async def get_benchmark_results():
    return await get_model_evaluation()

@router.get("/demo-samples", response_model=list[DemoSampleMeta])
async def get_demo_samples():
    return [DemoSampleMeta(id=k, filename=v[0], title=v[1], scenario=v[2],
        expected_verdict="UNSPECIFIED", target_score_range="Not an accuracy benchmark",
        description=v[2], tags=["Synthetic fixture"], url=f"/samples/{v[0]}") for k,v in CASE_CATALOG.items()]

@lru_cache(maxsize=10)
def _cached_demo_analysis(filename: str, mtime_ns: int, path_str: str) -> ForensicAnalysisReport:
    """Caches forensic analysis of static demo fixtures so CPU isn't thrashing on repeated clicks."""
    with open(path_str, "rb") as f:
        content = f.read()
    return analyze_screenshot(content, filename=filename)


@router.post("/analyze", response_model=ForensicAnalysisReport)
async def analyze_upload(request: Request, file: UploadFile = File(...)):
    """Upload and run full 4-layer forensic investigation on any screenshot (non-blocking threadpool execution)."""
    content = await read_image(file)

    try:
        report = await asyncio.to_thread(run_bounded, analyze_screenshot, content, filename=file.filename or "upload.png")
        await save_case(report, "upload")
        return compact_report(report, request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@router.post("/analyze-sample", response_model=ForensicAnalysisReport)
async def analyze_sample(request: Request, sample_id: str = Form(...)):
    """Instantly executes the 4-layer pipeline against a golden demo sample via form body."""
    return compact_report(await execute_sample_analysis(sample_id), request)

@router.post("/analyze-sample/{sample_id}", response_model=ForensicAnalysisReport)
async def analyze_sample_path(sample_id: str, request: Request):
    """Instantly executes the 4-layer pipeline against a golden demo sample via path parameter."""
    return compact_report(await execute_sample_analysis(sample_id), request)

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
    return report.model_copy(update={"timestamp": datetime.now().isoformat(), "case_id": sample_id, "sample_id": sample_id, "source_kind": "SYNTHETIC_FIXTURE"})

@router.post("/simulate-whatsapp", response_model=WhatsAppSimulationResponse)
async def simulate_whatsapp(request: Request, file: UploadFile = File(...)):
    """Simulates WhatsApp laundering on an uploaded image and returns before vs after comparison."""
    content = await read_image(file)
    try:
        sim_response = await asyncio.to_thread(run_bounded, run_whatsapp_simulation, content, filename=file.filename or "image.png")
        sim_response.reanalysis = compact_report(sim_response.reanalysis, request)
        sim_response.diff_heatmap_b64 = store_extra_media(sim_response.diff_heatmap_b64,request)
        sim_response.simulated_image_b64 = store_extra_media(sim_response.simulated_image_b64,request)
        return sim_response
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@router.get("/research/robustness")
async def robustness_research():
    """Only original synthetic per-image predictions; never user-upload history."""
    import json, hashlib
    folder=settings.BASE_DIR / "research" / "results"
    manifest=settings.BASE_DIR / "research" / "datasets" / "robustness" / "manifest.json"
    required=[folder/"robustness-summary.json",folder/"baseline-all.json",folder/"upgraded-all.json",manifest]
    if not all(p.is_file() for p in required):
        return {"status":"UNAVAILABLE","message":"Reproducible synthetic research artifacts are not installed in this environment."}
    summary,baseline,upgraded=[json.loads(p.read_text()) for p in required[:3]]
    digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
    if any(d.get("manifest_sha256")!=digest for d in [summary,baseline,upgraded]):
        raise HTTPException(status_code=409,detail="Research artifact manifest mismatch; rerun evaluation.")
    for name in ["baseline","upgraded"]:
        if summary.get("prediction_sha256",{}).get(name)!=hashlib.sha256((folder/(name+"-all.json")).read_bytes()).hexdigest():
            raise HTTPException(status_code=409,detail="Prediction checksum mismatch; do not display stale metrics.")
    rows=[]
    old={r["sample_id"]:r for r in baseline["rows"]}
    for r in upgraded["rows"]:
        if "error" in r or r["sample_id"] not in old:
            raise HTTPException(status_code=409,detail="Incomplete evaluation predictions.")
        rows.append({k:r[k] for k in ["sample_id","label","partition","delivery_path","source_group_id","pair_id"]}|{"baseline":old[r["sample_id"]]["score"],"operational":r["score"],"candidate":r["candidate_score"]})
    return {"status":"SYNTHETIC_ONLY","summary":summary,"predictions":rows,"release_gate":"BLOCK","candidate_decision":"REJECTED_FOR_PROMOTION: no matched-pair improvement"}


@router.get("/review-media/{token}")
async def review_media(token: str, request: Request):
    return get_media(token,request)
