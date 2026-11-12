import asyncio
import base64
import io
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.services.artifacts import ArtifactStore, delivery_report
from app.services.image_validation import decode_image, ImageTooLarge
from app.services.private_access import PrivateAccess
from app.services import supabase_store


def data(content):
    return 'data:image/png;base64,' + base64.b64encode(content).decode()


def test_capabilities_expire_and_storage_is_bounded(tmp_path, monkeypatch):
    clock=[100.0]
    monkeypatch.setattr('app.services.artifacts.time.monotonic', lambda:clock[0])
    store=ArtifactStore(tmp_path,ttl=10,budget=5)
    url=store.put(data(b'12345'));token=url.rsplit('/',1)[1]
    assert store.get(token)==(b'12345','image/png')
    assert store.get('../secret') is None
    assert (tmp_path/token).stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError):store.put(data(b'1'))
    clock[0]=111
    assert store.get(token) is None
    assert not (tmp_path/token).exists()
    store.put(data(b'1'));store.clear();assert not list(tmp_path.iterdir())


def test_delivery_preserves_input_and_does_not_mutate():
    original={'layer1':{'ela_b64':data(b'x'*100000)}}
    result=delivery_report(original)
    assert result['layer1']['ela_b64'].startswith('/api/artifacts/')
    assert original['layer1']['ela_b64'].startswith('data:')
    with TestClient(app) as client:
        response=client.get(result['layer1']['ela_b64'])
        assert response.status_code==200 and response.content==b'x'*100000
        assert 'no-store' in response.headers['cache-control']
    assert client.get(result['layer1']['ela_b64']).status_code==404


def test_declared_pixel_limit_is_enforced_before_analysis():
    buf=io.BytesIO();Image.new('RGB',(2000,1001)).save(buf,format='PNG')
    with pytest.raises(ImageTooLarge,match='2 megapixels'):decode_image(buf.getvalue())


@pytest.mark.parametrize('host,scheme,password,credential,status',[
    ('127.0.0.1','http','','',200),
    ('198.51.100.1','https','','',401),
    ('198.51.100.1','http','secret','verisight:secret',403),
    ('198.51.100.1','https','secret','verisight:bad',401),
    ('198.51.100.1','https','secret','verisight:secret',200),
])
def test_private_boundary(monkeypatch,host,scheme,password,credential,status):
    monkeypatch.setenv('VERISIGHT_ACCESS_PASSWORD',password)
    monkeypatch.delenv('VERCEL',raising=False)
    async def inner(scope,receive,send):
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':b'ok'})
    async def run():
        result=[]
        async def receive():return {'type':'http.request','body':b''}
        async def send(message):result.append(message)
        await PrivateAccess(inner)({'type':'http','scheme':scheme,'client':(host,123),
            'headers':[(b'authorization',b'Basic '+base64.b64encode(credential.encode()))]},receive,send)
        assert result[0]['status']==status
    asyncio.run(run())


def test_persistence_disabled_and_missing_configuration_are_explicit(monkeypatch):
    from types import SimpleNamespace
    report=SimpleNamespace(persistence_status='NOT_REQUESTED')
    monkeypatch.delenv('VERISIGHT_PERSIST_CASES',raising=False)
    assert asyncio.run(supabase_store.save_case(report)) is False
    assert report.persistence_status=='DISABLED'
    monkeypatch.setenv('VERISIGHT_PERSIST_CASES','1')
    monkeypatch.delenv('SUPABASE_URL',raising=False)
    assert asyncio.run(supabase_store.save_case(report)) is False
    assert report.persistence_status=='NOT_CONFIGURED'


def test_retention_only_deletes_tagged_expired_summaries(monkeypatch):
    from urllib.parse import urlparse, parse_qs
    captured=[]
    class Response:
        status=204
        def __enter__(self):return self
        def __exit__(self,*args):pass
    def fake_open(request,timeout):
        captured.append(request);return Response()
    monkeypatch.setenv('SUPABASE_URL','https://example.invalid')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY','test-only')
    monkeypatch.setattr(supabase_store,'urlopen',fake_open)
    assert asyncio.run(supabase_store.expire_private_cases())
    query=parse_qs(urlparse(captured[0].full_url).query)
    assert query['layer_summary->>retention_policy']==['eq.private-prototype-7d']
    assert query['created_at'][0].startswith('lt.')
    assert captured[0].method=='DELETE'


def test_chunked_request_size_is_bounded():
    from app.services.resource_boundary import AnalysisBoundary
    async def run():
        async def inner(scope,receive,send):
            await receive();await receive()
            raise AssertionError('oversized input must not reach processing')
        async def receive():return {'type':'http.request','body':b'x'*(11*1024*1024),'more_body':True}
        messages=[]
        async def send(message):messages.append(message)
        await AnalysisBoundary(inner)({'type':'http','path':'/api/analyze'},receive,send)
        assert messages[0]['status']==413
    asyncio.run(run())


def test_cross_origin_submission_is_rejected(monkeypatch):
    monkeypatch.delenv('VERISIGHT_ACCESS_PASSWORD',raising=False)
    with TestClient(app) as client:
        response=client.post('/api/analyze',headers={'origin':'https://untrusted.invalid'})
        assert response.status_code==403


def test_database_failure_is_explicit(monkeypatch):
    from app.services.forensic.pipeline import analyze_screenshot
    sample=Path(__file__).resolve().parents[2]/'samples/sample_1_clean_synthetic_ui.png'
    report=analyze_screenshot(sample.read_bytes())
    monkeypatch.setenv('VERISIGHT_PERSIST_CASES','1')
    monkeypatch.setenv('SUPABASE_URL','https://example.invalid')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY','test-only')
    def fail(*args,**kwargs):raise OSError('network unavailable')
    monkeypatch.setattr(supabase_store,'urlopen',fail)
    assert asyncio.run(supabase_store.save_case(report)) is False
    assert report.persistence_status=='FAILED'
