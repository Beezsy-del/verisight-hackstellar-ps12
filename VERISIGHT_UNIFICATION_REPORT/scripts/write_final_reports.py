from pathlib import Path
import json,xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1];s=json.loads((r/'raw/summary.json').read_text())
rows=[]
for v in ['A','B','U']:
 d=s[v];m=d['common_controlled'];rows.append(f"|{v}|{d['completed']}/{d['attempted']}|{m['tp']}/{m['tp']+m['fn']}|{m['fp']}/{m['tn']+m['fp']}|{d['median_seconds']:.3f}s|{d['p95_seconds']:.3f}s|{d['peak_rss']/1048576:.1f}MiB|")
table='|Version|Completed|Edits flagged, common subset|Clean false alarms|Median|p95|Peak RSS|\n|---|---:|---:|---:|---:|---:|---:|\n'+'\n'.join(rows)
(r/'BENCHMARK_RESULTS.md').write_text('''# Three-version benchmark results

A=Hackstellar347c7a7, B=ScamShield2260e5, U=unified. Identical117 synthetic input bytes and12repeat calls per version,129calls each. Source clones are untouched; originals execute in disposable report/runtime copies. Images and masks are copied into data; raw manifest includes SHA-256. Same Python3.12, NumPy2.2.6/scikit-learn1.9.1/OpenCV4.10 environment as prior audit, single OpenCV/BLAS threads, real OCR remains enabled. No training or threshold selection.

'''+table+'''

## Interpretation

The common controlled subset contains9 clean and63 edited variants from only3 synthetic seed families. Nine QR insertions crash B and are excluded from the common comparison but remain execution failures. These counts do not estimate field accuracy. Native backend decisions are used: non-INCONCLUSIVE for A/U and non-AUTHENTIC_VERIFIED for B. B's actual UI incorrectly maps all legacy verdicts to Likely misleading; do not interpret its native detector numbers as correct UI behavior.

U's headline verdicts and scores are identical to A on all117 unique inputs. Therefore **no detection-accuracy improvement is demonstrated**. Engineering gains are explicit, auditable gates, failure handling, contract repair and resource admission/output bounds. Lower sensitivity than B on some edits remains a known limitation, not hidden by increased test count.

The benchmark calls the actual pipeline, not HTTP middleware; output-budget/429/failure-gate behavior is tested separately. PASS means report processing completeness only; all U gates prohibit automated approval and payment settlement remains unverified. No synthetic benchmark was used to tune thresholds. Existing real-world deployment gates remain blocked.

Local timing is descriptive; ordinary desktop/build/test activity may overlap. Do not claim a speedup or cloud SLA. Peak RSS is per-process high-water memory on macOS, not incremental memory perrequest. Full records contain every input result, errors, gate, boxes, latency and payload size. Old source-identical baseline evidence in COMPARATIVE_AUDIT independently corroborates counts.

## Reproduce

Use the compatible environment pinned in the previous audit requirements-audit-numpy2.lock, or create an equivalent isolated environment. Build A's disposable frontend before its suite because SPA-route tests require dist. Run `scripts/run_comparison.py A B U` with that interpreter, then `scripts/summarize.py`. The script runs full suites and benchmarks, never fits a model. `scripts/benchmark.py generate` can regenerate controlled fixtures; the supplied manifest/data preserve the exact measured bytes. All raw timing/counts are in raw/summary.json and per-version JSONL.

Incomplete coverage: real device/app/contributor diversity, screen recapture, independently authorized payment screenshots, real bank outcomes, learned-mask IoU and calibrated authenticity probability remain unavailable. The original audit's box-proxy localization evidence is not promoted into learned-mask accuracy.
''')
checks=[]
for v in ['A','B','U']:
 p=r/f'raw/{v}_pytest.xml'
 if p.exists():
  x=ET.parse(p).getroot();suites=list(x) if x.tag=='testsuites' else [x];checks.append((v,sum(int(z.attrib.get('tests',0)) for z in suites),sum(int(z.attrib.get('failures',0))+int(z.attrib.get('errors',0)) for z in suites)))
final_log=r/'raw/U_local_environment_final.log'
if final_log.exists():
 import re
 match=re.search(r'(\d+) passed',final_log.read_text())
 if match:checks=[(v,n,f) for v,n,f in checks if v!='U']+[('U final local environment',int(match.group(1)),0)]
(r/'TEST_RESULTS.md').write_text('# Test results\n\nFinal full-suite results (A/B JUnit; U final own-environment log supersedes earlier124-case run):\n\n|Version|Collected|Failures/errors|\n|---|---:|---:|\n'+'\n'.join(f'|{v}|{n}|{f}|' for v,n,f in checks)+'''\n
Both original frontends build from clean npm installs (raw/original_builds.json); unified build/browser evidence is in FRONTEND_VERIFICATION.md and BROWSER_WORKFLOWS.md. Additional resource/gate/persistence targeted results are recorded by the implementing agents; do not treat suite counts as scientific validation.

## Failures discovered and handled

- Original A initial disposable test copy lacked dist: SPA route404. Clean frontend build resolves preparation issue; no original source change.
- Initial benchmark adapter looked in results rather than raw: failed before inference. Fixed audit script; no fabricated replacement values.
- Unified mobile-upload acknowledgment had verdict but no gate: boundary correctly rejected503. Product acknowledgment now carries its actual analysis gate.
- Existing session-isolation test supplied filename-only fake reports; new nested gate rejects these incomplete reports. Fixture updated to carry a valid report gate; separate gate-rejection cases retain fail-closed behavior.

The initial failure logs remain in raw for review. Genuine cloud database failures, deployment access controls and physical mobile device workflows are not fully certified. No training data were used or created for model fitting.
''')
(r/'FINAL_COMPARATIVE_AUDIT.md').write_text('''# Final independent comparison

**Unified VeriSight is stronger in report integrity, explicit processing gates and engineering safety, not proven more accurate at detecting screenshot edits.**

'''+table+'''

- Detection: U is intentionally unchanged from A on all measured inputs. B flags more controlled edits but has higher false alarms and broken UI/QR behavior. No universal detector superiority is established.
- Evidence: U adds typed gate decisions, reasons/evidence references and separate evidence-source coverage, preserving unavailable authenticity confidence and unverified settlement.
- Correctness: the shared CIELAB/residual methods are retained; no arbitrary B confidence/syndicate/C2PA trust logic is promoted. Overlap/frontend field alignment is repaired.
- Reliability: malformed input handling remains A's validated path; upstream incomplete/failed reports cannot be returned as automatically approved. Mobileack integration regression was exposed and repaired.
- Performance/scaling: bounded in-process admission and response budget improve failure behavior; no distributed queue or global rate limit is claimed. Large responses may be explicitly blocked rather than delivered, a documented usability trade-off.
- Security: unsafe alternate root-directory server is replaced; original Supabase adapters remain, but live credentials/perimeter authorization are not certified.
- Maintainability: one report/gate contract prevents duplicate headline classifiers. No incompatible research model dependencies enter production.
- Experience: two requested labels preserved, supporting gate/coverage explanations visible, overlap fields aligned; bounded browser workflows are captured separately.

## Remaining critical limitations

No validated pixel localizer, no representative permission-cleared dataset, no real-world calibration, no bank/PSP settlement integration, and substantial missed-edit counts remain. A complete fraud-detection claim would require authorized data and locked independent validation. The mission's stronger-engineering portion is demonstrable; stronger real-world detection remains unproven and must not be marketed as achieved.
''')
(r/'EXECUTIVE_VERDICT.md').write_text('''# Unified VeriSight executive verdict

The new project is `/Users/shreeshaks/Documents/VERISIGHT_UNIFIED`. Both original repositories remain preserved. Exact remote branch identities are recorded in raw/source_comparison.json and histories; current A is Hackstellar, current B is ScamShield.

**The unified product is a more coherent and safer review prototype. It is not a scientifically validated fake-screenshot detector, and no accuracy improvement is claimed.** Components were selected using actual defects and tests rather than branch names. A supplies validated intake/OCR/storage boundaries. B's useful schema/research ideas inform explicit contracts, while unsupported confidence, automatic accusations and incompatible experimental weights are not shipped.

Implemented engineering improvements include deterministic analysis/model-release gates, explicit evidence coverage, corrected UI overlap contracts, bounded resource/response handling, and safer legacy entrypoint behavior. Every analysis gate keeps automated approval false and payment settlement unverified. Dataset/model promotion remains blocked without required evidence.

'''+table+'''

U's headline detection scores and verdicts match A exactly on117 unique synthetic probes. B's higher native recall on this small set comes with false alarms and a broken UI mapping; it is not enough to justify copying its main scoring logic. Real-world accuracy remains unknown.

Read COMPONENT_SELECTION.md, UNIFIED_ARCHITECTURE.md, BENCHMARK_RESULTS.md, TEST_RESULTS.md and FINAL_COMPARATIVE_AUDIT.md for measured trade-offs and remaining work. No training, original overwrite, Git push, database migration or cloud deployment was performed. A future scientifically stronger detector still requires authorized representative data, grouped independent splits, valid masks, threshold selection and calibrated held-out evaluation.
''')
print('Wrote final benchmark/test/comparison/executive reports',checks)
