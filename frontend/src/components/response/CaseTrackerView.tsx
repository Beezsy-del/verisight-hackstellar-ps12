import React, { useState, useEffect } from "react";
import {
  Clock,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Edit2,
  Save,
  Plus,
  FileText,
  Calendar,
  Hash,
  ArrowRight,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";
import { CaseRecord, CaseStatus } from "../../types/response";
import { fetchCases, saveCaseRecord } from "../../services/api";

const STATUS_OPTIONS: Array<{ value: CaseStatus; label: string; color: string }> = [
  { value: "DRAFTING", label: "Drafting", color: "text-slate-300 border-slate-700 bg-slate-900" },
  { value: "READY_FOR_REVIEW", label: "Ready for Review", color: "text-sky-300 border-sky-800 bg-sky-950" },
  { value: "READY_TO_SUBMIT", label: "Ready to Submit", color: "text-amber-300 border-amber-800 bg-amber-950" },
  { value: "SUBMITTED_BY_USER", label: "Submitted by User", color: "text-blue-300 border-blue-800 bg-blue-950" },
  { value: "ACKNOWLEDGEMENT_RECEIVED", label: "Acknowledgement Received", color: "text-emerald-300 border-emerald-800 bg-emerald-950" },
  { value: "FOLLOW_UP_REQUIRED", label: "Follow-up Required", color: "text-rose-300 border-rose-800 bg-rose-950" },
  { value: "RESOLVED", label: "Resolved / Refunded", color: "text-emerald-200 border-emerald-700 bg-emerald-900" },
  { value: "CLOSED", label: "Closed", color: "text-slate-400 border-slate-800 bg-slate-950" },
];

export const CaseTrackerView: React.FC = () => {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseRecord | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Editable fields for active case
  const [editStatus, setEditStatus] = useState<CaseStatus>("DRAFTING");
  const [editAckNo, setEditAckNo] = useState("");
  const [editSubmissionDate, setEditSubmissionDate] = useState("");
  const [editFollowUpDate, setEditFollowUpDate] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [newTimelineTitle, setNewTimelineTitle] = useState("");
  const [newTimelineDesc, setNewTimelineDesc] = useState("");

  useEffect(() => {
    void loadCases();
  }, []);

  const loadCases = async () => {
    setIsLoading(true);
    try {
      const data = await fetchCases();
      setCases(data);
      if (data.length > 0 && !selectedCase) {
        selectCase(data[0]);
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to load cases");
    } finally {
      setIsLoading(false);
    }
  };

  const selectCase = (c: CaseRecord) => {
    setSelectedCase(c);
    setEditStatus(c.status);
    setEditAckNo(c.acknowledgement_number || "");
    setEditSubmissionDate(c.submission_date || "");
    setEditFollowUpDate(c.follow_up_date || "");
    setEditNotes(c.notes || "");
  };

  const handleSaveCaseChanges = async () => {
    if (!selectedCase) return;
    setIsSaving(true);
    try {
      const updated: CaseRecord = {
        ...selectedCase,
        status: editStatus,
        acknowledgement_number: editAckNo.trim() || undefined,
        submission_date: editSubmissionDate || undefined,
        follow_up_date: editFollowUpDate || undefined,
        notes: editNotes.trim() || undefined,
        updated_at: new Date().toISOString(),
      };

      // Add a timeline event if status changed or acknowledgement was added
      if (editStatus !== selectedCase.status) {
        updated.timeline.push({
          timestamp: new Date().toISOString(),
          title: `Status Changed to ${editStatus.replace(/_/g, " ")}`,
          description: `Case updated by user.`,
          actor: "USER",
        });
      }
      if (editAckNo && editAckNo !== selectedCase.acknowledgement_number) {
        updated.timeline.push({
          timestamp: new Date().toISOString(),
          title: "Official Acknowledgment Number Recorded",
          description: `Acknowledgment #${editAckNo} registered.`,
          actor: "USER",
        });
      }

      const res = await saveCaseRecord(updated);
      setSelectedCase(res);
      setCases((prev) => prev.map((c) => (c.case_id === res.case_id ? res : c)));
      toast.success("Case updates saved successfully.");
    } catch (err: any) {
      toast.error(err.message || "Failed to save case");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTimelineEvent = async () => {
    if (!selectedCase || !newTimelineTitle.trim()) return;
    try {
      const updated: CaseRecord = {
        ...selectedCase,
        timeline: [
          ...selectedCase.timeline,
          {
            timestamp: new Date().toISOString(),
            title: newTimelineTitle.trim(),
            description: newTimelineDesc.trim() || "Follow-up logged.",
            actor: "USER",
          },
        ],
        updated_at: new Date().toISOString(),
      };
      const res = await saveCaseRecord(updated);
      setSelectedCase(res);
      setCases((prev) => prev.map((c) => (c.case_id === res.case_id ? res : c)));
      setNewTimelineTitle("");
      setNewTimelineDesc("");
      toast.success("Timeline event added.");
    } catch (err: any) {
      toast.error(err.message || "Failed to add event");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl backdrop-blur-md">
        <div>
          <h2 className="text-base font-bold text-white font-sans flex items-center gap-2">
            <Clock className="h-5 w-5 text-sky-400" />
            Official Incident Response & Complaint Tracking
          </h2>
          <p className="mt-0.5 text-xs text-slate-400 font-sans">
            Track official submission acknowledgements, record 1930 / NCRP reference numbers, and manage statutory follow-up deadlines.
          </p>
        </div>
      </div>

      {/* Grid: Case List vs Detailed Case View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Case List (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
            <span>SAVED CASES ({cases.length})</span>
            <button
              onClick={() => loadCases()}
              className="text-sky-400 hover:text-sky-300 flex items-center gap-1"
            >
              <RotateCcw className="h-3 w-3" />
              <span>Refresh</span>
            </button>
          </div>

          {cases.map((c) => {
            const isSelected = selectedCase?.case_id === c.case_id;

            return (
              <div
                key={c.case_id}
                onClick={() => selectCase(c)}
                className={`cursor-pointer rounded-xl border p-3.5 transition-all ${
                  isSelected
                    ? "border-sky-500/50 bg-[#0E172E] shadow-lg ring-1 ring-sky-500/30"
                    : "border-white/[0.08] bg-[#0A0E1A]/80 hover:border-white/20"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-[10px] text-slate-400">
                    {c.case_id}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.2 font-mono text-[9px] font-bold ${
                      c.status === "ACKNOWLEDGEMENT_RECEIVED"
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800/40"
                        : c.status === "READY_TO_SUBMIT"
                        ? "bg-amber-950 text-amber-300 border border-amber-800/40"
                        : "bg-sky-950 text-sky-300 border border-sky-800/40"
                    }`}
                  >
                    {c.status.replace(/_/g, " ")}
                  </span>
                </div>

                <h4 className="text-xs font-semibold text-white truncate">
                  {c.title}
                </h4>

                <div className="mt-2 flex items-center justify-between font-mono text-[10px] text-slate-500">
                  <span>
                    Loss: {c.financial_loss > 0 ? `₹${c.financial_loss.toLocaleString()}` : "Zero loss"}
                  </span>
                  <span>{c.updated_at.slice(0, 10)}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Detailed Case Manager & Timeline (8 cols) */}
        <div className="lg:col-span-8">
          {selectedCase ? (
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/95 p-6 shadow-2xl backdrop-blur-md space-y-6">
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] pb-4">
                <div>
                  <span className="font-mono text-[10px] text-sky-400">
                    ACTIVE INCIDENT TRACKER • {selectedCase.case_id}
                  </span>
                  <h3 className="text-base font-bold text-white font-sans mt-0.5">
                    {selectedCase.title}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={handleSaveCaseChanges}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 rounded-lg bg-sky-600 px-4 py-2 font-mono text-xs font-semibold text-white hover:bg-sky-500 shadow-md shadow-sky-600/30 active:scale-[0.98]"
                >
                  <Save className="h-3.5 w-3.5" />
                  <span>{isSaving ? "Saving..." : "Save Case Progress"}</span>
                </button>
              </div>

              {/* Status & Official Acknowledgement Form */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 rounded-xl border border-white/[0.06] bg-[#0C1222] p-4 text-xs font-sans">
                {/* Status Selector */}
                <div>
                  <label className="block font-mono text-[10px] uppercase text-slate-400 mb-1">
                    CURRENT TRACKING STATUS
                  </label>
                  <select
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value as CaseStatus)}
                    className="w-full rounded-lg border border-white/10 bg-[#060911] px-3 py-2 text-xs font-mono text-slate-200 focus:border-sky-500 focus:outline-none"
                  >
                    {STATUS_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Acknowledgement Number */}
                <div>
                  <label className="block font-mono text-[10px] uppercase text-slate-400 mb-1">
                    OFFICIAL ACKNOWLEDGEMENT / TICKET NO.
                  </label>
                  <input
                    type="text"
                    value={editAckNo}
                    onChange={(e) => setEditAckNo(e.target.value)}
                    placeholder="e.g. NCRP Ref # 202611... or Bank Docket #"
                    className="w-full rounded-lg border border-white/10 bg-[#060911] px-3 py-2 text-xs font-mono text-slate-200 focus:border-sky-500 focus:outline-none"
                  />
                </div>

                {/* Submission Date */}
                <div>
                  <label className="block font-mono text-[10px] uppercase text-slate-400 mb-1">
                    SUBMISSION DATE
                  </label>
                  <input
                    type="date"
                    value={editSubmissionDate}
                    onChange={(e) => setEditSubmissionDate(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-[#060911] px-3 py-2 text-xs font-mono text-slate-200 focus:border-sky-500 focus:outline-none"
                  />
                </div>

                {/* Follow-up Reminder Date */}
                <div>
                  <label className="block font-mono text-[10px] uppercase text-slate-400 mb-1">
                    NEXT STATUTORY FOLLOW-UP DATE
                  </label>
                  <input
                    type="date"
                    value={editFollowUpDate}
                    onChange={(e) => setEditFollowUpDate(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-[#060911] px-3 py-2 text-xs font-mono text-slate-200 focus:border-sky-500 focus:outline-none"
                  />
                </div>

                {/* Notes */}
                <div className="md:col-span-2">
                  <label className="block font-mono text-[10px] uppercase text-slate-400 mb-1">
                    INVESTIGATION NOTES & POLICE CORRESPONDENCE
                  </label>
                  <textarea
                    value={editNotes}
                    onChange={(e) => setEditNotes(e.target.value)}
                    placeholder="Record IO officer details, police station GD number, or bank chargeback communication..."
                    rows={2}
                    className="w-full rounded-lg border border-white/10 bg-[#060911] p-2 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Portal Handoff Assistant */}
              <div className="rounded-xl border border-sky-500/30 bg-sky-950/20 p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-sky-300">
                    Official Portal Submission Handoff
                  </span>
                  <a
                    href="https://cybercrime.gov.in"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 font-mono text-xs text-sky-400 hover:underline"
                  >
                    <span>Open cybercrime.gov.in</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  To complete official reporting, visit the government portal, paste your generated complaint, upload the VeriSight forensic dossier, and enter your issued acknowledgement number above.
                </p>
              </div>

              {/* Timeline of Events */}
              <div className="space-y-3 pt-2">
                <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Case Activity Timeline
                </h4>

                <div className="space-y-2.5">
                  {selectedCase.timeline.map((event, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 rounded-xl border border-white/[0.05] bg-[#070B16] p-3 text-xs font-sans"
                    >
                      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-950 text-sky-400 border border-sky-800 text-[10px] font-mono mt-0.5">
                        {idx + 1}
                      </div>
                      <div className="space-y-0.5 flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-100">
                            {event.title}
                          </span>
                          <span className="font-mono text-[10px] text-slate-500">
                            {event.timestamp.slice(0, 16).replace("T", " ")}
                          </span>
                        </div>
                        <p className="text-slate-400 text-[11px] leading-relaxed">
                          {event.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Add Timeline Event Quick Form */}
                <div className="rounded-xl border border-white/[0.06] bg-[#070B16] p-3 space-y-2">
                  <span className="font-mono text-[10px] text-slate-400 uppercase">
                    Log New Case Follow-Up Event
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <input
                      type="text"
                      value={newTimelineTitle}
                      onChange={(e) => setNewTimelineTitle(e.target.value)}
                      placeholder="Event Title (e.g. Visited Cyber Cell)"
                      className="rounded-lg border border-white/10 bg-[#060911] px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
                    />
                    <input
                      type="text"
                      value={newTimelineDesc}
                      onChange={(e) => setNewTimelineDesc(e.target.value)}
                      placeholder="Event Notes / Officer Name"
                      className="rounded-lg border border-white/10 bg-[#060911] px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={handleAddTimelineEvent}
                      disabled={!newTimelineTitle.trim()}
                      className="rounded-lg bg-white/10 px-3 py-1 font-mono text-[11px] text-slate-200 hover:bg-white/20 active:scale-[0.98] disabled:opacity-40"
                    >
                      Add Event
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex h-96 items-center justify-center rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 text-slate-500 font-mono text-xs">
              Select a case to inspect timeline and track official progress.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
