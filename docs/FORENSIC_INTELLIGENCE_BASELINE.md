# Frozen baseline and investigation

Source: complete uncommitted working tree in VERISIGHT_EXTENSION_VOICE, branch extension-voice-too, HEAD 406c835 plus previous parity fixes. New work is isolated in `verisight tester fix`; neither original checkout nor its running ports are changed. The pre-upgrade backend is frozen at `research/baseline_backend/app`; baseline outputs are in `research/results`.

## Verified scoring path
`analyze_screenshot` decodes bounded image bytes, composites alpha, computes ELA at JPEG Q90 (Q75 only for explicitly simulated delivery), db4-like diagonal residual variance, ORB descriptor translation clusters, connected-component word candidates, bottom-edge baseline rows, patch color/sharpness, metadata/QR, then `calibrate_ensemble`. The API returns `overall_tamper_score` and the frontend renders it unchanged in the dossier. Higher means more heuristic review cues, **not more authenticity**, and it is not a probability. Confidence is null. Layer panel scores are not used as weighted means in the final score.

Final baseline formula:
- Any baseline row flagged: 35 points.
- Clone count >=20: 28 points; >=40: 42.
- Supplied metadata time conflict: 35; reference-format mismatch: 20.
- ELA block existence: 4; noise score >40: 4; color/sharpness flag: 4; software metadata: 3. Weak subtotal capped at 12.
- Total capped at 92. Spatial clone/baseline overlap can force minimum72; >=12 means review; below12 inconclusive. Thresholds/points are hand-selected, not fitted to a representative validation set.

**43 and 39 are exactly expressible as 35+8 and 35+4.** That is a code-supported explanation for score clustering, not a diagnosis of the user's two files: those files and their analysis responses were not supplied. A generic component-baseline flag can dominate unrelated receipts, and the weak cues only shift the total in four-point steps.

## Technical bottlenecks
1. `extract_text_tokens(...use_neural=False)` returns strings `token_N`, not recognized text. The hardcoded component confidence .92 is not OCR confidence. Bottom edges vary naturally with descenders, antialiasing, segmentation and resizing; fixed pixel drift thresholds do not normalize typography.
2. Global ELA blocks compare complex edges to blank backgrounds, not like-for-like text regions. Wavelet flat-region detection assumes natural-camera noise, which is a poor fit for deliberately flat UI cards.
3. ELA, wavelet and sharpness can all reflect the same recompression/resizing event. They are not independent evidence.
4. ORB allowed ambiguous zero-distance matches and lacked fitted geometric verification; repeated UI shapes can resemble copy-move.
5. No operational OCR/layout model, no representative classifier, and no valid probability calibration. A historical GBDT artifact exists but is deliberately not loaded; archived synthetic leakage prevents promoting it.
6. JPEG/no-EXIF does not identify WhatsApp or prove forgery. Missing metadata already contributes zero in the parity baseline. Exact number of encodes or recapture history is not reliably identifiable from a single image.
7. QR payload or metadata consistency is not bank settlement or identity verification. Unknown templates must remain unknown.

## Baseline data and metrics
All five existing synthetic fixtures are evaluated twice by `scripts/benchmark-parity.py`; the imported sixth receipt is separately run but excluded from accuracy statistics because its provenance/label is undocumented. There is no authorized representative real-world labeled test set. Baseline real-world confusion matrix, FPR/FNR, ROC/PR-AUC and calibration are **unavailable**, not zero.

A new original CC0 synthetic software-stress set contains 120 images (60 unedited synthetic,60 controlled edited),10 original groups,5 invented templates,6 delivery conditions. Each original/edit pair shares all transformations. Masks mark edited rectangles, not a validated pixel segmentation target. Six groups are development and four groups in two unseen invented templates are locked synthetic evaluation. All share a generator and simulated device: no real-world independence claim. Neither original nor transformed fixtures are used for training. Screenshot recapture is a resampling proxy, not a real phone capture. WhatsApp-style transforms are controlled JPEG/resizing operations, not assertions about proprietary current app encoding.

See the final experiment report for genuine measured software-stress confusion matrices and errors. The original WhatsApp pair remains unresolved until the exact files and ground-truth explanation can be evaluated.
