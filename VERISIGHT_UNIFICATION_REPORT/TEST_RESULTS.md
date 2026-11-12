# Test results

Final full-suite results (A/B JUnit; U final own-environment log supersedes earlier124-case run):

|Version|Collected|Failures/errors|
|---|---:|---:|
|A|93|0|
|B|38|0|
|U final local environment|126|0|

Both original frontends build from clean npm installs (raw/original_builds.json); unified build/browser evidence is in FRONTEND_VERIFICATION.md and BROWSER_WORKFLOWS.md. Additional resource/gate/persistence targeted results are recorded by the implementing agents; do not treat suite counts as scientific validation.

## Failures discovered and handled

- Original A initial disposable test copy lacked dist: SPA route404. Clean frontend build resolves preparation issue; no original source change.
- Initial benchmark adapter looked in results rather than raw: failed before inference. Fixed audit script; no fabricated replacement values.
- Unified mobile-upload acknowledgment had verdict but no gate: boundary correctly rejected503. Product acknowledgment now carries its actual analysis gate.
- Existing session-isolation test supplied filename-only fake reports; new nested gate rejects these incomplete reports. Fixture updated to carry a valid report gate; separate gate-rejection cases retain fail-closed behavior.

The initial failure logs remain in raw for review. Genuine cloud database failures, deployment access controls and physical mobile device workflows are not fully certified. No training data were used or created for model fitting.


Final actual-API response-budget probe:3,694,273-byte high-entropy PNG returns413 with a217-byte explicit FAILED/BLOCK response, not oversized JSON. Raw evidence: `raw/response_budget.json`; reproducible `scripts/verify_response_budget.py`. This bounds transport, not worst-case upstream memory. Audit artifacts are excluded from Vercel deployment; pytest discovery is restricted to backend/tests.
