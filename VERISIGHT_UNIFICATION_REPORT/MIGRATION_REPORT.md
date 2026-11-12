# Migration report

The implementation is a new directory `/Users/shreeshaks/Documents/VERISIGHT_UNIFIED`. Originals are cloned separately under `VERISIGHT_UNIFICATION_SOURCES/A` and `/B`, with exact branches retained. No conventional Git merge or original overwrite occurred.

A's application shell is the initial scaffold, selected from inspected validation/storage/UI boundaries rather than its branch name. Component selection precedes production promotion; B's trained artifacts are not silently copied into runtime. A's current dependency envelope avoids B's NumPy2 pickle compatibility requirement. The comparison runner deliberately uses NumPy2 for both originals and unified to hold numerical environment constant; production installation is separately checked by the parent.

## Compatibility boundaries

- Current A=Hackstellar; historical audit B=Hackstellar. This mapping is explicitly recorded in every inherited audit.
- Verdicts are one evidence-state vocabulary. Display labels remain `Likely accurate` and `Likely misleading`.
- New `analysis_gate` is a processing/review policy, not a bank or payment-release authorization.
- Frontend overlap fields must match `region_overlap_found` and `primary_review_locus`; no fallback to old fraud-localization names.
- Authenticated financial settlement is not implemented; every result preserves that boundary.
- Existing Supabase migrations are retained; no remote migration or database mutation was performed during implementation.
- Originals' benchmark/image/model artifacts remain research-only and untouched. Audit data are copied into report/data for reproducibility.

No model training occurs: suitable authorized representative data remain unavailable. Preserve original history and test evidence when future releases add an approved model. Rollback of the new local application means stopping it and using either untouched original; cloud rollback has not been exercised because no deployment occurred.
