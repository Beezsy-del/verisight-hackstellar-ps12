# VeriSight: primary-source literature and experimental foundation

Reviewed 2026-11-12. Scope: payment-screenshot image forensics and the comparison of source snapshots A and B. This is a source audit and a proposed experimental foundation, not a completed external-model benchmark. No restricted datasets or pretrained weights were downloaded; no training was performed. Existing snapshots remain unchanged. Equations labelled “proposed” are our operational formulations, not claims that a cited paper implemented VeriSight.

## Findings that change the project

Neither visual consistency nor a lack of detected manipulation proves that money arrived. Screenshot tampering, consistency of displayed fields, provenance of the file, and settlement of the transaction are distinct targets. The system should report those targets separately. A fabricated interface can be rendered coherently from scratch, and an authentic old receipt can be presented for a new purchase: both may have perfectly consistent pixels. This is an identifiability limit of the input, not a reason to manufacture greater confidence.

Snapshot A's `docs/RESEARCH_REVIEW.md` is not a dependable benchmark. It mixes actual architectural ideas with unsupported CPU/GPU timings, unverified dataset counts, broad model rankings and fixed messaging-platform JPEG settings. Replace those comparisons with “not measured” until the same inputs, output definition, hardware and preprocessing are evaluated. In particular, do not call heuristic agreement a calibrated reliability map or present “HIGH WhatsApp robustness” as an established result.

## 1. STFL-Net / STFD: text-aware screenshot localization

**Verified contribution.** The ICASSP 2023 author presentation describes an RGB stream and complementary OCR stream, a dual-stream Y-net, and multi-teacher knowledge distillation to reduce dependence on one forgery trace. This supports studying text-aware feature fusion. It does not verify the snapshot's more detailed claims about character embeddings, cross-attention, backbone choices or runtime. [IEEE SPS author abstract](https://rc.signalprocessingsociety.org/conferences/icassp-2023/spsicassp23vid2300)

**Operational model (proposed abstraction).** Let image `I` and OCR-derived representation `O(I)` feed `M = fθ(I, O(I))`, where `M[u,v]` estimates local manipulation evidence. OCR is an input with its own failure modes; a low-confidence or missing OCR region must not become evidence of authenticity. Teacher disagreement is useful to investigate, but agreement alone is not correctness.

**Assumption and limit.** Training and evaluation on screenshot text makes this closer to VeriSight's input than generic camera-forensics benchmarks. It still requires target-language, app-family, small-glyph and transformed-image testing. The official repository currently contains stale “coming soon” items alongside a 2026 dataset release and public extraction password; availability of an executable checkpoint must be checked artifact by artifact. [Author repository](https://github.com/ZeqinYu/STFL-Net)

**License.** The author-linked Hugging Face card displays CC-BY-4.0 metadata while its notice restricts the dataset to academic research. This conflict remains unresolved; a permissive metadata tag is insufficient clearance. The card's institutional password-request text is also inconsistent with the newer GitHub public password. Do not repeat the old access requirement as if it were current everywhere. [STFD card](https://huggingface.co/datasets/Zegkim/STFD/blob/main/README.md)

**Concrete change.** Add an optional, separately scored OCR geometry branch and explicit `ocr_unavailable` state; evaluate it by ablation. Keep STFD out of a commercial data pipeline pending written clarification. Do not claim STFL performance from a substitute heuristic implementation.

## 2. DocTamper / DTD: visual and compression traces

**Verified contribution.** DocTamper is the dataset; DTD is the detector. The author slides describe visual and frequency heads, early fusion into a multimodal transformer, and a Multi-view Iterative Decoder. Frequency features encode discrete DCT coefficients and quantization information to expose block-grid irregularities. Selective synthesis matches text size and foreground/background statistics rather than pasting obviously incompatible text. The dataset includes photographed contracts, receipts and other documents. Its source-separated test sets are an important design precedent. [CVPR author slides, slides 5–17](https://cvpr2023.thecvf.com/media/cvpr-2023/Slides/21237.pdf)

**Mechanism.** JPEG quantization can be represented as `Cq[u,v] = round(DCT(block)[u,v] / Q[u,v])`. This is a codec relation, not the complete DTD architecture. A pasted region can have a different compression history. A coherent re-render, global recompression, resize, or crop may remove or alter that distinction. Therefore a bright edge is not a causal proof of editing.

**Correction and limit.** The snapshot's claim that DTD essentially depends on paper grain or scanner halftoning is unsupported by the inspected author materials. The relevant hypothesis is compression-domain and layout shift, which must be measured on screenshots. The authors also study compression-oriented curriculum training and image-level authentication in supplementary experiments. [Author supplementary material](https://openaccess.thecvf.com/content/CVPR2023/supplemental/Qu_Towards_Robust_Tampered_CVPR_2023_supplemental.pdf)

**License and change.** The official repository explicitly limits dataset use to noncommercial research and describes an institutional application process. It does not establish the snapshot's precise “CC BY-NC 4.0” assertion. It also says the dataset does not cover AIGC text tampering. Keep code, dataset and checkpoint permissions separate. Add matched compression conditions, plausible edits and independent authentic images to evaluation; treat DTD as a possible research baseline only after access is approved. [DocTamper repository](https://github.com/qcf-568/DocTamper)

## 3. TruFor: localization and predicted reliability

**Verified contribution.** TruFor combines RGB with a learned noise-sensitive fingerprint and predicts a localization map, an image-level score and a reliability map. Its fingerprint captures processing traces; describing Noiseprint++ simply as camera-specific PRNU is inaccurate. The reliability output estimates where localization can be wrong. It is not interchangeable with overlap between two hand-designed heatmaps. [Author paper abstract](https://arxiv.org/abs/2212.10957)

**Operational abstraction (proposed).** `(M, R, s) = fθ(I, Nθ(I))`. Keep localization evidence `M`, learned reliability `R`, and image-level decision `s` distinct. No source inspected here establishes that VeriSight's screenshot domain produces uniformly useless noise features; that is a testable transfer hypothesis, not a proven fact.

**Assumption and limit.** An anomaly detector needs a meaningful regular pattern and sufficient departures from it. Native rendered screenshots differ from camera photos; photographed screens form another domain again. A locally uniform fake can escape any anomaly-based method. Report results separately for those acquisition types.

**License and concrete change.** The official repository permits its software only for informational and nonprofit purposes. Public weights do not mean commercial permission. Borrow the conceptual separation of evidence and reliability; do not copy restricted software into a commercial release. Any eventual baseline should retain model/version and input-domain details. [TruFor repository and license notice](https://github.com/grip-unina/TruFor)

## 4. ADCD-Net: make compression evidence conditional

**Verified contribution and equation.** ADCD-Net adaptively weights DCT features with a learned alignment score, then separates content and forgery features and estimates a pristine-background prototype. Its Equation 1 is `F_fuse^(i+1) = f_fuse^i(F_rgb^i + ŝ_aln F_dct^i)`. The alignment head is trained using aligned and disrupted grids, including non-multiples-of-eight shifts. This gives a concrete reason to reduce dependence on compression cues after resampling. The mostly-pristine-background assumption can fail on full-image generation, large replacement regions, decorative backgrounds and heavily transformed screenshots. Its reported distortion gains are paper-specific, not evidence of payment-receipt accuracy. [Author paper, Sections 3–4](https://arxiv.org/html/2507.16397v1)

**Evaluation caveat.** The official repository's Doc Protocol explicitly skips authentic images. A localization score under that protocol cannot establish image-level specificity, false-positive rate or safety of an “authentic” verdict. The repository trains on DocTamper. [ADCD-Net repository](https://github.com/KahimWong/ADCD-Net)

**License.** The repository code has an MIT license. This does not establish a license for DocTamper data or settle commercial rights to a separately distributed trained checkpoint. Require an artifact-level permission record. [Code license](https://github.com/KahimWong/ADCD-Net/blob/master/LICENSE)

**Concrete change.** Record whether the input is native PNG, JPEG, resized or otherwise transformed when known. Expose unavailable compression evidence as unavailable, not zero-risk. Test a condition-dependent compression branch against a fixed-weight branch. Test false alarms on authentic images before considering deployment.

## 5. ELA: a recompression experiment, not an authenticity detector

The originating presentation treats ELA as an image-analysis method in a broader forensic workflow, with experimental limitations. The operation is `E_Q(I) = |I - Decode(JPEG_Q(I))|`; display normalization is another transformation and must be recorded. [Krawetz, Black Hat DC 2008](https://www.blackhat.com/presentations/bh-dc-08/Krawetz/Presentation/bh-dc-08-krawetz.pdf)

**Inference from the operation.** On a native PNG screenshot, this measures the error introduced by the analyst's JPEG conversion, not an observed pre-existing JPEG history. Sharp legitimate text and flat backgrounds need not have equal error. A locally edited area may have no distinguishing residual after a coherent export. Per-image max normalization also makes similarly bright maps incomparable in absolute magnitude.

**Concrete change.** Label the map “JPEG recompression residual,” record quality and encoder settings, preserve raw residual statistics, and avoid probability wording. Run untouched rendered text, benign resize and JPEG round-trip controls at each tested quality. A fallback that silently recompresses PNG is not an independent validation of that PNG. Do not hardcode an asserted universal WhatsApp/Telegram quality; record the actual observed transformation or label it unknown.

## 6. Calibration and grouped validation

Guo et al. show that good classification accuracy does not imply reliable confidence. Temperature scaling fits a positive `T` on validation logits: `p_k = softmax(z/T)_k`. Expected calibration error compares confidence and accuracy within bins: `ECE = Σ_b (n_b/n) |acc_b - conf_b|`. It is a descriptive, bin-dependent measure, not a guarantee on a new app or capture channel. [Guo et al., ICML 2017](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf)

**Concrete change.** Stop converting arbitrary heuristic scores into percentages of authenticity. For a learned binary model, reserve a calibration partition and fit a suitable mapping there; evaluate calibration only on the untouched test partition. A sigmoid or temperature cannot create information or establish generalization. Report Brier score `mean((p-y)^2)`, reliability diagrams and counts alongside ECE. Label uncalibrated scores explicitly.

Grouped validation is required when samples share a source. The official cross-validation documentation explains that dependent groups violate independent-sample assumptions and must stay on one side of a split. [scikit-learn grouped validation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data)

**Proposed protocol.** Assign the original receipt, all its edits, crops, resizes and recompressions to one group before splitting. Keep shared renderer templates or app/layout families together for the harder domain holdout. A single concatenated ID is insufficient when two groups share a template through another relationship: construct connected components of the leakage relationships or run separate source and template holdouts. Use a development split, independent calibration/threshold split and sealed test split. Add a later-time holdout. Bootstrap intervals by source group, not by pixel or transformed copy. Tune neither weights nor threshold on the reported test set.

## 7. C2PA: provenance must remain separate from settlement

C2PA binds signed provenance to an asset using cryptographic mechanisms. Its explainer explicitly states that provenance alone cannot establish whether depicted content is true. Provenance can be incomplete or removed. A valid manifest therefore supports a statement about signer, asset binding and recorded history; an absent manifest is not evidence of forgery. [C2PA explainer, Sections 7.1–7.2](https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html)

**Proposed verification abstraction.** `provenance_valid = signature_valid ∧ asset_binding_valid ∧ trust_policy_satisfied`. This is not `settlement_confirmed`. A financial-status check would additionally require an authorized authoritative record, matched identifiers and explicit status/time semantics. This review implements no bank access and makes no claim that a screenshot transaction ID authenticates itself.

**Concrete change.** Return separate fields for `image_evidence`, `content_consistency`, `provenance_status`, and `settlement_status`. Until authoritative verification is actually integrated, settlement must remain `not_verified`, including when all image checks pass.

## 8. License-cleared data and scientifically useful experiments

This is a proposed plan, not a claim that such a dataset already exists.

1. Build project-owned receipt-like layouts with fictitious identities and transaction references, original graphics, and fonts/assets whose redistribution and ML use terms have been recorded. Save generator version, seed, renderer, dimensions, language and asset-license inventory. Owning a script does not establish ownership of an embedded logo or font.
2. Keep a clean image and a semantic source record before every edit. Generate matched edits of amount, recipient, timestamp and status; include same-style re-rendering and whole-interface fabrication. Record a binary changed-pixel mask plus semantic field labels. Pure rendering differences and benign transformations need separate labels from material manipulation.
3. Keep realistic authentic controls: varied font sizes, accessibility settings, dark themes, languages, older valid receipts, empty metadata, legitimate annotations and redactions. Authorize and document any later real-device contribution; avoid collecting financial secrets. Use synthetic data for early debugging, not a substitute for consented target-domain validation.
4. Apply the same transformation distribution to authentic and tampered images: PNG, single and repeated JPEG export, scaling, crop, screenshot recapture and, in a separate stratum, camera photographs of screens. Preserve operation order, codec settings and masks transformed with the image. Otherwise the model can learn the pipeline label instead of manipulation.
5. Separate development renderers from test renderers and reserve human-created plausible edits by an independent contributor. Include edits whose changed glyphs survive and edits too small after downsampling to support confident localization. Record this loss of observability.
6. Measure image detection and localization separately. Image metrics: AUROC/AUPRC, sensitivity at a prespecified false-positive rate, specificity, confusion counts, abstention rate and coverage. Localization: per-image IoU/F1 on tampered cases, plus false-positive pixel/region burden on authentic cases. Define empty-mask behavior explicitly. Macro-average by source so one large image or augmentation family cannot dominate.
7. Use paired comparisons of A/B on identical bytes, report disagreements, and ablate each evidence branch. Hold OCR and preprocessing conditions fixed or report them separately. Capture cold/warm runtime, peak memory, input dimensions, model loading and OCR inclusion on named hardware. External paper timings are not substitute measurements.
8. Record dataset/checkpoint/code licenses independently. Restricted research data remain outside production and outside redistributed artifacts. Any commercial clearance must name the exact artifact and intended uses. An MIT implementation trained on project-owned data is a candidate route, subject to its dependencies and initialization-weight terms.

**Illustrative sample-size planning.** With zero false positives among `n` independent authentic sources, the one-sided 95% binomial upper bound is `1 - 0.05^(1/n)` (approximately `3/n`). For `n=300`, that is about 1%, not proof of zero risk. Hundreds of transformations of ten originals still do not provide 300 independent sources. Determine acceptable error and coverage targets before looking at the final test results; no deployment claim is justified by a small procedural smoke set.

## Decision

The defensible near-term role is evidence-assisted review with explicit missing-data and abstention states. Prioritize honest output semantics, matched authentic controls, source-grouped evaluation and calibration before adding complex models. STFL offers the closest task framing; DTD and ADCD supply specific compression mechanisms and failure tests; TruFor motivates separate reliability estimation; C2PA supplies a different kind of provenance evidence. None converts a screenshot into proof of payment.
