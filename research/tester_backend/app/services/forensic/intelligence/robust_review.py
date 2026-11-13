"""Quality-aware review measurements. No trained authenticity classifier or probabilities.
Candidate score is experimental and never automatically replaces the released heuristic.
"""
from __future__ import annotations
import csv, io, math, os, re, shutil, subprocess
from collections import defaultdict
import cv2
import numpy as np
from PIL import Image

VERSION='quality-local-review-v1'

def acquisition_profile(raw: bytes, image: np.ndarray) -> dict:
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    with Image.open(io.BytesIO(raw)) as p:
        fmt=p.format; tables=getattr(p,'quantization',None)
    quant_mean=float(np.mean(tables[0])) if tables and 0 in tables else None
    sharp=float(cv2.Laplacian(gray,cv2.CV_32F).var())
    low=min(gray.shape)<300 or (sharp<12 and float(gray.std())>5)
    compression='STRONG_JPEG_QUANTIZATION' if quant_mean is not None and quant_mean>35 else 'JPEG_ENCODED' if fmt=='JPEG' else 'LOSSLESS_CONTAINER'
    # A JPEG or missing EXIF cannot identify WhatsApp, previous encodes, or recapture.
    reliability=.35 if low else .6 if compression=='STRONG_JPEG_QUANTIZATION' else 1.0
    return dict(estimated_profile='LOW_QUALITY' if low else 'UNKNOWN_PROVENANCE',encoding=fmt,width=image.shape[1],height=image.shape[0],jpeg_quantization_mean=round(quant_mean,3) if quant_mean else None,compression_condition=compression,laplacian_variance=round(sharp,3),pixel_cue_reliability=reliability,reliability_kind='engineering availability factor, not calibrated confidence',resizing='NOT_IDENTIFIABLE',recapture='NOT_IDENTIFIABLE',platform='NOT_IDENTIFIABLE',limitations=['Missing metadata is not manipulation evidence.','Encoding does not establish delivery platform or number of recompressions.'])

def ocr_available():
    return os.getenv('VERISIGHT_OCR_ENABLED','1')!='0' and bool(shutil.which(os.getenv('VERISIGHT_TESSERACT','tesseract')))

def recognize(image: np.ndarray) -> dict:
    binary=shutil.which(os.getenv('VERISIGHT_TESSERACT','tesseract'))
    base=dict(engine='Tesseract LSTM',language='eng',confidence_kind='OCR engine word score; not authenticity probability',tokens=[],lines=[],fields=[],template='UNKNOWN',limitations=['No bank, payee, reference or settlement verification.','English model only; inspect the source for recognition errors.'])
    if os.getenv('VERISIGHT_OCR_ENABLED','1')=='0' or not binary:
        return dict(base,status='UNAVAILABLE',reason='Optional Tesseract executable is not installed or OCR is disabled.')
    h,w=image.shape[:2];scale=min(1.,1800/max(h,w));scaled=cv2.resize(image,(round(w*scale),round(h*scale))) if scale<1 else image
    data=cv2.imencode('.png',scaled)[1].tobytes()
    try:
        proc=subprocess.run([binary,'stdin','stdout','-l','eng','--psm','11','tsv'],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8,env={**os.environ,'OMP_THREAD_LIMIT':'1'},check=False)
    except subprocess.TimeoutExpired:return dict(base,status='TIMEOUT',reason='OCR exceeded the 8-second budget; no recognized fields are inferred.')
    except OSError:return dict(base,status='UNAVAILABLE',reason='OCR executable could not start.')
    if proc.returncode:return dict(base,status='ERROR',reason='OCR failed; check local executable and eng language data.')
    grouped=defaultdict(list)
    for row in csv.DictReader(io.StringIO(proc.stdout.decode('utf-8',errors='replace')),delimiter='\t'):
        if row.get('level')!='5' or not row.get('text','').strip():continue
        try:conf=float(row['conf']);x,y,ww,hh=[int(round(float(row[k])/scale)) for k in ('left','top','width','height')]
        except (ValueError,KeyError):continue
        if conf<0 or ww<=0 or hh<=0:continue
        x=max(0,min(w-1,x));y=max(0,min(h-1,y));ww=min(ww,w-x);hh=min(hh,h-y)
        tok=dict(id=f'ocr-{len(base["tokens"])}',text=row['text'][:200],confidence=round(conf,2),readable=conf>=70,box=dict(x=x,y=y,width=ww,height=hh))
        base['tokens'].append(tok);grouped[(row['block_num'],row['par_num'],row['line_num'])].append(tok)
        if len(base['tokens'])>=400:break
    for tokens in grouped.values():
        tokens.sort(key=lambda t:t['box']['x']);box=dict(x=min(t['box']['x'] for t in tokens),y=min(t['box']['y'] for t in tokens));box['width']=max(t['box']['x']+t['box']['width'] for t in tokens)-box['x'];box['height']=max(t['box']['y']+t['box']['height'] for t in tokens)-box['y']
        line=dict(text=' '.join(t['text'] for t in tokens),confidence=min(t['confidence'] for t in tokens),token_ids=[t['id'] for t in tokens],box=box);base['lines'].append(line)
        if line['confidence']<70:continue
        value=line['text'];kind=None
        if re.search(r'\b(?:INR|Rs\.?|USD)\s*[\d,.]+|₹\s*[\d,.]+',value,re.I):kind='amount'
        elif re.search(r'[\w.\-]+@[\w.\-]+',value):kind='payment_address'
        elif re.search(r'\b(?:completed|successful|failed|pending)\b',value,re.I):kind='status'
        elif re.search(r'\b\d{1,2}:\d{2}\b',value):kind='time'
        elif re.search(r'\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b',value):kind='date'
        elif re.search(r'\b\d{10,18}\b',value):kind='reference_candidate'
        if kind:base['fields'].append(dict(kind=kind,**line,verified=False))
    # Label-guided candidates require a nearby readable line; never fill missing values.
    for label in base['lines']:
        if label['confidence']<70:continue
        match=re.fullmatch(r"(?:recipient|paid to|payee|reference|transaction id|amount|status|date|time)",label['text'].strip(),re.I)
        if not match:continue
        b=label['box'];candidates=[l for l in base['lines'] if l is not label and l['confidence']>=70 and 0<l['box']['y']-(b['y']+b['height'])<max(45,b['height']*3) and abs(l['box']['x']-b['x'])<40]
        if not candidates:continue
        value=min(candidates,key=lambda l:l['box']['y']);kind=label['text'].lower().replace(' ','_')+'_candidate'
        if not any(f['token_ids']==value['token_ids'] for f in base['fields']):base['fields'].append(dict(kind=kind,**value,verified=False))
    return dict(base,status='AVAILABLE' if any(t['readable'] for t in base['tokens']) else 'UNREADABLE',reason=None)

def _crop(a,box,pad=2):
    h,w=a.shape[:2];x,y,bw,bh=[box[k] for k in ('x','y','width','height')]
    return a[max(0,y-pad):min(h,y+bh+pad),max(0,x-pad):min(w,x+bw+pad)]

def local_measurements(image: np.ndarray, ocr:dict, quality:dict) -> tuple[list, list]:
    """Compare recognized words to nearby words of similar size/density/luminance.
    Edge-normalized JPEG residuals and two-scale high-pass energy share ONE family.
    Measurements are not likelihood ratios; robust z's are not probabilities.
    """
    h,w=image.shape[:2];factor=min(1.,1600/max(h,w));im=cv2.resize(image,(round(w*factor),round(h*factor))) if factor<1 else image
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    grad=cv2.magnitude(cv2.Sobel(gray,cv2.CV_32F,1,0),cv2.Sobel(gray,cv2.CV_32F,0,1))
    residuals=[]
    for q in [70,85,95]:
        jpg=cv2.imdecode(cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,q])[1],1)
        residuals.append(np.abs(gray-cv2.cvtColor(jpg,cv2.COLOR_BGR2GRAY)))
    high=[np.abs(gray-cv2.GaussianBlur(gray,(0,0),s)) for s in [.7,1.4]]
    records=[]
    for t in ocr['tokens']:
        if not t['readable'] or t['box']['height']<9 or len(t['text'])<3:continue
        box={k:round(v*factor) for k,v in t['box'].items()};patch=_crop(gray,box);edge=_crop(grad,box)
        if not patch.size:continue
        strength=float(edge.mean());density=float((edge>30).mean())
        if strength<4 or density<.04:continue
        vec=[float(_crop(m,box).mean())/(strength+1) for m in residuals+high]
        records.append(dict(token_id=t['id'],box=t['box'],text=t['text'],height=t['box']['height'],density=density,luminance=float(patch.mean()),features=vec))
    evidence=[]
    for r in records:
        peers=[p for p in records if p is not r and .8<=p['height']/r['height']<=1.25 and abs(p['density']-r['density'])<.2 and abs(p['luminance']-r['luminance'])<35]
        peers=sorted(peers,key=lambda p:abs(p['box']['y']-r['box']['y'])+abs(p['box']['x']-r['box']['x'])*.2)[:12]
        if len(peers)<5:
            r.update(status='INSUFFICIENT_PEERS',peer_count=len(peers));continue
        values=np.log(np.maximum(np.array([p['features'] for p in peers]),1e-5));v=np.log(np.maximum(r['features'],1e-5));median=np.median(values,axis=0);mad=np.maximum(.25,1.4826*np.median(np.abs(values-median),axis=0));z=np.abs(v-median)/mad
        # Require repeated quality/scale measurements, not an isolated brightest pixel.
        z_ela=float(np.median(z[:3]));z_noise=float(np.min(z[3:]));strength=min(z_ela,z_noise)
        r.update(status='MEASURED',peer_count=len(peers),ela_robust_z=round(z_ela,3),multiscale_robust_z=round(z_noise,3),joint_effect=round(strength,3))
        evidence.append(dict(id='local-'+r['token_id'],source_layer=1,family='local_rendering',value=round(strength,3),reliability=quality['pixel_cue_reliability'],confidence=None,availability='AVAILABLE',direction='POSSIBLE_MANIPULATION' if strength>=3 else 'CONSISTENCY',box=r['box'],explanation='Edge-normalized residuals compared to '+str(len(peers))+' nearby words with similar height, density and luminance. JPEG residual and high-pass energy are correlated; they count once.',peer_ids=[p['token_id'] for p in peers]))
    return records,evidence

def review_intelligence(raw,image,clone_boxes=None,qr_details=None):
    quality=acquisition_profile(raw,image);ocr=recognize(image);measurements,evidence=local_measurements(image,ocr,quality)
    if not evidence:evidence.append(dict(id='local-unavailable',source_layer=1,family='local_rendering',value=None,reliability=0,confidence=None,availability='UNAVAILABLE',direction='MISSING',box=None,explanation='No sufficiently readable, comparable text regions. Absence is not proof of consistency.'))
    for i,b in enumerate(clone_boxes or []):
        evidence.append(dict(id=f'copy-{i}',source_layer=1,family='geometric_repetition',value=b.details.get('inlier_ratio',0),reliability=.5,confidence=None,availability='AVAILABLE',direction='POSSIBLE_MANIPULATION',box=dict(x=b.x,y=b.y,width=b.width,height=b.height),explanation='Geometrically consistent repeated region. Repeated legitimate UI remains an alternative explanation.'))
    # Max within each correlated family, never add ELA/noise/sharpness as independent votes.
    local=max((max(0,e['value']-3)/5*100*e['reliability'] for e in evidence if e['family']=='local_rendering' and e['value'] is not None),default=0)
    repetition=max((e['value']*40*e['reliability'] for e in evidence if e['family']=='geometric_repetition'),default=0)
    score=round(min(100,max(local,repetition)),1)
    return dict(version=VERSION,acquisition=quality,ocr=ocr,semantic_checks=semantic_checks(ocr,qr_details or {}),measurements=measurements,evidence=evidence,candidate_score=score,candidate_score_definition='Experimental 0–100 review priority: max of quality-weighted, peer-normalized local residual excess and geometrically verified repetition. Higher means more review evidence. Not probability; not empirically calibrated.',candidate_state='REVIEW_REQUIRED' if score>0 else 'INCONCLUSIVE',promotion_status='BLOCKED_PENDING_INDEPENDENT_VALIDATION',layout_status='UNRECOGNIZED_TEMPLATE_NO_LAYOUT_PENALTY',classifier_confidence=None,limitations=['Original WhatsApp failure pair was not supplied.','Synthetic stress testing does not establish real-world accuracy.','No confidence calibration or payment verification.'])

def semantic_checks(ocr,qr_details):
    """Internal formatting/cross-source comparisons only; never issuer verification."""
    from datetime import datetime
    from decimal import Decimal, InvalidOperation
    from urllib.parse import urlparse, parse_qs
    checks=[]
    for f in ocr['fields']:
        if f['kind']!='date' or f['confidence']<90:continue
        value=f['text'].strip()
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
            try:datetime.strptime(value,'%Y-%m-%d');state='CONSISTENT_FORMAT'
            except ValueError:state='FORMAT_REVIEW'
            checks.append(dict(kind='visual_date_format',state=state,box=f['box'],explanation='OCR date checked as YYYY-MM-DD; OCR errors remain possible. Not a trusted transaction timestamp.'))
    amounts=[]
    for f in ocr['fields']:
        if f['kind']!='amount' or f['confidence']<90:continue
        m=re.fullmatch(r'(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d{1,2})?)',f['text'].strip(),re.I)
        if m:
            try:amounts.append((Decimal(m[1].replace(',','')),f['box']))
            except InvalidOperation:pass
    values=set(a for a,_ in amounts)
    for qr in qr_details.get('results',[]):
        parsed=urlparse(str(qr.get('payload','')))
        if parsed.scheme.lower()!='upi' or parsed.netloc.lower()!='pay':continue
        am=parse_qs(parsed.query).get('am',[])
        if len(am)!=1 or len(values)!=1:continue
        try:
            qr_amount=Decimal(am[0])
            if not qr_amount.is_finite():continue
        except InvalidOperation:continue
        amount=next(iter(values));checks.append(dict(kind='visual_QR_amount_comparison',state='CONSISTENT_CONTENT' if amount==qr_amount else 'CONTENT_REVIEW',box=amounts[0][1],explanation='High-scoring OCR amount '+str(amount)+' compared with QR payload amount '+str(qr_amount)+'. QR may serve a different purpose; neither source validates settlement or recipient identity.'))
    if not checks:checks.append(dict(kind='semantic_checks',state='UNAVAILABLE',box=None,explanation='No sufficiently reliable, comparable fields. Missing evidence is not consistency.'))
    return checks
