import React, { useEffect } from "react";
import {
  X,
  ExternalLink,
  MapPin,
  Calendar,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Scale,
  ArrowRight,
  Layers,
  Sparkles,
  Building2,
  ShieldAlert,
} from "lucide-react";
import { RealWorldFraudCase } from "../data/realWorldCases";

interface CaseInvestigationModalProps {
  caseItem: RealWorldFraudCase | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigateWorkbench?: () => void;
  onNavigateResponse?: (category?: string) => void;
}

export const CaseInvestigationModal: React.FC<CaseInvestigationModalProps> = ({
  caseItem,
  isOpen,
  onClose,
  onNavigateWorkbench,
  onNavigateResponse,
}) => {
  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !caseItem) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-white/10 bg-[#0A0F1F] shadow-2xl overflow-hidden font-sans text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Header Bar */}
        <div className="flex items-center justify-between border-b border-white/[0.08] bg-[#070B16] px-6 py-4 shrink-0">
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="rounded bg-rose-950 px-2 py-0.5 text-rose-300 font-bold border border-rose-800/40">
              REPORTED CASE
            </span>
            <div className="flex items-center gap-1 text-slate-400">
              <MapPin className="h-3.5 w-3.5 text-sky-400" />
              <span>
                {caseItem.city}, {caseItem.state}
              </span>
            </div>
            <span className="text-slate-600">•</span>
            <div className="flex items-center gap-1 text-slate-400">
              <Calendar className="h-3.5 w-3.5 text-slate-500" />
              <span>{caseItem.incidentMonthYear}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition-colors"
            title="Close Dossier"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Featured Editorial Photo Header */}
          {caseItem.imageUrl && (
            <div className="relative h-48 sm:h-60 w-full overflow-hidden rounded-xl border border-white/10 bg-slate-900 shadow-md">
              <img
                src={caseItem.imageUrl}
                alt={caseItem.imageAlt || caseItem.headline}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0A0F1F] via-transparent to-transparent opacity-80" />
              <div className="absolute top-3 right-3 transform -rotate-6 rounded border-2 border-red-500 bg-red-950/90 px-2.5 py-0.5 font-mono text-[10px] font-black tracking-widest text-red-400 shadow-xl uppercase">
                REPORTED CASE
              </div>
            </div>
          )}

          {/* Headline & Loss Figure */}
          <div className="space-y-3">
            <span className="font-mono text-xs font-semibold text-sky-400 uppercase tracking-wider">
              {caseItem.scamCategory}
            </span>
            <h2 className="text-xl sm:text-2xl font-bold text-white leading-snug">
              {caseItem.headline}
            </h2>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-white/[0.06]">
              <div>
                <span className="block font-mono text-[10px] text-slate-400 uppercase">
                  DOCUMENTED FINANCIAL LOSS
                </span>
                <span className="text-2xl sm:text-3xl font-extrabold text-amber-400 font-mono tracking-tight">
                  {caseItem.reportedLoss}
                </span>
              </div>

              {/* Publisher & Source Link */}
              <div className="text-right">
                <span className="block font-mono text-[10px] text-slate-400 uppercase">
                  VERIFIED SOURCE ATTRIBUTION
                </span>
                <a
                  href={caseItem.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 font-mono text-xs font-semibold text-sky-400 hover:text-sky-300 hover:underline pt-0.5"
                >
                  <span>{caseItem.publisher}</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
                <span className="block text-[10px] text-slate-500 font-mono">
                  Published: {caseItem.sourceDate}
                </span>
              </div>
            </div>
          </div>

          {/* Incident Narrative Summary */}
          <div className="rounded-xl border border-white/[0.08] bg-[#070B16] p-4 space-y-2">
            <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
              Documented Incident Overview
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {caseItem.summary}
            </p>
          </div>

          {/* Step-by-Step Modus Operandi */}
          <div className="space-y-3">
            <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-400" />
              <span>Alleged Modus Operandi</span>
            </h3>
            <div className="space-y-2">
              {caseItem.modusOperandi.map((step, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 rounded-lg border border-white/[0.04] bg-white/[0.02] p-3 text-xs text-slate-300"
                >
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded bg-sky-950 font-mono text-[10px] font-bold text-sky-400 border border-sky-800">
                    {idx + 1}
                  </span>
                  <p className="leading-relaxed">{step}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Two-Column: Warning Signs & Prevention Insight */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Warning Signs */}
            <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4 space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-rose-300 uppercase">
                <AlertTriangle className="h-4 w-4 text-rose-400" />
                <span>Red Flag Warning Signs</span>
              </div>
              <ul className="space-y-1.5 text-xs text-rose-200/90 pl-1">
                {caseItem.warningSigns.map((sign, i) => (
                  <li key={i} className="leading-snug">
                    • {sign}
                  </li>
                ))}
              </ul>
            </div>

            {/* Prevention Insight */}
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-emerald-300 uppercase">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>What Could Have Prevented It</span>
              </div>
              <p className="text-xs text-emerald-200/90 leading-relaxed">
                {caseItem.preventionInsight}
              </p>
            </div>
          </div>

          {/* VeriSight Forensic & Investigative Relevance (The Major Value Add) */}
          <div className="rounded-xl border border-sky-500/30 bg-gradient-to-br from-sky-950/40 via-[#070D1B] to-[#0A1224] p-5 space-y-3">
            <div className="flex items-center gap-2 font-mono text-xs font-bold text-sky-300 uppercase">
              <Sparkles className="h-4 w-4 text-sky-400" />
              <span>How VeriSight Relates to This Case</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="rounded-lg border border-white/[0.06] bg-[#060911] p-3 space-y-1">
                <span className="font-mono text-[10px] text-sky-400 uppercase font-semibold">
                  Relevant Forensic Layer
                </span>
                <p className="text-slate-200 font-medium">
                  {caseItem.verisightRelevance.forensicLayer}
                </p>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#060911] p-3 space-y-1">
                <span className="font-mono text-[10px] text-cyan-400 uppercase font-semibold">
                  Examination Findings
                </span>
                <p className="text-slate-300">
                  {caseItem.verisightRelevance.examination}
                </p>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#060911] p-3 space-y-1">
                <span className="font-mono text-[10px] text-amber-400 uppercase font-semibold">
                  Investigator Guidance
                </span>
                <p className="text-slate-300">
                  {caseItem.verisightRelevance.userGuidance}
                </p>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#060911] p-3 space-y-1">
                <span className="font-mono text-[10px] text-emerald-400 uppercase font-semibold">
                  Statutory Response Feature
                </span>
                <p className="text-slate-300">
                  {caseItem.verisightRelevance.responseFeature}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.08] bg-[#070B16] px-6 py-4 shrink-0">
          <a
            href={caseItem.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 font-mono text-xs text-slate-400 hover:text-white transition-colors"
          >
            <span>Read Original Publisher Article</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>

          <div className="flex items-center gap-2">
            {onNavigateWorkbench && (
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onNavigateWorkbench();
                }}
                className="flex items-center gap-1.5 rounded-xl border border-sky-500/40 bg-sky-500/20 px-4 py-2 font-mono text-xs font-semibold text-sky-300 hover:bg-sky-500/30 transition-all active:scale-[0.98]"
              >
                <Layers className="h-3.5 w-3.5" />
                <span>Launch Workbench</span>
              </button>
            )}

            {onNavigateResponse && (
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onNavigateResponse(caseItem.categoryCode);
                }}
                className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-2 font-mono text-xs font-semibold text-white hover:from-emerald-400 hover:to-teal-500 shadow-md transition-all active:scale-[0.98]"
              >
                <span>Report Similar Incident</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
