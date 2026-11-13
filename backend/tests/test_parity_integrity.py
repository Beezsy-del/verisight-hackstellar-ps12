import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints import CASE_CATALOG, _cached_demo_analysis
from app.core.config import settings
from app.services.evaluation_metrics import threshold_metrics
from app.services.forensic.pipeline import analyze_screenshot
from app.services.forensic.intelligence.syndicate import extract_financial_entities
from app.services.response import case_store
client=TestClient(app)

def image_bytes(size=(64,64), mode="RGB"):
    buf=io.BytesIO(); Image.new(mode,size).save(buf,"PNG"); return buf.getvalue()

@pytest.mark.parametrize("data", [b"",b"not an image",b"\x89PNG\r\n\x1a\n"])
def test_corrupt_upload_is_client_error(data):
    assert client.post("/api/analyze",files={"file":("x.png",data,"image/png")}).status_code==422

def test_limits_and_extensions():
    assert client.post("/api/analyze",files={"file":("x.txt",b"abc","text/plain")}).status_code==415
    assert client.post("/api/analyze",files={"file":("x.png",b"a"*(20*1024*1024+1),"image/png")}).status_code==413
    assert client.post("/api/analyze",files={"file":("x.png",image_bytes((8001,32)),"image/png")}).status_code==413

def test_missing_fixture_not_regenerated(tmp_path,monkeypatch):
    monkeypatch.setattr(settings,"SAMPLES_DIR",tmp_path)
    assert client.post("/api/analyze-sample/sample_clean").status_code==404
    assert list(tmp_path.iterdir())==[]
    assert client.post("/api/analyze-sample/nonexistent").status_code==404

@pytest.mark.parametrize("sample_id", list(CASE_CATALOG))
def test_case_contract_bound_to_bytes(sample_id):
    d=client.post(f"/api/analyze-sample/{sample_id}").json()
    path=settings.SAMPLES_DIR/CASE_CATALOG[sample_id][0]
    assert d["case_id"]==d["sample_id"]==sample_id
    assert d["file_sha256"]==hashlib.sha256(path.read_bytes()).hexdigest()
    assert d["filename"]==path.name
    assert d["confidence_score"] is None
    assert d["processing_status"]=="COMPLETE"
    assert d["verdict"] in {"INCONCLUSIVE","REVIEW_REQUIRED","CORROBORATED_ANOMALIES"}
    assert d["syndicate_intelligence"]["entity_summary"]["payee_vpa"] is None

def test_filename_cannot_inject_entities():
    for name in ("sample_1.png","sample_2.jpg","sample_1_synthetic_backup.png","upload.png"):
        d=extract_financial_entities([],filename=name)
        assert d["payee_vpa"] is None and d["utr_number"] is None and d["amount"] is None

def test_unknown_detectors_are_unavailable():
    h=client.get("/api/health").json()
    assert h["database"]=="NOT_CONFIGURED"
    assert not h["capabilities"]["server_transcription"]
    assert client.post("/api/upload-session", json={"filename":"test.png","content_type":"image/png","size":100}).status_code==503
    assert client.get("/api/latest-mobile-upload?session_id=anything").status_code==422

def test_case_persistence_and_hosted_gate(tmp_path,monkeypatch):
    monkeypatch.setattr(case_store,"STORE_FILE",tmp_path/"notes.sqlite3")
    details=client.post("/api/response/understand",json={"user_text":"I received a suspicious receipt."}).json()["extracted_details"]
    c=client.post("/api/response/cases/create",json={"details":details}).json()
    c["notes"]="Review with bank; no submission made"
    assert client.post("/api/response/cases",json=c).status_code==200
    assert case_store.get_case(c["case_id"]).notes==c["notes"]
    assert case_store.get_case(c["case_id"]).acknowledgement_number is None
    monkeypatch.setenv("VERCEL","1")
    assert client.get("/api/response/cases").status_code==401

def test_cross_origin_write_denied():
    assert client.post("/api/analyze-sample/sample_clean",headers={"Origin":"https://unrelated.invalid"}).status_code==403

def test_metrics_are_derived_and_zero_denominators_unavailable():
    d=threshold_metrics([1,1,0,0],[.9,.3,.8,.1],.5)
    assert (d["tp"],d["fn"],d["fp"],d["tn"])==(1,1,1,1)
    assert d["sensitivity"]==d["specificity"]==d["precision"]==d["fpr"]==.5
    d=threshold_metrics([1,1,0,0],[.9,.3,.8,.1],.85)
    assert d["precision"]==1 and d["fpr"]==0
    assert threshold_metrics([],[],.5)["precision"] is None
    with pytest.raises(ValueError): threshold_metrics([1],[float('nan')],.5)

def test_synthetic_corpus_cannot_claim_group_isolation():
    manifest=json.loads((settings.BASE_DIR/"ml/datasets/manifests/benchmark_manifest.json").read_text())
    groups={}
    for row in manifest: groups.setdefault(row["screenshot_template"],set()).add(row["split_assignment"])
    assert any(len(splits)>1 for splits in groups.values())
    assert client.get("/api/model/evaluation").json()["release_gate"]=="BLOCK"

def test_parallel_cases_do_not_cross_contaminate():
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda k:client.post(f"/api/analyze-sample/{k}").json(),["sample_clean","sample_2"]))
    assert [r["case_id"] for r in results]==["sample_clean","sample_2"]
    assert results[0]["file_sha256"]!=results[1]["file_sha256"]

def test_busy_analysis_rejects_and_recovers():
    from app.api.endpoints import _WORKERS
    _WORKERS.acquire(); _WORKERS.acquire()
    try:
        assert client.post("/api/analyze-sample/sample_clean").status_code==429
    finally:
        _WORKERS.release(); _WORKERS.release()
    assert client.get("/api/health").status_code==200

def test_transparent_preview_matches_composited_pixels():
    import base64
    d=analyze_screenshot(image_bytes(mode="RGBA"),"transparent.png")
    preview=Image.open(io.BytesIO(base64.b64decode(d.original_image_b64.split(',')[1])))
    assert preview.convert("RGB").getpixel((10,10))==(255,255,255)

def test_complaint_does_not_invent_bank_checks_or_submission():
    d=client.post('/api/response/understand',json={'user_text':'Someone sent me a receipt; I have not checked my bank.'}).json()['extracted_details']
    response=client.post('/api/response/generate-complaint',json={'details':d}).json()
    assert 'no corresponding deposit had occurred' not in response['chronological_narrative']
    assert 'captured and preserved' not in response['chronological_narrative']
    assert response['title'].startswith('DRAFT')
    assert 'Not submitted' in response['disclaimer']
