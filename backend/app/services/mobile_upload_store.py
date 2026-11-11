"""Private, short-lived storage for mobile-to-desktop handoff on serverless."""
import asyncio
import json
import logging
import os
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from uuid import UUID
from starlette.concurrency import run_in_threadpool

from app.services.supabase_store import save_case

log = logging.getLogger(__name__)
BUCKET = "mobile-evidence"
ALLOWED_UPLOAD_TYPES = {"image/png", "image/jpeg", "image/webp", "image/bmp"}


def _credentials() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        raise RuntimeError("Supabase mobile storage is not configured")
    return url, key


def _request(path: str, key: str, method: str = "GET", body: bytes | None = None,
             content_type: str | None = None, prefer: str | None = None,
             extra_headers: dict[str, str] | None = None) -> bytes:
    url, _ = _credentials()
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    if content_type:
        headers["Content-Type"] = content_type
    if prefer:
        headers["Prefer"] = prefer
    if extra_headers:
        headers.update(extra_headers)
    request = Request(f"{url}{path}", data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            return response.read()
    except HTTPError as exc:
        # Storage's response body identifies path, auth, and object-state errors;
        # include it in server logs while keeping public API errors generic.
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        exc.storage_detail = detail
        log.warning("Supabase Storage %s failed for %s: HTTP %s %s", method, path, exc.code, detail)
        raise


async def save_mobile_image(session_id: UUID, filename: str, content: bytes) -> bool:
    """Queue one private image for the desktop paired to this QR session."""
    try:
        def save() -> None:
            _, key = _credentials()
            _cleanup_expired(key)
            path = f"{session_id}/evidence"
            encoded_path = quote(path, safe="/")
            _request(
                f"/storage/v1/object/{BUCKET}/{encoded_path}", key, "POST", content,
                Image.MIME[Image.open(BytesIO(content)).format], extra_headers={"x-upsert": "true"},
            )
            row = {
                "session_id": str(session_id),
                "filename": (filename.rsplit("/", 1)[-1] or "mobile_upload")[:255],
                "storage_path": path,
                "consumed_at": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            _request(
                "/rest/v1/mobile_uploads?on_conflict=session_id", key, "POST",
                json.dumps(row).encode(), "application/json", "resolution=merge-duplicates,return=minimal",
            )
        await asyncio.to_thread(save)
        return True
    except Exception:
        log.exception("Could not queue private mobile evidence")
        return False


async def create_signed_upload(session_id: UUID, filename: str) -> dict:
    """Create a short-lived, one-object upload token so browsers bypass Vercel's body limit."""
    safe_name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1][:255] or "screenshot.png"
    path = f"{session_id}/evidence"

    def create() -> dict:
        _, key = _credentials()
        _cleanup_expired(key)
        encoded_path = quote(path, safe="/")
        signed = json.loads(_request(
            f"/storage/v1/object/upload/sign/{BUCKET}/{encoded_path}", key, "POST",
            b"{}", "application/json",
        ))
        row = {
            "session_id": str(session_id),
            "filename": safe_name,
            "storage_path": path,
            "consumed_at": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _request(
            "/rest/v1/mobile_uploads?on_conflict=session_id", key, "POST",
            json.dumps(row).encode(), "application/json", "resolution=merge-duplicates,return=minimal",
        )
        return {"path": path, "token": signed["token"]}

    return await asyncio.to_thread(create)


async def delete_mobile_image(session_id: UUID) -> None:
    """Remove the private image after the paired desktop has retrieved it."""
    try:
        def delete() -> None:
            _, key = _credentials()
            path = quote(f"{session_id}/evidence", safe="/")
            _request(f"/storage/v1/object/{BUCKET}/{path}", key, "DELETE")
        await asyncio.to_thread(delete)
    except HTTPError as exc:
        if exc.code != 404:
            log.warning("Could not remove consumed mobile evidence: HTTP %s", exc.code)
    except Exception:
        log.exception("Could not remove consumed mobile evidence")


async def consume_mobile_upload(session_id: UUID) -> dict | None:
    """Read and analyze one queued image, then mark the handoff as consumed."""
    try:
        def fetch() -> tuple[dict | None, bytes | None]:
            _, key = _credentials()
            query = urlencode({
                "session_id": f"eq.{session_id}",
                "consumed_at": "is.null",
                "select": "session_id,filename,storage_path",
                "limit": "1",
                "created_at": "gt." + (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            })
            rows = json.loads(_request(f"/rest/v1/mobile_uploads?{query}", key))
            if not rows:
                return None, None
            row = rows[0]
            object_path = quote(row["storage_path"], safe="/")
            try:
                image = _request(f"/storage/v1/object/{BUCKET}/{object_path}", key)
            except HTTPError as exc:
                # Desktop polling often arrives before the signed upload finishes.
                if exc.code == 404 or (exc.code == 400 and "not found" in getattr(exc, "storage_detail", "").lower()):
                    return None, None
                raise
            return row, image

        row, content = await asyncio.to_thread(fetch)
        if not row or content is None:
            return None

        def claim() -> bool:
            _, key = _credentials()
            query = urlencode({"session_id": f"eq.{session_id}", "consumed_at": "is.null"})
            body = json.dumps({"consumed_at": datetime.now(timezone.utc).isoformat()}).encode()
            rows = json.loads(_request(f"/rest/v1/mobile_uploads?{query}", key, "PATCH", body,
                                       "application/json", "return=representation"))
            return len(rows) == 1

        # The conditional UPDATE is atomic in PostgreSQL. Only its winner may
        # analyze, persist, or delete the object; concurrent polls return empty.
        if not await asyncio.to_thread(claim):
            return None
        try:
            from app.services.forensic.pipeline import analyze_screenshot
            report = await run_in_threadpool(analyze_screenshot, content, filename=row["filename"])
            await save_case(report, "mobile_upload")
            return report.model_dump()
        finally:
            await delete_mobile_image(session_id)

    except Exception:
        log.exception("Could not consume mobile evidence session %s", session_id)
        raise


def _cleanup_expired(key: str) -> None:
    """Best-effort 24-hour cleanup for uploads whose desktop never polled."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    query = urlencode({
        "created_at": f"lt.{cutoff}",
        "select": "session_id,storage_path",
    })
    try:
        rows = json.loads(_request(f"/rest/v1/mobile_uploads?{query}", key))
        for row in rows:
            object_path = quote(row["storage_path"], safe="/")
            try:
                _request(f"/storage/v1/object/{BUCKET}/{object_path}", key, "DELETE")
            except HTTPError as exc:
                if exc.code != 404:
                    raise
        delete_query = urlencode({"created_at": f"lt.{cutoff}"})
        _request(f"/rest/v1/mobile_uploads?{delete_query}", key, "DELETE")
    except Exception:
        log.warning("Best-effort expired mobile upload cleanup failed", exc_info=True)
