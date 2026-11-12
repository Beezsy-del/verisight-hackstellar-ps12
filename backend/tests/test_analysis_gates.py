import pytest
from app.evaluation.gates import evaluate_analysis_gate, evaluate_model_release, require_model_release, MODEL_RELEASE_CONDITIONS
from app.core.schemas import ForensicFinding, AnalysisGate, BoundingBox

def gate(**kw):
    return evaluate_analysis_gate(**({'score':0,'verdict':'INCONCLUSIVE','findings':[], 'ocr_status':'AVAILABLE','image_width':100,'image_height':100}|kw))

def finding(**kw):
    return ForensicFinding(**({'id':'edit','layer':1,'severity':'HIGH','title':'Region variation','description':'Measured region variation','metric_name':'variation','metric_value':'15'}|kw))

def test_complete_is_not_payment_approval():
    r=gate();assert r.state=='PASS';assert not r.settlement_verified;assert not r.allowed_actions['automated_approval']

@pytest.mark.parametrize('status',['UNAVAILABLE','NO_READABLE_TEXT',None,'unexpected'])
def test_missing_text_blocks_without_fraud_claim(status):
    r=gate(ocr_status=status);assert r.state=='BLOCK';assert r.processing_status=='INCOMPLETE';assert r.reasons[0].code=='OCR_INCOMPLETE'

@pytest.mark.parametrize('score',[float('nan'),float('inf'),-1,101])
def test_bad_scores_fail_closed(score):
    assert gate(score=score).processing_status=='FAILED'

def test_real_evidence_warns():
    r=gate(score=35,verdict='REVIEW_REQUIRED',findings=[finding()]);assert r.state=='WARNING';assert r.reasons[0].evidence_ids==['edit']

def test_conflicting_high_evidence_blocks():
    assert gate(findings=[finding()]).state=='BLOCK'

def test_no_support_blocks_review():
    assert gate(verdict='REVIEW_REQUIRED').state=='BLOCK'

def test_region_outside_image_blocks():
    b=BoundingBox(x=90,y=0,width=30,height=5,label='bad',layer=1,anomaly_type='test')
    assert gate(verdict='REVIEW_REQUIRED',findings=[finding(bounding_box=b)]).processing_status=='FAILED'

def test_default_gate_blocks():
    assert AnalysisGate().state=='BLOCK'

@pytest.mark.parametrize('condition',MODEL_RELEASE_CONDITIONS)
def test_every_model_release_condition_enforced(condition):
    evidence={k:True for k in MODEL_RELEASE_CONDITIONS};evidence[condition]=False
    with pytest.raises(RuntimeError):require_model_release(evidence)

def test_model_gate_no_truthy_shortcuts():
    assert evaluate_model_release({k:'true' for k in MODEL_RELEASE_CONDITIONS})['state']=='BLOCK'
    assert require_model_release({k:True for k in MODEL_RELEASE_CONDITIONS})['state']=='PASS'
