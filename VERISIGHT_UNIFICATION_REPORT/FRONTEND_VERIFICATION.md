# Frontend integration and verification

Current version names: A is Hackstellar release-gates, B is remote ScamShield scaling. Prior COMPARATIVE_AUDIT reversed these letters. Original repositories untouched.

## Selection and implementation

Retained the shared React workbench, image viewer, comparison/loupe, report, mobile intake and simulator flows. Hackstellar's existing request-version protection, original-source simulation and explicit limitations are useful behaviors rather than proof that its entire frontend is superior. ScamShield's corresponding overlap fields match its own older API, but cannot be copied into the unified evidence API: its categorical authenticity states also disagree with the shared two-label helper. Its experimental calibration dashboard is not appropriate as the unified runtime's status display without an approved active model.

Fixed the actual unified API/TypeScript contracts: `region_overlap_found`, `primary_review_locus`, and baseline `is_alignment_outlier`. Sidebar and print summary now consume those fields; viewer baseline cues use the actual backend outlier flag. Removed the non-existent multiplier boost and renamed the locus toast to an overlapping review cue. Box confidence admits null rather than pretending every box has a probability.

Added `AnalysisGatePanel` to sidebar and report modal with the coordinated backend schema: state PASS/WARNING/BLOCK, processing status, policy version, reasons, allowed actions and settlement flag. UI translates these to Checks complete / Review needed / Incomplete without presenting a pass as authenticity or payment approval. Missing gate explicitly displays incomplete/block. Gate reasons are ordinary React text nodes, so upstream text does not become HTML.

Preserved exact verdict labels **Likely accurate** / **Likely misleading**. Unknown verdicts remain the warning label; sidebar styling now uses the same favorable-state test, avoiding an unknown verdict receiving contradictory green styling. Supporting text states that authenticity remains unknown and settlement requires independent authorized integration.

## Verification

- `npm ci --prefix frontend --no-audit --no-fund`: passed.
- `npm run build --prefix frontend`: TypeScript and Vite production build passed. Main bundle remains about517 kB uncompressed, with the existing large-chunk warning.
- `npm run test --prefix frontend`: passed. Test transpiles the actual TypeScript helper/component, renders gate states with React SSR, checks missing gate fallback, exact verdict labels and active overlap contract references.
- No new UI results or calibration values were fabricated. Rendering tests supply isolated test props, not production mock logic.
- Parent integration/browser verification must exercise the complete updated backend/frontend. This component work does not claim browser screenshots or successful production cloud storage.

## Remaining limits

The requested binary verdict vocabulary still compresses a nuanced review state; the accompanying coverage and gate explanations are essential. The frontend cannot turn heuristic absence of cues into proof of authenticity. A gate pass never authorizes release of money or goods. An unavailable/blocked model cannot be made available through a dashboard label.
