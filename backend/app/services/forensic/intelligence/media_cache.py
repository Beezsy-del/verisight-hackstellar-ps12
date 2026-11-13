"""Bounded ephemeral local-only media cache. No disk storage or public upload listing."""
import base64,secrets,threading,time
from collections import OrderedDict
from fastapi import HTTPException,Request
from fastapi.responses import Response
import os
LOCK=threading.Lock();CACHE=OrderedDict();MAX_BYTES=64*1024*1024;TTL=600

def _prune(now):
 for k,(expiry,_,_) in list(CACHE.items()):
  if expiry<=now:del CACHE[k]

def compact_report(report,request:Request):
 if request.query_params.get('media')!='urls':return report
 if os.getenv('VERCEL') or request.url.hostname not in {'localhost','127.0.0.1','testserver'}:
  raise HTTPException(503,'URL media transport is local-only; configure private authenticated storage for hosted use.')
 d=report.model_copy(deep=True); urls={};pending=[]
 for key,parent,field in [('original',d,'original_image_b64'),('ela',d.layer1,'ela_b64'),('wavelet',d.layer1,'wavelet_noise_b64'),('clone',d.layer1,'clone_b64')]:
  value=getattr(parent,field);header,encoded=value.split(',',1);mime=header.split(':',1)[1].split(';')[0];raw=base64.b64decode(encoded,validate=True)
  token=secrets.token_urlsafe(24);pending.append((token,(time.monotonic()+TTL,mime,raw)));urls[key]='/api/review-media/'+token;setattr(parent,field,'')
 size=sum(len(v[2]) for _,v in pending)
 if size>MAX_BYTES:raise HTTPException(413,'Rendered evidence exceeds the local media memory budget.')
 with LOCK:
  _prune(time.monotonic());total=sum(len(v[2]) for v in CACHE.values())
  while CACHE and total+size>MAX_BYTES:
   _,v=CACHE.popitem(last=False);total-=len(v[2])
  CACHE.update(pending)
 d.media_urls=urls;return d

def get_media(token,request:Request):
 if os.getenv('VERCEL') or request.url.hostname not in {'localhost','127.0.0.1','testserver'}:raise HTTPException(503,'Local media only.')
 with LOCK:
  _prune(time.monotonic());item=CACHE.get(token)
 if item is None:raise HTTPException(410,'Evidence preview expired. Analyze the image again.')
 return Response(item[2],media_type=item[1],headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'})

def store_extra_media(data_url,request):
    if request.query_params.get('media')!='urls':return data_url
    if os.getenv('VERCEL') or request.url.hostname not in {'localhost','127.0.0.1','testserver'}:raise HTTPException(503,'Local media only.')
    header,encoded=data_url.split(',',1);mime=header.split(':',1)[1].split(';')[0];raw=base64.b64decode(encoded,validate=True)
    if len(raw)>MAX_BYTES:raise HTTPException(413,'Preview exceeds memory budget.')
    token=secrets.token_urlsafe(24)
    with LOCK:
        _prune(time.monotonic());total=sum(len(v[2]) for v in CACHE.values())
        while CACHE and total+len(raw)>MAX_BYTES:
            _,v=CACHE.popitem(last=False);total-=len(v[2])
        CACHE[token]=(time.monotonic()+TTL,mime,raw)
    return '/api/review-media/'+token
