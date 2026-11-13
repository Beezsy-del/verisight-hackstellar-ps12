import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Mic,
  FileText,
  Search,
  Clock,
  Fingerprint,
  ArrowLeft,
  X,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Layers,
} from "lucide-react";
import { toast } from "sonner";
import {
  ExtractedIncidentDetails,
  AttachedForensicContext,
  CaseRecord,
  IncidentCategory,
} from "../../types/response";
import { fetchCases } from "../../services/api";
import { IncidentCentre } from "./IncidentCentre";
import { VoiceReportingAssistant } from "./VoiceReportingAssistant";
import { ComplaintBuilder } from "./ComplaintBuilder";
import { EvidenceDossierView } from "./EvidenceDossierView";
import { ReportingDirectoryView } from "./ReportingDirectoryView";
import { CaseTrackerView } from "./CaseTrackerView";

export type ResponseTab =
  | "incident-centre"
  | "voice"
  | "builder"
  | "dossier"
  | "directory"
  | "tracking";

interface ResponseModuleProps {
  onNavigateWorkbench: () => void;
  attachedForensicContext?: AttachedForensicContext | null;
  onClearForensicContext?: () => void;
  initialTab?: ResponseTab;
}

export const ResponseModule: React.FC<ResponseModuleProps> = ({
  onNavigateWorkbench,
  attachedForensicContext,
  onClearForensicContext,
  initialTab = "incident-centre",
}) => {
  const [activeTab, setActiveTab] = useState<ResponseTab>(() => {
    // If coming from Forensic Workbench with attached evidence, default to Voice Assistant or Dossier
    if (attachedForensicContext) return "voice";
    return initialTab;
  });

  const [extractedDetails, setExtractedDetails] = useState<ExtractedIncidentDetails | null>(null);
  const [initialCategoryHint, setInitialCategoryHint] = useState<string | undefined>(undefined);
  const [cases, setCases] = useState<CaseRecord[]>([]);

  useEffect(() => {
    void loadCases();
  }, []);

  const loadCases = async () => {
    try {
      const data = await fetchCases();
      setCases(data);
    } catch (err) { toast.error(err instanceof Error ? err.message : "Case notes unavailable"); }
  };

  const handleNavigateTab = (tab: string, category?: IncidentCategory) => {
    if (category) {
      setInitialCategoryHint(category);
    }
    setActiveTab(tab as ResponseTab);
  };

  const handleProceedToBuilder = (details: ExtractedIncidentDetails) => {
    setExtractedDetails(details);
    setActiveTab("builder");
    toast.success("Incident facts transferred to formal complaint builder");
  };

  const handleCaseSaved = (caseId: string) => {
    void loadCases();
    setActiveTab("tracking");
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden bg-[#060911] text-slate-100">
      {/* 1. Context-Aware Forensic Workbench Banner (if arrived from workbench) */}
      {attachedForensicContext && (
        <div className="border-b border-sky-500/30 bg-gradient-to-r from-sky-950/70 via-[#0a1529]/80 to-[#070b14]/80 px-4 py-2.5 backdrop-blur-md shrink-0">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-sky-400/40 bg-sky-500/20 text-sky-400">
                <Fingerprint className="h-4 w-4" />
              </div>
              <div className="text-xs">
                <span className="font-mono text-[10px] uppercase font-bold text-sky-300">
                  Forensic Workbench Evidence Linked:
                </span>{" "}
                <strong className="text-white font-mono">{attachedForensicContext.filename}</strong>
                <span className="text-slate-400 font-mono ml-2">
                  (SHA-256: {attachedForensicContext.file_sha256.slice(0, 10)}... • Score:{" "}
                  {attachedForensicContext.overall_tamper_score.toFixed(1)}/100 • {attachedForensicContext.verdict})
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 font-mono text-xs">
              <button
                type="button"
                onClick={onNavigateWorkbench}
                className="flex items-center gap-1.5 rounded-lg border border-sky-500/40 bg-sky-500/15 px-3 py-1 text-sky-300 hover:bg-sky-500/25 active:scale-[0.98]"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Return to Forensic Workbench</span>
              </button>

              {onClearForensicContext && (
                <button
                  type="button"
                  onClick={onClearForensicContext}
                  className="rounded-lg p-1 text-slate-400 hover:text-slate-200 hover:bg-white/5"
                  title="Detach workbench evidence"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 2. Response Module Navigation Sub-Header */}
      <div className="border-b border-white/[0.07] bg-[#090D16]/90 px-4 py-3 shrink-0 backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Module Brand & Tagline */}
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-950/60 text-sky-400 shadow-sm">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-mono text-sm font-bold tracking-wider text-white">
                  VERISIGHT RESPONSE & GUIDANCE
                </h1>
                <span className="rounded bg-sky-950 px-1.5 py-0.2 font-mono text-[9px] font-bold text-sky-400 border border-sky-800">
                  INCIDENT RESPONSE
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans italic">
                "From suspicious evidence to informed action."
              </p>
            </div>
          </div>

          {/* 6 Module Sub-Tabs */}
          <div className="flex items-center gap-1 overflow-x-auto rounded-xl border border-white/[0.08] bg-[#070B16] p-1 text-xs font-mono scrollbar-none">
            <button
              onClick={() => setActiveTab("incident-centre")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "incident-centre"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Incident Centre</span>
            </button>

            <button
              onClick={() => setActiveTab("voice")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "voice"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <Mic className="h-3.5 w-3.5" />
              <span>Voice Assistant</span>
            </button>

            <button
              onClick={() => setActiveTab("builder")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "builder"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Complaint Builder</span>
            </button>

            <button
              onClick={() => setActiveTab("dossier")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "dossier"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <Fingerprint className="h-3.5 w-3.5" />
              <span>Evidence Dossier</span>
            </button>

            <button
              onClick={() => setActiveTab("directory")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "directory"
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <Search className="h-3.5 w-3.5" />
              <span>Reporting Directory</span>
            </button>

            <button
              onClick={() => setActiveTab("tracking")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all shrink-0 ${
                activeTab === "tracking"
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]"
              }`}
            >
              <Clock className="h-3.5 w-3.5" />
              <span>Complaint Tracking</span>
            </button>
          </div>
        </div>
      </div>

      {/* 3. Main Scrollable Routed Content Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        <div className="mx-auto max-w-7xl">
          {activeTab === "incident-centre" && (
            <IncidentCentre
              onNavigateTab={handleNavigateTab}
              cases={cases}
              hasAttachedForensicContext={!!attachedForensicContext}
            />
          )}

          {activeTab === "voice" && (
            <VoiceReportingAssistant
              onProceedToBuilder={handleProceedToBuilder}
              attachedForensicContext={attachedForensicContext}
              initialCategoryHint={initialCategoryHint}
            />
          )}

          {activeTab === "builder" && (
            <ComplaintBuilder
              initialDetails={extractedDetails}
              attachedForensicContext={attachedForensicContext}
              onSavedToCaseTracker={handleCaseSaved}
            />
          )}

          {activeTab === "dossier" && (
            <EvidenceDossierView
              attachedForensicContext={attachedForensicContext}
              onNavigateWorkbench={onNavigateWorkbench}
            />
          )}

          {activeTab === "directory" && <ReportingDirectoryView />}

          {activeTab === "tracking" && <CaseTrackerView />}
        </div>
      </div>
    </div>
  );
};
