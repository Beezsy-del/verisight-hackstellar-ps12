import asyncio
import io
import json
from uuid import uuid4
from urllib.error import HTTPError
from unittest.mock import AsyncMock

import cv2
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.services.image_validation import decode_image, ImageTooLarge, InvalidImage
from app.services import mobile_upload_store as store

client = TestClient(app)

def image_bytes(fmt='PNG', size=(64, 64)):
    out = io.BytesIO()
    Image.new('RGB', size, '#8fa4bd').save(out, format=fmt)
    return out.getvalue()

@pytest.mark.parametrize('path', ['/api/analyze', '/api/simulate-whatsapp', '/api/mobile-upload'])
@pytest.mark.parametrize('payload', [b'', b'not an image', b'<svg></svg>'])
def test_invalid_uploads_are_client_errors(path, payload):
    response = client.post(path, files={'file': ('fake.png', payload, 'image/png')})
    assert response.status_code == 422
    assert 'Traceback' not in response.text

@pytest.mark.parametrize('fmt', ['PNG', 'JPEG', 'WEBP', 'BMP'])
def test_supported_images_decode(fmt):
    assert decode_image(image_bytes(fmt)).shape == (64, 64, 3)

def test_oversized_dimensions_rejected_before_cv_decode(monkeypatch):
    monkeypatch.setattr(cv2, 'imdecode', lambda *args: pytest.fail('allocated oversized raster'))
    with pytest.raises(ImageTooLarge):
        decode_image(image_bytes(size=(8193, 16)))

def test_unsupported_and_tiny_images_rejected():
    for data in (image_bytes('GIF'), image_bytes(size=(1, 1))):
        with pytest.raises(InvalidImage):
            decode_image(data)

def test_mobile_poll_cannot_read_or_clear_another_session():
    from app.api import endpoints
    a, b = str(uuid4()), str(uuid4())
    from time import monotonic
    endpoints._MOBILE_UPLOADS[a] = {'report': {'filename': 'a.png'}, 'received_at': monotonic()}
    endpoints._MOBILE_UPLOADS[b] = {'report': {'filename': 'b.png'}, 'received_at': monotonic()}
    assert client.get('/api/latest-mobile-upload?clear=true').json()['report'] is None
    assert client.get(f'/api/latest-mobile-upload?session_id={uuid4()}&clear=true').json()['report'] is None
    assert client.get(f'/api/latest-mobile-upload?session_id={a}').json()['report']['filename'] == 'a.png'
    assert client.get(f'/api/latest-mobile-upload?session_id={a}').json()['report'] is None
    assert client.get(f'/api/latest-mobile-upload?session_id={b}').json()['report']['filename'] == 'b.png'

def test_local_mobile_requires_session():
    r = client.post('/api/mobile-upload', files={'file': ('test.png', image_bytes(), 'image/png')})
    assert r.status_code == 400

def test_poll_before_signed_object_exists_is_empty(monkeypatch):
    monkeypatch.setattr(store, '_credentials', lambda: ('https://example.test', 'test'))
    def request(path, *args):
        if path.startswith('/rest'):
            return json.dumps([{'storage_path': 'session/evidence', 'filename': 'test.png'}]).encode()
        raise HTTPError('https://example.test', 404, 'missing', {}, io.BytesIO())
    monkeypatch.setattr(store, '_request', request)
    assert asyncio.run(store.consume_mobile_upload(uuid4())) is None

def test_losing_concurrent_consumer_does_not_analyze_or_delete(monkeypatch):
    monkeypatch.setattr(store, '_credentials', lambda: ('https://example.test', 'test'))
    def request(path, key, method='GET', *args):
        if method == 'PATCH':
            assert 'consumed_at=is.null' in path
            assert args[-1] == 'return=representation'
            return b'[]'
        if path.startswith('/rest'):
            return json.dumps([{'storage_path': 'session/evidence', 'filename': 'test.png'}]).encode()
        return image_bytes()
    monkeypatch.setattr(store, '_request', request)
    delete = AsyncMock()
    monkeypatch.setattr(store, 'delete_mobile_image', delete)
    assert asyncio.run(store.consume_mobile_upload(uuid4())) is None
    delete.assert_not_called()

def test_corrupt_claimed_image_is_deleted(monkeypatch):
    monkeypatch.setattr(store, '_credentials', lambda: ('https://example.test', 'test'))
    def request(path, key, method='GET', *args):
        if method == 'PATCH': return b'[{}]'
        if path.startswith('/rest'): return b'[{"storage_path":"s/evidence","filename":"bad.png"}]'
        return b'corrupt'
    monkeypatch.setattr(store, '_request', request)
    delete = AsyncMock()
    monkeypatch.setattr(store, 'delete_mobile_image', delete)
    with pytest.raises(InvalidImage): asyncio.run(store.consume_mobile_upload(uuid4()))
    delete.assert_awaited_once()

def test_difference_heatmap_saturates_without_integer_wrap(monkeypatch):
    from app.simulation.whatsapp_pipeline import run_whatsapp_simulation
    from app.services.forensic.pipeline import analyze_screenshot
    data = image_bytes()
    report = analyze_screenshot(data)
    monkeypatch.setattr('app.services.forensic.pipeline.analyze_screenshot', lambda **kw: report)
    decoded = iter([np.full((64,64,3), 255, np.uint8), np.zeros((64,64,3), np.uint8)])
    monkeypatch.setattr(cv2, 'imdecode', lambda *a: next(decoded))
    captured=[]
    original = cv2.applyColorMap
    monkeypatch.setattr(cv2, 'applyColorMap', lambda image, cmap: (captured.append(image.copy()), original(image,cmap))[1])
    run_whatsapp_simulation(data)
    assert np.all(captured[0] == 255)
