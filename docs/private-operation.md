# Private prototype operation

This build supports a single local process for private development. It does not establish real-world fraud detection accuracy, a public service capacity guarantee, authenticated multi-user history, or payment settlement. Keep both verdict labels unchanged and the accompanying uncertainty visible. Model promotion remains blocked pending authorized representative evaluation.

## Access and supported scope

Run `./start-verisight.sh` for loopback-only development, or build the frontend and run `.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8101 --no-access-log` for the combined application. Do not expose the Vite development proxy. No deployment was performed.

For a shared private HTTPS host set `VERISIGHT_ACCESS_PASSWORD` to a strong unique secret in the process environment. The browser's Basic authentication username is `verisight`. Without a password, non-loopback requests are refused; remote HTTP requests are refused even with a correct password. All application routes, API results and artifacts use this boundary. This is shared single-reviewer authentication, not individual accounts or tenant isolation. Rotation revokes the old credential. Use a trusted TLS reverse proxy, restrict proxy-header trust to that proxy, disable access logs containing capability paths, and test the real perimeter before sharing. Local reverse proxies can make clients appear local: the password is mandatory for any shared proxy. Cross-origin form submissions are rejected; same-origin operation is supported.

`GET /api/operating-envelope` exposes the declared limits:

- 20 MiB file; 21 MiB multipart transport; two million decoded pixels; 3200 pixels maximum side. Larger dimensions fail before forensic processing.
- Two concurrent analyses per process; additional work receives retryable503. Exactly one worker is supported for local preview and phone-session state.
- JSON responses bounded to4,000,000 bytes; individual local private previews below6,500,000 bytes (these routes are not used on Vercel). Temporary preview storage capped128 MiB.
- Large viewer assets use unpredictable256-bit capability URLs, filesystem permissions0700/0600, no-store responses and no-referrer policy. Never share those URLs. Small assets remain inline.
- Previews expire after10 minutes. A30-second background sweep deletes expired files while the service runs; expiration is enforced on reads. Normal shutdown deletes remaining previews. A hard crash can leave temporary directories under the OS temporary directory: remove old `verisight-previews-*` directories after stopping the process. This is not cryptographic erasure or a retention guarantee while the host is off.
- Full-resolution analysis still allocates working image arrays; there is no guaranteed hard RSS ceiling or process timeout. This implementation avoids large JSON serialization but does not eliminate forensic memory costs. No worker farm, persistent queue, throughput SLA or serverless artifact delivery is implemented.

Vercel uses inline bounded responses because local temporary URLs cannot reliably survive another invocation. Authentication is required there, but cloud end-to-end correctness and deployment readiness remain unverified. Do not deploy as a public product.

## Storage and retention

`VERISIGHT_PERSIST_CASES=0` is the default. Set it to1 only for authorized storage with the documented Supabase credentials and migrations. Reports expose `persistence_status`: DISABLED, NOT_CONFIGURED, FAILED, SAVED or NOT_REQUESTED. A usable screenshot report can coexist with a failed save; the UI must not claim it was saved. SAVED means the summary write was accepted, not that a backup or retrieval workflow was verified.

New persisted summaries carry `layer_summary.retention_policy=private-prototype-7d`. While database credentials are configured and the single process is running, the background sweep deletes only tagged summaries older than7 days. Existing untagged history is not deleted. Signed-upload orphan cleanup runs in the same lifecycle loop when storage credentials exist; it uses the existing24-hour policy. Local unconsumed mobile reports expire after10 minutes. Retention failures are logged, not reported as success; live Supabase retention has not been verified. An always-on external scheduler is required for retention while this process is offline. Original upload bytes are not stored in the summary table, but findings and filenames may contain sensitive text; consent and access restrictions are still required.

## Reproduction

```sh
.venv/bin/python -m pytest -q
npm run test --prefix frontend
npm run build --prefix frontend
.venv/bin/python scripts/verify_operating_envelope.py
```

The resource probe generates its own noise image; it tests delivery and admission, never accuracy. On this development host, a960×1280 noise PNG (3,692,522 bytes) returned200 with5,629 JSON bytes and four retrievable previews; the earlier inline approach rejected a comparable noise image. Single request2.0621s; the maximum2MP probe returned200 in3.1021s with four retrievable previews and5,645 JSON bytes. A three-request burst returned two200s and one503; observed process peak RSS1,119.14MiB across this broader run. The analysis correctly retained a BLOCK gate for unavailable OCR, despite successful delivery. These are one-run measurements, not a benchmark distribution or a memory bound. Raw output: `docs/operating-envelope-results.json`.

## Rollback and recovery

Stop the service before changing delivery code. Existing source repositories remain untouched and can be used as historical references. Do not revert only the frontend URL support while retaining private artifact URLs. If preview delivery fails, preserve the error and rerun after capacity expires; do not substitute a favorable verdict. Restart invalidates existing local preview URLs and phone handoffs. Leave persistence disabled if storage or retention checks fail. Model release remains blocked independently of transport success.

Verification completed:157 backend tests passed (one existing dependency deprecation warning); frontend contract tests and production build passed (existing bundle-size warning). Browser upload of the noise fixture loaded the full-resolution private preview and completed the simulation with zero console errors or warnings. Storage failure and preview expiration are covered by deterministic tests; no live Supabase, public TLS ingress or human comprehension study was exercised.
