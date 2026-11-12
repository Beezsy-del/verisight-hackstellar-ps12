# Unified detection engine

The engine remains an evidence-assisted review system. It does not verify settlement and has no representative trained tampering-localization model. Both user-facing labels remain unchanged.

The retained path computes hash and validated decode; metadata/QR/provenance markers; ELA, residual variation, ORB repeated regions; component geometry and background margins; conservative rule correlation; real RapidOCR statement findings; then deterministic evidence validation and report-use gating. No LLM decides the verdict.

`visual_tamper_score` captures the original visual/metadata heuristic aggregation before OCR warnings alter legacy review priority. `score_kind=uncalibrated_review_priority` names the overall score accurately. Neither score is a probability. `evidence_sources` independently exposes visual processing, OCR coverage, untrusted metadata, QR decode-only state, absent trained tamper model and absent bank integration. OCR confidence remains recognition confidence, never authenticity probability.

ScamShield's canonical-schema idea is useful, but its current model is not imported into production: the prior audit demonstrated mismatched runtime/offline flags, unreliable confidence, dependency conflicts and an auxiliary probability disconnected from the verdict. Its syndicate/legal accusations and literal C2PA trust markers are not defensible detection improvements. Both branches already share corrected background-margin analysis; duplicating it adds no value.

No newly claimed detection accuracy follows from these engineering changes. Compare original/unified same-input benchmark results in BENCHMARK_RESULTS. Coverage blocks and evidence validation improve reliability independently of edit recall. Plausible re-rendered receipts, subtle edits, unfamiliar apps and semantic claims remain challenging; only licensed representative data and independent evaluation can support future promotion.
