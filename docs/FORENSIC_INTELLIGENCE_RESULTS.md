# Forensic intelligence tester — measured results

**Decision: do not promote the candidate fusion.** The tester adds actual OCR, acquisition measurements, local comparisons, geometrically verified repetition and reproducible evaluation. It does not demonstrate improved real-world authenticity discrimination. The original 43/39 pair was not supplied. No training, push or deployment occurred.

## Experiments A–H

| Experiment | Subset | N (unedited/edited) | Baseline ROC-AUC / FPR / FNR | Candidate ROC-AUC / FPR / FNR | Baseline / candidate pair wins | Mean margin old / candidate |
|---|---|---|---|---|---|---|
| A | All locked synthetic | 48 (24/24) | 0.587 / 0.000 / 0.792 | 0.604 / 0.000 / 0.792 | 0.250 / 0.208 | 6.67 / 4.10 |
| B | Original | 8 (4/4) | 0.562 / 0.000 / 0.750 | 0.625 / 0.000 / 0.750 | 0.250 / 0.250 | 9.50 / 4.75 |
| C | JPEG75 | 8 (4/4) | 0.625 / 0.000 / 0.750 | 0.625 / 0.000 / 0.750 | 0.250 / 0.250 | 7.00 / 5.00 |
| C | Resize + JPEG | 8 (4/4) | 0.562 / 0.000 / 0.750 | 0.625 / 0.000 / 0.750 | 0.500 / 0.250 | 6.00 / 5.00 |
| C | Multiple encodes | 8 (4/4) | 0.625 / 0.000 / 0.750 | 0.625 / 0.000 / 0.750 | 0.250 / 0.250 | 7.00 / 5.00 |
| D | Recapture proxy | 8 (4/4) | 0.625 / 0.000 / 0.750 | 0.625 / 0.000 / 0.750 | 0.250 / 0.250 | 10.50 / 4.88 |
| E | Matched pairs | 48 (24/24) | 0.587 / 0.000 / 0.792 | 0.604 / 0.000 / 0.792 | 0.250 / 0.208 | 6.67 / 4.10 |
| F | Unseen invented templates | 48 (24/24) | 0.587 / 0.000 / 0.792 | 0.604 / 0.000 / 0.792 | 0.250 / 0.208 | 6.67 / 4.10 |
| G | Low quality | 8 (4/4) | 0.500 / 0.000 / 1.000 | 0.500 / 0.000 / 1.000 | 0.000 / 0.000 | 0.00 / 0.00 |
| H | Independent real-world holdout | 0 | Unavailable | Unavailable | Unavailable | Unavailable |

The upgraded **operational** score has identical performance to the frozen baseline on this corpus. The experimental candidate is separate and is not used for the verdict. Candidate AUC alone is not enough: pair win rate worsened, false-negative rate remains high and OCR-normalized residual effects did not separate the edits. No post-test threshold or feature tuning was used to improve these results.

Candidate threshold: 18.6 selected on the 72-image development subset for FPR ≤0.10, maximizing recall and breaking ties by lower FPR. Existing operational threshold remains12. The locked subset has48 images (24 each class),24 pairs,4 original groups and2 held-out invented templates. Both subsets share one generator and simulated device, so neither constitutes independent real-world validation.

## Locked synthetic confusion matrices and metrics

### baseline

TP=5, TN=24, FP=0, FN=19; precision=1.0, recall=0.208, F1=0.345, specificity=1.000, balanced accuracy=0.604, PR average precision=0.604.
ROC-AUC source-group bootstrap 95% interval: [0.4375, 0.7994791666666667]. Pair-win interval: [0.0, 0.625]. With four synthetic source groups these intervals do not support external validity.
Candidate-box union IoU against edited rectangles: 0.0344. This measures legacy candidate-region localization, not a trained pixel-level mask. The experimental candidate retains those same legacy boxes; OCR selections are evidence locations, not predicted tampering masks.

### upgraded_operational

TP=5, TN=24, FP=0, FN=19; precision=1.0, recall=0.208, F1=0.345, specificity=1.000, balanced accuracy=0.604, PR average precision=0.604.
ROC-AUC source-group bootstrap 95% interval: [0.4375, 0.7994791666666667]. Pair-win interval: [0.0, 0.625]. With four synthetic source groups these intervals do not support external validity.
Candidate-box union IoU against edited rectangles: 0.0406. This measures legacy candidate-region localization, not a trained pixel-level mask. The experimental candidate retains those same legacy boxes; OCR selections are evidence locations, not predicted tampering masks.

### experimental_candidate

TP=5, TN=24, FP=0, FN=19; precision=1.0, recall=0.208, F1=0.345, specificity=1.000, balanced accuracy=0.604, PR average precision=0.604.
ROC-AUC source-group bootstrap 95% interval: [0.5, 0.8125]. Pair-win interval: [0.0, 0.625]. With four synthetic source groups these intervals do not support external validity.
Candidate-box union IoU against edited rectangles: 0.0406. This measures legacy candidate-region localization, not a trained pixel-level mask. The experimental candidate retains those same legacy boxes; OCR selections are evidence locations, not predicted tampering masks.

Brier score/calibration remain unavailable because neither score is a probability. No probability transform is applied. Per-condition, template and edit-type metrics, ROC/PR coordinates and confusion matrices are in `research/results/robustness-summary.json`. Per-image predictions and features remain in baseline-all.json/upgraded-all.json.

## Failure analysis and rejected approach

- **Verified:** no peer-normalized joint local residual effect reached the candidate review cutoff in this corpus (maximum0.241 robust units). The new JPEG/high-pass candidate did not identify the controlled text edits. This candidate is rejected for active scoring. It may be too conservative, or these edits may lack discriminative residual differences; the current test cannot establish which cause dominates.
- **Verified:** 113 images had at least one readable OCR word;7 were UNREADABLE. This is availability, not measured word error rate. Low-confidence words are retained with an explicit warning; unreadable fields are not invented.
- **Verified:** the operational and baseline scores tie for most matched pairs. Repeated-region candidates account for the nonzero experimental scores; consistent geometry alone cannot distinguish legitimate repeated UI from copy-move.
- **Hypotheses only:** ordinary compression, natural UI repetition, resizing and legitimate rendering can create false positives; weak local evidence, blurred text, unknown layouts and missing comparable words can cause false negatives. `error-analysis.json` logs actual misclassifications with observed features and labels its causal category as a hypothesis. No automated causal attribution is claimed.
- **Information limit:** a plausible replacement rendered consistently and then recompressed may leave no detectable screenshot-only contradiction. OCR reads what is visible; it cannot recover the original amount or validate the transaction.

## Implemented architecture

1. Existing bounded decoding and image-coordinate pipeline retained.
2. Acquisition profile records encoding, quantization-table mean, dimensions, Laplacian variance and a documented engineering reliability factor. Unknown delivery provenance stays unknown; no EXIF penalty.
3. Optional local Tesseract English LSTM runs in a time-bounded subprocess with one OpenMP thread. Maximum input edge1800px,400 output words,8-second timeout. Missing executable, timeout, failure and unreadability are explicit. Recognized words include source-space boxes and actual engine scores.
4. Label-guided nearby OCR lines suggest amounts, dates, times, references, statuses and recipients; fields are unverified. No recognized app template is assumed. Unknown layouts carry no penalty.
5. Local residual comparisons normalize by edge strength and select nearby words with similar size, foreground density and luminance. Three JPEG qualities and two high-pass scales form one correlated family; repeated measurements do not become independent votes. This experimental mechanism is visible but not promoted.
6. ORB now rejects ambiguous zero-distance descriptor alternatives and checks spatial extent plus RANSAC fitted consistency; it remains a repetition candidate, not proof.
7. Risk dossier shows acquisition/OCR availability, source-located words and experimental evidence. Two original verdict labels remain unchanged. Evaluation loads actual saved predictions and recalculates confusion metrics when an exploration threshold changes; it cannot change the backend threshold or release gate.

## Performance and deployment

Locked synthetic median pipeline latency: baseline 0.1778s; upgraded 0.3900s. These are small local CPU images, not a throughput/service-level claim. OCR and comparisons add work. The optional binary is not assumed to exist on Vercel; its absence produces UNAVAILABLE. No hosted inference service or new large model is required.

The tester runs on localhost5175/API8001; the original remains localhost5174/API8000. No cloud deployment performed. Production build has a large-JS-chunk warning. Serverless response size, packaging, cold starts and binary availability remain staging checks.

## Reproduction

```sh
python scripts/build_robustness_benchmark.py
python scripts/evaluate_robustness.py --engine baseline
python scripts/evaluate_robustness.py --engine upgraded
python scripts/summarize_robustness.py
python scripts/generate_intelligence_report.py
python scripts/training_preflight.py research/datasets/robustness/manifest.json
# Expected exit2: training blocked
python -m pytest backend/tests -q
npm run build --prefix frontend
```

Use the project virtual environment. Tesseract5.5.4 with eng language data was installed locally. Set VERISIGHT_OCR_ENABLED=0 to test unavailable behavior. Scripts never train on this synthetic corpus. The frozen baseline is under research/baseline_backend. Before/after captures and browser results are in research/screenshots and research/results.

See FORENSIC_INTELLIGENCE_RESEARCH.md for primary literature and explicit dataset permission restrictions, DATA_COLLECTION_PLAN.md for collection requirements, and TESTER_IMPLEMENTATION.md for interfaces and tests.

## Coverage and regression caveats

Amount replacement appears in development, not in the locked synthetic subset. The latter contains recipient, timestamp, copy-move and removal edits. Real device/contributor/app diversity is absent.

The first candidate output is preserved in `upgraded-first-frozen.json`. A subsequent correctness fix records the measured pre-filter RANSAC inlier fraction; it changed three candidate scores. The same development-only operating-point selection rule was reapplied. Final test-set reuse is software regression, not a fresh independent validation. Pair discrimination still failed promotion.

Lossless decoded-image previews are now served separately on localhost; the uploaded file hash remains bound to its original bytes. Tests verify original decoded pixels match, and the simulator's comparison source and residual amplification were corrected. See `TESTER_IMPLEMENTATION.md` for transport limits and `FORENSIC_INVESTIGATION_LOG.md` for failures and fixes.

## Delivery stability and candidate-box F1

Delivery stability from current per-image predictions (0=unedited synthetic;1=edited; five delivered variants per original):

```json
{
  "baseline": {
    "0": {
      "n": 20,
      "mean_absolute_score_drift": 2.0,
      "classification_flip_rate": 0.0
    },
    "1": {
      "n": 20,
      "mean_absolute_score_drift": 5.8,
      "classification_flip_rate": 0.05
    }
  },
  "candidate": {
    "0": {
      "n": 20,
      "mean_absolute_score_drift": 0.0,
      "classification_flip_rate": 0.0
    },
    "1": {
      "n": 20,
      "mean_absolute_score_drift": 1.125,
      "classification_flip_rate": 0.05
    }
  }
}
```

A stable wrong classification is not successful robustness. These variants are correlated; n is not an independent sample count.

- baseline: candidate-region F1 0.0621.
- upgraded_operational: candidate-region F1 0.0707.
- experimental_candidate: candidate-region F1 0.0707.

These union-of-boxes metrics are coarse localization stress results against rectangular edit masks, not pixel-localization model validation.
