# Tester implementation and operation

## Location and isolation

`/Users/shreeshaks/Documents/verisight tester fix` is a new folder copied from the complete working tree, including prior uncommitted parity fixes. Original source and Git history were not reset, overwritten, committed or pushed. New frontend5175/API8001 run separately from original5174/API8000. The Python `.venv` is a local symlink to the existing environment. Frontend dependencies and Vite's `.vite-tester` cache are independent copies. Application sources and runtime note storage are separate. For distribution, create an independent environment/install dependencies, do not package these the Python environment symlink or private notes. Tesseract was installed via Homebrew with English language data; no ML model was trained.

Run `./start-verisight.sh` with these ports free. Optional settings: `VERISIGHT_OCR_ENABLED=0` explicitly disables OCR; `VERISIGHT_TESSERACT` names the executable. The current API capability flag and per-image OCR result distinguish unavailable, error, timeout, unreadable and available states. Missing OCR does not fabricate a transcript or reroute to a learned authenticity classifier.

## Source map

- `backend/app/services/forensic/intelligence/robust_review.py`: technical acquisition profile, bounded Tesseract TSV recognition, source-coordinate boxes/word scores, label-guided field candidates, internal date/QR-amount comparisons, local peer-normalized three-quality ELA/two-scale residual measurements, grouped experimental evidence. Unknown templates and acquisition history remain unknown. Semantic mismatches are review observations, not payment verification or active score increases.
- `pixel_analysis/copy_move.py`: rejects ambiguous zero-distance alternatives; RANSAC verifies spatially distributed near-unit-scale matches. Repeated UI remains a confounder.
- `pipeline.py`, `core/schemas.py`: additive `intelligence` and optional `media_urls`, separate recognized text from connected-component baseline overlays. Existing operational ensemble retained after failed candidate promotion.
- `intelligence/media_cache.py`: **local-only** optional `?media=urls` transport. Metadata stays compact; original/overlay bytes are unchanged. Ephemeral 64MiB bounded memory cache,10-minute TTL, random192-bit tokens, no disk writes, no listing, no-store responses, explicit410 expiry/503 hosted refusal. This is not authenticated cloud storage. Old inline API representation remains the default; hosted frontend does not request local URL transport.
- `api/endpoints.py`: real synthetic research artifacts, manifest and prediction checksum checks, explicit missing/stale artifact errors, local media routes and optional compact response mapping. API contract keeps existing clients compatible.
- `simulation/whatsapp_pipeline.py`: fixes uint8 multiplication overflow in the amplified difference map. Simulator's frontend “before” image now refers to the actual source, not its reanalysis output. Comparison uses a delivery approximation and makes no guarantee about real WhatsApp forgery detection.
- `frontend/src/components/IntelligencePanel.tsx`: acquisition/availability, recognized words and field source selection, semantic checks and rejected experimental evidence. OCR selections use blue boxes distinct from tamper-review cues.
- `RobustnessResearch.tsx`: actual saved predictions, selectable experimental/operational/baseline scorer and partition, synchronized exploration confusion metrics and genuine ROC/PR points. Exploration cannot tune backend thresholds or promote models. Research figures are explicitly synthetic-only.
- `ForensicViewer.tsx`, `RiskDossierSidebar.tsx`, `App.tsx`, `services/api.ts`, shared types: source-box highlighting, preserved workbench, media URL normalization and source fetching for simulation. Both user verdict labels remain unchanged.
- `scripts/build_robustness_benchmark.py`, `evaluate_robustness.py`, `summarize_robustness.py`, `evaluate_existing_fixtures.py`, `training_preflight.py`: reproducible generation, grouped split validation, per-image results, measured metrics/failures and fail-closed training governance.

## Validation artifacts

- `research/results/final-tests.log`: final backend suite including genuine Tesseract recognition, unavailable/timeout/error/low-confidence paths, no invented fields, quality/provenance distinctions, correlated-cue deduplication, source/template/session split isolation, synthetic training block, research endpoint and ephemeral media byte equality/expiry/hosted restriction/memory cap, semantic abstention. Upstream Starlette/AnyIO emits one deprecation warning.
- `research/results/final-build.log`: TypeScript and production Vite build. Large JS chunk warning remains; no lint script exists in this repository.
- `research/results/intelligence-browser.json`: exact real-upload, OCR source selection, interactive research threshold/partition calculations, responsive checks and browser exception checks.
- `research/results/parity-browser.log` and `output/playwright/browser-results.json`: full existing35-check workflow regression suite on port5175.
- `research/screenshots/`: actual before/after workbench, OCR inspection, research metrics and phone views. Other five-page/four-viewport captures remain under output/playwright.

Commands used:

```sh
.venv/bin/python -m pytest backend/tests -q
npm run build --prefix frontend
NODE_PATH=/Users/shreeshaks/.npm/_npx/e41f203b7505f1fb/node_modules node scripts/test_intelligence_browser.cjs
BASE_URL=http://127.0.0.1:5175 NODE_PATH=/Users/shreeshaks/.npm/_npx/e41f203b7505f1fb/node_modules node scripts/parity-browser.cjs
```

The NODE_PATH is the existing installed Playwright package on this machine; use a resolvable Playwright package elsewhere. Tests use the real backend except deliberate failure injection and print-handler/microphone-denial checks. Actual microphone recognition success, multilingual OCR, multilingual PDF fonts, cloud deployment and payment verification were not validated.

Initial browser runs revealed large inline media responses taking longer than the30-second UI-test timeout, including in the unchanged original. The tester now returns about52KB of report metadata for the clean fixture instead of about5.8MB embedded JSON, with lossless binary assets requested separately. Image transfer still has real latency; tests wait for actual image decoding. Earlier research-check test failures during artifact regeneration are retained in the investigation notes: the checksum gate correctly refused stale/mismatched artifacts; final tests run after regeneration, not concurrently with it.

## Release status

Read `FORENSIC_INTELLIGENCE_RESULTS.md` before interpreting the new features. The candidate did not improve pair discrimination and **was not promoted**. The actual43/39 user pair remains unavailable. Authenticity accuracy, trained segmentation, calibration, real WhatsApp robustness and independent real-world holdout performance remain unproven. No external datasets were ingested; no training used the five demo fixtures or new synthetic corpus. The data-collection and licensing work required before training is in `DATA_COLLECTION_PLAN.md` and `FORENSIC_INTELLIGENCE_RESEARCH.md`.

No Vercel deployment was performed. The optional OCR binary and private media storage need an explicit hosted design; the prototype's cloud request-size and startup/memory limits remain unverified. Existing database/mobile intake/settlement unavailability remains truthful. Rollback is selecting the untouched original folder, not resetting any Git history.

## Final executed checks

- Backend: **93 passed**, one upstream deprecation warning,24.20s in the final recorded run.
- Existing browser regression suite: **35 passed,0 failed** after dependency/cache isolation and removing the redundant legacy transfer from the case-hash assertion. No browser exceptions recorded.
- Targeted intelligence/browser suite: **6 passed,0 failed** (actual upload/OCR selection, before/after capture, real metric recomputation and responsive checks).
- Production build: **passed**; main JS chunk-size warning remains.
- All six existing image fixtures analyzed by both versions;120 paired delivery-stress images evaluated by both versions.
- Training gate: **BLOCK**, expected exit2; no model trained or promoted.
- Local frontend5175 and API8001 respond; original frontend5174 remains untouched. No push or deployment.

Large lossless images still require download time. The browser regression waits for actual image decoding (up to120s), rather than claiming a sub-second end-to-end upload/preview SLA. Benchmark CPU times do not include browser transfer.
