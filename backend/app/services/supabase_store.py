"""Server-only persistence for analysis summaries; never store uploaded image bytes."""
import logging
import os
import asyncio
import json
from urllib.request import Request, urlopen

log = logging.getLogger(__name__)

async def save_case(report, source: str = "web") -> bool:
    if os.getenv("VERISIGHT_PERSIST_CASES") != "1":
        report.persistence_status = "DISABLED"
        return False
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        report.persistence_status = "NOT_CONFIGURED"
        return False
    layer3_summary = report.layer3.model_dump(mode="json")
    qr_summary = layer3_summary.get("details", {}).get("qr_inspection")
    if isinstance(qr_summary, dict):
        qr_summary["results"] = []
        qr_summary["payloads_persisted"] = False
    row = {
        "file_sha256": report.file_sha256,
        "filename": (report.filename or "evidence image")[:255],
        "image_width": report.image_width,
        "image_height": report.image_height,
        "overall_tamper_score": report.overall_tamper_score,
        "confidence_score": report.confidence_score,
        "verdict": report.verdict,
        "channel_detected": report.channel_detected,
        "findings": [x.model_dump(mode="json") for x in report.findings if not x.id.startswith("f-qr-")],
        "layer_summary": {
            "retention_policy": "private-prototype-7d",
            "analysis_gate": report.analysis_gate.model_dump(mode="json"),
            "evidence_sources": report.evidence_sources,
            "visual_tamper_score": report.visual_tamper_score,
            "score_kind": report.score_kind,
            "layer1": report.layer1.model_dump(mode="json", exclude={"ela_b64", "wavelet_noise_b64", "clone_b64"}),
            "layer2": report.layer2.model_dump(mode="json"),
            "layer3": layer3_summary,
            "layer4": report.layer4.model_dump(mode="json"),
        },
        "source": source,
    }
    def send():
        request = Request(
            f"{url}/rest/v1/forensic_cases",
            data=json.dumps(row).encode(),
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=minimal"},
            method="POST",
        )
        with urlopen(request, timeout=8) as response:
            return 200 <= response.status < 300
    try:
        saved = await asyncio.to_thread(send)
        report.persistence_status = "SAVED" if saved else "FAILED"
        return saved
    except Exception:
        report.persistence_status = "FAILED"
        log.warning("Supabase forensic case persistence failed")
        return False


async def database_status() -> str:
    """Return a safe connectivity status without exposing credentials or rows."""
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return "NOT_CONFIGURED"

    def check() -> bool:
        request = Request(
            f"{url}/rest/v1/forensic_cases?select=id&limit=0",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        with urlopen(request, timeout=4) as response:
            return 200 <= response.status < 300

    try:
        return "HEALTHY" if await asyncio.to_thread(check) else "UNAVAILABLE"
    except Exception:
        log.warning("Supabase health check failed")
        return "UNAVAILABLE"


async def expire_private_cases() -> bool:
    """Delete only summaries written under this explicit seven-day policy."""
    from datetime import datetime, timedelta, timezone
    from urllib.parse import urlencode
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return False
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    query = urlencode({"created_at": "lt." + cutoff,
                       "layer_summary->>retention_policy": "eq.private-prototype-7d"})
    def delete():
        request = Request(f"{url}/rest/v1/forensic_cases?{query}", method="DELETE",
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "return=minimal"})
        with urlopen(request, timeout=8) as response:
            return 200 <= response.status < 300
    try:
        return await asyncio.to_thread(delete)
    except Exception:
        log.warning("Private summary retention sweep failed")
        return False
