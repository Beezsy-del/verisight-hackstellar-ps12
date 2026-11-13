import asyncio
import contextlib
from app.services.image_validation import InvalidImage, ImageTooLarge
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add parent directory to sys.path so 'app' and 'samples' imports work seamlessly
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from samples.generator import generate_all_samples

from app.api.endpoints import router as api_router
from app.api.response_endpoints import router as response_router
from app.api.cloud_endpoints import router as cloud_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.artifacts import store
    async def sweep():
        while True:
            await asyncio.sleep(30)
            store.cleanup()
            from app.api.cloud_endpoints import _MOBILE_UPLOADS
            from time import monotonic
            for key, item in list(_MOBILE_UPLOADS.items()):
                if monotonic() - item["received_at"] > 600:
                    _MOBILE_UPLOADS.pop(key, None)
            if os.getenv("SUPABASE_SERVICE_ROLE_KEY") and os.getenv("SUPABASE_URL"):
                from app.services.supabase_store import expire_private_cases
                await expire_private_cases()
            if os.getenv("SUPABASE_SERVICE_ROLE_KEY") and os.getenv("SUPABASE_URL"):
                from app.services.mobile_upload_store import _cleanup_expired
                await asyncio.to_thread(_cleanup_expired, os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    cleanup = asyncio.create_task(sweep())
    try:
        if not os.getenv("VERCEL") and not any(settings.SAMPLES_DIR.glob("sample_*")):
            from samples.generator import generate_all_samples
            generate_all_samples()
        yield
    finally:
        cleanup.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cleanup
        store.clear()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multi-Layer Digital Screenshot Verification & Tamper Forensics Platform",
    lifespan=lifespan
)

@app.exception_handler(InvalidImage)
async def invalid_image_handler(request, exc):
    return JSONResponse(status_code=413 if isinstance(exc, ImageTooLarge) else 422,
                        content={"detail": str(exc)})

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.services.private_access import PrivateAccess
from app.services.resource_boundary import AnalysisBoundary
import os
app.add_middleware(AnalysisBoundary, capacity=2, response_budget=4_000_000 if os.getenv("VERCEL") else 16_000_000)
app.add_middleware(PrivateAccess)

# Mount samples static directory

app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

# Mount API router
app.include_router(api_router, prefix="/api")
app.include_router(response_router, prefix="/api")
app.include_router(cloud_router, prefix="/api")

# Reject cross-origin mutations even from non-browser clients; CORS alone is not CSRF protection.
@app.middleware("http")
async def origin_guard(request, call_next):
    origin = request.headers.get("origin")
    if request.method not in {"GET", "HEAD", "OPTIONS"} and origin:
        expected = str(request.base_url).rstrip("/")
        if origin != expected and origin not in settings.CORS_ORIGINS:
            return JSONResponse({"detail": "Origin is not permitted."}, status_code=403)
    return await call_next(request)

frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.is_dir():
    @app.get("/workbench", include_in_schema=False)
    @app.get("/evaluation", include_in_schema=False)
    @app.get("/response", include_in_schema=False)
    @app.get("/guide", include_in_schema=False)
    @app.get("/why-verisight", include_in_schema=False)
    async def spa_page():
        return FileResponse(frontend_dist / "index.html")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
