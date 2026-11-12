# Known limitations

- This is an evidence-assisted screenshot review product, not a validated authenticity oracle. Two requested labels cannot by themselves express all uncertainty; gate/coverage explanations remain necessary.
- No authorized representative real-device screenshot corpus is available. No training, external calibration, independent held-out real-world accuracy or validated false-positive target can be claimed.
- Actual OCR can read explicit misleading/failed/pending statements, but semantic wording is not visual tampering and cannot verify payment settlement.
- Neither original has a trained pixel-level localization model. Heuristic boxes/heatmaps are exploratory evidence; they can flag benign rendering/compression.
- Carefully fabricated screenshots with plausible text/pixels may evade detection. New implementation safeguards cannot manufacture information absent from the image.
- The reference benchmark has117 synthetic inputs, strongly related templates, and known labels. Improvements on it are regression/mechanism evidence only, not real-world fraud accuracy.
- Source/template/device/contributor grouping, calibration and data permissions still gate any future learned model release.
- No bank/PSP status integration, live Supabase credentials, cloud entitlement or real multi-region deployment was exercised. Retained adapters/migrations are implementation, not proof of configured service health.
- Local resource admission controls do not constitute a globally shared distributed queue or multi-instance rate limiter. Public deployment needs its own authentication, perimeter controls and operational monitoring.
- Browser smoke is bounded; physical mobile devices, accessibility breadth and external storage workflows need deployment-specific verification.
- Analysis PASS means only that configured checks completed without the gate's review conditions; it never authorizes funds, delivery of goods, or an authenticity guarantee.
