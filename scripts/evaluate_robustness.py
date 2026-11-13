"""Frozen paired benchmark runner. Scores are review priorities, never probabilities."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--engine',choices=['baseline','upgraded','integrated'],required=True);p.add_argument('--partition',default='all');args=p.parse_args()
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/({'baseline':'research/baseline_backend','upgraded':'research/tester_backend','integrated':'backend'}[args.engine])));sys.path.insert(1,str(root))
from app.services.forensic.pipeline import analyze_screenshot
manifest=root/'research/datasets/robustness/manifest.json';data=json.loads(manifest.read_text());samples=data['samples']
# Fail on source/template leakage; all contributors are synthetic, so real-world independence is NOT claimed.
for key in ['source_group_id','template','editing_session']:
 seen={}
 for r in samples:
  if r[key] in seen and seen[r[key]]!=r['partition']:raise ValueError(f'Partition leakage: {key}')
  seen[r[key]]=r['partition']
rows=[];dest=root/f'research/results/{args.engine}-{args.partition}.json'
for r in samples:
 if args.partition!='all' and r['partition']!=args.partition:continue
 raw=(root/r['path']).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('Changed locked input')
 start=time.perf_counter()
 try:
  d=analyze_screenshot(raw,Path(r['path']).name).model_dump()
  row={**r,'score':d['overall_tamper_score'],'candidate_score':d.get('intelligence',{}).get('candidate_score'),'verdict':d['verdict'],'seconds':round(time.perf_counter()-start,4),'features':{'baseline_drift':d['layer2']['max_baseline_drift_px'],'baseline_rows':sum(x['is_tampered'] for x in d['layer2']['lasers']),'ela':d['layer1']['ela_score'],'ela_blocks':d['layer1']['anomalous_blocks_count'],'noise':d['layer1']['wavelet_noise_score'],'clones':d['layer1']['clone_count']},'intelligence':d.get('intelligence',{}),'boxes':[{k:b[k] for k in ['x','y','width','height','anomaly_type']} for b in d['all_bounding_boxes']]}
  # Candidate-region union is an intentionally coarse localization metric, not a trained pixel segmentation metric.
  import cv2
  mask=cv2.imread(str(root/r['mask_path']),0)>0;pred=np.zeros(mask.shape,bool)
  for b in row['boxes']:pred[max(0,b['y']):b['y']+b['height'],max(0,b['x']):b['x']+b['width']]=True
  inter=int((mask&pred).sum());union=int((mask|pred).sum());den=int(mask.sum()+pred.sum())
  row['candidate_region_iou']=inter/union if union else None;row['candidate_region_f1']=2*inter/den if den else None
 except Exception as e:row={**r,'error':str(e),'seconds':time.perf_counter()-start}
 rows.append(row);dest.write_text(json.dumps({'engine':args.engine,'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'rows':rows},indent=2));print(args.engine,len(rows),r['sample_id'],row.get('score',row.get('error')),flush=True)
