from pathlib import Path
import os

from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = "VeriSight Forensics Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    SAMPLES_DIR: Path = BASE_DIR / "samples"
    REPORTS_DIR: Path = Path("/tmp/verisight/reports") if os.getenv("VERCEL") else BASE_DIR / "reports"

    # File limits
    MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS: set = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    # Forensic Thresholds
    ELA_DYNAMIC_GAIN: int = 18
    ELA_Z_SCORE_THRESHOLD: float = 2.6
    BASELINE_DRIFT_THRESHOLD_PX: float = 3.2
    CIELAB_DELTA_E_THRESHOLD: float = 2.4
    SHARPNESS_Z_THRESHOLD: float = 2.1
    COPY_MOVE_MIN_VECTORS: int = 4
    CROSS_LAYER_SYNERGY_MULTIPLIER: float = 1.35

    # CORS
    CORS_ORIGINS: list[str] = [x.strip() for x in os.environ.get("VERISIGHT_CORS_ORIGINS", "http://127.0.0.1:5175,http://localhost:5175,http://127.0.0.1:5174,http://localhost:5174").split(",") if x.strip()]

settings = Settings()

# Ensure directories exist
if not os.getenv("VERCEL"):
    settings.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
