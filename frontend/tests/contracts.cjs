const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const req = createRequire(path.resolve(__dirname, '../package.json'));
const ts = req('typescript');
const React = req('react');
const {renderToStaticMarkup} = req('react-dom/server');
function load(file) {
 const code=ts.transpileModule(fs.readFileSync(path.resolve(__dirname,'../src',file),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true}}).outputText;
 const module={exports:{}};new Function('require','module','exports',code)(req,module,module.exports);return module.exports;
}
const {AnalysisGatePanel}=load('components/AnalysisGatePanel.tsx');
const render=gate=>renderToStaticMarkup(React.createElement(AnalysisGatePanel,{gate}));
assert.match(render(undefined), /Incomplete/);
assert.match(render(undefined), /No readiness decision/);
for(const state of ['PASS','WARNING','BLOCK']) {
 const html=render({state,processing_status:state==='BLOCK'?'INCOMPLETE':'COMPLETE',policy_version:'analysis-review-v1',reasons:[{code:'one',state,message:'Evidence needs review',evidence_ids:[]}],allowed_actions:{view_report:true,automated_approval:false},settlement_verified:false});
 assert.match(html,/do not approve a payment/);assert.match(html,/Evidence needs review/);
 assert.match(html,state==='PASS'?/Checks complete/:state==='WARNING'?/Review needed/:/Incomplete/);
}
const {verdictLabel}=load('services/verdictLabel.ts');
assert.equal(verdictLabel('INCONCLUSIVE'),'Likely accurate');
for(const verdict of ['REVIEW_REQUIRED','CORROBORATED_ANOMALIES','UNKNOWN']) assert.equal(verdictLabel(verdict),'Likely misleading');
for(const file of ['components/RiskDossierSidebar.tsx','components/ForensicReportModal.tsx']) {
 const source=fs.readFileSync(path.resolve(__dirname,'../src',file),'utf8');
 assert.ok(source.includes('synergy.region_overlap_found'));
 assert.ok(!source.includes('synergy.synergy_multiplier_applied'));
}
console.log('Frontend gate rendering, verdict and overlap contracts passed.');

const {ReviewLimitations}=load('components/ReviewLimitations.tsx');
const notice=verdict=>renderToStaticMarkup(React.createElement(ReviewLimitations,{verdict}));
for (const verdict of [undefined, 'INCONCLUSIVE', 'REVIEW_REQUIRED', 'CORROBORATED_ANOMALIES', 'UNKNOWN']) {
 const html=notice(verdict);
 assert.match(html,/Private development prototype/);
 assert.match(html,/authenticity not verified/);
 assert.match(html,/Do not release money or goods/);
 assert.match(html,/authorized bank or PSP transaction-status check/);
 if (verdict !== undefined) {
  assert.match(html,/not a probability of fraud/);
  assert.match(html,/Real-world detection accuracy is not established/);
 }
}
assert.match(notice(undefined),/screenshots you are authorized to use/);
assert.match(notice('INCONCLUSIVE'),/Edited screenshots can still receive this result/);
assert.doesNotMatch(notice('INCONCLUSIVE'),/Likely misleading/);
assert.match(notice('REVIEW_REQUIRED'),/Benign screenshots can also trigger/);
assert.doesNotMatch(notice('UNKNOWN'),/Likely accurate means/);
console.log('Submission and result uncertainty explanations passed.');

assert.match(notice(undefined),/20 MiB, 2 megapixels and 3200 pixels/);
assert.match(notice('INCONCLUSIVE'),/expire after 10 minutes/);
const {loadSimulationSource}=load('services/simulationSource.ts');
(async () => {
 const original = new Blob(['original'], {type:'image/png'});
 let calls=[];
 const fetcher=async(url,opts)=>{calls.push([url,opts]);return new Response(new Blob(['preview']));};
 assert.strictEqual(await loadSimulationSource(original,'/samples/a.png','/api/artifacts/expired',fetcher),original);
 assert.equal(calls.length,0,'Original bytes must avoid even attempting expired preview retrieval');
 await loadSimulationSource(null,'/samples/a.png','/api/artifacts/expired',fetcher);
 assert.equal(calls[0][0],'/samples/a.png');
 await loadSimulationSource(null,undefined,'/api/artifacts/token',fetcher);
 assert.equal(calls[1][0],'/api/artifacts/token');
 assert.equal(calls[1][1].credentials,'same-origin');
 assert.equal(await (await loadSimulationSource(null,undefined,'data:image/png;base64,YQ==')).text(),'a');
 await assert.rejects(loadSimulationSource(null,undefined,'/api/artifacts/expired',async()=>new Response('',{status:410})),/expired.*Re-run/);
 console.log('Simulation original-source priority and private preview retrieval passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

const {PersistenceNotice}=load('components/PersistenceNotice.tsx');
const savedNotice=status=>renderToStaticMarkup(React.createElement(PersistenceNotice,{status}));
assert.match(savedNotice('DISABLED'),/not saved to the database/);
assert.match(savedNotice('NOT_CONFIGURED'),/storage is not configured/);
assert.match(savedNotice('FAILED'),/Saving the analysis summary failed/);
assert.match(savedNotice('SAVED'),/summary saved to the private database/);
assert.match(savedNotice('SAVED'),/does not mean the screenshot or expiring previews were saved/);
assert.match(savedNotice('NOT_REQUESTED'),/did not request a case-history save/);
assert.match(savedNotice(undefined),/Do not assume this analysis was saved/);
assert.match(savedNotice('UNKNOWN'),/Do not assume this analysis was saved/);
console.log('Explicit persistence success, failure and unavailable messages passed.');

assert.match(savedNotice('DISABLED'),/saving is opt-in/);
assert.match(savedNotice('SAVED'),/7-day retention policy/);
assert.match(savedNotice('SAVED'),/while the server is running and the database is reachable/);
assert.match(notice(undefined),/summary saving is opt-in/);
assert.match(notice('INCONCLUSIVE'),/private preview files on this server/);
console.log('Opt-in persistence and bounded preview/retention explanations passed.');

const {isReportPreviewFailure}=load('services/previewFailure.ts');
const previewSources=['/api/artifacts/active','data:image/png;base64,YQ=='];
assert.equal(isReportPreviewFailure('IMG','/api/artifacts/active',previewSources),true);
assert.equal(isReportPreviewFailure('IMG','/api/artifacts/previous-report',previewSources),false);
assert.equal(isReportPreviewFailure('IMG','/logo.png',previewSources),false);
assert.equal(isReportPreviewFailure('VIDEO','/api/artifacts/active',previewSources),false);
assert.equal(isReportPreviewFailure('IMG',null,previewSources),false);
const {PreviewUnavailable}=load('components/PreviewUnavailable.tsx');
const previewFailure=renderToStaticMarkup(React.createElement(PreviewUnavailable));
assert.match(previewFailure,/role="alert"/);
assert.match(previewFailure,/Preview expired or unavailable; run analysis again/);
console.log('Private preview failure filtering and accessible recovery notice passed.');
