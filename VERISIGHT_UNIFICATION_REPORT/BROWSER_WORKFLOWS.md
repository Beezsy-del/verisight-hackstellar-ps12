# Real browser workflow verification

Native unified FastAPI app served the freshly built React app on loopback127.0.0.1:8899 with cloud credentials removed, using the audit Python3.12 environment. Headed Chromium through Playwright CLI completed:

1. Home → workbench, automatic sample1 analysis200. New readiness panel showed Review needed; no payment approval.
2. Upload Evidence file chooser → actual synthetic `FAKE PAYMENT RECEIPT` PNG. `/api/analyze`200. UI showed Likely misleading55, OCR evidence box around the text, readiness Review needed, and settlement caveat. Screenshot visually inspected.
3. Export report modal opened with readiness panel. Escape closed it.
4. WhatsApp simulation using the uploaded source returned200 and opened comparison/heatmap modal. The transformed result remained review-required. Close worked.
5. Evaluation navigation loaded `/api/model/status` and `/api/model/evaluation`200.

Browser console reported0errors/0warnings after workflows. No app crash observed. Captured screenshots and accessibility snapshots live under `output/playwright/` (unified_sample_gate.png, unified_uploaded_fake.png, unified_report.png, unified_simulation.png, unified_evaluation.png). Server process15998 and named browser unified-verisight were shut down.

These are real computed results on a synthetic diagnostic input, not real-world accuracy proof. Live database/signed storage, actual mobile hardware, printing/PDF, responsive layouts, positive-overlap rendering and concurrency were not browser-tested here. Backend tests and parent benchmarks cover separate concerns; no production deployment performed.
