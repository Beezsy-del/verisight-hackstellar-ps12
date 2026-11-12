# VeriSight — Screenshot Forensic Triage Prototype

> A private development prototype that computes visual review cues for screenshots. It is not a trained or calibrated authenticity classifier.

## Unified local project

This folder combines inspected components from Hackstellar's `feat/screenshot-analysis-release-gates` and ScamShield's `feature/scamshield-scaling-enhancements`. Originals are preserved separately. Component choices and measured limitations are in [VERISIGHT_UNIFICATION_REPORT](VERISIGHT_UNIFICATION_REPORT/EXECUTIVE_VERDICT.md).

This unified version has **not been deployed**. Any historical public demo is a different build. Start locally using the instructions below.

## Operating and evaluation scope

Use this build privately. [Operating guide](docs/private-operation.md) describes access, expiring previews, retention, measured delivery limits and rollback. [Evaluation protocol](docs/evaluation-protocol.md) defines authorized collection, grouped splits, validation-only threshold selection and reviewer comprehension testing. Neither a completed product mission nor improved real-world detection has been established.

## What It Does

VeriSight accepts common image formats and computes pixel, layout, metadata, and QR review cues. The current build cannot determine that every screenshot is authentic or edited: it has no trained image classifier, and it does not verify payments. Analysis runs server-side. Case summaries are persisted only when explicitly enabled and Supabase is configured; original image bytes are not stored in the case table. A short-lived private storage object is used by the signed-upload flow and deleted after analysis.

**Layer 1 — Pixel & Frequency Signal Forensics**
- **Error Level Analysis (ELA):** Re-encodes the decoded pixels as JPEG and compares residuals. The residual heatmap is exploratory; score-based localization is disabled for non-JPEG sources. ELA residuals alone do not show splicing.
- **Wavelet Noise Analysis:** Computes high-frequency residual variation and flags large low-variation areas. Flat UI regions, resizing, and recompression can produce similar cues.
- **Copy-Move Cue:** Matches ORB descriptors and displacement clusters. Repeated icons and text can match; this is a candidate region, not a confirmed clone.
- **JPEG Quality Sweep:** Reports global reconstruction error across selected JPEG qualities. It does not localize a JPEG ghost or determine whether editing occurred.

**Layer 2 — Typographic Geometry Forensics**
- **Text-like geometry:** OpenCV connected components provide boxes; they do not recognize text. Rows are grouped and compared against a median baseline, so ordinary UI alignments may trigger cues. QR-detected regions are excluded.
- **CIELAB and sharpness cues:** Compare local colors beside components and Laplacian variation among components. Thresholds are exploratory and can flag normal rendering differences.

**Layer 3 — Metadata & Protocol Rules**
- **Metadata:** Reads selected available image metadata. A software tag or absent EXIF is not proof of editing or forwarding.
- **C2PA:** Searches raw bytes for possible marker strings only. It does not parse or cryptographically validate a Content Credential.
- **QR decoding:** Uses OpenCV to decode readable QR payloads and identify broad types such as UPI URIs or web links. It does not test QR pixel integrity, validate a recipient, open a destination, or verify a payment.
- **Text rules:** RapidOCR recognizes visible text and applies narrow receipt-statement rules. Receipt-time and UTR rules are separate from those statement checks and must not be mistaken for issuer validation. If such data is present in supported metadata chunks, rule results remain format/context cues, not issuer validation.
- **Channel and viewport cues:** Metadata, encoding and dimensions are compared with simple heuristics. They cannot reliably identify an app or prove cropping.

**Layer 4 — Ensemble & Cross-Layer Corroboration**
- **Weighted risk aggregation:** Strong indicators (`text_geometry` = 35 pts, `copy_move` = 28–42 pts, `time_consistency` = 35 pts, `reference_format` = 20 pts) are combined with weak review cues (ELA macroblock count, wavelet noise, rendering variation, software metadata) capped at 12 pts. Total score is capped at 92.0.
- **Cross-Layer Spatial IoU:** For each clone-detected bounding box and each anomalous baseline box, pairwise IoU is computed. A primary review region is reported when IoU ≥ 0.20, upgrading the verdict and adding a `CROSS_LAYER_SYNERGY_LOCUS` bounding box to the report.
- **Assessment:** The API returns `INCONCLUSIVE`, `REVIEW_REQUIRED`, or `CORROBORATED_ANOMALIES` as heuristic evidence states. Error probability and calibrated confidence are unavailable.

---

## Supported File Types

| Format | Notes |
|---|---|
| **PNG** | ELA heatmap may be viewed, but contributes no anomaly score |
| **JPEG / JPG** | JPEG-specific recompression cues are available; they are not proof of editing |
| **WebP** | Supported via OpenCV decode |
| **BMP** | Supported; no JPEG-specific metadata checks apply |

Maximum upload size: **20 MiB**, **2 megapixels**, **3200 pixels per side**. These are enforced development limits, not validated capacity guarantees. Two analyses per process; one worker only.

---

## Intended Screenshot Inputs

The upload accepts these images, but the pipeline has not been validated across these app templates or message types:

- UPI receipts and QR screens
- WhatsApp or other message screenshots
- Bank transfer confirmations and wallet receipts

---

## Verdicts

| Verdict | Score Range | Meaning |
|---|---|---|
| `INCONCLUSIVE` | score < 12 without corroboration | No configured strong cue crossed threshold. This does not imply authenticity. |
| `REVIEW_REQUIRED` | score ≥ 12 without corroboration | At least one configured cue crossed threshold; inspect the parameter and region. |
| `CORROBORATED_ANOMALIES` | candidate ORB region overlaps a baseline-geometry cue | This is a region-overlap rule, not a probability or a verified tampering determination. |

---

## Demo Samples

Five synthetic, watermarked samples are bundled for instant demonstration:

| ID | Sample | Expected Verdict | Key Signals |
|---|---|---|---|
| `sample_1` | Clean Synthetic Payment UI (₹1,250) | `REVIEW_REQUIRED` | Clean pixels, but OCR reads its not-a-real-transaction watermark |
| `sample_2` | Synthetic Edited Amount (₹95,250) | `REVIEW_REQUIRED` | Known altered fixture; current signals are heuristic and do not establish that an arbitrary edit will be found |
| `sample_3` | Synthetic Metadata Conflict Fixture | `REVIEW_REQUIRED` | Embedded metadata clock and reference-format cues; score can be high without a localized overlap |
| `sample_4` | Synthetic JPEG Re-encode | `REVIEW_REQUIRED` | Re-encoded fixture; app/source cannot be identified from the image profile |
| `sample_5` | Synthetic Repeated-Region Fixture | `REVIEW_REQUIRED` | ORB feature matches and dimensions; repeated interface elements can match |

> **Important:** These are synthetic test fixtures, not real payment screenshots. They do not validate actual payments or demonstrate real-world forensic accuracy.

---

## Running Locally

### Prerequisites

- Python 3.12+
- Node.js 18+

### Quick Start

```bash
cd /Users/shreeshaks/Documents/VERISIGHT_UNIFIED

# Backend
python3.12 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/pip install --no-deps --force-reinstall opencv-python-headless==4.10.0.84

# Frontend
cd frontend && npm ci && npm run build && cd ..

# Start both servers
./start-verisight.sh
```

Open **http://localhost:5174** for the React forensic workbench.
API interactive docs at **http://localhost:8101/docs**.

### Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side service role key (never expose in browser) |
| `SUPABASE_ANON_KEY` | Public anon key for Storage signed upload URLs |

> Never commit `.env`, `.env.local`, or `.env.production.local` to version control.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VeriSight System                              │
│                                                                  │
│  Browser (React/TypeScript + Vite)                               │
│  ├── Forensic Workbench (multi-view image viewer)                 │
│  ├── ELA / Wavelet / ORB candidate overlays                      │
│  ├── Baseline laser & findings sidebar                           │
│  ├── Messaging-style JPEG transform simulator                    │
│  └── Mobile QR intake (stage judge handoff)                      │
│                        │  same-origin API requests               │
│  FastAPI (Python 3.12)                                           │
│  ├── Layer 1: pixel_analysis/ (ELA, wavelet, ORB candidates)    │
│  ├── Layer 2: typography/ (baseline_laser, cielab_patch, OCR)    │
│  ├── Layer 3: metadata/ (exif, viewport_db, domain_rules, QR)    │
│  ├── Layer 4: ensemble/calibrator.py (rule aggregation)          │
│  └── supabase_store.py → Supabase PostgreSQL (metadata only)     │
│                                                                  │
│  Supabase                                                        │
│  ├── forensic_cases table (verdict, score, findings metadata)    │
│  └── mobile-evidence Storage bucket (private, short-lived)       │
└─────────────────────────────────────────────────────────────────┘
```

**Deployment:** Vercel serverless FastAPI with the Vite-built frontend served on the same origin.

Vercel installs the slim production set from `requirements.vercel.txt` plus the frontend packages. The complete local/test dependencies remain in `requirements.txt`; Pillow is needed for generating missing synthetic fixtures locally, while the checked-in sample fixtures are deployed with the app.

The Vercel project uses Fluid Compute and the `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` setting because the OpenCV-backed Python function exceeds the standard package cap. Keep that non-secret setting enabled in Production and Preview when deploying.

---

## API Reference

All endpoints are served under `/api`.

### `GET /api/model/status` and `GET /api/model/evaluation`

These power the Evaluation dashboard. The status endpoint reports that the deployed system is heuristic-only and uncalibrated. The evaluation endpoint reports the five bundled synthetic fixtures and returns `metrics: null`; there is no representative labeled dataset or held-out evaluation from which to claim model accuracy.

### `GET /api/health`

Returns service readiness and database connectivity.

**Response:**
```json
{
  "status": "HEALTHY",
  "database": "HEALTHY",
  "service": "VeriSight Forensics Engine",
  "version": "1.0.0",
  "active_layers": ["L1_Signal_Heuristics", "L2_Geometry_Heuristics", "L3_Metadata_QR", "L4_Evidence_Review"]
}
```

---

### `POST /api/analyze`

Upload an image file for full 4-layer forensic analysis.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | File | PNG, JPEG, WebP, or BMP image (max 20 MB) |

**Response:** `ForensicAnalysisReport` JSON (see schema below)

**Example:**
```bash
curl -X POST https://verisight-ps12.vercel.app/api/analyze \
  -F "file=@receipt.png" | jq .verdict
```

> On Vercel, large files should use the signed upload flow (`POST /api/upload-session` → PUT to Storage URL → `POST /api/analyze-upload-session/{session_id}`) to avoid function body size limits.

---

### `POST /api/upload-session`

Create a one-use signed Supabase Storage upload URL for large files.

**Request:** JSON body
```json
{
  "filename": "receipt.jpg",
  "content_type": "image/jpeg",
  "size": 2048000,
  "session_id": "optional-uuid"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "upload_url": "https://...supabase.co/storage/v1/object/upload/sign/...",
  "storage_key": "anon-key"
}
```

---

### `POST /api/analyze-upload-session/{session_id}`

Analyze a screenshot already placed in private Storage via signed upload. Consumes and deletes the stored object after analysis.

**Response:** `ForensicAnalysisReport` JSON

---

### `POST /api/analyze-sample/{sample_id}`

Instantly run the 4-layer pipeline against one of the five bundled synthetic demo samples. Results are LRU-cached per sample file mtime.

**Path param:** `sample_id` ∈ `{sample_1, sample_2, sample_3, sample_4, sample_5}`

**Response:** `ForensicAnalysisReport` JSON

---

### `GET /api/demo-samples`

Returns metadata for all five demo samples.

**Response:** Array of `DemoSampleMeta` with `id`, `filename`, `title`, `scenario`, `expected_verdict`, `target_score_range`, `description`, `tags`, `url`.

---

### `POST /api/simulate-whatsapp`

Simulate WhatsApp laundering on an uploaded image. Re-encodes it at Q77 JPEG with 4:2:0 chroma subsampling, then re-runs the full forensic pipeline and returns a side-by-side comparison.

**Request:** `multipart/form-data` with `file` field

**Response:** `WhatsAppSimulationResponse`
```json
{
  "original_size_bytes": 245000,
  "simulated_size_bytes": 103000,
  "compression_ratio": 2.38,
  "original_dimensions": [1080, 1920],
  "simulated_dimensions": [1080, 1920],
  "simulated_image_b64": "data:image/jpeg;base64,...",
  "diff_heatmap_b64": "data:image/webp;base64,...",
  "reanalysis": { ... }
}
```

---

### `POST /api/mobile-upload`

Receive a screenshot from a mobile device (stage judge QR scan flow). On Vercel, stores to private `mobile-evidence` bucket. Locally, analyzes in-process.

**Query param:** `session_id` (UUID, required on Vercel)

**Request:** `multipart/form-data` with `file` field

---

### `GET /api/latest-mobile-upload`

Desktop workbench polling endpoint. Returns the analyzed report for the given session once the mobile upload has been retrieved and processed.

**Query params:** `session_id` (UUID), `clear` (bool)

---

### `GET /api/network-info`

Returns the host's LAN IP address for generating the mobile QR code URL.

---

## ForensicAnalysisReport Schema

```typescript
interface ForensicAnalysisReport {
  file_sha256: string;          // SHA-256 of original uploaded bytes
  filename: string | null;
  timestamp: string;            // ISO 8601
  image_width: number;
  image_height: number;
  overall_tamper_score: number; // 0–92 heuristic score (not a probability)
  confidence_score: null;       // No calibrated probability model is available
  verdict: "INCONCLUSIVE" | "REVIEW_REQUIRED" | "CORROBORATED_ANOMALIES";
  channel_detected: string;     // Weak image-profile cue; source may remain unknown
  layer1: Layer1SignalResult;
  layer2: Layer2GeometryResult;
  layer3: Layer3MetadataResult;
  layer4: Layer4SemanticResult;
  synergy: CrossLayerSynergy;
  findings: ForensicFinding[];
  all_bounding_boxes: BoundingBox[];
  original_image_b64: string;   // lossless WebP for the viewer overlay
}
```

Each `ForensicFinding` has: `id`, `layer` (1–4), `severity` (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`), `title`, `description`, `metric_name`, `metric_value`, and optionally a `bounding_box` with pixel coordinates.

---

## Database

PostgreSQL via **Supabase** (project reference `ytxfhmdzlelcpjsnlndh`).

**Persisted case metadata:**
- `forensic_cases` table: case UUID, timestamp, filename, SHA-256 hash, image dimensions, heuristic points, null confidence field, evidence-state verdict, channel cue, findings, layer summaries, and submission source.

- Original image bytes are not stored in `forensic_cases`. The mobile handoff temporarily places an image in private Storage and deletes it after analysis. A best-effort cleanup runs when a later upload session is created; this is not a scheduled deletion guarantee.
- ELA / wavelet / ORB heatmap payloads are returned in-band as base64 and are not persisted in the case row.

**Security:**
- Row-level security (RLS) is enabled on `forensic_cases` with no public read/write policies — writes go via service role key on the server only.
- The `mobile-evidence` Storage bucket is private. Handoff records can only be consumed once, and the analyzed object is deleted after processing. Expired unconsumed objects are removed best-effort when a later upload is created.
- Schema versioned under `supabase/migrations/`.

---

## Accuracy & Limitations

VeriSight is a **heuristic triage tool**, not a validated forensic classifier.

| Limitation | Detail |
|---|---|
| **No trained model** | All decisions use deterministic signal thresholds and weighted rules — no ML model was trained on a labeled payment screenshot dataset. |
| **Synthetic test set** | The five bundled samples are synthetic regression fixtures, not real payments. Demo scores describe configured rules only and are not accuracy measurements. |
| **False positives** | Standard JPEG re-compression, screenshot capture pipelines, display scaling, and app UI rendering can all trigger ELA, wavelet, and sharpness cues on authentic images. |
| **Text extraction** | The default pipeline groups connected components but does not recognize their text. Pixel-only receipt times and UTRs are not reliably read. |
| **QR payment not verified** | QR payloads are decoded locally for content inspection. The payee identity, URL destination, and actual payment state are not verified against any payment rail. |
| **C2PA not validated** | Possible marker strings are searched in bytes; manifest presence, signature, and trust anchor are not verified. |
| **Not a legal instrument** | Outputs are investigative cues for a human reviewer. Do not use VeriSight results as sole evidence to determine whether a payment occurred. Always confirm with the payment provider or bank. |

---

## Project Structure

```
verisight-hackstellar-ps12/
├── backend/
│   └── app/
│       ├── api/endpoints.py          # FastAPI routes
│       ├── core/
│       │   ├── config.py             # Settings (thresholds, paths)
│       │   └── schemas.py            # Pydantic models
│       ├── services/forensic/
│       │   ├── pipeline.py           # 4-layer orchestrator
│       │   ├── pixel_analysis/       # ELA, wavelet, copy-move, JPEG ghosts
│       │   ├── typography/           # Baseline laser, CIELAB, OCR engine
│       │   ├── metadata/             # EXIF, domain rules, viewport DB
│       │   ├── qr_inspector.py       # QR payload decoding only
│       │   ├── provenance/           # C2PA inspector
│       │   └── ensemble/calibrator.py # Cross-layer IoU + verdict
│       ├── services/supabase_store.py
│       └── simulation/whatsapp_pipeline.py
├── frontend/src/
│   ├── components/                   # React forensic workbench UI
│   ├── services/api.ts               # Typed API client
│   └── types/forensic.ts             # TypeScript type definitions
├── samples/                          # 5 synthetic demo fixtures + generator
├── supabase/migrations/              # PostgreSQL schema migrations
├── api/index.py                      # Vercel ASGI entry point
├── vercel.json                       # Vercel deployment config
├── start-verisight.sh                # Local dev launcher (macOS/Linux)
├── start-verisight.bat               # Local dev launcher (Windows)
└── docs/                             # Design docs, API contract, demo script
```

---

## License

[MIT](LICENSE)

---

> **HackStellar PS-12** · Built for rapid forensic triage of digital payment screenshots in a hackathon context. Not a production-certified fraud detection product.

### Visible receipt text checks

The local pipeline now runs RapidOCR/ONNX alongside component geometry. It flags
high-confidence, whole-line fake/demo/non-real or failed/pending payment
statements. OCR failure or unreadable text cannot silently yield a favorable
result. These checks do not validate plausible-looking fabricated receipts or
confirm payment settlement. The two UI result labels remain Likely misleading
and Likely accurate. See [the reproduction and scope](docs/receipt-scanning-verification.md).

On headless hosts, install `opencv-python-headless==4.10.0.84` last with
`--force-reinstall --no-deps` after installing requirements; RapidOCR also declares
a GUI OpenCV dependency. Vercel installation and CI include this step.

### Localization training and release gate

The current localization-model release is **blocked**: no suitable screenshot
corpus has documented intended-use permission and no independent locked-test
evaluation exists. No localization model has been trained or deployed.
See [the dataset permission audit, collection plan, and release protocol](docs/LOCALIZATION_DATA_AND_RELEASE_PLAN.md).
`/api/model/status` and `/api/model/evaluation` expose this readiness state;
metrics, model version, threshold, and calibrated confidence remain unavailable.
Manifest provenance checks are in `backend/app/evaluation/data_audit.py`; they
do not certify licensing or discover image duplicates by themselves.


## Unified processing decisions

`analysis_gate` separates processing readiness from review findings. PASS means required processing completed without a configured review cue; WARNING requires review; BLOCK means required evidence or processing is incomplete/invalid. None approves money, goods, authenticity or settlement. `visual_tamper_score` remains separate from receipt statement warnings, and `confidence_score` remains null without validated calibration. The frontend shows **Likely accurate** / **Likely misleading** exactly as requested, with evidence and readiness limitations beside them.

Verify frontend contracts with `npm run test --prefix frontend`; run backend tests with `.venv/bin/python -m pytest backend/tests -q`. Production UI compilation is `npm run build --prefix frontend`. Optional Supabase configuration enables cloud persistence and signed-upload workflows; local image analysis works without it. No bank/PSP transaction-status integration is configured.
