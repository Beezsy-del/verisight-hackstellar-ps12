> Updated review: see [Localization data and release plan](LOCALIZATION_DATA_AND_RELEASE_PLAN.md)
> for the current permission audit, proposed gates, and blocked training decision.
> The existing two UI verdict labels remain unchanged.

# VeriSight model readiness and training plan

## Current state

- There is **no trained image-forgery model** in this deployment. `AdvancedModelAdapter.run_inference()` always returns `inference_run: false`.
- The repository contains five synthetic demo fixtures (one clean baseline and four altered examples), not a representative labeled corpus of real payment/QR screenshots.
- The clean fixture is synthetic and is not a verified authentic bank receipt. A screenshot that has no visual anomaly is not proof of origin or settlement.
- The image pipeline is heuristic triage. It now returns `INCONCLUSIVE`, `REVIEW_REQUIRED`, or `CORROBORATED_ANOMALIES`; none of those means a payment is confirmed or denied. Classifier confidence is `null` until a model is trained and calibrated.
- QR decoding reports the embedded payload and basic type locally. It does not certify the QR, payee, website, or transaction.

Training on augmented copies of the five fixtures would leak the same layouts into both training and test data and teach the model fixture-specific clues. It would not justify an accuracy claim. We therefore did **not** train or ship a model on this data.

## Data needed for a meaningful screenshot model

1. Obtain permission to use authentic screenshots from the payment apps/devices that the product must support. Remove personal names, account identifiers, phone numbers, and transaction identifiers, or use controlled test accounts with synthetic transactions.
2. For every source screenshot, keep a verified untouched original and create controlled edits: amount/text replacement, pasted patches, cloned regions, generated UI, QR destination replacement, and recompression/resizing/cropping. Save pixel masks for local edits and record each transformation.
3. Label payment state separately from image editing. A real payment requires a trusted provider/bank record or a controlled test transaction. Human review of a screenshot alone is not payment ground truth.
4. Split by source transaction, app version, device, and template before augmentation. Keep entire groups out of training; never split near-identical derivatives across train and test.
5. Test on untouched originals, unseen templates/devices, and realistic social-media recompression. Report false-positive rate on authentic screenshots, false-negative rate on altered screenshots, precision/recall, ROC/PR curves, calibration error, and localization IoU with confidence intervals. Tune the acceptance threshold to the desired false-positive cost.
6. Do not ship a `FAKE` or `AUTHENTIC` determination until an independent holdout evaluation supports it. Keep transaction/provider verification as a separate check.

## Research datasets and model limitations

- [NIST OpenMFC](https://mfc.nist.gov/?datasets=openmfc) provides media-manipulation evaluation material through registration and licensing. Its image forensics task is not a payment-screenshot verification dataset.
- [TruFor](https://github.com/grip-unina/TruFor) provides research code and weights for image manipulation localization, with dataset/license conditions. It is a candidate for offline experimentation, not a drop-in payment-authentication model; domain transfer to flat UI screenshots must be measured.
- Image-forensics benchmarks can help pretrain or compare pixel manipulation detectors, but they cannot verify that a bank transfer settled. For payment state, use an authorized payment-provider/bank integration or an independently verified test ledger.

## Release gates

- Model artifact, source commit, training data manifest, license, preprocessing configuration, and reproducible training command are versioned.
- Real screenshot families are represented in a source-grouped holdout set.
- A calibration set is separate from the final test set; score thresholds are fixed before final evaluation.
- Production displays metrics from that evaluation and returns `INCONCLUSIVE` when the input is outside the validated domain or the necessary modality is unavailable.
