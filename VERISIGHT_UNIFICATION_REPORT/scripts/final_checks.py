from pathlib import Path
import os,sys,subprocess,json,time
r=Path(__file__).resolve().parents[1];env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ['SUPABASE','VERCEL','DATABASE_URL'])};env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');records=[]
for v,kind in [('U','pytest'),('A','pytest'),('A','benchmark'),('B','benchmark')]:
 cwd=r.parent if v=='U' else r/'runtime'/v;e=env.copy();e['PYTHONPATH']=os.pathsep.join([str(cwd/'backend'),str(cwd),str(cwd/'ml')]);cmd=([sys.executable,'-m','pytest','backend/tests','-q','-p','no:cacheprovider',f'--junitxml={r}/raw/{v}_pytest.xml'] if kind=='pytest' else [sys.executable,str(r/'scripts/benchmark.py'),v]);t=time.perf_counter()
 with (r/f'raw/{v}_{kind}.log').open('w') as f:p=subprocess.run(cmd,cwd=cwd,env=e,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 records.append({'version':v,'kind':kind,'command':cmd,'seconds':time.perf_counter()-t,'exit':p.returncode});(r/'raw/final_checks.json').write_text(json.dumps(records,indent=2));print(records[-1],flush=True)
