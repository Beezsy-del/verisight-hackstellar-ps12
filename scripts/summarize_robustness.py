"""Metrics calculated only from saved per-image predictions; no confidence probabilities."""
import json,hashlib
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,roc_curve,precision_recall_curve
R=Path(__file__).resolve().parents[1];out=R/'research/results'
b=json.loads((out/'baseline-all.json').read_text());n=json.loads((out/'upgraded-all.json').read_text())
assert b['manifest_sha256']==n['manifest_sha256']
assert len(b['rows'])==len(n['rows'])==120 and not any('error' in r for r in b['rows']+n['rows'])

def metrics(rows,field,threshold):
 y=np.array([r['label'] for r in rows]);s=np.array([r[field] for r in rows]);p=s>=threshold
 tp=int(((y==1)&p).sum());tn=int(((y==0)&~p).sum());fp=int(((y==0)&p).sum());fn=int(((y==1)&~p).sum())
 div=lambda a,b:float(a/b) if b else None
 precision=div(tp,tp+fp);recall=div(tp,tp+fn);specificity=div(tn,tn+fp)
 d=dict(n=len(y),positive=int(y.sum()),negative=int((y==0).sum()),threshold=threshold,TP=tp,TN=tn,FP=fp,FN=fn,precision=precision,recall=recall,specificity=specificity,FPR=div(fp,fp+tn),FNR=div(fn,fn+tp),F1=div(2*tp,2*tp+fp+fn),balanced_accuracy=(recall+specificity)/2 if recall is not None and specificity is not None else None,ROC_AUC=float(roc_auc_score(y,s)) if len(set(y))>1 else None,PR_AUC_average_precision=float(average_precision_score(y,s)) if len(set(y))>1 else None,Brier=None,calibration='UNAVAILABLE: scores are not probabilities')
 pairs={}
 for r in rows:pairs.setdefault(r['pair_id'],{})[r['label']]=r[field]
 margins=[p[1]-p[0] for p in pairs.values() if 0 in p and 1 in p]
 d['pairs']=len(margins);d['pair_win_rate']=float(np.mean(np.array(margins)>0)) if margins else None;d['pair_tie_rate']=float(np.mean(np.array(margins)==0)) if margins else None;d['mean_pair_margin']=float(np.mean(margins)) if margins else None
 d['candidate_region_F1']=float(np.mean([r['candidate_region_f1'] or 0 for r in rows if r['label']]))
 d['median_seconds']=float(np.median([r['seconds'] for r in rows]));d['candidate_region_IoU']=float(np.mean([r['candidate_region_iou'] or 0 for r in rows if r['label']]))
 return d
# Threshold selection on development ONLY: largest recall under <=10% FPR, ties prefer smaller FPR.
dev=[r for r in n['rows'] if r['partition']=='development'];options=sorted(set([0.0]+[r['candidate_score'] for r in dev]+[100.0001]));ms=[metrics(dev,'candidate_score',t) for t in options];eligible=[m for m in ms if m['FPR']<=.1];chosen=max(eligible,key=lambda m:(m['recall'],-m['FPR'],-m['threshold']));threshold=chosen['threshold']
result=dict(prediction_sha256={name:hashlib.sha256((out/(name+'-all.json')).read_bytes()).hexdigest() for name in ['baseline','upgraded']},manifest_sha256=n['manifest_sha256'],purpose='SYNTHETIC SOFTWARE STRESS ONLY; no real-world accuracy claim',target_validation_FPR=.1,candidate_threshold=threshold,threshold_selection='Development only; maximize recall subject to FPR<=.10. Frozen before locked-subset metric calculation.',release_gate='BLOCK',calibration='UNAVAILABLE',dataset=dict(n=120,positive=60,negative=60,source_groups=10,templates=5,shared_generator=True),models={})
for name,rows,field,thr in [('baseline',b['rows'],'score',12),('upgraded_operational',n['rows'],'score',12),('experimental_candidate',n['rows'],'candidate_score',threshold)]:
 model={}
 for part in ['development','locked_synthetic_test']:
  selected=[r for r in rows if r['partition']==part];m=metrics(selected,field,thr)
  fpr,tpr,_=roc_curve([r['label'] for r in selected],[r[field] for r in selected]);prec,rec,_=precision_recall_curve([r['label'] for r in selected],[r[field] for r in selected]);m['roc_curve']=[dict(x=float(x),y=float(y)) for x,y in zip(fpr,tpr)];m['pr_curve']=[dict(x=float(x),y=float(y)) for x,y in zip(rec,prec)]
  # Source-group bootstrap respects delivery pairing; tiny synthetic group count limits interpretation.
  groups=sorted(set(r['source_group_id'] for r in selected));rng=np.random.default_rng(512);aucs=[];wins=[]
  for _ in range(200):
   chosen_groups=rng.choice(groups,len(groups),replace=True);rr=[r for g in chosen_groups for r in selected if r['source_group_id']==g];aucs.append(roc_auc_score([r['label'] for r in rr],[r[field] for r in rr]));margins=[]
   for g in chosen_groups:
    gr=[r for r in selected if r['source_group_id']==g];pp={}
    for r in gr:pp.setdefault(r['pair_id'],{})[r['label']]=r[field]
    margins.extend(p[1]-p[0] for p in pp.values())
   wins.append(np.mean(np.array(margins)>0))
  m['ROC_AUC_group_bootstrap_95CI']=np.percentile(aucs,[2.5,97.5]).tolist();m['pair_win_group_bootstrap_95CI']=np.percentile(wins,[2.5,97.5]).tolist();m['conditions']={c:metrics([r for r in selected if r['delivery_path']==c],field,thr) for c in sorted(set(r['delivery_path'] for r in selected))};m['templates']={c:metrics([r for r in selected if r['template']==c],field,thr) for c in sorted(set(r['template'] for r in selected))};m['edit_types']={c:metrics([r for r in selected if r['manipulation_category']==c or r['label']==0],field,thr) for c in sorted(set(r['manipulation_category'] for r in selected if r['label']))};model[part]=m
 result['models'][name]=model
# Failure categories are hypotheses based on observed cues, not assumed causal truth.
failures=[]
for r in n['rows']:
 prediction=r['candidate_score']>=threshold
 if prediction!=bool(r['label']):failures.append(dict(sample_id=r['sample_id'],kind='FP' if prediction else 'FN',condition=r['delivery_path'],hypothesis='poor image quality or unreadable text' if r['intelligence']['ocr']['status']!='AVAILABLE' else 'weak local evidence / unfamiliar layout',features=r['features'],candidate_score=r['candidate_score'],label=r['label']))
(out/'error-analysis.json').write_text(json.dumps(failures,indent=2));(out/'robustness-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v['locked_synthetic_test'] for k,v in result['models'].items()},indent=2)[:3500])
