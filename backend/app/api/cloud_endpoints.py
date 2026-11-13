"""Retained repository signed-upload/mobile/storage interfaces."""
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

from app.services.artifacts import delivery_report, store

from fastapi.responses import Response

from app.services.mobile_upload_store import (
    ALLOWED_UPLOAD_TYPES,
    consume_mobile_upload,
    create_signed_upload,
    save_mobile_image,
)

router = APIRouter()

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
        return delivery_report(report)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="The uploaded screenshot could not be retrieved or analyzed. Please try again with a PNG, JPG, WebP, or BMP file.",
        ) from exc

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
    await save_case(report, "mobile_upload")
    _MOBILE_UPLOADS[str(session_id)] = {
        "received_at": monotonic(),
        "session_id": str(session_id) if session_id else None,
        "filename": file.filename or "mobile_upload.jpg",
        "timestamp": report.timestamp,
        "report": delivery_report(report).model_dump()
    }

    return {"status": "SUCCESS", "message": "Screenshot uploaded and analyzed.", "verdict": report.verdict, "analysis_gate": report.analysis_gate.model_dump()}

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
        return {"report": delivery_report(report)}

    if session_id is None:
        return {"report": None}
    data = _MOBILE_UPLOADS.pop(str(session_id), None)
    if data and monotonic() - data["received_at"] > 600:
        data = None
    return {"report": delivery_report(data.get("report")) if data else None}

@router.get("/artifacts/{token}")
def get_artifact(token: str):
    artifact = store.get(token)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Preview expired or unavailable. Run the analysis again.")
    content, media_type = artifact
    return Response(content, media_type=media_type, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})

@router.get("/operating-envelope")
async def operating_envelope():
    return {
        "status": "PRIVATE_DEVELOPMENT_PROTOTYPE", "validated_public_service": False,
        "max_file_bytes": settings.MAX_FILE_SIZE_BYTES, "max_pixels": 2_000_000,
        "max_side_pixels": 3200, "max_concurrent_analyses_per_process": 2,
        "supported_workers": 1, "preview_ttl_seconds": 600,
        "preview_store_budget_bytes": store.budget, "max_local_preview_bytes": 6_500_000,
        "preview_delivery": "inline_bounded" if os.getenv("VERCEL") else "private_capability_urls",
        "memory_limit_guaranteed": False, "real_world_accuracy": None,
        "settlement_verification": "NOT_INTEGRATED",
    }
