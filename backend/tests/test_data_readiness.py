from copy import deepcopy
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.evaluation.data_audit import audit_manifest, GROUP_FIELDS, test_manifest_digest as digest
from app.services.forensic.adapters.advanced_model_adapter import AdvancedModelAdapter


def manifest():
    return [dict(sample_id=f'{s}-{label}', split=s, label=label, dataset_id='owned',
                 sha256=f'{i*2+j:064x}', mask_path=f'{s}-{label}.png', demo_fixture=False,
                 near_duplicate_reviewed=True, **{key:f'{s}-{key}' for key in GROUP_FIELDS})
            for i,s in enumerate(('train','validation','test'))
            for j,label in enumerate(('authentic','tampered'))]

PERMISSIONS={'owned':dict(intended_use_approved=True,evidence_ref='consent-record',
                          license_revision='v1',reviewer='rights-reviewer')}


def test_complete_manifest_passes_structural_audit():
    assert audit_manifest(manifest(), PERMISSIONS) == []

@pytest.mark.parametrize('field', [*GROUP_FIELDS, 'sha256'])
def test_each_shared_identity_prevents_split_leakage(field):
    rows=manifest(); rows[2][field]=rows[0][field]
    assert any(field+' crosses' in e for e in audit_manifest(rows, PERMISSIONS))

@pytest.mark.parametrize('change',[{'demo_fixture':True},{'near_duplicate_reviewed':False},
                                    {'device_id':'unknown'},{'mask_path':None}])
def test_incomplete_or_demo_provenance_rejected(change):
    rows=manifest();rows[0].update(change)
    assert audit_manifest(rows, PERMISSIONS)


def test_empty_and_unauthorized_data_rejected():
    assert audit_manifest([], PERMISSIONS)
    assert audit_manifest(manifest(), {})
    permissions=deepcopy(PERMISSIONS);permissions['owned']['intended_use_approved']=False
    assert audit_manifest(manifest(),permissions)


def test_locked_test_manifest_detects_changes_only_to_test():
    rows=manifest(); locked=digest(rows)
    assert digest(list(reversed(rows))) == locked
    rows[0]['mask_path']='train-change.png'
    assert digest(rows)==locked
    rows[-1]['mask_path']='test-change.png'
    assert digest(rows)!=locked


def test_no_weights_never_claims_loading_or_inference():
    adapter=AdvancedModelAdapter()
    assert adapter.is_enabled is False
    result=adapter.run_inference(np.zeros((32,32,3),dtype=np.uint8))
    assert result['inference_run'] is False


def test_endpoints_expose_blocked_release_and_no_confidence():
    client=TestClient(app)
    status=client.get('/api/model/status').json()
    evaluation=client.get('/api/model/evaluation').json()
    for result in (status,evaluation):
        assert result['release_readiness']['deployment_permitted'] is False
        assert result['release_readiness']['training_permitted'] is False
        assert result['release_readiness']['threshold'] is None
    assert status['active_model_id'] == 'heuristic-review-v2'
    assert status['evidence_sources']['payment_status']['settlement_verified'] is None
    assert status['evidence_sources']['visual_tampering']['calibrated_confidence'] is None
    assert evaluation['metrics'] is None
    assert evaluation['test_set_locked'] is False
