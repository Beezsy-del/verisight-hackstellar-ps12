"""Synthetic delivery/resource probe; never an accuracy benchmark. Run from root."""
import io
import json
import resource
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app


def main():
    data=np.random.default_rng(42).integers(0,256,(1280,960,3),dtype=np.uint8)
    content=io.BytesIO();Image.fromarray(data).save(content,format='PNG')
    raw=content.getvalue()
    with TestClient(app) as client:
        def run(_):
            start=time.perf_counter()
            response=client.post('/api/analyze',files={'file':('generated.png',raw,'image/png')})
            result={'status':response.status_code,'seconds':round(time.perf_counter()-start,4),'json_bytes':len(response.content)}
            if response.status_code==200:
                body=response.json();urls=[body['original_image_b64']]+[body['layer1'][key] for key in ('ela_b64','wavelet_noise_b64','clone_b64')]
                result['artifacts']=[{'status':(r:=client.get(url)).status_code,'bytes':len(r.content)} for url in urls if url.startswith('/api/artifacts/')]
                result['gate']=body['analysis_gate']['state']
            return result
        single=run(0)
        original_raw=raw
        maximum=io.BytesIO()
        Image.fromarray(np.random.default_rng(43).integers(0,256,(1000,2000,3),dtype=np.uint8)).save(maximum,format='PNG')
        raw=maximum.getvalue()
        maximum_result=run(0)
        raw=original_raw
        with ThreadPoolExecutor(max_workers=3) as pool: concurrent=list(pool.map(run,range(3)))
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result={'synthetic_only':True,'input_bytes':len(raw),'dimensions':[960,1280],
                'single':single,'maximum_2mp':maximum_result,'concurrent_3':concurrent,'peak_rss_mib':round(rss/(1024**2 if sys.platform=='darwin' else 1024),2),
                'limits':client.get('/api/operating-envelope').json()}
        print(json.dumps(result,indent=2))
        assert single['status']==200 and single['json_bytes']<4_000_000
        assert maximum_result['status']==200 and all(x['status']==200 for x in maximum_result['artifacts'])
        assert single['artifacts'] and all(x['status']==200 for x in single['artifacts'])
        assert all(x['status'] in (200,503) for x in concurrent)
        assert sum(x['status']==200 for x in concurrent)>=1
if __name__=='__main__':main()
