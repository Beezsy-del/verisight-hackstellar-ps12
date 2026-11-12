# Three-version benchmark results

A=Hackstellar347c7a7, B=ScamShield2260e5, U=unified. Identical117 synthetic input bytes and12repeat calls per version,129calls each. Source clones are untouched; originals execute in disposable report/runtime copies. Images and masks are copied into data; raw manifest includes SHA-256. Same Python3.12, NumPy2.2.6/scikit-learn1.9.1/OpenCV4.10 environment as prior audit, single OpenCV/BLAS threads, real OCR remains enabled. No training or threshold selection.

|Version|Completed|Edits flagged, common subset|Clean false alarms|Median|p95|Peak RSS|
|---|---:|---:|---:|---:|---:|---:|
|A|117/117|11/63|0/9|0.636s|1.917s|801.4MiB|
|B|108/117|21/63|1/9|0.262s|0.873s|334.9MiB|
|U|117/117|11/63|0/9|0.635s|1.868s|799.9MiB|

## Interpretation

The common controlled subset contains9 clean and63 edited variants from only3 synthetic seed families. Nine QR insertions crash B and are excluded from the common comparison but remain execution failures. These counts do not estimate field accuracy. Native backend decisions are used: non-INCONCLUSIVE for A/U and non-AUTHENTIC_VERIFIED for B. B's actual UI incorrectly maps all legacy verdicts to Likely misleading; do not interpret its native detector numbers as correct UI behavior.

U's headline verdicts and scores are identical to A on all117 unique inputs. Therefore **no detection-accuracy improvement is demonstrated**. Engineering gains are explicit, auditable gates, failure handling, contract repair and resource admission/output bounds. Lower sensitivity than B on some edits remains a known limitation, not hidden by increased test count.

The benchmark calls the actual pipeline, not HTTP middleware; output-budget/429/failure-gate behavior is tested separately. PASS means report processing completeness only; all U gates prohibit automated approval and payment settlement remains unverified. No synthetic benchmark was used to tune thresholds. Existing real-world deployment gates remain blocked.

Local timing is descriptive; ordinary desktop/build/test activity may overlap. Do not claim a speedup or cloud SLA. Peak RSS is per-process high-water memory on macOS, not incremental memory perrequest. Full records contain every input result, errors, gate, boxes, latency and payload size. Old source-identical baseline evidence in COMPARATIVE_AUDIT independently corroborates counts.

## Reproduce

Use the compatible environment pinned in the previous audit requirements-audit-numpy2.lock, or create an equivalent isolated environment. Build A's disposable frontend before its suite because SPA-route tests require dist. Run `scripts/run_comparison.py A B U` with that interpreter, then `scripts/summarize.py`. The script runs full suites and benchmarks, never fits a model. `scripts/benchmark.py generate` can regenerate controlled fixtures; the supplied manifest/data preserve the exact measured bytes. All raw timing/counts are in raw/summary.json and per-version JSONL.

Incomplete coverage: real device/app/contributor diversity, screen recapture, independently authorized payment screenshots, real bank outcomes, learned-mask IoU and calibrated authenticity probability remain unavailable. The original audit's box-proxy localization evidence is not promoted into learned-mask accuracy.
