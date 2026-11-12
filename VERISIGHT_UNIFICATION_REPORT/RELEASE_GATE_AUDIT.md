# Release and analysis gates

The two originals expose different claims: Hackstellar reports BLOCKED model readiness but does not enforce promotion; ScamShield reports an experimental loaded model and an unrelated heuristic verdict. Unified separates **report-use** from **model-promotion**.

## Report-use policy `analysis-review-v1`

`backend/app/evaluation/gates.py:evaluate_analysis_gate` is called by the actual screenshot pipeline on every returned analysis. It emits typed PASS, WARNING or BLOCK, processing COMPLETE/INCOMPLETE/FAILED, reason codes and evidence IDs. PASS only means configured processing finished without a review decision. It never verifies image authenticity or settlement. `automated_approval` is always false.

- PASS: recognized OCR coverage, valid finite score and evidence, no review decision/conflicting high-severity finding.
- WARNING: review verdict with specific supporting evidence IDs.
- BLOCK/INCOMPLETE: missing/unavailable/unknown OCR status. The reason explicitly describes a processing limitation, not fraud.
- BLOCK/FAILED: invalid score, unsupported verdict, duplicate/missing finding fields, out-of-image region, unexplained review verdict or high evidence contradicting an inconclusive verdict. `view_report` is false for such invalid results.
- Missing gate data defaults to BLOCK. A blocked result cannot retain the favorable INCONCLUSIVE presentation.

OCR recognition is not semantic completeness: a few recognized lines do not prove all meaningful fields were read. This remains a documented limitation; no gate is an authenticity classifier.

## Model promotion policy

`require_model_release` raises unless each of ten independent conditions is literally True: permission, image/mask integrity, source groups, locked test, fixed validation threshold, calibration, passing metrics, artifact identity, deployment limits and rollback. Truthy strings do not pass. Inputs must come from a trusted independent release auditor, never user HTTP payloads. This helper cannot establish legal permission or experimental validity by itself. There is no deployed tampering model and no new training. No claim is made that Vercel organization-level deployment policy is enforced by this helper.

Tests: `backend/tests/test_analysis_gates.py` covers PASS, evidence WARNING, unavailable OCR, malformed numeric outputs, contradictory evidence, invalid regions, safe defaults, every missing model condition and truthy input rejection. See TEST_RESULTS for final suite results.
