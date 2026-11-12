"""Current release facts. These are blockers, never fabricated evaluation scores."""


def release_readiness():
    from app.evaluation.gates import evaluate_model_release
    # No independently verified release record is installed. Client-supplied
    # assertions are deliberately never accepted as promotion evidence.
    decision = evaluate_model_release({})
    return {
        'status': 'BLOCKED',
        'training_permitted': False,
        'deployment_permitted': False,
        'scope': 'New visual tampering-localization model',
        'reasons': [
            'No suitable screenshot corpus has documented intended-use authorization.',
            'No audited source-grouped split or locked independent test set exists.',
            'No trained localization artifact or measured evaluation is available.',
            'Deployment bundle, response size, memory and latency gates are unmeasured.',
        ],
        'validation_false_positive_target': 0.01,
        'threshold': None,
        'model_version': None,
        'gate': decision,
    }


def evidence_sources():
    return {
        'visual_tampering': {'method': 'pixel_and_geometry_heuristics', 'trained_model': None,
                             'calibrated_confidence': None},
        'ocr': {'method': 'RapidOCR text recognition and receipt statement rules',
                'authenticity_classifier': False},
        'metadata': {'method': 'untrusted container fields and marker checks'},
        'qr': {'method': 'payload decoding only', 'destination_verified': False},
        'payment_status': {'status': 'NOT_INTEGRATED', 'settlement_verified': None,
                           'requires': 'Authorized bank or PSP transaction-status integration'},
    }
