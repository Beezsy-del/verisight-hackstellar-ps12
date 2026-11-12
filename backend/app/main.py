import asyncio
import contextlib
import sys
import os
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
from fastapi.responses import FileResponse, JSONResponse
from app.services.image_validation import InvalidImage, ImageTooLarge
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.endpoints import router as api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.artifacts import store
    async def sweep():
        while True:
            await asyncio.sleep(30)
            store.cleanup()
            from app.api.endpoints import _MOBILE_UPLOADS
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
    description="Multi-layer screenshot forensic review using heuristic image cues",
    lifespan=lifespan
)

@app.exception_handler(InvalidImage)
async def invalid_image_handler(request, exc):
    return JSONResponse(status_code=413 if isinstance(exc, ImageTooLarge) else 422,
                        content={"detail": str(exc)})

from app.services.resource_boundary import AnalysisBoundary
app.add_middleware(AnalysisBoundary, capacity=2, response_budget=4_000_000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.services.private_access import PrivateAccess
app.add_middleware(PrivateAccess)

# Mount samples static directory
if not settings.SAMPLES_DIR.exists():
    raise RuntimeError(f"Packaged sample directory is missing: {settings.SAMPLES_DIR}")
app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

# Mount API router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Serve the built Vite SPA from the same FastAPI origin in production.
frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    @app.get("/workbench", include_in_schema=False)
    async def workbench_page():
        return FileResponse(frontend_dist / "index.html")

    @app.get("/evaluation", include_in_schema=False)
    async def evaluation_page():
        return FileResponse(frontend_dist / "index.html")

    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
