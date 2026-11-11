"""Read visible receipt text locally. OCR is not payment verification."""
import logging
import re
from threading import Lock
import numpy as np
from app.core.schemas import BoundingBox, ForensicFinding

_engine = None
_lock = Lock()
log = logging.getLogger(__name__)


def inspect_receipt_text(image):
    global _engine
    try:
        # Shared engines have mutable detection state; serialize their use.
        with _lock:
            if _engine is None:
                from rapidocr_onnxruntime import RapidOCR
                _engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
            results, _ = _engine(image)
        lines = []
        for box, text, confidence in results or []:
            if confidence < .85:
                continue
            points = np.asarray(box)
            x,y=points.min(axis=0); right,bottom=points.max(axis=0)
            lines.append({'text': text, 'confidence': float(confidence),
                          'bbox': [int(x),int(y),int(right-x),int(bottom-y)]})
        findings = receipt_text_findings(lines)
        return findings, {'status': 'AVAILABLE' if lines else 'NO_READABLE_TEXT',
                          'engine': 'RapidOCR PP-OCR ONNX', 'recognized_lines': len(lines),
                          'note': 'Text recognition is not an authenticity classifier or bank verification.'}
    except Exception:
        log.exception('Receipt text recognition unavailable')
        return [], {'status': 'UNAVAILABLE', 'engine': 'RapidOCR PP-OCR ONNX', 'recognized_lines': 0}


def receipt_text_findings(lines):
    findings=[]
    for line in lines:
        if line.get('confidence',0) < .85:
            continue
        text = re.sub(r'[^a-z0-9? ]', ' ', line['text'].lower())
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace(' ', '')
        # Whole-line assertions avoid flagging help text such as "Report fake payments".
        explicit = re.fullmatch(r'(?:fake(?:payment|transaction)(?:receipt|screenshot)?|(?:for)?demoonly|(?:syntheticdemonstration)?notarealtransaction)', text)
        failed = re.fullmatch(r'(?:payment|transaction|transfer)(?:failed|declined|cancelled|canceled|unsuccessful|pending)', text)
        if not (explicit or failed):
            continue
        x,y,w,h=line['bbox']
        box=BoundingBox(x=x,y=y,width=w,height=h,layer=3,anomaly_type='RECEIPT_TEXT_WARNING',label='Visible receipt statement')
        findings.append(ForensicFinding(id=f'f-receipt-text-{len(findings)+1}',layer=3,severity='HIGH',
            title='Receipt text contradicts successful-payment evidence',
            description=f'Visible text reads "{line["text"]}". This image should not be treated as proof of a completed real payment. OCR can make errors; inspect the highlighted text.',
            metric_name='Recognized receipt statement',metric_value=line['text'],bounding_box=box))
    return findings
