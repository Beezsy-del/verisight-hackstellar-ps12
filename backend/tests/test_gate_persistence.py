import asyncio
import json
from pathlib import Path
from app.services.forensic.pipeline import analyze_screenshot
from app.services import supabase_store


def test_saved_case_keeps_gate_provenance_without_images(monkeypatch):
    sample=Path(__file__).resolve().parents[2]/'samples/sample_1_clean_synthetic_ui.png'
    report=analyze_screenshot(sample.read_bytes())
    captured=[]
    class Response:
        status=201
        def __enter__(self):return self
        def __exit__(self,*args):pass
    def fake_open(request,timeout):
        captured.append(json.loads(request.data));return Response()
    monkeypatch.setenv('VERISIGHT_PERSIST_CASES','1')
    monkeypatch.setenv('SUPABASE_URL','https://example.invalid')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY','test-only')
    monkeypatch.setattr(supabase_store,'urlopen',fake_open)
    assert asyncio.run(supabase_store.save_case(report))
    row=captured[0]
    assert row['layer_summary']['analysis_gate']['allowed_actions']['automated_approval'] is False
    assert row['layer_summary']['score_kind']==report.score_kind
    assert 'original_image_b64' not in row
    assert 'ela_b64' not in row['layer_summary']['layer1']
