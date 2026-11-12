"""Deterministic report-use and model-promotion policies. Never approve payment."""
import math
from app.core.schemas import AnalysisGate, GateReason

POLICY_VERSION = 'analysis-review-v1'


def evaluate_analysis_gate(*, score, verdict, findings, ocr_status, image_width, image_height):
    reasons = []
    failed = False
    def reason(code, state, message, ids=None):
        reasons.append(GateReason(code=code, state=state, message=message, evidence_ids=ids or []))
    if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        failed = True
        reason('INVALID_SCORE', 'BLOCK', 'The analyzer returned an invalid review score.')
    if verdict not in {'INCONCLUSIVE', 'REVIEW_REQUIRED', 'CORROBORATED_ANOMALIES'}:
        failed = True
        reason('INVALID_VERDICT', 'BLOCK', 'The analyzer returned an unsupported evidence state.')
    ids = [f.id for f in findings]
    if len(set(ids)) != len(ids):
        failed = True
        reason('DUPLICATE_EVIDENCE', 'BLOCK', 'Evidence identifiers are not unique.')
    for f in findings:
        box = f.bounding_box
        if not f.id or not f.description or not f.metric_name or not f.metric_value:
            failed = True
            reason('INCOMPLETE_EVIDENCE', 'BLOCK', 'A finding is missing its supporting explanation or metric.', [f.id])
        if box and (box.x < 0 or box.y < 0 or box.width <= 0 or box.height <= 0 or box.x + box.width > image_width or box.y + box.height > image_height):
            failed = True
            reason('INVALID_EVIDENCE_REGION', 'BLOCK', 'A finding points outside the submitted image.', [f.id])
    if ocr_status != 'AVAILABLE':
        reason('OCR_INCOMPLETE', 'BLOCK', 'Reliable text coverage is unavailable; this is a processing limitation, not proof of fraud.')
    review_ids = [f.id for f in findings if f.id != 'f-text-coverage' and f.severity in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}]
    if verdict != 'INCONCLUSIVE' and review_ids:
        reason('REVIEW_EVIDENCE', 'WARNING', 'Inspect the reported evidence before relying on this screenshot.', review_ids)
    elif verdict != 'INCONCLUSIVE' and ocr_status == 'AVAILABLE':
        reason('UNSUPPORTED_REVIEW', 'BLOCK', 'A review decision has no supporting evidence.')
        failed = True
    if verdict == 'INCONCLUSIVE' and any(f.severity in {'HIGH', 'CRITICAL'} for f in findings):
        reason('CONFLICTING_EVIDENCE', 'BLOCK', 'The decision conflicts with high-severity evidence.', review_ids)
        failed = True
    state = 'BLOCK' if any(r.state == 'BLOCK' for r in reasons) else 'WARNING' if reasons else 'PASS'
    if not reasons:
        reason('PROCESSING_COMPLETE', 'PASS', 'Configured processing completed without a review decision. Authenticity and payment status remain unverified.')
    return AnalysisGate(state=state, processing_status='FAILED' if failed else 'INCOMPLETE' if state == 'BLOCK' else 'COMPLETE', reasons=reasons, allowed_actions={'view_report': not failed, 'automated_approval': False})


MODEL_RELEASE_CONDITIONS = ('permissions_verified', 'files_and_masks_verified', 'source_groups_verified', 'locked_test_verified', 'validation_threshold_fixed', 'calibration_verified', 'metrics_passed', 'artifact_verified', 'deployment_limits_verified', 'rollback_verified')


def evaluate_model_release(evidence):
    """Input must be produced by an independent release auditor, not a request payload.

    Missing, false and truthy strings never satisfy conditions. This is a software
    interlock, not a substitute for legally/empirically verifying its evidence.
    """
    failures = [key for key in MODEL_RELEASE_CONDITIONS if evidence.get(key) is not True]
    return {'state': 'BLOCK' if failures else 'PASS', 'policy_version': 'model-promotion-v1', 'failed_conditions': failures}


def require_model_release(evidence):
    result = evaluate_model_release(evidence)
    if result['state'] != 'PASS':
        raise RuntimeError('Model promotion blocked: ' + ', '.join(result['failed_conditions']))
    return result
