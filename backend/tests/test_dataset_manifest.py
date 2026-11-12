import copy
import hashlib

import pytest
from PIL import Image

from app.evaluation.dataset_manifest import (
    POLICY_VERSION, lock_record, validate_manifest, validate_threshold_policy, verify_lock,
)
from app.evaluation.data_audit import GROUP_FIELDS


@pytest.fixture
def manifest(tmp_path):
    use = 'VeriSight commercial and research development'
    data = {'policy_version': POLICY_VERSION, 'intended_use': use, 'permissions': {
        'owned': {'source': 'consented collection', 'license_revision': 'signed release v1',
                  'access_restrictions': 'private authorized evaluators only',
                  'evidence_ref': 'consent/owned.pdf', 'reviewer': 'rights reviewer',
                  'payment_relevance': 'mobile payment app screenshots', 'intended_use': use,
                  'intended_use_approved': True, 'available_size': 6,
                  'labels': ['authentic', 'tampered']}}, 'samples': []}
    for index, (split, label) in enumerate((s, l) for s in ('train', 'validation', 'test') for l in ('authentic', 'tampered')):
        image = tmp_path / f'{index}.png'
        mask = tmp_path / f'{index}-mask.png'
        Image.new('RGB', (16, 16), (index, 0, 0)).save(image)
        Image.new('L', (16, 16), 255 if label == 'tampered' else 0).save(mask)
        data['samples'].append({
            'sample_id': str(index), 'dataset_id': 'owned', 'split': split, 'label': label,
            'demo_fixture': False, 'near_duplicate_reviewed': True, 'synthetic': False,
            **{field: f'{field}-{split}' for field in GROUP_FIELDS},
            'image_path': image.name, 'mask_path': mask.name,
            'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
            'mask_sha256': hashlib.sha256(mask.read_bytes()).hexdigest(),
            'condition': 'original', 'edit_type': 'amount' if label == 'tampered' else 'none'})
    return data


def test_preflight_is_byte_checked_and_lock_is_order_independent(manifest, tmp_path):
    assert validate_manifest(manifest, tmp_path) == []
    lock = lock_record(manifest)
    manifest['samples'].reverse()
    assert verify_lock(manifest, lock) == []
    (tmp_path / '4.png').write_bytes(b'corrupt')
    assert any('hash mismatch' in e for e in validate_manifest(manifest, tmp_path))


@pytest.mark.parametrize('group', GROUP_FIELDS)
def test_all_group_axes_cannot_leak(manifest, tmp_path, group):
    manifest['samples'][2][group] = manifest['samples'][0][group]
    assert any(f'{group} crosses' in e for e in validate_manifest(manifest, tmp_path))


def test_permissions_and_test_metadata_cannot_change_after_lock(manifest):
    lock = lock_record(manifest)
    modified = copy.deepcopy(manifest)
    modified['samples'][-1]['edit_type'] = 'recipient'
    assert verify_lock(modified, lock)
    manifest['permissions']['owned']['license_revision'] = 'changed'
    assert verify_lock(manifest, lock)


@pytest.mark.parametrize('approval', [False, 'true', 1, None])
def test_permission_requires_explicit_boolean(manifest, tmp_path, approval):
    manifest['permissions']['owned']['intended_use_approved'] = approval
    assert any('permission not documented' in e for e in validate_manifest(manifest, tmp_path))


def test_empty_and_invalid_container_cannot_pass(tmp_path):
    assert validate_manifest({'samples': [], 'permissions': {}}, tmp_path)
    assert validate_manifest({'samples': [[]], 'permissions': {}}, tmp_path)


def test_masks_must_match_labels_and_hashes(manifest, tmp_path):
    mask = tmp_path / '1-mask.png'
    Image.new('L', (16, 16), 0).save(mask)
    manifest['samples'][1]['mask_sha256'] = hashlib.sha256(mask.read_bytes()).hexdigest()
    assert any('nonempty edit mask' in e for e in validate_manifest(manifest, tmp_path))


def test_paths_cannot_escape_private_root(manifest, tmp_path):
    manifest['samples'][0]['image_path'] = '../outside.png'
    assert any('outside the private data root' in e for e in validate_manifest(manifest, tmp_path))


def test_threshold_selection_must_precede_test_use():
    record = {'selection_split': 'validation', 'target_false_positive_rate': 0.01,
              'threshold': 42, 'validation_manifest_digest': 'a' * 64,
              'model_digest': 'b' * 64, 'selection_evidence_ref': 'selection.json',
              'test_seen_during_selection': False}
    assert validate_threshold_policy(record) == []
    record['selection_split'] = 'test'
    assert validate_threshold_policy(record)
    record['selection_split'] = 'validation'
    record['threshold'] = float('nan')
    assert validate_threshold_policy(record)


def test_malformed_edit_and_condition_return_errors(manifest, tmp_path):
    manifest['samples'][1]['edit_type'] = []
    manifest['samples'][1]['condition'] = {}
    errors = validate_manifest(manifest, tmp_path)
    assert any('invalid edit_type' in error for error in errors)
    assert any('transformation condition' in error for error in errors)
