import { RobustnessResearch } from "./RobustnessResearch";
import React, { useEffect, useState } from "react";
import { fetchModelEvaluation, fetchModelStatus, ModelStatus } from "../services/api";
export const EvaluationDashboard: React.FC<{onNavigateWorkbench:()=>void}> = ({onNavigateWorkbench}) => {
  const [status,setStatus]=useState<ModelStatus|null>(null);
  const [message,setMessage]=useState("Checking evaluation availability…");
  const [error,setError]=useState(false);
  const [attempt,setAttempt]=useState(0);
  useEffect(()=>{let active=true; Promise.all([fetchModelStatus(),fetchModelEvaluation()]).then(([s,e])=>{if(active){setStatus(s);setMessage(e.message || "Evaluation unavailable");setError(false);}}).catch(e=>{if(active){setError(true);setMessage(e.message);}});return()=>{active=false;};},[attempt]);
  return <main className="page-scroll"><div className="page-container space-y-6">
    <div><p className="eyebrow">Evaluation & Research</p><h1>Evidence before accuracy claims</h1><p className="text-slate-400 mt-2">Operational image review uses heuristics. No validated probability of fraud or authenticity is available.</p></div>
    <section className="panel" role={error?"alert":"status"}><h2>{error?"Evaluation service unavailable":"Representative evaluation unavailable"}</h2><p>{message}</p>{error&&<button onClick={()=>setAttempt(a=>a+1)}>Retry evaluation</button>}</section>
    <section className="panel"><h2>Model registry</h2><dl className="grid gap-3 sm:grid-cols-2"><div><dt>Active engine</dt><dd>{status?.active_model_id || "Checking…"}</dd></div><div><dt>Version</dt><dd>{status?.active_model_version || "Unavailable"}</dd></div><div><dt>Calibration</dt><dd>{status?.calibration_status || "Unavailable"}</dd></div><div><dt>Release gate</dt><dd className="text-amber-300">BLOCKED — representative validation required</dd></div></dl></section>
    <section className="panel"><h2>Dataset and operating point</h2><label>Dataset<select disabled aria-label="Evaluation dataset"><option>No eligible evaluation run</option></select></label><label className="block mt-4">Operating threshold<input disabled aria-label="Operating threshold" type="range" min="0" max="100" /></label><p>Threshold controls and ROC/PR charts require per-image labels and predictions from the same locked evaluation run. They cannot be reconstructed from hardcoded summary numbers.</p><div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">{["Sensitivity","Specificity","Precision","False-positive rate","ROC-AUC","PR-AUC","Calibration","Confusion matrix"].map(x=><div className="rounded border border-slate-700 p-3" key={x}><div>{x}</div><strong className="text-slate-400">Unavailable</strong></div>)}</div></section>
    <RobustnessResearch/>
    <section className="panel"><h2>Research assets and limitations</h2><p>The repository includes 27 synthetic examples and experimental fusion checkpoints. Shared templates, missing device/contributor/edit-session grouping, and ground-truth metadata used as features prevent these artifacts from establishing real-world accuracy. Historical external-corpus claims lack a reproducible authorized corpus in this checkout.</p><p>No new training was performed. Release requires authorized representative data, grouped splits, validation-only threshold selection, untouched test results, and calibration checks.</p></section>
    <button className="action-button" onClick={onNavigateWorkbench}>Return to workbench</button>
  </div></main>;
};
