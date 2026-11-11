# Screenshot localization: data audit and release plan

Reviewed 2026-11-11. **Decision: STOP BEFORE TRAINING. No deployment.**
No third-party corpus or checkpoint was downloaded, decrypted, trained on, or
redistributed during this review. No permission email was sent. A public link,
password, code license, or pretrained checkpoint is not a grant for this
project's intended data/model use. Intended commercial use has not been ruled
out and no project-specific academic permission is documented.

## Dataset register (before any training)

| Candidate / primary source | Published size (not locally audited) | Labels and domain relevance | License / access / decision |
|---|---|---|---|
| [STFD author project](https://github.com/ZeqinYu/STFL-Net), [dataset card](https://huggingface.co/datasets/Zegkim/STFD) | 4,094 images reported in the authors' [later paper](https://proceedings.neurips.cc/paper_files/paper/2025/file/df34ea73a7e2108b816194200f1442be-Paper-Datasets_and_Benchmarks_Track.pdf); HF lists 2.96 GB. Counts and authentic-source availability require audit. | Smartphone screenshots, including payment/banking; paired binary masks for copy-move, splice, removal, insertion, replacement. Best domain match. | HF metadata says CC-BY-4.0, but its notice limits use to academic research and restricts redistribution of images with information leakage. HF requests institutional-email access; current author GitHub publishes the extraction password. Access information conflicts, and a published password does not resolve rights. **Blocked pending written intended-use clarification and source-group metadata.** No commercial permission inferred. |
| [DocTamper official repository](https://github.com/qcf-568/DocTamper) | 170,000 document images according to the authors' [CVPR slides](https://cvpr2023.thecvf.com/media/cvpr-2023/Slides/21237.pdf). | Document text manipulation with ground-truth masks; documents/receipts, not a representative mobile payment screenshot corpus. | Explicit non-commercial restriction; education-email/password application or official application form. Original providers retain copyright; access described for universities/research institutions. **Blocked for unspecified product use; no project grant.** |
| [FSTS official dataset card](https://huggingface.co/datasets/Zegkim/FSTS) | HF reports 588,368 rows and 46 GB; these are not verified unique image/mask pairs. | Text-forgery synthesis/localization resource; mask pairing and grouping metadata require inspection after permission. Synthetic training material cannot establish real-world screenshot accuracy. | CC-BY-NC-4.0. Public download does not remove the non-commercial restriction. **Blocked for unrestricted product deployment.** |
| [CORD official release](https://github.com/clovaai/cord), [license](https://github.com/clovaai/cord/blob/master/LICENSE-CC-BY) | 1,000 released receipts, 800/100/100 split; broader collection over 11,000 is not the released dataset. | Indonesian shop/restaurant receipt photos with OCR boxes/text and parsing labels. No screenshot edit masks or verified image-authenticity labels. | CC-BY-4.0 with attribution; release omits certain classes due to legal issues. **Permissive OCR auxiliary candidate, not sufficient for this localization task or independent payment screenshot evaluation.** Not downloaded. |

These are reviewed candidates, not an exhaustive assertion that no suitable
public dataset can exist. Do not substitute a mirror's looser license for the
author's terms. Obtain separate permission for images, annotations, weights,
derivatives, commercial deployment, and redistribution. Record version, terms
snapshot/hash, permitted purpose, expiry, reviewer, and approval evidence.
If STFD is authorized only for academic experiments, isolate those artifacts
from any commercial training/promotion lineage.

## Existing implementation and deployment inspection

- Base Git commit: `510042f25597b12c90f858131845019ef399747c`. The workspace
  contains earlier uncommitted repairs; this review preserves them.
- `pipeline.py` computes ELA (JPEG scoring only), wavelet residuals, ORB repeated
  features, component-baseline/color/edge geometry, metadata rules, QR payloads,
  and overlapping bounding boxes. These are uncalibrated cues, not pixel masks.
- RapidOCR recognizes text and checks explicit non-real/failed receipt wording.
  It is a pretrained OCR model, **not** a trained tampering localizer. OCR
  confidence is not authenticity confidence. Metadata is untrusted; marker-only
  C2PA inspection is not signature verification. QR decoding verifies neither
  destination nor settlement.
- `AdvancedModelAdapter` never loads weights or runs inference, even if torch
  is installed. There is no training entrypoint, approved artifact registry,
  representative corpus, calibrated threshold, or independent test result.
- `/api/model/status` remains `HEURISTIC_ONLY`; `/api/model/evaluation` remains
  `NOT_EVALUATED` with null metrics. They now expose blocked training/release
  readiness and distinct evidence-source descriptions. This is telemetry, not
  an enforced Vercel organization deployment policy. No automatic deploy was run.
- The UI labels stay **Likely accurate** and **Likely misleading**. Neither is
  a payment-status response. Workbench supporting text explicitly states this.
- Python 3.12/FastAPI, Fluid compute, configured 300-second maximum. Input
  validation allows 20 MiB, 12 MP, 8192 pixels/side, minimum 16 pixels/side.
  Large analysis uploads use private storage; simulation still posts directly.
- [Vercel's current limits](https://vercel.com/docs/functions/limitations):
  Python standard bundle 500 MB uncompressed; large-function beta up to 5 GB
  requires enablement. Request and nonstreamed response limit 4.5 MB. Hobby
  memory 2 GB/1 vCPU; Pro/Enterprise up to 4 GB/2 vCPU. Project entitlement and
  Linux artifact size are unverified. Configuring 300 seconds is not a latency
  benchmark. Inline original/heatmap base64 may exceed the response limit even
  when signed uploads bypass the request limit.
- Do not add training frameworks or large checkpoints to the request handler.
  Prefer an isolated, access-controlled inference worker if an approved model
  fails measured CPU/bundle/memory gates. Serve heatmaps through expiring private
  URLs if payload testing requires it; preserve source pixels for measurements.

## Authorized data-collection plan

1. Obtain contributor consent and app/test-environment rights covering model
   training, evaluation, intended deployment and retention. Prefer app-owner/PSP
   sandbox accounts with permission and non-sensitive test identities. Never
   scrape private chats. Request author clarification for STFD; do not infer a
   commercial grant from academic access. Keep evidence outside the public repo.
2. Capture real device screenshots from distinct app/version/template, OS,
   display-scale, language and theme combinations. Capture original bytes and
   provenance before edits. Include unsuccessful/pending genuine screens as
   **visually authentic**, not fake; transaction state is a separate annotation.
3. An initial collection budget is 10,000 independent originals, with prospective
   60/20/20 train/validation/test cohorts. This is a planning target, not proof
   of adequate coverage. Reserve unseen app/template/device/contributor cohorts
   at capture time. Target at least 2,000 independent authentic test originals
   plus controlled edits; do not count crops or re-encodes as independent cases.
4. Each edited image records amount, recipient, timestamp, reference or QR-payload
   target, plus insertion/removal/replacement/splice/copy-move method, editor and
   editing-session ID. Keep pixel masks, original/edited hashes, tool/version,
   edit log and reviewer-adjudicated mask. QR payload replacement is a visual
   edit label; decoded destination legitimacy remains unknown.
5. Redact or avoid personal data **before** defining capture ground truth. Record
   sanitization, apply it consistently and exclude privacy-redacted pixels from
   scored masks. Never label a redacted image an untouched original. Store
   restricted originals privately with deletion/withdrawal procedures.
6. Schema: sample ID, dataset/license/consent revision, source app, template ID,
   device ID/model/OS, contributor ID, original screenshot ID, editing session ID,
   exact SHA-256, reviewed near-duplicate group, label, mask path/hash, dimensions,
   edit type/target, compression/transform condition, split. Clean originals get
   zero masks and a unique capture-session ID rather than a shared null value.
7. Build connected components across **every** shared identity above and exact
   duplicates. Assign whole components to one split; never concatenate fields
   into a composite that permits partial identity overlap. Review perceptual
   similarity/crop/re-encode matches before assigning near-duplicate groups.
   If shared contributors/apps connect everything, collect fresh disjoint cohorts
   rather than relaxing the split. Unknown provenance is excluded, not randomized.
8. Apply resize, JPEG re-encode, crops, real authorized forwarding and recapture
   to both classes with balanced settings **after** splitting. Transform masks
   using matching geometry and nearest-neighbor labels. Record originals as
   parents. If a crop removes all changed pixels, re-label visible-tamper status
   accordingly; do not preserve a positive label for absent visual evidence.
9. Lock test manifest, image and mask hashes with restricted access before
   experiments. Researchers use train/validation only. Designate an independent
   test custodian. The manifest auditor checks declared groups/hashes, not the
   images themselves: it cannot discover undeclared near-duplicates or certify
   legal rights. Real-image duplicate/mask inspection remains a mandatory gate.

## Training design (not executed)

Start with a license-cleared encoder/decoder segmentation model trained on
RGB plus a separate forensic residual branch. Predict one tampering map at
original-image coordinates, using overlapping tiles to preserve small text edits.
Use masked BCE + Dice, balanced authentic zero-mask batches, and sample edits
by source group rather than letting abundant derivatives dominate. Choose
architecture, pixel threshold and hyperparameters on train/validation only.

Derive an image-level score from top-region map statistics (not raw max-pixel
probability alone), region area and existing pixel/geometry cues. Fit fusion on
training/out-of-fold training features. Split validation groups into threshold
selection and calibration subsets. OCR semantics, metadata and QR evidence stay
separate in responses and ablations; neither a failed payment message nor an
unusual reference proves a visual edit. Preserve the current baseline as-is for
comparison, including its OCR warning policy, and also report pixel-only baseline.

Proposed provenance per result: visual mask/version/score; OCR text/recognition
confidence and boxes; untrusted metadata cues; decoded QR fields; payment-status
integration state. Show localized regions and measured contributing cues, not
attention heatmaps represented as ground-truth explanations. Never fabricate a
mask where only a bounding-box heuristic exists. No model confidence is exposed
until representative calibration and release gates pass.

## Prospective evaluation and release gates

These targets are design decisions, **not measured results**. Freeze them before
training; changes require a new protocol and, after test inspection, a new test set.

- Validation false-positive target: **1%** on independent authentic screenshots.
  Select the lowest threshold maximizing recall subject to a one-sided 95% FPR
  upper confidence bound at or below 1%. If none qualifies, do not ship.
- On the locked test set report TP/FP/TN/FN, FPR, FNR, precision, recall, PR-AUC
  (state prevalence and average-precision convention), and group-bootstrap 95%
  intervals. Do not select thresholds or models using these results.
- Report pixel IoU and F1 on tampered images, macro per-image and micro aggregate;
  define empty-mask cases separately and report authentic false-positive pixel
  area. Do not inflate IoU by averaging thousands of empty backgrounds.
- Report Brier score, ECE with predeclared bins and reliability plots, both before
  and after validation-only calibration. No calibration from the test set.
- Break down by app/template, edit target/method, device/OS, and compression/
  transformation, plus intersections with adequate counts. Show sample counts,
  uncertainty and N/A for insufficient groups; do not hide worst-group failures.
- Proposed promotion criteria: test FPR upper bound <=1%; recall lower bound
  >=80%; macro localization IoU >=0.50 and F1 >=0.65; ECE <=0.05; and improvement
  over the frozen baseline at the same validation-selected FPR target, with paired
  group-bootstrap intervals for recall and localization improvement excluding zero.
  All advertised app/condition groups must meet the FPR requirement or be excluded
  from supported scope. A small/nonrepresentative set cannot pass by aggregate luck.
- Runtime gates on Linux/deployment-equivalent hardware: hash-verified weights,
  deterministic preprocessing, valid finite [0,1] maps, coordinate alignment,
  empty/corrupt/unsupported inputs, no-weight/mismatch/timeout behavior,
  cold/warm p95 latency and peak memory under real concurrency. Proposed localizer
  target: warm p95 <=10s, cold p95 <=30s, RSS <=75% of provisioned memory,
  nonstreamed response <4 MB. Verify actual package cap and no runtime downloads.
- Full tests and production frontend build must pass. These are software checks,
  not dataset accuracy measurements. The current no-model adapter is tested to
  **not** claim loading/inference; trained-model tests remain blocked until an
  authorized artifact exists.

## Release record and rollback

Current model version: **none**. Training: **not run**. Threshold: **unset**.
FPR/FNR, precision/recall, PR-AUC, localization IoU/F1, calibration: **unavailable**.
Dataset permissions: **not sufficient for the intended screenshot task**.
Release status: **blocked**. No new model or code deployed in this task.

A future release must attach artifact SHA-256/version, training source commit,
license/permission register, train/validation/locked-test manifest hashes,
preprocessing and feature schemas, calibration artifact, frozen thresholds,
full measured result tables, supported scope, runtime measurements, and previous
approved deployment/model IDs. CI must refuse model promotion without that record;
the present readiness endpoint alone is not such an enforcement mechanism.

Rollback: disable the new inference worker/model feature flag; atomically restore
the recorded previous model/preprocessing/threshold tuple (or heuristic-only mode
with confidence null); restore the previously recorded Vercel deployment through
Instant Rollback or redeploy its exact commit; run health/status, sample-upload,
corrupt-upload and private-storage handoff smoke tests. Keep case model versions
for traceability and do not rewrite historical assessments. No previous trained
model exists today. Retain this working tree's earlier repairs; do not reset them
as a shortcut to rolling back a future model.

## Verification performed in this working tree

- `.venv/bin/python -m pytest backend/tests -q`: **93 passed**, 36.85 seconds;
  one existing Starlette/AnyIO deprecation warning.
- `npm run build --prefix frontend`: TypeScript and Vite production build passed;
  Vite warns that the main JavaScript chunk exceeds 500 kB.
- `git diff --check`: passed. Verdict-label helper unchanged.
- Public production status was read only: `HEURISTIC_ONLY`, no active model,
  `NOT_CALIBRATED`. Local source changes were not published to Vercel/GitHub.
- New checks cover split-identity/hash leakage, incomplete/unauthorized manifests,
  fixture exclusion, test-manifest changes, disabled model loading/inference, and
  endpoint confidence/release state. Existing full suite covers real OCR inference,
  empty/corrupt uploads and synthetic regression fixtures.
- Not performed: trained-localizer loading/inference, mask quality evaluation,
  real-corpus near-duplicate discovery, held-out accuracy/calibration, or production
  bundle/load tests. These remain blocked; software test success does not pass
  the model release gate.
