from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    points: list[list[int]] | None = None
    label: str
    confidence: float = 1.0
    layer: int
    anomaly_type: str
    details: dict[str, Any] | None = None

class BaselineLaser(BaseModel):
    row_index: int
    y_baseline: float
    slope: float = 0.0
    tokens_count: int
    delta_y_max: float
    is_tampered: bool
    status: str  # "ALIGNED_CYAN" or "CRITICAL_RED"
    callout_text: str | None = None
    token_indices: list[int] = Field(default_factory=list)
    x_start: int | None = None
    x_end: int | None = None

class Layer1SignalResult(BaseModel):
    ela_score: float
    ela_b64: str
    wavelet_noise_score: float
    wavelet_noise_b64: str
    clone_detected: bool
    clone_count: int
    clone_b64: str
    anomalous_blocks_count: int
    layer_score: float
    bounding_boxes: list[BoundingBox] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

class Layer2GeometryResult(BaseModel):
    baseline_drift_score: float
    max_baseline_drift_px: float
    max_delta_e: float
    cielab_patch_anomaly: bool
    sharpness_z_anomaly: bool
    layer_score: float
    lasers: list[BaselineLaser] = Field(default_factory=list)
    bounding_boxes: list[BoundingBox] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

class Layer3MetadataResult(BaseModel):
    channel_detected: str
    is_whatsapp_laundered: bool
    exif_stripped: bool
    software_signature: str | None = None
    c2pa_present: bool = False
    c2pa_status: str = "NO_MANIFEST_FOUND"
    viewport_aspect_ratio: str
    is_non_native_viewport: bool
    clock_paradox_detected: bool
    status_bar_clock: str | None = None
    transaction_time: str | None = None
    upi_utr_valid: bool | None = None
    upi_utr_value: str | None = None
    layer_score: float
    bounding_boxes: list[BoundingBox] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

class Layer4SemanticResult(BaseModel):
    vlm_used: bool = False
    vlm_provider: str | None = None
    semantic_inconsistency: bool = False
    layer_score: float = 0.0
    findings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)

class CrossLayerSynergy(BaseModel):
    synergy_multiplier_applied: bool = False
    multiplier_factor: float = 1.0
    max_iou: float = 0.0
    primary_forgery_locus: BoundingBox | None = None
    synergy_explanation: str = "No cross-layer anomaly alignment detected."

class ForensicFinding(BaseModel):
    id: str
    layer: int
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    title: str
    description: str
    metric_name: str
    metric_value: str
    bounding_box: BoundingBox | None = None

class AssessmentDimensions(BaseModel):
    image_integrity_score: float = Field(default=1.0, description="Physical pixel & frequency integrity (0.0 to 1.0)")
    image_integrity_status: str = Field(default="INTACT", description="INTACT, COMPRESSION_NOISE, or TAMPER_DETECTED")
    text_consistency_score: float = Field(default=1.0, description="Sub-pixel baseline & OCR geometry consistency (0.0 to 1.0)")
    text_consistency_status: str = Field(default="CONSISTENT", description="CONSISTENT, SUBPIXEL_DRIFT, or GEOMETRIC_ANOMALY")
    payment_verification_status: str = Field(default="INDEPENDENT_SOURCE_QUERY_REQUIRED", description="Financial gateway verification state")
    payment_verification_details: str = Field(default="A digital screenshot cannot independently prove financial transfer. Independent bank/NPCI verification required.")
    forensic_uncertainty_status: str = Field(default="HIGH_CONFIDENCE", description="HIGH_CONFIDENCE, MODERATE_UNCERTAINTY, or INCONCLUSIVE")
    forensic_uncertainty_score: float | None = Field(default=None, description="Uncertainty index (0.0 low to 1.0 high)")
    uncertainty_explanation: str = Field(default="Resolution and noise characteristics sufficient for algorithmic evaluation.")

class ModelInferenceMetadata(BaseModel):
    model_id: str = "verisight-fusion-gbdt-v1"
    model_version: str = "1.2.1"
    architecture: str = "HistGradientBoosting Classifier with 3-fold CalibratedClassifierCV"
    calibration_status: str = "CALIBRATED_SIGMOID_CV3"
    promotion_status: str = "EXPERIMENTAL"
    feature_schema_version: str = "1.0.0"
    inference_status: str = "EXECUTED"
    calibrated_probability: float | None = None
    raw_model_score: float | None = None
    missing_evidence: list[str] = Field(default_factory=list)
    is_operational_triage_alert: bool = False
    is_synthetic_benchmark: bool = False
    disclaimer: str = "EXPERIMENTAL MODEL: Evaluated on synthetic benchmark. Not validated for independent real-world legal certainty."

class ForensicAnalysisReport(BaseModel):
    media_urls: dict[str, str] = Field(default_factory=dict)
    intelligence: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "2.0"
    case_id: str = ""
    sample_id: str | None = None
    source_kind: str = "USER_UPLOAD_UNVERIFIED"
    processing_status: str = "COMPLETE"
    ai_origin_status: str = "UNAVAILABLE"
    ai_origin: dict[str, Any] = Field(default_factory=dict)
    payment_status: str = "NOT_VERIFIED"
    limitations: list[str] = Field(default_factory=lambda: ["Screenshot analysis does not verify payment settlement.", "Confidence unavailable; heuristic cues are not proof of editing.", "No AI-origin classifier or OCR text recognition is active."])
    file_sha256: str
    filename: str | None = "screenshot.png"
    timestamp: str
    image_width: int
    image_height: int
    overall_tamper_score: float
    confidence_score: float | None = None
    verdict: str  # "AUTHENTIC_VERIFIED", "SUSPICIOUS_ANOMALIES", "MANIPULATED_FORGERY", "CORROBORATED_ANOMALIES", "REVIEW_REQUIRED", "INCONCLUSIVE"
    channel_detected: str
    layer1: Layer1SignalResult
    layer2: Layer2GeometryResult
    layer3: Layer3MetadataResult
    layer4: Layer4SemanticResult
    synergy: CrossLayerSynergy
    findings: list[ForensicFinding] = Field(default_factory=list)
    all_bounding_boxes: list[BoundingBox] = Field(default_factory=list)
    original_image_b64: str
    syndicate_intelligence: dict[str, Any] | None = None
    section91_notice: str | None = None
    assessment_dimensions: AssessmentDimensions = Field(default_factory=AssessmentDimensions)
    model_metadata: ModelInferenceMetadata = Field(default_factory=ModelInferenceMetadata)

class ModelStatusResponse(BaseModel):
    active_model_id: str
    active_model_version: str
    architecture: str
    calibration_status: str
    promotion_status: str
    available_models: list[dict[str, Any]]
    ml_environment_ready: bool

class BenchmarkRunResponse(BaseModel):
    status: str
    benchmark_dataset: str
    sample_count: int
    models_evaluated: list[str]
    report: dict[str, Any]

class DemoSampleMeta(BaseModel):
    id: str
    filename: str
    title: str
    scenario: str
    expected_verdict: str
    target_score_range: str
    description: str
    tags: list[str]
    url: str

class WhatsAppSimulationResponse(BaseModel):
    original_size_bytes: int
    simulated_size_bytes: int
    compression_ratio: float
    original_dimensions: list[int]
    simulated_dimensions: list[int]
    simulated_image_b64: str
    diff_heatmap_b64: str
    reanalysis: ForensicAnalysisReport
