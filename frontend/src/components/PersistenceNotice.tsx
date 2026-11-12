import React from "react";
import { PersistenceStatus } from "../types/forensic";

export function PersistenceNotice({ status }: { status?: PersistenceStatus }) {
  const messages: Record<PersistenceStatus, string> = {
    DISABLED: "Case history is disabled (saving is opt-in). This analysis summary was not saved to the database.",
    NOT_CONFIGURED: "Case history is unavailable because storage is not configured. This analysis summary was not saved to the database.",
    FAILED: "Saving the analysis summary failed. Do not assume it is in case history; keep a copy of this report if needed.",
    SAVED: "Analysis summary saved to the private database. This does not mean the screenshot or expiring previews were saved. This summary is tagged for a 7-day retention policy; cleanup is attempted while the server is running and the database is reachable, not guaranteed by a cloud schedule.",
    NOT_REQUESTED: "This analysis did not request a case-history save. Do not assume this result is stored in the database.",
  };
  return (
    <p role="status" className="rounded-lg border border-slate-600/40 p-3 text-xs text-slate-300 print:text-black print:border-gray-400">
      <strong>Case history: </strong>
      {status && messages[status] ? messages[status] : "Saving status is unavailable. Do not assume this analysis was saved to the database."}
    </p>
  );
}
