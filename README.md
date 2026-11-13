# VeriSight — forensic intelligence tester integration

A screenshot-review workbench combining the `quality-of-life-updates` repository foundation with the isolated **verisight tester fix** implementation. Screenshot analysis does **not** establish payment settlement, recipient identity, or authenticity.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
npm ci --prefix frontend
./start-verisight.sh
```

Open http://127.0.0.1:5175 (API: port 8001). Stop other services on these ports first. Optional Tesseract with English language data enables the additional word/field OCR evidence. RapidOCR supplies the retained receipt-statement checks. Unavailable recognition is reported explicitly.

## Included

- Four-layer visual, geometry, metadata and cross-layer review; ELA, wavelet, ORB and source-linked regions.
- Optional OCR fields, acquisition-quality measurements, evidence explanations and review gates.
- Two product labels: **Likely accurate** and **Likely misleading**, with uncertainty and settlement limitations.
- Response & Guidance, browser-supported voice intake, editable complaint drafts and local notes.
- Private-access controls, bounded analysis, opt-in persistence, signed-storage/mobile endpoints and temporary preview delivery.
- A reproducible 120-image synthetic delivery-transformation experiment and explicit model-release blockers.

The experimental fusion candidate **failed its improvement gate and was not promoted**. No real-world detection accuracy or calibrated probability is established. Historical experiment outputs describe the frozen tester engine, not the combined engine's added receipt warnings. A synthetic receipt marked “not a real transaction” can trigger a textual warning independently of its visual score.

## Configuration and deployment

Copy `.env.example` to a local environment file and configure variables in the process environment. Never commit credentials. Remote operation requires `VERISIGHT_ACCESS_PASSWORD`; cloud storage needs the documented Supabase configuration. Missing services return unavailable states. Storage and hosted deployment have not been verified against live credentials in this integration. Vercel configuration is retained; this branch has not been deployed.

Uploads are bounded to 20 MiB, 2 megapixels and 3200 pixels per edge. Local media URLs expire after ten minutes. Notes use local persistence and are unavailable in hosted mode. Database case summaries are opt-in.

## Validation and research

```sh
.venv/bin/python -m pytest backend/tests -q
npm test --prefix frontend
npm run build --prefix frontend
```

Read the [integration report](docs/REPOSITORY_INTEGRATION.md), [measured tester experiment](docs/FORENSIC_INTELLIGENCE_RESULTS.md), [research and dataset restrictions](docs/FORENSIC_INTELLIGENCE_RESEARCH.md), and [data collection plan](docs/DATA_COLLECTION_PLAN.md). The new synthetic corpus is in `research/datasets/robustness`; baseline code and per-image predictions are versioned for reproduction. Private user-provided images, legacy model binaries, credentials, dependency directories and generated frontend bundles are excluded.
