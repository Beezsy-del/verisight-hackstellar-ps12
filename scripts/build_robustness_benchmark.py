"""Original synthetic fixtures authored for this project; CC0-1.0. Never real payment data.
Not a representative forensic dataset. No third-party images or fonts required.
"""
import hashlib, io, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/datasets/robustness'; OUT.mkdir(parents=True,exist_ok=True)
rows=[]
def text(im,s,xy,size=.7,color=(45,45,45)):
 cv2.putText(im,s,xy,cv2.FONT_HERSHEY_SIMPLEX,size,color,1,cv2.LINE_AA)
def encode(im,ext,quality=85):
 return cv2.imencode(ext,im,[cv2.IMWRITE_JPEG_QUALITY,quality])[1].tobytes()
def transform(im,condition):
 if condition=='original': return encode(im,'.png'),'.png'
 if condition=='jpeg75': return encode(im,'.jpg',75),'.jpg'
 if condition=='resize_jpeg': return encode(cv2.resize(im,(360,600),interpolation=cv2.INTER_AREA),'.jpg',65),'.jpg'
 if condition=='multi_stage':
  a=cv2.imdecode(np.frombuffer(encode(im,'.jpg',75),np.uint8),1);a=cv2.resize(a,(420,700),interpolation=cv2.INTER_AREA)
  a=cv2.imdecode(np.frombuffer(encode(a,'.jpg',60),np.uint8),1)
  return encode(cv2.resize(a,(360,600)),'.jpg',70),'.jpg'
 if condition=='recapture_proxy':
  a=cv2.resize(im,(432,720),interpolation=cv2.INTER_LINEAR);a=cv2.resize(a,(540,900),interpolation=cv2.INTER_LINEAR)
  return encode(a,'.png'),'.png'
 return encode(cv2.GaussianBlur(cv2.resize(im,(216,360)),(3,3),.8),'.jpg',40),'.jpg'
for i in range(10):
 template=i//2; group=f'original-{i:02d}'; partition='locked_synthetic_test' if template>=3 else 'development'
 rng=np.random.default_rng(31000+i); im=np.full((900,540,3),246,np.uint8)
 # Different templates vary layout, color and field placement, not class.
 x=40+template*4; y=220+template*12
 cv2.rectangle(im,(20,90),(520,830),(255,255,255),-1)
 text(im,'SYNTHETIC SOFTWARE TEST - NO PAYMENT',(25,35),.43)
 text(im,f'Demo Wallet {template+1}',(x,140),.85)
 text(im,'Receipt details',(x,180),.65)
 fields=[('Amount',f'INR {1250+i*137}.00'),('Recipient',f'DEMO STORE {i+1}'),('Date','2026-01-14'),('Time','14:35'),('Reference',str(123456789000+i)),('Status','Completed')]
 for k,(label,val) in enumerate(fields):
  yy=y+k*74;text(im,label,(x,yy),.55);text(im,val,(x,yy+28),.7)
 text(im,'NOT A REAL TRANSACTION',(x,800),.6)
 # Natural repeated UI symbols and mixed fonts exist in BOTH classes.
 for yy in [180,400,620]:cv2.circle(im,(490,yy),9,(180,180,180),1)
 edited=im.copy();mask=np.zeros(im.shape[:2],np.uint8)
 edit_type=['amount_replacement','recipient_replacement','timestamp_replacement','copy_move','removal'][i%5]
 k={'amount_replacement':0,'recipient_replacement':1,'timestamp_replacement':3,'copy_move':1,'removal':4}[edit_type]; yy=y+k*74
 mask[yy+7:yy+36,x-4:470]=255
 if edit_type=='copy_move': edited[yy+7:yy+36,x-4:470]=im[y+7:y+36,x-4:470]
 else:
  cv2.rectangle(edited,(x-4,yy+7),(470,yy+36),(252,252,252),-1)
  if edit_type!='removal':
   replacement={'amount_replacement':'INR 9850.00','recipient_replacement':'DEMO OTHER STORE','timestamp_replacement':'19:57'}[edit_type]
   text(edited,replacement,(x,yy+31),.76,(25,25,25))
 # Every source and its edits/transforms remain in one partition.
 for label,img in [(0,im),(1,edited)]:
  for condition in ['original','jpeg75','resize_jpeg','multi_stage','recapture_proxy','low_quality']:
   data,ext=transform(img,condition);sid=f'{group}-{label}-{condition}';file=OUT/(sid+ext);file.write_bytes(data)
   with Image.open(io.BytesIO(data)) as p: dims=list(p.size)
   maskfile=OUT/(sid+'-mask.png'); m=cv2.resize(mask if label else np.zeros_like(mask),tuple(dims),interpolation=cv2.INTER_NEAREST);cv2.imwrite(str(maskfile),m)
   rows.append(dict(sample_id=sid,path=str(file.relative_to(ROOT)),mask_path=str(maskfile.relative_to(ROOT)),label=label,label_provenance='Generator records edit operation; mask is edited rectangle, not a pixel-precise semantic truth',source_type='synthetic',license='CC0-1.0',authorized_use=True,source_group_id=group,template=f'demo-{template}',device='synthetic-renderer',contributor='project-generator-v1',editing_session=group,partition=partition,delivery_path=condition,known_transformations=[condition],manipulation_category=edit_type if label else 'none',sha256=hashlib.sha256(data).hexdigest(),dimensions=dims,format=ext[1:],pair_id=group+'-'+condition))
payload=dict(version='robustness-synthetic-v1',purpose='Software stress benchmark only; not real-world accuracy or training authorization',license='CC0-1.0 for generated assets and this generator',seed=31000,samples=rows)
(OUT/'manifest.json').write_text(json.dumps(payload,indent=2));print(len(rows),'images; 10 source groups; 60 matched pairs; shared synthetic generator; no training')
