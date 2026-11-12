import React from "react";

export function PreviewUnavailable() {
  return <p role="alert" className="shrink-0 border-b border-amber-500/40 bg-amber-950/80 px-3 py-2 text-sm text-amber-100">
    Preview expired or unavailable; run analysis again. Do not rely on a missing image to interpret the findings.
  </p>;
}
