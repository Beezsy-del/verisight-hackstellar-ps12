"""Fail-closed data governance check. Does not train or load research checkpoints."""
import argparse,json,hashlib
from pathlib import Path
REQUIRED=('source_group_id','template','device','contributor','editing_session','sha256','partition')
def validate(manifest):
 rows=manifest.get('samples',[]);reasons=[]
 if len(rows)<500:reasons.append('Fewer than 500 images: collection planning floor only, not statistical sufficiency.')
 if not rows or any(r.get('source_type')=='synthetic' for r in rows):reasons.append('Synthetic-only or mixed synthetic corpus is not approved as representative real-world validation.')
 for r in rows:
  if not r.get('authorized_use') or not r.get('license') or not r.get('permission_evidence'):reasons.append('Missing explicit permission evidence for intended use.')
  if any(not r.get(k) for k in REQUIRED):reasons.append('Missing required split/provenance fields.')
 for key in REQUIRED[:-1]:
  seen={}
  for r in rows:
   value=r.get(key);part=r.get('partition')
   if value in seen and seen[value]!=part:reasons.append('Cross-partition leakage: '+key)
   seen[value]=part
 if set(r.get('partition') for r in rows)!={'train','validation','test'}:reasons.append('Need locked train/validation/test partitions.')
 for part in ['train','validation','test']:
  if set(r.get('label') for r in rows if r.get('partition')==part)!={0,1}:reasons.append('Both classes required in '+part)
 return sorted(set(reasons))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--output',type=Path,default=Path('research/results/training-gate.json'));a=p.parse_args();data=json.loads(a.manifest.read_text());reasons=validate(data)
 # Even an automated preflight pass still needs license review, near-duplicate review and approval of validation design.
 result=dict(status='BLOCK' if reasons else 'MANUAL_REVIEW_REQUIRED',manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),reasons=reasons,trained=False,model_artifact=None)
 a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(2 if reasons else 0)
