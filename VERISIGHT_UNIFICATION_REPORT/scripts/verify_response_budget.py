"""Bounded actual-API response budget probe, no external storage."""
import os,sys,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for k in list(os.environ):
    if 'SUPABASE' in k or k=='VERCEL':os.environ.pop(k)
sys.path.insert(0,str(root/'backend'))
import cv2,numpy as np
from fastapi.testclient import TestClient
from app.main import app
cv2.setNumThreads(1)
image=np.random.default_rng(20261112).integers(0,256,(1280,960,3),dtype=np.uint8)
_,encoded=cv2.imencode('.png',image)
t=time.perf_counter()
r=TestClient(app).post('/api/analyze',files={'file':('entropy.png',encoded.tobytes(),'image/png')})
result={'input_bytes':len(encoded),'status':r.status_code,'response_bytes':len(r.content),'response':r.json(),'seconds':time.perf_counter()-t}
assert r.status_code==413,result
assert r.json()['analysis_gate']['state']=='BLOCK'
(root/'VERISIGHT_UNIFICATION_REPORT/raw/response_budget.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
