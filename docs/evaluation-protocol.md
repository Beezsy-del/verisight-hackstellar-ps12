# Representative evaluation protocol v1

Status: collection is not started, no participants are enrolled, and no representative accuracy or reviewer-benefit result exists. VeriSight is an improved private development prototype. This protocol is a prerequisite to stronger claims, not evidence those claims are true. Existing synthetic regressions remain a separate engineering dataset. No training is authorized by a passing manifest check.

## Collection and permissions

Before collecting or training, the collection owner must publish an internal dataset register containing source, license revision, access restrictions, available size, labels, payment/mobile-app relevance, and a signed permission reference covering **VeriSight commercial and research development**. Have a named rights reviewer verify that exact scope. Academic-only terms do not cover it. Do not obtain STFD, private messages, or restricted images without applicable permission. Record redistribution separately; a training permission never implies permission to publish screenshots.

Use consenting contributors' authorized test accounts and non-sensitive transactions where possible. Obtain consent for collection, controlled editing, research, commercial model development and retention. Keep consent documents and original assets outside Git with access limited to designated evaluators. Store opaque contributor/device IDs in manifests. Document withdrawal and deletion rules before intake. Do not claim a screen proves settlement; transaction status is separate authorized bank/PSP evidence and is never a visual label.

A custodian records authentic originals captured directly from the source application with provenance. Create controlled amount, recipient, timestamp, reference, QR-payload, insertion, removal, replacement, splicing and copy-move edits. Record original screenshot and editing-session identifiers and exact binary masks; authentic images need all-zero masks. QR changes must reflect known payload changes, not merely insertion of a QR symbol. Unknown provenance is excluded rather than guessed.

Apply resizing, JPEG recompression, crops, messaging-app forwarding and screen capture to **both** classes. Actual forwarding/screen capture must use the named device/app; synthetic approximations must be labeled separately. Transform the edit mask with the same geometry and manually verify alignment. Capture app/template, device, contributor, original, session, compression parameters and acquisition conditions for each variant.

## Split and lock

Build connected components over shared source app, template, device, contributor, original, editing session, exact hash and independently reviewed near-duplicate group. Assign each component entirely to one of train/validation/test. This strict policy may force large connected components or require more independent collection; never relax it after seeing scores. Label authentic sessions with a real capture-session ID rather than a shared “none” value. Record model-training exclusions and blind the test custodian from model tuning.

The manifest uses the fields enforced by `backend/app/evaluation/data_audit.py`, plus `image_path`, `mask_sha256`, boolean `synthetic`, `edit_type`, and `condition`. Group fields are source_app, template_id, device_id, contributor_id, original_screenshot_id, editing_session_id and near_duplicate_group. Every dataset permission entry contains source, license_revision, access_restrictions, evidence_ref, reviewer, payment_relevance, intended_use, intended_use_approved, available_size and labels `["authentic", "tampered"]`.

Use the empty template, not the bundled demo images:

```sh
PYTHONPATH=backend .venv/bin/python -m app.evaluation.dataset_manifest /private/path/manifest.json --root /private/path/assets --write-lock /private/path/test-lock.json
PYTHONPATH=backend .venv/bin/python -m app.evaluation.dataset_manifest /private/path/manifest.json --root /private/path/assets --lock /private/path/test-lock.json
```

The tool checks permissions/provenance, all split axes, image/mask bytes and dimensions, label/mask agreement and the immutable test membership/metadata digest. It refuses to overwrite a lock. Store an independently timestamped copy with the custodian; the local digest does not prevent someone deliberately replacing both files. Verify again before every test run. A pass does **not** establish representativeness, authenticity of permission documents, sufficient sample size or model release eligibility.

## Threshold and statistical analysis

Predeclare a 1% false-positive target on authentic screenshots. Choose a score threshold using validation data only, maximizing recall subject to the target and a predeclared uncertainty criterion; if no threshold meets it, release stays blocked. Use `validate_threshold_policy` to validate a stored selection record: validation manifest digest, model digest, selection evidence reference, fixed threshold, target and explicit attestation that test outcomes were unseen. Fix the threshold before opening the locked test set. Do not change the current runtime heuristic threshold on the basis of this document.

A statistician must size the corpus using independent source groups and expected prevalence, not counts of augmented copies. Report uncertainty from source-group bootstrap and exact count denominators, including zero-event bounds; zero false alarms in a few clean screenshots cannot establish a 1% field false-positive rate. Do not claim the target is met while the prespecified confidence bound exceeds it.

Run A, B and unified with the same bytes, environment, budgets and recorded commit/model hashes. Preserve each native output and compare at a defined common review decision; never silently reinterpret incompatible labels. Include no-result failures in completion/coverage and reviewer outcomes rather than dropping them from accuracy denominators. Report FPR, FNR, precision, recall, PR-AUC, localization IoU/F1, calibration (reliability diagram, Brier/ECE only for actual probabilities), time, memory and failure rates. Break out app/template, edit type, device and compression; show sample/group counts. Confidence remains unavailable for uncalibrated heuristics. Record train/test differences, label uncertainty and unsupported strata.

## Reviewer and comprehension study

Use a separate permission-cleared set and representative intended users. Counterbalance A/B/unified order and include unaided review. Randomly assign disjoint equivalent screenshots across conditions so a participant never sees the same original twice. Blind manipulation labels; preserve time limits and instructions. Collect correct review decisions, missed edits, false alarms, no-result handling, time per case and willingness to rely. Analyze paired/user and source clustering; predeclare primary outcome and minimum useful difference before enrollment.

Ask users, **before explaining the answer**, whether “Likely accurate” proves authenticity, whether either verdict proves settlement, whether the score is a fraud probability, and what to do after an incomplete result. Correct answers are no/no/no/seek independent evidence. Preserve the two exact verdict labels. If the favorable label repeatedly creates false reassurance, improve adjacent explanations and repeat on fresh participants; do not hide comprehension failures behind a successful upload demo.

## First week and exit conditions

- Day 1: assign collection owner, rights reviewer, test custodian and evaluation lead; freeze protocol/version, metrics and decision criteria.
- Days 2–3: obtain signed access/consent and inventory permitted sources; perform a small provenance/mask intake pilot outside the test set. If access is absent, stop before training.
- Days 4–5: validate manifests, resolve group connectivity and obtain a justified sample-size plan. Recruit representative reviewers only after consent materials are ready.
- Schedule the actual blinded study when enough authorized data and reviewers exist. These are planning milestones, not claimed appointments or completed collection.

Release requires independently reviewed permissions, sufficient representative groups, a locked untouched test, validation-only threshold selection, successful measured outcomes, acceptable comprehension, verified operational limits and rollback. Failed criteria remain visible and block stronger claims. Do not train on the five bundled fixtures or present synthetic-only results as real-world accuracy.
