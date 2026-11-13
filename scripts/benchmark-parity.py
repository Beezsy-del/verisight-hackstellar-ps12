"""Deterministic software smoke timings, NOT accuracy evaluation or training."""
import argparse, sys, time, json, resource, hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--fixtures',required=True);p.add_argument('--output',required=True);args=p.parse_args()
root=Path(args.repo);sys.path[:0]=[str(root/'backend'),str(root)]
from app.services.forensic.pipeline import analyze_screenshot
results=[]
for filename in ['sample_1_synthetic_backup.png','sample_2_spliced_amount.jpg','sample_3_fake_generator_paradox.png','sample_4_whatsapp_laundered.jpg','sample_5_cloned_chat_receipt.jpg']:
 data=(Path(args.fixtures)/filename).read_bytes()
 for run in range(2):
  start=time.perf_counter()
  try:
   d=analyze_screenshot(data,filename)
   results.append(dict(file=filename,run=run,sha256=hashlib.sha256(data).hexdigest(),seconds=round(time.perf_counter()-start,4),score=d.overall_tamper_score,verdict=d.verdict,confidence=d.confidence_score,findings=len(d.findings)))
  except Exception as exc:results.append(dict(file=filename,run=run,error=str(exc)))
Path(args.output).write_text(json.dumps(dict(repo=str(root),purpose='Software smoke timing; five synthetic fixtures, no accuracy claim',peak_rss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,results=results),indent=2))
