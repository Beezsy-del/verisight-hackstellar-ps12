from pathlib import Path
import subprocess,os,sys,json,time
root=Path(__file__).resolve().parents[1]
env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ['SUPABASE','VERCEL','DATABASE_URL'])}
env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
records=[]
for version in sys.argv[1:] or ['A','B','U']:
 cwd=root.parent if version=='U' else root/'runtime'/version
 e=env.copy();e['PYTHONPATH']=os.pathsep.join([str(cwd/'backend'),str(cwd),str(cwd/'ml')])
 for kind,cmd in [('pytest',[sys.executable,'-m','pytest','backend/tests','-q','-p','no:cacheprovider',f'--junitxml={root}/raw/{version}_pytest.xml']),('benchmark',[sys.executable,str(root/'scripts/benchmark.py'),version])]:
  started=time.perf_counter()
  with (root/f'raw/{version}_{kind}.log').open('w') as out:
   try:p=subprocess.run(cmd,cwd=cwd,env=e,stdout=out,stderr=subprocess.STDOUT,timeout=600);code=p.returncode
   except subprocess.TimeoutExpired:code='TIMEOUT'
  rec={'version':version,'kind':kind,'command':cmd,'cwd':str(cwd),'exit':code,'seconds':time.perf_counter()-started};records.append(rec);print(rec,flush=True)
  (root/f'raw/checks_{"_".join(sys.argv[1:]) or "all"}.json').write_text(json.dumps(records,indent=2))
