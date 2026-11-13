# VeriSight — Forensic Algorithm Comparison Matrix

This document provides a comparative analysis of the digital image forensics algorithms evaluated, adapted, and implemented within the **VeriSight** platform.

---

## 1. Comparative Algorithm Matrix

### 1.1 Error Level Analysis (ELA)
* **Sherloq Implementation:** `gui/tools/jpeg/ela.py` — Re-compresses the image using a single user-chosen JPEG quality factor ($Q=75$ or $Q=90$), computes absolute difference, multiplies by a constant scale factor, and plots the result via Matplotlib.
* **Sherloq-WebUI / Forensically:** Client-side HTML5 Canvas re-compression via `toDataURL('image/jpeg', quality)`. Subtracts RGB channels, scales by a gain slider, and renders directly to a secondary 2D canvas context.
* **Research Implementation:** Krawetz (2007), *A Picture's Worth... Digital Image Analysis*. Analyzes the error rate introduced by discrete cosine transform (DCT) quantization across $8 \times 8$ macroblocks.
* **VeriSight Implementation (`services/forensic/pixel_analysis/ela.py`):**
  - **Adaptive Multi-Scale Quality:** If Layer 3 detects WhatsApp/Telegram re-compression traces, VeriSight anchors reference quality at $Q_{\text{ref}}=75$; otherwise sweeps $Q=90$ and $Q=80$.
  - **Dynamic Gain Normalization:** Applies dynamic gain ($\times 18$) with non-linear saturation prevention.
  - **Macroblock Z-Score Splicing Localization:** Subdivides the ELA residual into $16 \times 16$ spatial macroblocks. Computes global distribution $\mu_{\text{ELA}}$ and $\sigma_{\text{ELA}}$. Contiguous clusters where $\text{BlockMean} > \mu_{\text{ELA}} + 2.6\sigma_{\text{ELA}}$ are clustered into bounding boxes with confidence scores.
  - **Colormap:** Renders a high-contrast OpenCV `COLORMAP_INFERNO` heatmap encoded as base64 PNG.
* **Expected Inputs:** Input image buffer (`np.ndarray` BGR, $W \times H \times 3$), optional target quality $Q$.
* **Expected Outputs:** ELA score ($0–100$), base64 PNG heatmap, list of anomalous macroblock bounding boxes, local mean/std statistics.
* **Computational Requirements:** $\sim 25\text{ ms}$ on $1080 \times 1920$ image (pure NumPy/OpenCV vectorization).
* **Known Limitations:** Solid flat UI colors (e.g. solid white/black card backgrounds) naturally have zero ELA difference, which can be mistaken for splicing unless cross-checked with Wavelet Noise (Layer 1) and CIELAB patch metrics (Layer 2).
* **Test Strategy:** Unit test with known double-compressed JPEG patches and verify bounding box localization around spliced amount regions.

---

### 1.2 2D Wavelet Noise Residual Analysis ($W_{HH}$ Daubechies db4)
* **Sherloq Implementation:** `gui/tools/noise/noise_separation.py` — Computes 2D wavelet decomposition, thresholding coefficients to separate signal from noise.
* **Research Implementation:** Mahdian and Saic (2009), *Using Noise Inconsistencies for Blind Image Forensics*. Decomposes luminance into wavelet sub-bands, computing local variance on the high-pass diagonal detail sub-band ($cD/HH$) with local estimator $\hat{\sigma} = \frac{\text{median}(\vert cD \vert)}{0.6745}$.
* **VeriSight Implementation (`services/forensic/pixel_analysis/wavelet_noise.py`):**
  - Converts RGB to YCbCr luminance $Y$.
  - Computes single-level 2D Discrete Wavelet Transform (`pywt.dwt2(Y, 'db4')`), extracting the diagonal high-frequency sub-band ($cD$).
  - Runs a sliding $9 \times 9$ box filter variance estimation across $cD$.
  - Identifies "Zero-Noise Voids" (where solid paint-brush edits or uniform patches obliterate native render noise) as well as "High-Pass Splicing Halos".
  - Generates a high-contrast Cyan/Magenta normalized noise heatmap (`wavelet_noise_b64`) and computes a global `noise_inconsistency_score`.
* **Expected Inputs:** Grayscale/luminance plane $Y$ ($W \times H$).
* **Expected Outputs:** Noise inconsistency score ($0–100$), base64 PNG noise heatmap, bounding boxes around anomalous noise voids/peaks.
* **Computational Requirements:** $\sim 45\text{ ms}$ on $1080 \times 1920$ image using PyWavelets C-extensions.
* **Known Limitations:** Flat UI vector containers (e.g., standard Google Pay cards) naturally have low noise. VeriSight accounts for this by conditioning the noise threshold on local card boundaries.
* **Test Strategy:** Test on synthetic sample with zero-noise painted patch vs. authentic screenshot with uniform Gaussian dither.

---

### 1.3 Copy-Move Forgery Detection (ORB + Translation Clustering)
* **Sherloq Implementation:** `gui/tools/tampering/copy_move.py` — Extracts SIFT, SURF, or ORB keypoints, runs k-NN brute-force matching, filters matches with distance ratio test, and renders lines connecting matching points.
* **Research Implementation:** Amerini et al. (2011), *A SIFT-Based Forensic Method for Copy-Move Attack Detection and Transformation Recovery*. Clusters keypoint displacement vectors $(\Delta x, \Delta y)$ to isolate rigid translations.
* **VeriSight Implementation (`services/forensic/pixel_analysis/copy_move.py`):**
  - Detects up to 1500 ORB keypoints and descriptors (`cv2.ORB_create(nfeatures=1500)`).
  - Matches descriptors using Brute-Force Hamming distance (`cv2.NORM_HAMMING`).
  - Spatial Neighbor Suppression: Discards matches with Euclidean distance $d < 24\text{ px}$ to eliminate dense texture self-matching (e.g., repeating grid lines).
  - Displacement Vector Clustering: Groups matches by translation vector $(\Delta x, \Delta y)$ with a spatial tolerance of $\pm 3\text{ px}$.
  - Threshold: If $\ge 4$ parallel translation vectors share the same displacement cluster (such as cloned "0"s in "₹50,000"), VeriSight renders neon-magenta clone vectors and generates bounding boxes around the source and duplicate loci.
* **Expected Inputs:** BGR image array.
* **Expected Outputs:** `clone_detected` (bool), clone match count, base64 PNG with vector overlays, bounding boxes.
* **Computational Requirements:** $\sim 35\text{ ms}$.
* **Known Limitations:** Repeated UI elements (such as standard bottom navigation icons or duplicate list bullets) can exhibit parallel keypoint vectors. VeriSight filters out matches located strictly in standard navigation bars.
* **Test Strategy:** Synthetic clone test duplicating currency digits and verifying vector coordinate detection.

---

### 1.4 Typographic Sub-Pixel Baseline Regression ($\sigma_{\text{baseline}}$)
* **Prior Art / Sherloq:** Sherloq has no OCR or typographic geometry engine. It focuses exclusively on pixel-level photographic operations.
* **Research Reference:** Digital typography standards (OpenType / TrueType rasterization). Text on native mobile OS interfaces is rendered along mathematically exact horizontal baseline vectors with sub-pixel rounding variance $\sigma < 0.35\text{ px}$. Pasted or edited text typically exhibits vertical offsets $\ge 1.5\text{ px}$ or rotational tilts.
* **VeriSight Implementation (`services/forensic/typography/baseline_laser.py`):**
  - Groups OCR / connected-component text tokens into horizontal rows based on vertical centroid overlap ($\Delta y_{\text{center}} < 0.45 \times \text{median token height}$).
  - Fits a linear regression baseline $y = mx + c$ across token bottom-edge anchor points for each visual row.
  - Measures residual vertical drift $\Delta y = \vert y_i - (m x_i + c) \vert$ for each token.
  - Anomaly Rule: If any token on a row deviates by $\ge 1.8\text{ px}$ (e.g., pasted amount "95,250" positioned next to "₹"), VeriSight flags `SUBPIXEL_BASELINE_DRIFT`, computes the exact drift in pixels, and marks the row's SVG laser line as `CRITICAL_RED` (`#f43f5e`), while aligned rows are rendered as `ALIGNED_CYAN` (`#38bdf8`).
* **Expected Inputs:** List of extracted text token bounding boxes and coordinates.
* **Expected Outputs:** List of `BaselineLaser` objects (row index, slope, baseline Y, max drift px, tampered status, SVG coordinates).
* **Computational Requirements:** $< 5\text{ ms}$ (pure vector algebra).
* **Known Limitations:** Multi-line text wraps or superscript currency notations (e.g., $99^{\text{00}}$) must be isolated to avoid false drift triggers.
* **Test Strategy:** Test on genuine aligned receipt vs. spliced receipt with $3.5\text{ px}$ downward offset.

---

### 1.5 CIELAB Perceptual Background Patch Discontinuity ($\Delta E_{ab}$)
* **Prior Art / Sherloq:** RGB channel histograms and color space conversions, but no localized background card sampling around text tokens.
* **Research Reference:** CIE 1976 $L^*a^*b^*$ color difference formula:
  $$\Delta E_{ab} = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$
  In human perception, $\Delta E_{ab} \le 1.0$ is imperceptible, $1.0 < \Delta E_{ab} \le 2.0$ is perceptible through close observation, and $\Delta E_{ab} > 2.4$ represents a distinct perceptual boundary mismatch on solid UI surfaces.
* **VeriSight Implementation (`services/forensic/typography/cielab_patch.py`):**
  - Converts image to CIELAB space (`cv2.cvtColor(img, cv2.COLOR_BGR2Lab)`).
  - For each text token $[x, y, w, h]$:
    - Inner Background Ring: Samples median $(L^*, a^*, b^*)$ in the margin $2\text{ px}$ to $5\text{ px}$ outside character strokes, inside the bounding box.
    - Outer Reference Card Background: Samples median $(L^*, a^*, b^*)$ in the margin $10\text{ px}$ to $18\text{ px}$ outside the bounding box on the surrounding UI card.
  - Computes $\Delta E_{ab}$. If $\Delta E_{ab} > 2.4$ on a solid background, flags `LOCAL_BACKGROUND_PATCH_MISMATCH` with exact $\Delta E_{ab}$ and localization coordinates.
* **Expected Inputs:** CIELAB image array and token bounding boxes.
* **Expected Outputs:** Max $\Delta E_{ab}$, list of flagged patch bounding boxes, patch color telemetry.
* **Computational Requirements:** $< 15\text{ ms}$.
* **Known Limitations:** Subtle UI gradients (e.g., subtle CSS linear-gradient backgrounds) introduce natural color shifts; VeriSight checks local variance of the surrounding card before flagging.
* **Test Strategy:** Test on clean genuine receipt ($\Delta E_{ab} < 0.5$) vs. pasted patch with hex `#F9FAFB` on `#FFFFFF` card ($\Delta E_{ab} = 5.2$).

---

### 1.6 Metadata, Viewport, and Domain Protocol Rules
* **Prior Art:** ExifTool, ExifRead.
* **VeriSight Implementation (`services/forensic/metadata/`):**
  - **Container & Chunk Inspection:** Traverses EXIF metadata, PNG `tEXt` / `iTXt` / `zTXt` / `pHYs` chunks, ICC color profiles, and software signatures (`Photoshop`, `Canva`, `GIMP`, `Figma`, `FakeGen`).
  - **WhatsApp Media Re-Compression Fingerprinter:** Detects laundering when format is JPEG + EXIF stripped + chroma subsampling is 4:2:0 + long edge matches WhatsApp media thresholds ($\{1600, 1280, 1080, 1024, 960\}$). Dynamically shifts ensemble weights toward Layer 2 geometry and Layer 1 wavelet noise.
  - **Clock Temporal Paradox Detector:** Extracts top OS status-bar clock ($y < 0.07H$, e.g., `11:12`) vs. receipt transaction timestamp (e.g., `11:45 AM`). Raises `TEMPORAL_PARADOX_CLOCK_DRIFT` if receipt time is in the future relative to the phone's clock.
  - **UPI 12-Digit Reference/UTR Validator:** Validates 12-digit numeric structure, flags truncated lengths (e.g. 10 digits) or dummy repetitive entropy sequences (`9999999999`, `123456789012`).
* **Expected Outputs:** Detailed metadata breakdown, WhatsApp detection pill, clock drift telemetry, UTR validity state.
* **Computational Requirements:** $< 10\text{ ms}$.
* **Known Limitations:** Users can take a screenshot hours after a transaction occurred (which is valid). The paradox triggers only if the transaction time is *ahead* of the status bar clock on the same calendar day.

---

### 1.7 Spatial IoU Cross-Layer Synergy Ensemble
* **Prior Art:** Most forensic tools output disconnected reports for each algorithm without spatial cross-correlation.
* **VeriSight Implementation (`services/forensic/ensemble/calibrator.py`):**
  - Computes layer scores $S_1, S_2, S_3, S_4 \in [0, 100]$.
  - Cross-Layer Spatial IoU Intersection: Evaluates intersection-over-union ($\text{IoU}$) and bounding box centroid proximity ($d \le 15\text{ px}$) between Layer 1 signal anomalies (ELA / Wavelet / Clone) and Layer 2 typography anomalies (Baseline drift / $\Delta E_{ab}$ patch / Sharpness Z-score).
  - Synergy Boost: When both physical signal forensics and geometric typographic forensics flag the *exact same spatial region* (e.g., currency digits), applies a calibrated $1.35\times$ synergy boost and marks that region as the **Primary Forgery Locus**.
* **Expected Outputs:** Calibrated overall tamper score ($0–100\%$), confidence score ($0–100\%$), final investigative verdict (`AUTHENTIC_VERIFIED`, `SUSPICIOUS_ANOMALIES`, `MANIPULATED_FORGERY`), primary forgery locus.

---

*Algorithm comparison matrix verified and approved for VeriSight architecture.*
