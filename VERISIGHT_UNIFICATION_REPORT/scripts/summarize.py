from pathlib import Path
import json,collections,numpy as np
from sklearn.metrics import confusion_matrix,precision_recall_fscore_support,roc_auc_score,average_precision_score
r=Path(__file__).resolve().parents[1]
manifest={x['id']:x for x in json.loads((r/'raw/benchmark_manifest.json').read_text())}
data={v:[json.loads(l) for l in (r/f'raw/{v}_benchmark.jsonl').read_text().splitlines()] for v in ['A','B','U']}
common=set.intersection(*[{x['id'] for x in rows if x['repeat']==0 and not x.get('error')} for rows in data.values()])
summary={}
for v,rows in data.items():
 first=[x for x in rows if x['repeat']==0];ok=[x for x in first if not x.get('error')];controlled=[x for x in ok if x['id'] in common and manifest[x['id']]['kind']=='controlled']
 y=[manifest[x['id']]['label'] for x in controlled];pred=[int(x['verdict'] not in ['INCONCLUSIVE','AUTHENTIC_VERIFIED']) for x in controlled];scores=[x['score'] for x in controlled]
 tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel().tolist()
 summary[v]={'attempted':len(first),'completed':len(ok),'errors':dict(collections.Counter(x.get('error') for x in first if x.get('error'))),'common_controlled':{'n':len(y),'tn':tn,'fp':fp,'fn':fn,'tp':tp,'fpr':fp/(fp+tn),'fnr':fn/(fn+tp),'recall':tp/(tp+fn),'precision':tp/(tp+fp) if tp+fp else None,'roc_auc':roc_auc_score(y,scores),'average_precision':average_precision_score(y,scores)},'median_seconds':float(np.median([x['seconds'] for x in ok])),'p95_seconds':float(np.quantile([x['seconds'] for x in ok],.95)),'peak_rss':max(x['process_peak_rss_bytes'] for x in rows),'gate_states':dict(collections.Counter((x.get('analysis_gate') or {}).get('state','MISSING') for x in ok))}
a={x['id']:x for x in data['A'] if x['repeat']==0};u={x['id']:x for x in data['U'] if x['repeat']==0}
summary['A_U_differences']=[{'id':k,'a_verdict':a[k].get('verdict'),'u_verdict':u[k].get('verdict'),'a_score':a[k].get('score'),'u_score':u[k].get('score')} for k in a.keys()&u.keys() if a[k].get('verdict')!=u[k].get('verdict') or a[k].get('score')!=u[k].get('score')]
(r/'raw/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
