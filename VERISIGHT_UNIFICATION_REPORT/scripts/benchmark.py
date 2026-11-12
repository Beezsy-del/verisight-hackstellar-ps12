"""Audit-only synthetic probes. No training, threshold selection, or real-world accuracy claim.
Usage: python scripts/benchmark.py generate; python scripts/benchmark.py A|B
Both versions receive identical bytes, no ground-truth metadata is supplied to inference.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import json, sys, time, hashlib, resource, traceback
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'raw'/'fixtures'

def generate():
    import qrcode
    FIX.mkdir(exist_ok=True)
    rows=[]
    for seed in [17,29,43]:
        rng=np.random.default_rng(seed)
        base=np.full((800,540,3),245,np.uint8)
        cv2.rectangle(base,(20,70),(520,750),(255,255,255),-1)
        amount=int(rng.integers(100,999));shift=int(rng.integers(-4,5))
        def text(img,s,y,scale=.60):cv2.putText(img,s,(45+shift,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(25,25,25),1,cv2.LINE_AA)
        text(base,'Payment successful',135,.75)
        text(base,f'INR {amount}.00',245,.9)
        text(base,'To: Example Shop',350)
        text(base,'Date: 11 Nov 2026 14:30',445)
        text(base,f'Ref: 6316184920{seed}',530)
        text(base,'Transaction details',630)
        for edit in ['clean','amount','recipient','timestamp','reference','insertion','removal','copy_move','qr_payload']:
            img=base.copy();mask=np.zeros(base.shape[:2],np.uint8)
            if edit in ['amount','recipient','timestamp','reference']:
                y,s={'amount':(245,'INR 99000.00'),'recipient':(350,'To: Different Shop'),'timestamp':(445,'Date: 12 Nov 2026 19:45'),'reference':(530,'Ref: 631618999999')}[edit]
                cv2.rectangle(img,(35,y-35),(505,y+12),(252,252,252),-1)
                text(img,s,y,.9 if edit=='amount' else .6)
            elif edit=='insertion':text(img,'Refund approved',690)
            elif edit=='removal':cv2.rectangle(img,(35,500),(505,545),(255,255,255),-1)
            elif edit=='copy_move':img[660:705,40:505]=img[500:545,40:505]
            elif edit=='qr_payload':
                # Known pixel insertion of a harmless example-domain payload; not bank status.
                qr=np.array(qrcode.make(f'https://example.com/audit/{seed}').convert('RGB'))
                qr=cv2.resize(qr,(180,180),interpolation=cv2.INTER_NEAREST)
                img[555:735,330:510]=qr
            mask[np.any(img!=base,axis=2)]=255
            for transform in ['png','jpeg60','resize75']:
                out=img.copy();m=mask.copy()
                if transform=='resize75':
                    out=cv2.resize(out,(405,600),interpolation=cv2.INTER_AREA)
                    m=cv2.resize(m,(405,600),interpolation=cv2.INTER_NEAREST)
                suffix='.jpg' if transform=='jpeg60' else '.png'
                sid=f'probe_{seed}_{edit}_{transform}'
                path=FIX/(sid+suffix);mp=FIX/(sid+'_mask.png')
                cv2.imwrite(str(path),out,[cv2.IMWRITE_JPEG_QUALITY,60] if suffix=='.jpg' else [])
                cv2.imwrite(str(mp),m)
                rows.append(dict(id=sid,path=str(path),mask=str(mp),label=int(edit!='clean'),kind='controlled',edit=edit,transform=transform,seed=seed,group=f'probe_{seed}',mask_valid=True))
    for idx,s in enumerate(['FAKE PAYMENT RECEIPT','Payment failed','Payment pending','Payment successful','Report fake payments','Payment failed? Contact support','FOR DEMO ONLY','NOT A REAL TRANSACTION','Fake payment receipt - example']):
        img=np.full((800,720,3),255,np.uint8)
        cv2.putText(img,s,(35,300),cv2.FONT_HERSHEY_SIMPLEX,.65,(0,0,0),1,cv2.LINE_AA)
        path=FIX/f'semantic_{idx}.png';cv2.imwrite(str(path),img)
        rows.append(dict(id=f'semantic_{idx}',path=str(path),kind='semantic',text=s,label=None))
    a=ROOT/'runtime/B/ml'
    for item in json.loads((a/'datasets/manifests/benchmark_manifest.json').read_text()):
        path=a/Path(item['image_path'].replace('\\','/')); mask=a/Path(item['mask_path'].replace('\\','/'))
        rows.append(dict(id=item['sample_id'],path=str(path),mask=str(mask),label=item['ground_truth_label'],kind='bundled',edit=item['manipulation_type'],transform='jpeg77_then_png' if item['is_whatsapp'] else 'png',group=item['screenshot_template'],split=item['split_assignment'],mask_valid=item['manipulation_type']!='DOM_EDIT'))
    for item in rows:item['sha256']=hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()
    (ROOT/'raw/benchmark_manifest.json').write_text(json.dumps(rows,indent=2))
    print('Prepared',len(rows),'synthetic audit inputs; no training')

def benchmark(version):
    project=ROOT.parent if version=='U' else ROOT/'runtime'/version
    sys.path[:0]=[str(project/'backend'),str(project),str(project/'ml')]
    cv2.setNumThreads(1)
    from app.services.forensic.pipeline import analyze_screenshot
    rows=json.loads((ROOT/'raw/benchmark_manifest.json').read_text())
    # Fixed randomized order; repeat a small balanced subset to measure runtime/determinism.
    rng=np.random.default_rng(20261112);rng.shuffle(rows)
    jobs=[(r,0) for r in rows]
    subset=[r for r in rows if r['kind']=='controlled' and r['seed']==17 and r['edit'] in ['clean','amount']]
    jobs.extend((r,rep) for rep in [1,2] for r in subset)
    output=ROOT/f'raw/{version}_benchmark.jsonl'
    with output.open('w') as stream:
        for idx,(row,rep) in enumerate(jobs):
            data=Path(row['path']).read_bytes();t=time.perf_counter();record={'id':row['id'],'repeat':rep,'input_sha256':row['sha256']}
            try:
                report=analyze_screenshot(data,filename='uploaded'+Path(row['path']).suffix)
                d=report.model_dump(); boxes=d.get('all_bounding_boxes',[])
                record['analysis_gate']=d.get('analysis_gate'); record['evidence_sources']=d.get('evidence_sources'); record.update(verdict=d['verdict'],score=d['overall_tamper_score'],confidence=d['confidence_score'],findings=[{'id':f['id'],'title':f['title'],'metric':f.get('metric_value'),'box':f.get('bounding_box')} for f in d['findings']],model=d.get('model_metadata'),boxes=boxes,qr=d['layer3'].get('details',{}).get('qr'),ocr=d['layer2'].get('details',{}).get('receipt_text'),payload_bytes=len(report.model_dump_json().encode()))
                if row.get('mask') and row.get('mask_valid'):
                    truth=cv2.imread(row['mask'],0)>0;pred=np.zeros(truth.shape,bool);h,w=truth.shape
                    # Diagnostic rectangle rasterization only. Neither version predicts a mask.
                    for b in boxes:
                        x,y,bw,bh=[int(b[k]) for k in ['x','y','width','height']]
                        pred[max(0,y):min(h,y+bh),max(0,x):min(w,x+bw)]=True
                    inter=int(np.count_nonzero(pred&truth));union=int(np.count_nonzero(pred|truth));den=int(pred.sum()+truth.sum())
                    record['box_proxy']={'intersection':inter,'union':union,'truth_pixels':int(truth.sum()),'predicted_pixels':int(pred.sum()),'iou':inter/union if union else None,'f1':2*inter/den if den else None}
            except Exception as ex:
                record.update(error=type(ex).__name__,message=str(ex),traceback=traceback.format_exc())
            record['seconds']=time.perf_counter()-t
            record['process_peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            stream.write(json.dumps(record)+'\n');stream.flush()
            if idx%15==0:print(version,idx+1,'/',len(jobs),record.get('error') or record.get('verdict'),flush=True)
    print(version,'complete',len(jobs),flush=True)

if __name__=='__main__':
    generate() if sys.argv[1]=='generate' else benchmark(sys.argv[1])
