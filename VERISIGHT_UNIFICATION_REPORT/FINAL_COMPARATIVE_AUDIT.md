# Final independent comparison

**Unified VeriSight is stronger in report integrity, explicit processing gates and engineering safety, not proven more accurate at detecting screenshot edits.**

|Version|Completed|Edits flagged, common subset|Clean false alarms|Median|p95|Peak RSS|
|---|---:|---:|---:|---:|---:|---:|
|A|117/117|11/63|0/9|0.636s|1.917s|801.4MiB|
|B|108/117|21/63|1/9|0.262s|0.873s|334.9MiB|
|U|117/117|11/63|0/9|0.635s|1.868s|799.9MiB|

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
