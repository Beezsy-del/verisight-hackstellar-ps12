"""Permission/provenance and byte-level preflight; never authorizes model release.

Run with PYTHONPATH=backend python -m app.evaluation.dataset_manifest MANIFEST
--root PRIVATE_DATA_ROOT [--lock LOCK | --write-lock NEW_LOCK].
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image
from app.evaluation.data_audit import audit_manifest, test_manifest_digest

POLICY_VERSION = 'representative-evaluation-v1'
EDIT_TYPES = {'amount', 'recipient', 'timestamp', 'reference', 'qr_payload',
              'insertion', 'removal', 'replacement', 'splicing', 'copy_move'}
CONDITIONS = {'original', 'resize', 'jpeg_recompression', 'crop',
              'messaging_forward', 'screen_capture'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _asset(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('asset must have a relative path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('asset is missing or outside the private data root')
    return path


def validate_manifest(manifest, root):
    """Return actionable errors. A clean result only means preflight passed."""
    if not isinstance(manifest, dict):
        return ['Manifest must be an object.']
    rows = manifest.get('samples')
    permissions = manifest.get('permissions')
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        return ['samples must be a list of objects.']
    if not isinstance(permissions, dict) or not all(isinstance(p, dict) for p in permissions.values()):
        return ['permissions must map dataset identifiers to objects.']
    scalar_fields = ('sample_id', 'split', 'dataset_id', 'label')
    if any(not isinstance(row.get(field), str) for row in rows for field in scalar_fields):
        return ['Every sample needs string sample_id, split, dataset_id and label.']
    errors = audit_manifest(rows, permissions)
    if manifest.get('policy_version') != POLICY_VERSION:
        errors.append('Unsupported evaluation policy version.')
    if manifest.get('intended_use') != 'VeriSight commercial and research development':
        errors.append('Explicit project intended use must be recorded.')
    for dataset, permit in permissions.items():
        for field in ('source', 'license_revision', 'access_restrictions', 'evidence_ref',
                      'reviewer', 'payment_relevance', 'intended_use'):
            if not isinstance(permit.get(field), str) or not permit[field].strip():
                errors.append(f'{dataset}: permission record missing {field}')
        if permit.get('intended_use') != manifest.get('intended_use'):
            errors.append(f'{dataset}: permission does not cover declared intended use')
        if type(permit.get('available_size')) is not int or permit['available_size'] < 1:
            errors.append(f'{dataset}: document available dataset size')
        if permit.get('labels') != ['authentic', 'tampered']:
            errors.append(f'{dataset}: document authentic/tampered label availability')
    root = Path(root).resolve()
    for row in rows:
        sid = row['sample_id']
        if type(row.get('synthetic')) is not bool:
            errors.append(f'{sid}: synthetic provenance must be explicit')
        expected_edit = row.get('edit_type')
        if (row['label'] == 'authentic' and expected_edit != 'none') or (row['label'] == 'tampered' and (not isinstance(expected_edit, str) or expected_edit not in EDIT_TYPES)):
            errors.append(f'{sid}: invalid edit_type for label')
        if not isinstance(row.get('condition'), str) or row['condition'] not in CONDITIONS:
            errors.append(f'{sid}: missing supported transformation condition')
        try:
            image_path = _asset(root, row.get('image_path'))
            mask_path = _asset(root, row.get('mask_path'))
            if hashlib.sha256(image_path.read_bytes()).hexdigest() != row.get('sha256'):
                errors.append(f'{sid}: image hash mismatch')
            if hashlib.sha256(mask_path.read_bytes()).hexdigest() != row.get('mask_sha256'):
                errors.append(f'{sid}: mask hash mismatch')
            with Image.open(image_path) as image, Image.open(mask_path) as mask:
                if image.width * image.height > 12_000_000:
                    raise ValueError('image exceeds preflight pixel limit')
                if mask.size != image.size or mask.mode not in {'1', 'L'}:
                    raise ValueError('mask must be grayscale and match image dimensions')
                image.verify()
                values = {value for value, count in enumerate(mask.convert('L').histogram()) if count}
                if not values.issubset({0, 255}):
                    raise ValueError('mask must be binary (0 or 255)')
                if row['label'] == 'authentic' and values != {0}:
                    raise ValueError('authentic sample requires an all-zero mask')
                if row['label'] == 'tampered' and 255 not in values:
                    raise ValueError('tampered sample requires a nonempty edit mask')
        except (ValueError, OSError, Image.DecompressionBombError) as exc:
            errors.append(f'{sid}: {exc}')
    return errors


def lock_record(manifest):
    """Lock test membership and expected bytes/provenance; verify bytes separately."""
    return {'policy_version': POLICY_VERSION,
            'test_digest': test_manifest_digest(manifest['samples']),
            'permissions_digest': digest(manifest['permissions']),
            'intended_use': manifest['intended_use']}


def verify_lock(manifest, lock):
    return [] if lock == lock_record(manifest) else ['Locked test set or permission record changed.']


def validate_threshold_policy(record):
    """Validate selection provenance; achieved FPR needs independent review."""
    if not isinstance(record, dict):
        return ['Threshold record must be an object.']
    errors = []
    if record.get('selection_split') != 'validation':
        errors.append('Threshold selection must use validation only.')
    if record.get('target_false_positive_rate') != 0.01:
        errors.append('Predeclared false-positive target is 0.01.')
    threshold = record.get('threshold')
    if type(threshold) not in (int, float) or not math.isfinite(threshold) or not 0 <= threshold <= 100:
        errors.append('A finite threshold on the 0–100 review-score scale is required.')
    for key in ('validation_manifest_digest', 'model_digest', 'selection_evidence_ref'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            errors.append(f'Missing {key}.')
    if record.get('test_seen_during_selection') is not False:
        errors.append('Test-set independence must be explicitly attested.')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--lock', type=Path)
    group.add_argument('--write-lock', type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text())
        errors = validate_manifest(manifest, args.root)
        if not errors and args.lock:
            errors += verify_lock(manifest, json.loads(args.lock.read_text()))
        if not errors and args.write_lock:
            with args.write_lock.open('x') as file:
                json.dump(lock_record(manifest), file, indent=2)
        print(json.dumps({'preflight_passed': not errors, 'errors': errors,
                          'model_release_authorized': False,
                          'real_world_accuracy_established': False}, indent=2))
        return 1 if errors else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'preflight_passed': False, 'errors': [str(exc)]}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
