# Version B audit: verified remote implementation

ScamShield scaling,2260e5227ac34215e58bfe86974af2d9c4bbfa00. All inventoried application hashes match the prior independently tested snapshot. Current version letters below are normalized to this unification request. Evidence filenames retain historical naming and are located in `/Users/shreeshaks/Documents/COMPARATIVE_AUDIT`, where historical A=ScamShield and B=Hackstellar. Source references resolve against current `VERISIGHT_UNIFICATION_SOURCES/A` or `/B`. Fresh unification tests are reported separately.

# Project B deep audit — VeriSight

Audit date: 2026-11-12. Scope: read-only snapshot `snapshots/B`; original project and snapshot source were not edited. All relative source references below are under `snapshots/B/`. This is an implementation and evidence audit, not a legal or payment-authentication certification. Parent audit records full-suite/build results separately. Independent probes are in `scripts/a_math_probes.py` and `results/a_math_probes.json`; they load existing artifacts and never train.

**Conclusion — Strongly supported:** B contains a substantive classical image-forensics workbench and a real serialized learned fusion model, but its principal verdict remains a hand-tuned heuristic. The supplied evaluation cannot substantiate production screenshot authenticity: it uses 27 examples from one synthetic template, supplies unavailable semantic flags to offline inference, evaluates different thresholds and a different baseline from the live verdict, and contradicts its own saved per-sample results. Experimental status is appropriate; categorical authenticity and high numerical confidence are not supported by the supplied evidence.

Evidence labels: **Verified** = observed source/data fact or executed narrow probe; **Strongly supported** = inference supported by multiple concrete facts; **Unverified** = assertion without sufficient evidence in the audited material; **Hypothesis** = plausible mechanism needing a targeted experiment; **Not reproducible** = a specific reported result does not reproduce under the stated check, with environment/scope limitations identified. Source verification is not equivalent to successful end-to-end execution.

## 1. Actual decision path

**Verified:** `/api/analyze` reads the upload and calls `analyze_screenshot` in a thread (`backend/app/api/endpoints.py:205–216`). Pipeline execution is:

1. Decode and SHA-256 hash uploaded bytes; inspect metadata, viewport, C2PA markers, and QR (`backend/app/services/forensic/pipeline.py:53–76`).
2. Compute ELA, approximate db4 residuals, ORB copy-move, and JPEG ghost diagnostics (`:79–109`).
3. Extract connected-component boxes with `use_neural=False`, then geometry/colour diagnostics (`:113–151`).
4. Parse temporal/UTR rules, form Layer 3, and create a semantic layer with `vlm_used=False` and score `0.5 * l3_score` (`:154–207`). There is no live VLM inference in this path.
5. Set overall score, confidence, verdict, and findings through `calibrate_ensemble` (`:210–216`). These are then used for syndicate/legal-notice output (`:218–235`).
6. Only afterward assemble eleven features and call the learned-model service (`:241–265`). The returned dimensions and model metadata are appended; the overall verdict and confidence remain those of step 5 (`:267–288`).

**Verified:** B live learned probability exists when the checkpoint loads successfully, but it does not determine `overall_tamper_score`, `verdict`, or `confidence_score`. Calling this product's main verdict a learned calibrated classifier conflates two outputs.

## 2. Five most serious weaknesses

### W1. Offline evaluation does not evaluate the live evidence acquisition path

**Verified:** `ml/experiments/run_evaluation.py:59–64` copies `clock_paradox`, `upi_invalid`, and `is_whatsapp` from the labeled manifest into feature extraction. `ml/src/feature_extraction/extractor.py:135–151` directly uses those flags. These are scenario annotations, not independently extracted image evidence.

**Verified:** Live `pipeline.py:113` requests non-neural extraction. `typography/ocr_engine.py:25–74` returns boxes with strings `token_0`, `token_1`, etc. This is text-region detection, not text recognition. Temporal and UTR rules search `t.text` with time/digit regexes (`metadata/domain_rules.py:74–94,133–164`); placeholder text cannot supply those semantics. PNG textual metadata can provide a separate fallback (`:96–105`), but the corpus renderer saves images through `cv2.imwrite` without those annotations (`generate_benchmark_corpus.py:187–191`).

**Verified:** Corpus WhatsApp examples are JPEG-transcoded in memory and then saved as PNG (`generate_benchmark_corpus.py:116–119,187–191`). Live channel detection returns false for PNG (`domain_rules.py:31–32`), while offline extraction receives `is_whatsapp=True`; this changes both feature 10 and ELA quality (75 versus 90), not merely display metadata.

**Verified:** The parity test skips the temporal feature explicitly (`backend/tests/test_feature_parity.py:144–146`), feeds simulated channel truth rather than detecting it (`:85–88`), and re-validates the reported live vector (`:35–50`) rather than capturing the actual service input. It therefore does not demonstrate the advertised complete serving parity.

**Strongly supported:** Offline scores overstate what the live system can infer about semantic-only fake receipts. The problem is oracle-feature/evidence mismatch; it should not be loosely described as proof that `y_test` was passed directly to `.fit()`.

### W2. Evaluation scale, grouping, and documentation do not justify generalization

**Verified:** Every one of the 27 manifest records is `PIL_SYNTHESIS` and `GPAY_UPI`; all are rendered with one 720×1560 layout (`generate_benchmark_corpus.py:41–121,193–205`). There are 20 development and seven final-test samples (three negative, four positive). No donor/device/original-source grouping keys are present in the actual manifest. `docs/DATASET_GOVERNANCE.md:78` requires common templates/parent seeds to remain within a split, yet this template spans every split.

**Verified:** The fit code isolates `FINAL_TEST` from development rows (`run_evaluation.py:77–82`). This is a useful row-level separation, not a demonstration of template- or acquisition-independent validation. No field-collected independent validation is supplied in this corpus. B PhonePe description for `auth_10` in `docs/UPDATED_EVALUATION.md:67` conflicts with its actual GPAY_UPI manifest/template.

**Verified:** Saved GBDT held-out IDs end with `manip_wa_splice_03`, then `manip_clone_03`; their probabilities are 0.6005 and 0.4318 respectively (`ml/evaluation/benchmark_evaluation_report.json:24–31,203–210`). `docs/UPDATED_EVALUATION.md:60,71–72` swaps these assignments and attributes the miss to WhatsApp blur. That mechanism is unsupported by the saved predictions.

**Verified:** Saved GBDT OOF FPR at at-least-95% recall is 0.60 at threshold 0.0248 (`benchmark_evaluation_report.json:168–169`), while the updated prose claims 0.20 at 0.40 (`UPDATED_EVALUATION.md:91–93`). On ten development positives, empirical recall moves in increments of 10%; exactly 95% recall is not an attainable deterministic sample proportion. The code correctly searches for recall at least 95%, which requires 100% here.

**Verified mathematical limitation:** Zero false positives among three test negatives has a two-sided exact 95% binomial upper bound of approximately 70.8% (`1 - 0.025^(1/3)`). This is not evidence of near-zero deployment FPR. AUC=1.0 here means twelve positive-negative pairs are ordered correctly; it is compatible with a false negative at 0.5. These intervals/pair counts assume independent samples; shared-template dependence makes external generalization still less secure.

### W3. User-facing verdict contract is broken; confidence and probability claims exceed implementation

**Verified, critical integration defect:** Backend returns only `AUTHENTIC_VERIFIED`, `SUSPICIOUS_ANOMALIES`, or `MANIPULATED_FORGERY` (`calibrator.py:150–159`), but `frontend/src/services/verdictLabel.ts:1–5` maps only `INCONCLUSIVE` to “Likely accurate” and every other value to “Likely misleading”. Thus every completed B result displays “Likely misleading”, even a backend-authentic result. Simultaneously, `RiskDossierSidebar.tsx:105–114,240–260` recognizes only `REVIEW_REQUIRED`/`CORROBORATED_ANOMALIES` for warning styling; all three actual B verdicts receive green/check-mark treatment and “Signals consistent with native screenshot capture; no digital splicing identified.” This is a deterministic frontend/backend enum mismatch, not a model accuracy issue. TypeScript/build and backend tests can pass without catching the runtime contract. The actual UI label policy is always-positive on these completed backend outcomes and must not be credited with native-score performance.

**Verified:** `ensemble/calibrator.py:127–159` computes a weighted sum, multiplies by 1.35 on spatial synergy, forces a minimum score of 88, and assigns confidence through fixed expressions. It contains no Bayesian posterior calculation, prior, likelihood model, or empirically learned confidence mapping. Normal weights are (.35,.35,.25,.05); WhatsApp weights are (.35,.45,.15,.05). Layer 4 duplicates half of Layer 3, so these are not four independent evidence sources.

**Verified:** B pair of anomaly boxes with IoU > .15 **or centroid distance ≤25 pixels** triggers the 88-point floor (`:91–140`) and a locus confidence of .99 (`:114`). Thus proximity alone can leap to `MANIPULATED_FORGERY`, even at low weighted scores. The prose reports intersecting footprints even when only proximity triggered (`:119–121`). No data-supported likelihood ratio justifies that jump.

**Verified:** Main verdict thresholds are 25 and 70 (`:150–159`); offline baseline metrics use score ≥50 (`run_evaluation.py:90–106`); learned test classification uses probability ≥.50 (`learned_fusion.py:145–171`); runtime alert uses ≥.85 (`ml_calibrated_service.py:214–215`). None is interchangeable. Applying the actual .85 alert threshold to the seven saved GBDT test probabilities yields zero detected positives out of four; this is a check of saved scores, not a new deployment benchmark.

**Verified:** Model failure leads to `sigmoid(0.075*(overall_score-52))` (`ml_calibrated_service.py:210–212`). No fitted parameters or calibration evaluation for this fallback are supplied. Metadata still takes model ID, architecture, and `CALIBRATED_SIGMOID_CV3` from the registry (`:222–236`); only `inference_status=FALLBACK_HEURISTIC` distinguishes it. `/model/status` hardcodes `ml_environment_ready=True` (`endpoints.py:37–49`).

### W4. Serving validation and provenance contain concrete implementation defects

**Verified:** `ml_calibrated_service.py:22–47` imports `FEATURE_BOUNDS` and `FEATURE_DEFAULTS` from `ml/src/feature_extraction/schema.py`, which defines neither. The caught `ImportError` sets `validate_and_format_feature_vector=None`. Runtime then uses a reduced NaN/None conversion, with no canonical range clamp or infinity replacement (`:192–208`). The real validator would clamp/impute (`schema.py:144–183`), and offline extraction uses it. Schema-version mismatch only logs a warning (`ml_calibrated_service.py:89–94`); no strict feature-name/order compatibility check is performed before model execution.

**Verified by executable probe:** `provenance/c2pa_inspector.py:11–37` accepts the unsigned byte string `b'c2pa C2PA_TEST_VALID'` as `VERIFIED_AUTHENTIC`, with `signature_valid=True` and `VALID_TRUST_ANCHOR`. No manifest parsing, hash binding, certificate chain, signature verification, or trust-list validation occurs. This is a test-marker stub exposed in the production analysis path (`pipeline.py:75,179–195`). It does not override the main verdict, but its provenance output falsely claims cryptographic verification.

**Verified on Python 3.12:** B QR-containing image takes the branch defining `_in_any_qr(t: Any)` (`pipeline.py:116–118`), but the module does not import `Any` or defer annotations. Compiling/executing that exact nested definition yields `NameError`. B further defect would remain after adding the import: `TextToken` has `bbox`, not `box` or `.get()` (`ocr_engine.py:14–23`; `pipeline.py:119`). Offline exclusion also looks for nonexistent `qr_detected`/`bounding_boxes` keys (`extractor.py:109–118`); the QR inspector returns `decoded_count` and `regions` (`qr_inspector.py:47–54`). End-to-end QR reproduction is delegated to the parent test run; the narrow source/annotation failure is independently reproduced.

### W5. Reproducibility and benchmark semantics are incomplete

**Verified:** Backend installation requirements omit `joblib` and `scikit-learn`, although loading the live checkpoint needs them (`backend/requirements.txt`; `ml_calibrated_service.py:81–106`). Separate `ml/requirements.txt` declares them but uses lower bounds, despite calling itself pinned. README backend setup installs only backend requirements (`README.md:185–191`). B successfully installed backend can therefore silently use the heuristic fallback.

**Verified:** `POST /benchmark/run` returns stored JSON and does not run feature extraction, inference, or evaluation (`endpoints.py:64–84`). Its success status is not evidence of a fresh benchmark. Running `run_evaluation.py` would fit models and overwrite both checkpoints and the report (`:121–132,170–173`); this audit intentionally does not execute that script.

**Verified:** `wavelet_min_variance` is always default 0.5 in both canonical offline extraction and live features (`extractor.py:103`; `pipeline.py:246`), because `wavelet_noise.py:119–127` never exports `min_variance`. The record nonetheless says available=True and reliability=.82 (`extractor.py:163`). An equality-based parity test can pass for a constant placeholder feature while validating no measurement.

**Strongly supported:** Source, artifacts, registry, narrative tables, and runtime score roles are not bound together strongly enough to reconstruct the published scientific claims merely by checking a SUCCESS response. The exact checkpoint replay and environment evidence below should be preferred to prose claims.

## 3. Mathematics and algorithm implementation

| Component | Implemented calculation | Audit assessment |
|---|---|---|
| ELA | JPEG recompression at Q90 or Q75, absolute difference, 16×16 means, threshold max(8, mean+z·SD), density/z heuristic (`pixel_analysis/ela.py:24–119`) | **Verified:** real signal processing. Despite “multi-scale” wording, this function uses one reference quality per invocation. Compression texture is not a calibrated probability of manipulation. |
| Wavelet | Explicit db4 filter coefficients, reflected-border convolution/downsampling; local 9×9 `E[x²]-E[x]²`; morphology and low-noise-region count (`wavelet_noise.py:25–117`) | **Verified:** meaningful residual analysis, described in code as approximating PyWavelets. **Unverified:** exact equivalence to a particular DWT convention or camera PRNU. Synthetic screenshots are not sensor photographs. |
| Copy-move | ORB/Hamming self-match filtering, ratio/distance limits, 5px displacement bins, ≥10 compact matches (`copy_move.py:23–101`) | **Verified:** actual matching/localization. Header says ≥4 and ±3px, unlike implementation. Repeated legitimate UI can be a confounder; its prevalence is **Unverified** without diverse real data. |
| Baseline | Integer connected-component bottom edges, row grouping, zero slope and median intercept (`baseline_laser.py:37–95`) | **Verified:** it is median horizontal alignment, not fitted OLS/subpixel character-baseline regression. Fractional median/output rounding does not establish subpixel measurement accuracy. |
| CIELAB | Convert OpenCV Lab to standard units; compare side-margin median to above/below reference background using Euclidean ΔE76 (`cielab_patch.py:22–27,45–101`) | **Verified:** substantially better semantics than comparing black ink with white background. Independent probe demonstrates zero ΔE for dark ink on uniform white margins and positive ΔE for a changed margin patch. Brightness gate L*>45 and fixed geometry limit coverage, especially dark UI. |
| UTR/time | Regex, length/diversity checks, minute-of-day comparison (`domain_rules.py:36–53,107–185`) | **Verified:** no banking API, checksum algorithm, Julian-day/year-prefix verification, or calendar-date reconciliation is implemented here. README's fuller claims (`README.md:87–95`) exceed the code. |
| Fusion | Hand-set weights, proximity/IoU threshold, fixed floors and confidence formulas | **Verified:** deterministic score engineering; “Bayesian calibration” is unsupported terminology. |
| Learned model | Logistic regression or histogram gradient boosting on eleven engineered features, StandardScaler, separate sigmoid CV calibration (`learned_fusion.py:37–54,77–120`) | **Verified:** real conventional supervised ML, not an image foundation model or end-to-end neural forensic detector. |

**Verified calibration distinction:** Four-fold development OOF predictions use *uncalibrated* fold models (`learned_fusion.py:77–106`). The final model then fits `CalibratedClassifierCV(cv=3, method='sigmoid')` on development data (`:116–120`). Therefore OOF Brier/AUC/FPR are not estimates of the final calibrated pipeline's OOF performance. Scaling is correctly fit inside each outer OOF training fold (`:81–83`), but final calibration pre-fits a scaler on all development rows before its internal folds; this exposes internal calibration-fold covariates to scaler fitting. It does not expose held-out test rows and its practical effect on tree predictions may be limited. B nested pipeline would make the independence claim cleaner.

**Verified selection ambiguity:** Saved logistic held-out Brier=.1035 and accuracy=1.0 outperform GBDT Brier=.1648 and accuracy=.8571; logistic development AUC=.95 exceeds GBDT=.91, while GBDT development accuracy/F1 are higher. Calling GBDT “champion” requires an explicit preselected objective. The script hardcodes `best_development_model='learned_fusion_gbdt'` (`run_evaluation.py:160–163`). **Unverified:** that the final test was consulted only once historically; row separation in current code cannot establish that history.

## 4. Five substantive strengths

1. **Verified:** The project implements several independent families of classical diagnostics with concrete spatial outputs: ELA, local noise, ORB duplication, typography, colour margins, metadata and QR. These are meaningful inspectable components rather than a single opaque API claim (`pipeline.py:65–195`). Their forensic accuracy remains a separate question.
2. **Verified:** Analysis preserves a SHA-256 of original bytes, structured findings and boxes, and renders multiple evidence images (`pipeline.py:53–55,267–288`). This assists repeatable investigation, although a hash alone is not a complete custody record or authenticity proof.
3. **Verified:** The learned subsystem has stored estimator artifacts, explicit feature ordering/schema/version, row-held-out evaluation, fold-local scaling for OOF estimates, and calibrated-classifier code (`schema.py:13–31,144–183`; `learned_fusion.py:73–120,189–209`). These are useful foundations after repairing serving parity and validation.
4. **Verified:** Payment settlement is explicitly separated from image consistency: `INDEPENDENT_SOURCE_QUERY_REQUIRED` and an explanation are always returned (`ml_calibrated_service.py:146–151`); model metadata declares `EXPERIMENTAL` and synthetic-only validation (`:236`). These disclosures should govern stronger categorical labels elsewhere.
5. **Verified:** Synthetic generation has labels, masks, named splits and explicit ownership, and the repository includes unit/parity/endpoints tests plus perturbation-study code (`generate_benchmark_corpus.py:124–214`; `backend/tests/`; `run_ablation_study.py`). This provides a usable regression framework. The ablation script starts from only `auth_01` and `manip_splice_01` (`run_ablation_study.py:32–54`), so it does not establish broad robustness.

## 5. Reproducibility record and interpretation boundaries

Run `PYTHONDONTWRITEBYTECODE=1 .venv-numpy2/bin/python scripts/a_math_probes.py` from `COMPARATIVE_AUDIT`. This reads snapshot code and checkpoint, normalizes Windows separators in manifest paths, evaluates seven existing held-out files twice, and writes only audit results. The first replay supplies the manifest's semantic/channel flags, matching offline evaluation's evidence assumptions. The second supplies no oracle flags. Neither run fits, calibrates, regenerates images, or alters artifacts.

Read `results/a_math_probes.json` for exact predictions, feature vectors, metrics, serialized identity, and probe outcomes. “Without oracle” is an offline-feature ablation, **not** the full production path: it does not claim equivalence to every live step, particularly the additional QR and metadata orchestration. Full runtime/test outcomes belong to the parent execution report. Any difference from saved scores must be reported as environment-qualified non-reproduction, not as fabricated model weights or proof of intentional misconduct.

**Verified replay result:** Under Python 3.12.15, NumPy 2.2.6 and scikit-learn 1.9.1, the existing checkpoint reproduces the saved oracle-feature held-out metrics: AUC=1.0, Brier=0.1647993, confusion matrix `[[3,0],[1,3]]` at .50. This confirms that the saved result is recoverable from a real trained artifact in a compatible environment. Removing oracle flags changes Brier to 0.1821383, while AUC and the .50 confusion matrix remain unchanged on these seven cases. Therefore this ablation demonstrates probability/feature drift but **does not** demonstrate an accuracy collapse on the supplied seven samples. At runtime alert threshold .85, both runs yield `[[3,0],[4,0]]`. The artifact's internal ID is `verisight-fusion-gradient_boosting-v1`; registry/service identity is `verisight-fusion-gbdt-v1`, another unvalidated naming discrepancy.

**Environment-qualified non-reproduction:** The first probe in NumPy 1.26.4 failed to deserialize the checkpoint with a `PCG64` BitGenerator error. Repeating under NumPy 2.2.6 succeeded. This is an environment compatibility failure, not proof the model artifact is invalid. The backend lower-bound requirements admit environments in which the model fails and the service falls back. Parent audit reports all 38 B backend tests passing under the compatible NumPy 2 environment and a passing frontend build; these results do not negate the source-confirmed semantic and integration defects.

**Unverified from supplied evidence:** field sensitivity/specificity, donor/device/template-held-out results, calibration curves with adequate confidence intervals, spatial localization IoU against masks across the corpus, reliable domain-shift abstention, actual cryptographic provenance verification, and reproducible real-world operating-threshold performance. No such result should be inferred from demo visuals or static endpoint success.

## 6. Highest-value repair order

1. Repair the frontend/backend verdict enum contract immediately, then unify live/offline feature construction, recognize actual text when semantic rules are used, represent missing evidence explicitly, and evaluate images without oracle flags.
2. Fix schema imports, exact feature-order validation, QR contracts, and C2PA marker stubs; make readiness/fallback identity reflect execution truth.
3. Publish a single decision policy with explicitly distinct heuristic score, classifier probability, and alert threshold; remove unsupported authenticity/confidence claims.
4. Create donor/device/template/source-grouped real capture evaluation with enough negatives to estimate operational FPR, preregister threshold/model selection, and reserve an untouched final set.
5. Bind code, dependency versions, artifact hashes, dataset hashes, per-sample predictions and generated tables; make benchmark endpoints accurately state whether they run or read results.


## Bounded browser confirmation

Both built interfaces completed home, default sample1 analysis, report-modal and evaluation navigation with zero observed console errors/warnings. B's green Likely misleading18.4 badge alongside an Authentic case badge and no-splicing explanation was directly observed. Its report modal nevertheless labels classifier confidence Unavailable; numerical heuristic confidence remains an API defect, not a claim that the modal displays that number. See `results/browser_smoke.md/json` and `output/playwright/` for screenshots, the documented B static-serving harness, cleanup and untested features. This is a bounded smoke check, not exhaustive browser or cloud validation.
