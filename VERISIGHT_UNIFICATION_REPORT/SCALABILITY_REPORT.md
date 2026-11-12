# Resource and scaling boundary

The unified API uses a process-local two-slot nonblocking admission limit for analysis, simulation and mobile analysis. Saturation returns explicit503/Retry-After; no unlimited in-memory queue is introduced. Slots release in finally even on failures. This is per process, not a global distributed quota.

Analysis JSON is buffered up to4,000,000 bytes and rejected with413 if it exceeds that limit. The response explicitly reports failed processing/BLOCK rather than returning an oversized apparent success. No original analysis pixels are resized or changed. This fixes response transport correctness, but large high-entropy images remain unusable until private artifact delivery is implemented. Memory includes upstream serialization before this check; the existing image pixel cap still matters. No distributed scalability or throughput guarantee is claimed.

Tests cover concurrent saturation, recovery, response overflow and exception cleanup. Existing bounded OCR engine reuse remains. Background persistence and synthetic demo caching remain; no new job broker is required. Exact timings and three-way benchmarks are recorded in BENCHMARK_RESULTS.md. Cloud cold starts, multiple workers and actual database throughput remain unverified.


Final actual-API response-budget probe:3,694,273-byte high-entropy PNG returns413 with a217-byte explicit FAILED/BLOCK response, not oversized JSON. Raw evidence: `raw/response_budget.json`; reproducible `scripts/verify_response_budget.py`. This bounds transport, not worst-case upstream memory. Audit artifacts are excluded from Vercel deployment; pytest discovery is restricted to backend/tests.
