#!/usr/bin/env python3
"""Compatibility launcher: serve the maintained API, never the repository tree."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8101, access_log=False)
