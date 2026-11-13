# Repository integration

Destination: Beezsy-del/verisight-hackstellar-ps12. New branch: `feat/forensic-intelligence-tester`.
Foundation: `quality-of-life-updates`, commit c8aecbb307cbab70313bcd8c9d7191ca53256ed3. The remote main branch was older and lacked this foundation's private-access, storage, resource and gate safeguards. Originals and remote branches were not overwritten.

## Reconciliation

The tester workbench, response/voice workflows, optional Tesseract evidence, acquisition profile, local residual experiments, robust ORB candidates, isolated synthetic benchmark and research interface were integrated into a separate checkout.

Retained and connected: private access, analysis concurrency/response boundaries, structured analysis readiness gates, database health and opt-in persistence, signed upload/mobile routes, artifact expiry cleanup, receipt-statement OCR and model-release blockers. Mobile/cloud routes are isolated in `backend/app/api/cloud_endpoints.py`; all report consumers use the merged schema. Restored original-source priority for delivery simulation, explicit persistence messages, and review limitations. Corrupt uploads return client errors, including simulation input; resource limits remain 2 MP / 3200 pixels per side. No service credentials were introduced.

Legacy synergy fields remain compatibility aliases; the UI uses region_overlap_found and primary_review_locus, without claiming a score multiplier or proven forgery. Receipt text warnings may raise review priority separately from visual_tamper_score. This retains the existing repository's protection against visibly fake/pending/failed receipts; it is not bank verification. OCR availability gates remain distinct from classifier accuracy.

## Evidence and limitations

The stored baseline/upgraded prediction files are the **pre-integration frozen tester experiment**, not a fresh benchmark of the combined RapidOCR-enriched engine. Its experimental fusion candidate lost the promotion comparison (5/24 versus 6/24 matched-pair wins on locked synthetic pairs); it is not the production score. The 120 synthetic examples do not establish real-world generalization. The final integrated model has no representative held-out accuracy claim. Training and new-model deployment remain blocked.

An imported local receipt with undocumented permission was not copied. The stable sample_1 identifier now explicitly maps to the repository's original synthetic UI fixture. No silent missing-file substitution occurs. Private user-supplied datasets, old checkpoint binaries, local audit screenshots and machine-specific agent files were excluded. The new synthetic corpus retains its own manifest and license.

Cloud storage, public deployment, microphone permission on real devices and messaging-app delivery were not validated live. Browser voice support depends on browser permissions. Vercel dependencies/configuration were retained, but optional Tesseract is not bundled in serverless deployment. Local compact media transport is local-only. A bundle size warning remains; it does not prevent the production build.

## Validation

Commands and final results are recorded below after execution. Existing tests were retained and reconciled with deliberate contract changes: six synthetic cases, unavailable model metrics, auth-before-hosted-service rejection, the separated mobile router and a receipt-statement warning on synthetic text. New behavior is not validated by forcing expected numeric detector scores.

## Rollback

Use the existing quality-of-life-updates branch at c8aecbb or revert this integration commit on a separate branch. No database migration or deployment was performed. Stop local processes before switching code. Do not reset user working folders.

Historical reproducibility: `scripts/evaluate_robustness.py --engine upgraded` uses the frozen pre-integration tester backend in `research/tester_backend`; `--engine integrated` evaluates the combined engine into a separate output file. Neither command changes the promoted operational score. The preserved baseline source retains original whitespace intentionally. Legacy project-generated synthetic regression fixtures are included for existing software tests, independently of the newer 120-image corpus.

### Executed results (2026-11-13)

- `.venv/bin/python -m pytest backend/tests -q`: **220 passed**, one dependency deprecation warning. Repeated against a clean export of staged files: **220 passed in 57.86 seconds**.
- `npm test --prefix frontend`: gate rendering, verdict mapping, uncertainty notices, persistence, preview failure and original simulation-source contract checks passed.
- `npm run build --prefix frontend`: passed, with Vite's >500 kB chunk advisory. Clean-export build also passed.
- `BASE_URL=http://127.0.0.1:8002 node scripts/parity-browser.cjs` (Playwright available through NODE_PATH): **35 passed, 0 failed**. Navigation, upload/corrupt input, analysis modes, case races, memo, mobile handoff UI, recompression, evaluation unavailable states, complaint/PDF/notes and denied microphone behavior were checked. Four viewport sizes were captured: 1440×900, 1280×800, 1024×768 and 390×844. No uncaught browser errors. Raw results: `docs/validation/integration-browser-results.json`; local captures remain in ignored `output/playwright`.
- Staged-file credential/path scan: no private-key/token signatures, private user-supplied data paths, dependency symlinks or files above 50 MB found. This is a focused check, not a guarantee against all sensitive content.

No new model was trained, no live payment verification was performed, and no deployment was made.
