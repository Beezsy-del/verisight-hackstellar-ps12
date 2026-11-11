"""Manifest-only preflight. Does not load images, download data, or train models."""
import hashlib
import json
import re

GROUP_FIELDS = (
    'source_app', 'template_id', 'device_id', 'contributor_id',
    'original_screenshot_id', 'editing_session_id', 'near_duplicate_group',
)
SPLITS = {'train', 'validation', 'test'}


def audit_manifest(rows, permissions):
    """Reject incomplete provenance and cross-split group/hash leakage.

    Permissions are evidence references supplied by a rights reviewer, not legal
    conclusions inferred from a license string. Near-duplicate groups must have
    been assigned by a separate image-similarity review before this audit.
    """
    errors = []
    owners = {}
    ids = set()
    observed = set()
    classes = {split: set() for split in SPLITS}
    if not rows:
        return ['Manifest is empty; training is blocked.']
    for index, row in enumerate(rows):
        prefix = f'row {index}'
        split = row.get('split')
        sample_id = row.get('sample_id')
        if not sample_id or sample_id in ids:
            errors.append(f'{prefix}: missing or duplicate sample_id')
        ids.add(sample_id)
        if split not in SPLITS:
            errors.append(f'{prefix}: invalid split')
            continue
        observed.add(split)
        label = row.get('label')
        if label not in {'authentic', 'tampered'}:
            errors.append(f'{prefix}: invalid label')
        else:
            classes[split].add(label)
        permit = permissions.get(row.get('dataset_id'), {})
        if not (permit.get('intended_use_approved') is True and permit.get('evidence_ref')
                and permit.get('license_revision') and permit.get('reviewer')):
            errors.append(f'{prefix}: intended-use permission not documented')
        if row.get('demo_fixture') is not False:
            errors.append(f'{prefix}: demo fixtures or unknown provenance are excluded')
        if row.get('near_duplicate_reviewed') is not True:
            errors.append(f'{prefix}: near-duplicate review missing')
        for field in (*GROUP_FIELDS, 'sha256'):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip() or value.lower() in {'unknown', 'n/a', 'none'}:
                errors.append(f'{prefix}: missing {field}')
                continue
            if field == 'sha256' and not re.fullmatch('[a-f0-9]{64}', value):
                errors.append(f'{prefix}: invalid sha256')
            key = (field, value)
            if key in owners and owners[key] != split:
                errors.append(f'{prefix}: {field} crosses {owners[key]} and {split}')
            owners[key] = split
        if not row.get('mask_path'):
            errors.append(f'{prefix}: mask required (zero mask for authentic)')
    if observed != SPLITS:
        errors.append('All three splits are required.')
    for split, labels in classes.items():
        if labels != {'authentic', 'tampered'}:
            errors.append(f'{split}: both authentic and tampered samples required')
    return errors


def test_manifest_digest(rows):
    """Order-independent lock of test records; does not lock image bytes itself."""
    test = sorted((row for row in rows if row.get('split') == 'test'), key=lambda r: r['sample_id'])
    return hashlib.sha256(json.dumps(test, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
