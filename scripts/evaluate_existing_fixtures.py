import sys,json,hashlib,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];engine=sys.argv[1];sys.path[:0]=[str(root/('research/baseline_backend' if engine=='baseline' else 'backend')),str(root)]
from app.services.forensic.pipeline import analyze_screenshot
rows=[]
for p in sorted((root/'samples').iterdir()):
 if p.suffix.lower() not in {'.png','.jpg','.jpeg'}:continue
 raw=p.read_bytes();start=time.perf_counter();r=analyze_screenshot(raw,p.name)
 rows.append(dict(file=p.name,sha256=hashlib.sha256(raw).hexdigest(),label_status='UNVERIFIED_EXCLUDED' if p.name=='sample_1_authentic_gpay.png' else 'SYNTHETIC_SMOKE_ONLY',score=r.overall_tamper_score,verdict=r.verdict,seconds=time.perf_counter()-start,baseline_drift=r.layer2.max_baseline_drift_px,clones=r.layer1.clone_count,noise=r.layer1.wavelet_noise_score,ela=r.layer1.ela_score,confidence=r.confidence_score))
(root/f'research/results/{engine}-existing-fixtures.json').write_text(json.dumps(rows,indent=2));print(len(rows),'fixtures analyzed; no accuracy claims')
