from app.core.schemas import (
    BaselineLaser,
    BoundingBox,
    Layer1SignalResult,
    Layer2GeometryResult,
    Layer3MetadataResult,
    Layer4SemanticResult,
)
from app.services.forensic.ensemble.calibrator import calibrate_ensemble


def test_clean_ensemble_calibration():
    l1 = Layer1SignalResult(
        ela_score=5.0,
        ela_b64="",
        wavelet_noise_score=6.0,
        wavelet_noise_b64="",
        clone_detected=False,
        clone_count=0,
        clone_b64="",
        anomalous_blocks_count=0,
        layer_score=6.0,
        bounding_boxes=[]
    )
    l2 = Layer2GeometryResult(
        baseline_drift_score=2.0,
        max_baseline_drift_px=0.2,
        max_delta_e=0.8,
        cielab_patch_anomaly=False,
        sharpness_z_anomaly=False,
        layer_score=4.0,
        lasers=[],
        bounding_boxes=[]
    )
    l3 = Layer3MetadataResult(
        channel_detected="Lossless PNG (Native Capture)",
        is_whatsapp_laundered=False,
        exif_stripped=False,
        software_signature=None,
        c2pa_present=False,
        c2pa_status="NO_MANIFEST_FOUND",
        viewport_aspect_ratio="9:19.5 (Modern Mobile)",
        is_non_native_viewport=False,
        clock_paradox_detected=False,
        status_bar_clock="14:32",
        transaction_time="14:30",
        upi_utr_valid=True,
        upi_utr_value="631618492041",
        layer_score=0.0,
        bounding_boxes=[]
    )
    l4 = Layer4SemanticResult(vlm_used=False, layer_score=0.0)

    final_score, confidence, verdict, synergy, findings, all_boxes = calibrate_ensemble(l1, l2, l3, l4)

    assert final_score < 25.0
    assert verdict == "INCONCLUSIVE"
    assert confidence is None
    assert not synergy.synergy_multiplier_applied


def test_cross_layer_spatial_iou_synergy():
    # Construct overlapping bounding boxes in Layer 1 (signal) and Layer 2 (typography)
    box1 = BoundingBox(
        x=200, y=400, width=150, height=50,
        label="ELA Inconsistency Patch",
        layer=1,
        anomaly_type="ELA_LOCAL_VARIANCE_OUTLIER"
    )
    box2 = BoundingBox(
        x=210, y=405, width=140, height=45,
        label="Spliced Amount (Laser Drift)",
        layer=2,
        anomaly_type="CRITICAL_BASELINE_DRIFT"
    )

    l1 = Layer1SignalResult(
        ela_score=85.0,
        ela_b64="",
        wavelet_noise_score=78.0,
        wavelet_noise_b64="",
        clone_detected=False,
        clone_count=0,
        clone_b64="",
        anomalous_blocks_count=5,
        layer_score=82.0,
        bounding_boxes=[box1]
    )
    l2 = Layer2GeometryResult(
        baseline_drift_score=90.0,
        max_baseline_drift_px=3.4,
        max_delta_e=4.5,
        cielab_patch_anomaly=True,
        sharpness_z_anomaly=True,
        layer_score=88.0,
        lasers=[BaselineLaser(
            row_index=1,
            y_baseline=440.0,
            tokens_count=3,
            delta_y_max=3.4,
            is_tampered=True,
            status="CRITICAL_RED"
        )],
        bounding_boxes=[box2]
    )
    l3 = Layer3MetadataResult(
        channel_detected="Unknown JPEG Carrier",
        is_whatsapp_laundered=False,
        exif_stripped=True,
        software_signature="Adobe Photoshop",
        c2pa_present=False,
        c2pa_status="NO_MANIFEST_FOUND",
        viewport_aspect_ratio="9:19.5 (Modern Mobile)",
        is_non_native_viewport=False,
        clock_paradox_detected=False,
        layer_score=35.0,
        bounding_boxes=[]
    )
    l4 = Layer4SemanticResult(vlm_used=False, layer_score=0.0)

    final_score, confidence, verdict, synergy, findings, all_boxes = calibrate_ensemble(l1, l2, l3, l4)

    # IoU synergy multiplier should trigger!
    assert synergy.synergy_multiplier_applied is False
    assert synergy.multiplier_factor == 1.0
    assert synergy.primary_forgery_locus is None
    assert final_score < 70.0
    assert verdict == "REVIEW_REQUIRED"
    assert confidence is None
    assert len(findings) > 0
