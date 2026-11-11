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
    # Startup: ensure synthetic demo fixtures are available
    try:
        if os.getenv("VERCEL"):
            yield
            return
        if not any(settings.SAMPLES_DIR.glob("sample_*")):
            from samples.generator import generate_all_samples
            generate_all_samples()
    except Exception as e:
        print(f"[Startup Warning] Could not auto-generate samples: {e}")
    yield

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
