# Version A audit: verified remote implementation

Hackstellar release-gates,347c7a7612c59e0e8be56274187deb53ab251165. All inventoried application hashes match the prior independently tested snapshot. Current version letters below are normalized to this unification request. Evidence filenames retain historical naming and are located in `/Users/shreeshaks/Documents/COMPARATIVE_AUDIT`, where historical A=ScamShield and B=Hackstellar. Source references resolve against current `VERISIGHT_UNIFICATION_SOURCES/A` or `/B`. Fresh unification tests are reported separately.

# Project A deep audit

Audit date: 2026-11-12. Scope: the read-only `snapshots/A` source snapshot. Paths below are relative to that snapshot. This report distinguishes source-verified behavior, repository claims, and risks requiring runtime or deployment verification. Parent audit execution supplies independent full test/build and benchmark results. This inspection additionally ran 10 small API probes per version with credentials stripped and outbound network connections blocked; it did not modify application source.

## Assessment

A is a functioning heuristic-review application with real OCR, a reasonably explicit no-model state, and a substantive plan for a future permission-cleared localization model. It is **not a trained visual-tampering classifier or localizer**, and provides no independent evidence that its two displayed labels reliably separate authentic and edited screenshots. Stopping before training is the correct outcome under the supplied instruction when suitable authorized representative data is unavailable; absence of training is therefore not itself a failure. The remaining distinction is between a good blocked research plan and a completed, enforced production release process.

The five largest weaknesses are: (1) the displayed two-label decision mixes visual anomalies, failed-payment semantics, and scanner availability without validation; (2) the release gate is informational, not enforced; (3) a backend/frontend contract mismatch hides real overlap in the UI/report; (4) the data audit validates declarations rather than image/mask evidence; and (5) public expensive endpoints and opportunistic storage cleanup leave operational/privacy controls incomplete. None establishes that an unauthorized model was trained or that a new deployment occurred.

## Architecture and actual computation

The active stack is React/Vite/TypeScript plus FastAPI. `api/index.py:1–13` imports the FastAPI application; `backend/app/main.py:39–66` creates it, mounts samples, and includes `/api` routes. `vercel.json:1–13` builds the frontend, installs Python/Node dependencies, and configures a 300-second function limit. It does not run the Python test suite or inspect evaluation readiness before building.

`backend/app/services/forensic/pipeline.py:37–206` hashes original bytes, bounds/decodes the image, computes ELA/wavelet/ORB repetition cues, component geometry, metadata and QR checks, then combines manually weighted evidence. Layer 2 explicitly uses `extract_text_tokens(..., use_neural=False)` at line 105; these are connected-component boxes with invented `token_N` strings, not recognized words (`typography/ocr_engine.py:25–73`). That does **not** mean the application lacks OCR: the separate RapidOCR path runs at `pipeline.py:208–227`, with ONNX inference in `typography/receipt_text.py:13–36`. The optional EasyOCR geometry branch and the active RapidOCR receipt branch must not be conflated.

The ensemble uses clone/baseline IoU >=0.20 for corroboration, heuristic weights and score cutoffs, and always returns classifier confidence `None` (`ensemble/calibrator.py:33–75,156–183`). Its output is bounding boxes/cue maps, not a learned pixel mask. `AdvancedModelAdapter` remains disabled and returns `inference_run=False` (`adapters/advanced_model_adapter.py:11–32`); its docstring's conditional inference wording is stale. Layer 4 has `vlm_used=False` and copies metadata-derived signals (`pipeline.py:189–197`), so it is not an independent semantic model. Treating the four layers as four independent learned detectors would overstate this architecture.

## Five most significant weaknesses

### 1. Unvalidated displayed verdict conflates distinct questions — high impact, source verified

`frontend/src/services/verdictLabel.ts:1–5` maps `INCONCLUSIVE` to **Likely accurate**, and every other state to **Likely misleading**. The ensemble means only “no strong signal” by INCONCLUSIVE (`calibrator.py:165–171`); it does not establish authenticity. The supporting UI correctly says authenticity remains unknown and settlement is not verified (`RiskDossierSidebar.tsx:257–262`), but that qualification cannot make the favorable headline an empirically validated classifier result.

RapidOCR's whole-line regex flags exact forms of fake/demo/non-real messages and failed/declined/cancelled/pending payments (`receipt_text.py:39–57`). Any matching text raises the overall score to at least 55 and may change the verdict (`pipeline.py:212–218`). B visually untouched genuine failed-payment screenshot therefore receives the same warning label as an anomalous edit. This can be useful for “proof of successful payment” triage, but it is not visual-tampering detection. Conversely, OCR unavailable or no readable text changes an otherwise INCONCLUSIVE result to REVIEW_REQUIRED even without positive forgery evidence (`pipeline.py:219–227`); because the UI maps that to Likely misleading, scanner coverage affects the apparent classification. B zero-point warning is possible through this branch.

The regex is a deliberately narrow English lexical rule, not semantic understanding. Variants, translations, split OCR lines, low OCR confidence, and unseen typography have no demonstrated coverage. `receipt_text.py:24–25` ignores lines below .85 recognition confidence; that threshold is not an authenticity calibration. Metadata time/reference rules consume untrusted PNG chunks (`metadata/domain_rules.py:94–103`) and can add score without changing visible pixels (`calibrator.py:77–94`). All of this must remain distinct from visual-edit evidence and authorized transaction verification. Preserve the requested two labels, but attach a clearly separate evidence state/coverage/settlement explanation and evaluate their behavior on independently labeled data before making accuracy claims.

### 2. BLOCKED release status is telemetry, not a release interlock — high impact, source verified

`backend/app/evaluation/readiness.py:4–19` returns a hardcoded BLOCKED dictionary with training/deployment false. `/model/status` and `/model/evaluation` display it (`endpoints.py:113–148`). The upload and sample inference paths directly call `analyze_screenshot` (`endpoints.py:256–313`), application startup does not consult readiness (`main.py:25–44`), and `vercel.json:4–10` does not gate deployment on tests or evaluation. Tests assert that the dictionary says false, not that promotion is refused (`test_data_readiness.py:59–71`).

Important scope qualification: readiness explicitly applies to the **new visual tampering-localization model** (`readiness.py:9`), which does not exist. Existing heuristic inference while that new model is blocked is not automatically a violation. The verified gap is the lack of an executable model-promotion/deployment guard for the future workflow; it is not evidence of an unauthorized new deployment. A itself acknowledges this limitation (`docs/LOCALIZATION_DATA_AND_RELEASE_PLAN.md:42–45,177–182`). Implement an independently checked, fail-closed release record and deployment CI when model promotion becomes possible.

### 3. Frontend/backend overlap contract is broken — medium/high impact, source verified

Backend `CrossLayerSynergy` serializes `region_overlap_found` and `primary_review_locus` (`core/schemas.py:84–87`; set in `calibrator.py:174–180`). Frontend type `CrossLayerSynergy` instead expects `synergy_multiplier_applied`, `multiplier_factor`, and `primary_forgery_locus` (`frontend/src/types/forensic.ts:82–87`). The printed report checks the missing `synergy_multiplier_applied` property and renders **None found** (`ForensicReportModal.tsx:252–256`); sidebar checks also use the stale property (`RiskDossierSidebar.tsx:352,607`). B backend report with overlap true consequently has an undefined/falsy value in these branches. This hides the banner and misstates overlap in the report, although all-boxes/findings can still convey the region elsewhere.

The client trusts `res.json()` as a declared TypeScript return type without runtime schema checking (`services/api.ts:46–56,59–80`). Compilation cannot detect the wire mismatch. Frontend `BoundingBox.confidence` is also a required number (`types/forensic.ts:8`) while backend regions legitimately contain null (`core/schemas.py:15–16`). Generate or validate the shared response contract and add one UI integration case with a real corroborated response. This is a concrete defect independent of whether the heuristics are accurate.

### 4. Data preflight is useful but cannot certify a dataset — medium/high future-release impact, source verified

`evaluation/data_audit.py:13–69` checks required declared fields, permissions flags/references, valid labels, all three splits, both classes, mask-path presence, and cross-split equality for each individual group identity/hash. Checking each identity separately is a sound protection against partial-group leakage; it is better than concatenating group IDs. However, it never opens an image or mask, computes its SHA-256, validates mask shape/alignment/content, checks legal evidence, or discovers undeclared perceptual duplicates. B fabricated but structurally complete manifest passes. `test_data_readiness.py:10–22` proves this structural-only behavior with arbitrary formatted hashes and mask paths. `test_manifest_digest` locks JSON records, not actual file bytes (`data_audit.py:72–75`).

This is accurately disclosed in the module header and plan (`LOCALIZATION_DATA_AND_RELEASE_PLAN.md:104–108`), so it is a capability boundary, not a hidden claim of completed scientific validation. There is no real corpus, segmentation training run, calibrated threshold, mask benchmark, subgroup result, or locked independent test result in the implemented workflow. Add file-bound integrity and annotation inspection before treating this validator as a training gate.

### 5. Operational controls and storage lifecycle are incomplete — high potential impact, code verified; exploit/deployment state unverified

Active FastAPI upload/session/analysis routes have no application authentication, authorization dependency, rate limit, queue, or explicit workload concurrency bound (`api/endpoints.py:50–98,256–267,315–324,326–390`). CORS allows every origin (`main.py:51–58`). CORS is not authorization, and wildcard CORS does not itself prove credential theft. UUID mobile sessions act as bearer capabilities rather than user identities: possessing the session permits polling/consumption, and clients can supply session IDs when requesting signed uploads (`endpoints.py:43–75`). This is appropriate to assess as an anonymous demo threat model, not as verified cross-account access. Rate/cost abuse and capability disclosure deserve testing before public production use. Infrastructure protection may exist but was not verified.

There are real protections: input bytes are capped, Pillow checks dimensions before OpenCV allocation, malformed/unsupported/animated images are rejected (`image_validation.py:13–41`), storage is private with SQL limits, and the conditional claim prevents two consumers from analyzing/deleting the same handoff (`mobile_upload_store.py:158–176`). But image decoding occurs once in the direct upload handler and again in the pipeline (`endpoints.py:36–39`; `pipeline.py:51–53`). Every request can still run expensive analysis; RapidOCR serializes its engine behind a lock (`receipt_text.py:16–21`), which limits engine concurrency but can create queuing under load.

Abandoned upload cleanup is triggered only by later create/save operations (`mobile_upload_store.py:59,91,183–202`) and is best effort. No scheduled 24-hour deletion guarantee exists; this is honestly disclosed in `README.md:353,358`. Deletion errors are swallowed/logged (`mobile_upload_store.py:113–125`). B claimed upload is marked consumed before inference; if inference fails it is deleted in `finally`, so retries cannot recover the same evidence (`158–176`). Original/heatmap base64 is returned inline (`pipeline.py:229–251`, layer construction at 85–100); request limits do not establish response-size/memory/latency safety. Deployment-equivalent payload/load measurements remain required.

## Security and privacy detail

Supabase migrations enable RLS for case and handoff tables with no anonymous read policies, create a private bucket, cap objects at 20 MiB and restrict MIME types (`supabase/migrations/202611100001_create_forensic_cases.sql:21–22`; `...0002_add_private_mobile_handoff.sql:12–17`; `...0003_limit_private_evidence_uploads.sql:3–6`). The later insert policy checks a recent unconsumed handoff path (`...0004_allow_session_scoped_uploads.sql:3–29`). These files establish intended schema, not that migrations are applied on a live project.

Case persistence omits original bytes, three image overlays, and QR payload/result findings (`services/supabase_store.py:15–35`). It still persists filenames, hashes, other findings, metadata, reference values and layer summaries. Therefore “no image storage in forensic_cases” is true; “no sensitive information persisted” would not follow. Receipt warning text and metadata may themselves be sensitive. Save failures return false and are ignored by callers (`supabase_store.py:47–51`; `endpoints.py:263–265`), so an otherwise successful report does not guarantee a durable audit record. No case retention/deletion policy is implemented in the inspected code.

B separate legacy `server.py` is a conditional additional concern: it serves the entire repository through `SimpleHTTPRequestHandler(directory=ROOT)` (`13–15,46`), exposes global latest/evidence routes (`21–35`), writes uploads and metadata permanently (`78–79`), and binds 0.0.0.0 (`96`). If launched on an accessible machine it can expose source, retained evidence, and any readable files in that served root; no paired-session protection is present. This is **not** the active FastAPI/Vercel route and should not be reported as a demonstrated production leak. Remove/deprecate or confine this alternate implementation to avoid divergent security claims.

## Compliance with the requested scientific workflow

| Requirement | A implementation and status |
|---|---|
| Suitable authorized representative data, otherwise stop | Correctly stops. Detailed candidate register and permission caveats in `LOCALIZATION_DATA_AND_RELEASE_PLAN.md:3–25`. Published dataset facts/terms were not independently revalidated by this static audit. |
| Pixel model only after permission | No localizer/checkpoint inference implemented; adapter disabled. Correct conditional outcome, not a delivered trained model. |
| Group by app/template/device/contributor/original/edit session/near duplicate | Structural validator checks every declared identity; plan describes connected components and disjoint cohorts (`93–108`). No actual split exists. |
| Pixel masks and integrity | Required nonempty path only in code; file/mask validation planned, not implemented. |
| FPR/FNR, precision/recall, PR-AUC, localization IoU/F1 | Prospective protocol documented (`139–147`); no measured independent results. API metrics correctly null (`endpoints.py:131–148`). |
| Calibration, uncertainty and subgroup evaluation | Plan specifies Brier/ECE/reliability, intervals and subgroup counts (`142–158`); no calibrated classifier or results. |
| No confidence until validated | Backend classifier/region confidence null; correct. Heuristic score and two-label semantics remain unvalidated. |
| Preserve two labels; separate settlement | Labels preserved; settlement disclaimer and evidence-source state present. Failed-payment OCR still changes the shared verdict, so visual and transaction evidence are not fully separated operationally. |
| Tests/build, no release with failed gates | Backend regressions pass: 93 tests in both audit environments; production frontend build passes. Repo documents prior 93-pass/build result (`193–209`), which is not independent current-run evidence. No enforced promotion gate. |

## Testing quality and strengths

The suite meaningfully tests corrupt/tiny/oversized inputs, early dimension rejection, mobile session isolation, losing concurrent consumer behavior, cleanup on corrupt claimed image, transform arithmetic, null confidence, metadata/QR/C2PA behavior, and manifest group leakage. Real OCR inference is exercised on generated text in PNG and JPEG (`tests/test_receipt_text.py:15–25`), which is more useful than mocking every recognition call.

Its limits are equally important. All five published demo expectations are REVIEW_REQUIRED (`endpoints.py:194–254`), so matching every demo verdict does not demonstrate classification discrimination. The “authentic screenshot transforms” test uses a synthetic image and only asserts it is not CORROBORATED_ANOMALIES (`test_synthetic_samples.py:46–64`), not that the two-label UI remains favorable. Mobile/Supabase concurrency tests mock the HTTP storage interface (`test_workflow_regressions.py:61–96`); they do not establish deployed SQL behavior or simultaneous races. `frontend/package.json:6–10` has no frontend test script. Static type checks do not catch the actual response-contract defect. There is no independent held-out authentic/tampered test corpus, adversarial generalization study, or pixel-level evaluation.

Five strongest aspects are: (1) explicit refusal to invent a trained model, calibration or metrics; (2) an unusually concrete permission/grouping/mask/evaluation/rollback plan with a justified stop; (3) null classifier/region confidence and qualified forensic finding language; (4) substantive bounded input validation plus private mobile storage and atomic consumption; and (5) real OCR and broad backend workflow regressions with honest synthetic-fixture labeling.

## Unverified matters and recommended disposition

No live attack, real customer upload, credential use, model training, deployment, or external data download was performed in this inspection. The API probes below used in-process TestClient and generated data only. Live RLS/migrations, project-level rate limiting/auth controls, deployed bundle parity, actual network privacy, final payload limits, load behavior, dataset-license grants and independent scientific performance remain unverified. Repository historical verification files are claims, not substitutes for present reproducible results.

Retain A as an explicitly unvalidated heuristic review prototype and permission-blocked model plan. Fix the schema/UI mismatch now. Before model promotion, bind data checks to files/masks, implement the release interlock, separate evidence/coverage from the displayed decision explanation, and obtain independent metrics. Before broader public use, test resource limits and storage lifecycle, and disable the insecure alternate server path. Training remains stopped unless the data-permission gate is actually satisfied.

## Independent audit execution results

Fresh parent-produced logs confirm **93 backend tests pass** under NumPy 1.26.4 (48.02 seconds; `results/B_pytest.log`) and under NumPy 2.2.6 (48.04 seconds; `results/B_numpy2_pytest.log`). The production TypeScript/Vite build passes (`results/B_build.log`), with a >500 kB main-chunk warning (515.57 kB uncompressed JavaScript). These verify software checks, not scientific accuracy.

The reproducible command `.venv-numpy2/bin/python scripts/b_api_probes.py` ran isolated subprocesses for B and A with Python 3.12.15/NumPy 2.2.6, credential environment variables removed, outbound socket connections blocked, and no authentication headers. `results/b_api_probes.json` contains status, response summaries, exceptions/error bodies and child stdout/stderr paths. These few generated examples are correctness probes, not a representative performance estimate.

| Probe | A observed | B comparator observed |
|---|---|---|
| Health/model status/evaluation | 200; database NOT_CONFIGURED, heuristic-only/no confidence | 200 |
| Empty/corrupt/truncated PNG | 422 with bounded client errors | 500; empty upload exposes OpenCV diagnostic path |
| Valid 8×8 PNG | 422, minimum 16 pixels per side | 200, AUTHENTIC_VERIFIED, confidence 95.2 |
| QR-only generated PNG | 200; one URL decoded; INCONCLUSIVE, score 0, confidence null | 500: `name 'Any' is not defined` |
| Generated “Payment failed” text | REVIEW_REQUIRED, score 55, confidence null | AUTHENTIC_VERIFIED, confidence 93.1 |
| Generated “Payment successful” text | INCONCLUSIVE, score 0, confidence null | AUTHENTIC_VERIFIED, confidence 93.1 |

A's semantic pair directly reproduces the shared verdict's sensitivity to payment wording. Its QR-only input unexpectedly reports RapidOCR AVAILABLE with two recognized lines despite containing no designed readable receipt text; the report does not expose those lines, so their content is unverified. The rule finds no warning and the UI helper maps that report to Likely accurate. This is an observed coverage-status weakness on one synthetic QR, not an OCR error-rate estimate.

The anonymous valid-analysis responses confirm that application authentication is not required for `/api/analyze` in this local configuration. They do not establish internet reachability or the absence of deployment-layer protection. B's QR failure is supported by `snapshots/B/backend/app/services/forensic/pipeline.py:118`, which annotates a nested function with undefined `Any`, and the endpoint exception echo at `snapshots/B/backend/app/api/endpoints.py:215–216`. A's corrected annotation-free QR filtering is at `pipeline.py:108–116`.

## Executed frontend helper and contract check

`node scripts/ui_contract_probe.cjs` transpiled each snapshot's **actual** `verdictLabel.ts` with its installed TypeScript package and executed the resulting module in a Node VM. Both helpers return Likely misleading for AUTHENTIC_VERIFIED, SUSPICIOUS_ANOMALIES, MANIPULATED_FORGERY, REVIEW_REQUIRED and CORROBORATED_ANOMALIES; only INCONCLUSIVE returns Likely accurate. `results/ui_contract_probe.json` records source hashes, tool versions, the full six-case table and exact rendering-reference lines. A's native three evidence states match its helper's intended mapping; B's older backend verdicts do not. B's AUTHENTIC_VERIFIED therefore maps to the misleading headline despite the source's green/default styling branches.

The same probe extracts the actual backend and frontend synergy field declarations: B supplies all fields referenced by its frontend; A lacks `synergy_multiplier_applied`, `multiplier_factor`, and `primary_forgery_locus` and instead supplies `region_overlap_found` and `primary_review_locus`. Report and sidebar source references are recorded alongside this mismatch.

These are executed helper results plus inspected component source, **not a browser screenshot, mounted component test, or visual verification**. Statements above about resulting text/visibility describe the direct code-path consequence; interactive/browser presentation was not independently exercised by this inspector.


## Bounded browser confirmation

Both built interfaces completed home, default sample1 analysis, report-modal and evaluation navigation with zero observed console errors/warnings. A displays a red Likely misleading55 result for the synthetic non-real-transaction watermark, with settlement limitations. This does not exercise the known positive-overlap rendering defect. See `results/browser_smoke.md/json` and `output/playwright/` for screenshots, the documented B static-serving harness, cleanup and untested features. This is a bounded smoke check, not exhaustive browser or cloud validation.
