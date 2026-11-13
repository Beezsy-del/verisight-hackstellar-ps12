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
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multi-Layer Digital Screenshot Verification & Tamper Forensics Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount samples static directory

app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

# Mount API router
app.include_router(api_router, prefix="/api")
app.include_router(response_router, prefix="/api")

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
