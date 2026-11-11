# Receipt text scanning repair — 2026-11-11

Reproduction: a white PNG with the visible text `FAKE PAYMENT RECEIPT` returned
`INCONCLUSIVE` (0 points), displayed as `Likely accurate`. The original component
extractor returned bounding boxes with placeholder text, not recognized words.

Added local RapidOCR/ONNX text recognition alongside the existing geometry
extractor. High-confidence, whole-line fake/demo/non-real and failed/pending
payment assertions now produce a visible-text finding with its bounding box.
Whitespace normalization handles JPEG OCR joining adjacent words. Help text and
low-confidence matches are not treated as affirmative evidence. OCR failures and
no-readable-text cases require review rather than silently returning favorable.
The two display labels remain `Likely misleading` and `Likely accurate`.

This is a specific false-negative repair, not a validated general fake-receipt
classifier. A carefully fabricated receipt with plausible text and consistent
pixels may still evade these rules. No bank/payment-provider verification is
performed. OCR confidence measures recognition, not authenticity. No classifier
was retrained and no real-world accuracy percentage is claimed. The user's
specific failing screenshot was not available for reproduction.

Regression command: `.venv/bin/python -m pytest backend/tests/test_receipt_text.py -q`.
The tests render assertions into PNG and JPEG pixels and run real OCR through the
full analysis pipeline, alongside non-assertion controls and failure handling.
The clean synthetic demo now requires review because its visible watermark says
it is not a real transaction; it remains a clean *pixel* baseline.

Sources consulted:
- https://rapidai.github.io/RapidOCRDocs/latest/install_usage/rapidocr/usage
- https://openaccess.thecvf.com/content/CVPR2023/html/Qu_Towards_Robust_Tampered_Text_Detection_in_Document_Image_New_Dataset_CVPR_2023_paper.html
- https://openaccess.thecvf.com/content/ICCV2025/html/Wong_ADCD-Net_Robust_Document_Image_Forgery_Localization_via_Adaptive_DCT_Feature_ICCV_2025_paper.html

Document forgery localization models are promising candidates for a separate,
representative held-out receipt evaluation. Their document benchmark results do
not establish accuracy on this application's payment screenshots. Blindly adding
such a model or increasing heuristic weights would not establish that accuracy.

Deployment note: RapidOCR ships pretrained OCR models and declares a GUI OpenCV
wheel. Install the pinned headless OpenCV wheel last on headless hosts. The
Vercel install command and CI account for this. Cloud packaging and latency still
need verification before publishing this change.
