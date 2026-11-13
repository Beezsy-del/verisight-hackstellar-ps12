import io,json,subprocess,sys
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.forensic.intelligence.robust_review import acquisition_profile,recognize,review_intelligence,ocr_available,local_measurements
from app.services.forensic.pixel_analysis.copy_move import run_copy_move_analysis
ROOT=Path(__file__).resolve().parents[2]

def png(im):return cv2.imencode('.png',im)[1].tobytes()

def test_quality_is_not_platform_or_authenticity():
 im=np.full((600,360,3),240,np.uint8);cv2.putText(im,'Receipt',(20,200),0,1,(0,0,0),2)
 for q in [30,75,95]:
  raw=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,q])[1].tobytes();p=acquisition_profile(raw,im)
  assert p['platform']==p['recapture']==p['resizing']=='NOT_IDENTIFIABLE'
  assert p['estimated_profile']=='UNKNOWN_PROVENANCE'
  assert 0<p['pixel_cue_reliability']<=1

def test_unavailable_ocr_never_invents_tokens(monkeypatch):
 monkeypatch.setenv('VERISIGHT_OCR_ENABLED','0');r=recognize(np.zeros((60,60,3),np.uint8))
 assert r['status']=='UNAVAILABLE' and r['tokens']==r['fields']==[]

def test_timeout_explicit():
 with patch('shutil.which',return_value='/bin/tesseract'),patch('subprocess.run',side_effect=subprocess.TimeoutExpired('tesseract',8)):
  assert recognize(np.zeros((80,80,3),np.uint8))['status']=='TIMEOUT'

def test_ocr_failure_explicit():
 with patch('shutil.which',return_value='/bin/tesseract'),patch('subprocess.run',return_value=subprocess.CompletedProcess([],1,b'',b'failure')):
  r=recognize(np.zeros((80,80,3),np.uint8));assert r['status']=='ERROR' and not r['fields']

def test_low_confidence_no_field_invention():
 tsv=b'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n5\t1\t1\t1\t1\t1\t10\t10\t30\t15\t25\tINR999\n'
 with patch('shutil.which',return_value='/bin/tesseract'),patch('subprocess.run',return_value=subprocess.CompletedProcess([],0,tsv,b'')):
  r=recognize(np.zeros((80,80,3),np.uint8));assert r['status']=='UNREADABLE' and not r['fields'];assert r['tokens'][0]['confidence']==25

def test_actual_ocr_reads_source_coordinates():
 if not ocr_available():pytest.skip('Optional Tesseract not installed')
 im=np.full((350,700,3),255,np.uint8);cv2.putText(im,'INR 1250.00',(40,140),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),2,cv2.LINE_AA)
 r=recognize(im);assert r['status']=='AVAILABLE';assert any('1250' in t['text'] for t in r['tokens']);assert any(f['kind']=='amount' for f in r['fields'])
 for t in r['tokens']:
  b=t['box'];assert 0<=b['x']<700 and 0<=b['y']<350 and b['x']+b['width']<=700 and b['y']+b['height']<=350

def test_missing_measurements_are_missing_not_negative(monkeypatch):
 monkeypatch.setenv('VERISIGHT_OCR_ENABLED','0');im=np.full((200,200,3),255,np.uint8);r=review_intelligence(png(im),im)
 assert r['candidate_state']=='INCONCLUSIVE';assert r['classifier_confidence'] is None
 assert r['evidence'][0]['direction']=='MISSING';assert r['promotion_status'].startswith('BLOCKED')

def test_duplicate_correlated_local_cues_cannot_accumulate():
 im=np.zeros((100,100,3),np.uint8)
 e=dict(id='one',family='local_rendering',value=5.,reliability=.6)
 with patch('app.services.forensic.intelligence.robust_review.recognize',return_value={'tokens':[],'fields':[]}),patch('app.services.forensic.intelligence.robust_review.local_measurements',return_value=([],[e])):
  one=review_intelligence(png(im),im)['candidate_score']
 with patch('app.services.forensic.intelligence.robust_review.recognize',return_value={'tokens':[],'fields':[]}),patch('app.services.forensic.intelligence.robust_review.local_measurements',return_value=([],[e,e,e])):
  assert review_intelligence(png(im),im)['candidate_score']==one

def test_blank_copy_move_not_positive():
 d,count,_,boxes,_=run_copy_move_analysis(np.full((400,400,3),255,np.uint8));assert not d and count==0 and not boxes

def test_manifest_source_template_and_session_isolation():
 m=json.loads((ROOT/'research/datasets/robustness/manifest.json').read_text())
 for k in ['source_group_id','template','editing_session']:
  a={r[k] for r in m['samples'] if r['partition']=='development'};b={r[k] for r in m['samples'] if r['partition']=='locked_synthetic_test'};assert a.isdisjoint(b)
 assert len(m['samples'])==120

def test_training_gate_blocks_synthetic_and_group_leakage():
 sys.path.insert(0,str(ROOT/'scripts'));from training_preflight import validate
 m=json.loads((ROOT/'research/datasets/robustness/manifest.json').read_text());assert any('Synthetic' in s for s in validate(m))
 m['samples'][0]['partition']='test';assert any('leakage' in s for s in validate(m))

def test_research_endpoint_returns_actual_predictions():
 d=TestClient(app).get('/api/research/robustness').json();assert d['status']=='SYNTHETIC_ONLY';assert len(d['predictions'])==120;assert d['release_gate']=='BLOCK'
 assert sum(r['label'] for r in d['predictions'])==60

def test_research_absent_not_fake_success(tmp_path,monkeypatch):
 monkeypatch.setattr(settings,'BASE_DIR',tmp_path);assert TestClient(app).get('/api/research/robustness').json()['status']=='UNAVAILABLE'

def test_compact_media_retains_exact_pixels_and_expires(monkeypatch):
 from app.services.forensic.intelligence import media_cache
 client=TestClient(app);r=client.post('/api/analyze-sample/sample_clean?media=urls');assert r.status_code==200
 d=r.json();assert len(r.content)<250000 and d['original_image_b64']==''
 image=client.get(d['media_urls']['original']);assert image.status_code==200;assert image.headers['cache-control']=='no-store'
 actual=cv2.imdecode(np.frombuffer(image.content,np.uint8),1);expected=cv2.imread(str(settings.SAMPLES_DIR/'sample_1_synthetic_backup.png'));assert np.array_equal(actual,expected)
 monkeypatch.setattr(media_cache,'_prune',lambda now:media_cache.CACHE.clear())
 assert client.get(d['media_urls']['original']).status_code==410

def test_local_media_refuses_hosted_use(monkeypatch):
 monkeypatch.setenv('VERCEL','1');assert TestClient(app).post('/api/analyze-sample/sample_clean?media=urls').status_code==401

def test_media_cache_bounded(monkeypatch):
 from starlette.requests import Request
 from app.services.forensic.intelligence import media_cache
 import base64
 monkeypatch.setattr(media_cache,'MAX_BYTES',10);media_cache.CACHE.clear()
 req=Request({'type':'http','method':'GET','path':'/','query_string':b'media=urls','server':('localhost',8001),'headers':[(b'host',b'localhost:8001')]})
 for _ in range(5):media_cache.store_extra_media('data:image/png;base64,'+base64.b64encode(b'12345678').decode(),req)
 assert sum(len(v[2]) for v in media_cache.CACHE.values())<=10;media_cache.CACHE.clear()

def test_semantic_checks_are_unverified_and_abstain_on_ambiguity():
 from app.services.forensic.intelligence.robust_review import semantic_checks
 box=dict(x=0,y=0,width=100,height=20)
 amount=dict(kind='amount',text='INR 1250.00',confidence=95,box=box)
 qr={'results':[{'payload':'upi://pay?am=9850.00&pa=demo%40example'}]}
 checks=semantic_checks({'fields':[amount]},qr);assert checks[0]['state']=='CONTENT_REVIEW';assert 'neither source validates' in checks[0]['explanation']
 assert semantic_checks({'fields':[amount,{**amount,'text':'INR 50.00'}]},qr)[0]['state']=='UNAVAILABLE'
 assert semantic_checks({'fields':[{**amount,'confidence':50}]},qr)[0]['state']=='UNAVAILABLE'
 assert semantic_checks({'fields':[dict(kind='date',text='2026-02-31',confidence=95,box=box)]},{})[0]['state']=='FORMAT_REVIEW'
