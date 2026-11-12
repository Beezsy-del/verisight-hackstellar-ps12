import React from "react";
import { AnalysisGate } from "../types/forensic";

export function AnalysisGatePanel({ gate }: { gate?: AnalysisGate }) {
  const state = gate?.state ?? "BLOCK";
  const ready = gate?.processing_status === "COMPLETE";
  return (
    <section aria-label="Analysis readiness" className="rounded-xl border border-slate-600/50 bg-slate-900/50 p-3 text-xs">
      <div className="flex items-center justify-between gap-2 font-semibold">
        <span>Analysis readiness</span>
        <span className={state === "BLOCK" ? "text-rose-300" : state === "WARNING" ? "text-amber-300" : "text-sky-300"}>
          {state === "PASS" ? "Checks complete" : state === "WARNING" ? "Review needed" : "Incomplete — do not rely on this result"}
        </span>
      </div>
      <p className="mt-2 text-slate-300">{ready ? "Processing completed. Findings still require review." : "Required analysis is incomplete or unavailable."}</p>
      <ul className="mt-2 space-y-1 text-slate-400">
        {gate?.reasons.map(reason => <li key={reason.code}>{reason.message}</li>) ?? <li>No readiness decision was returned.</li>}
      </ul>
      <p className="mt-2 text-slate-400">These checks do not approve a payment or verify settlement.</p>
    </section>
  );
}
