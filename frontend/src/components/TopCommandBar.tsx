import React, { useRef, useState, useEffect } from "react";
import {
  Upload,
  ChevronDown,
  Check,
  Share2,
  FileText,
  Loader2,
  ShieldAlert,
  Keyboard,
  LifeBuoy,
} from "lucide-react";
import { motion } from "framer-motion";
import { DemoSampleMeta } from "../types/forensic";
import { toast } from "sonner";
import { useVerdictTheme } from "./AmbientThreatBackground";

interface TopCommandBarProps {
  databaseStatus: "CHECKING" | "HEALTHY" | "UNAVAILABLE" | "NOT_CONFIGURED";
  demoSamples: DemoSampleMeta[];
  selectedSampleId: string | null;
  onSelectSample: (sampleId: string) => void;
  onFileUpload: (file: File) => void;
  onOpenWhatsAppModal: () => void;
  onOpenMobileModal: () => void;
  onOpenReportModal: () => void;
  onOpenSection91Modal?: () => void;
  onOpenShortcutsModal?: () => void;
  onOpenResponse?: () => void;
  isAdvancedMode: boolean;
  onToggleAdvancedMode: () => void;
  isLoading: boolean;
  hasReport: boolean;
}

export const TopCommandBar: React.FC<TopCommandBarProps> = ({
  demoSamples,
  selectedSampleId,
  onSelectSample,
  onFileUpload,
  onOpenWhatsAppModal,
  onOpenMobileModal,
  onOpenReportModal,
  onOpenSection91Modal,
  onOpenShortcutsModal,
  onOpenResponse,
  isAdvancedMode,
  onToggleAdvancedMode,
  isLoading,
  hasReport,
}) => {
  const SAMPLE_DETAILS: Record<string, { label: string; badge: string; color: string; desc: string }> = Object.fromEntries(demoSamples.map(sample => [sample.id, { label: sample.title, badge: sample.tags[0] || "Unverified", color: "sky", desc: sample.scenario }]));
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { theme, badgeBg, badgeText, badgeBorder } = useVerdictTheme();

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) {
      toast.info(`Uploading evidence: ${file.name}`);
      onFileUpload(file);
    }
  };

  const currentMeta = selectedSampleId
    ? SAMPLE_DETAILS[selectedSampleId] || {
        label: selectedSampleId,
        badge: "Case",
        color: "sky" as const,
        desc: "Custom uploaded screenshot",
      }
    : {
        label: "Custom Screenshot",
        badge: "Custom Upload",
        color: "sky" as const,
        desc: "Active forensic artifact",
      };

  // Derive trigger pill label and color from real-time verdict outcome
  let triggerBadgeText = currentMeta.badge;
  let triggerBadgeStyle = `${badgeBg} ${badgeText} ${badgeBorder}`;

  if (isLoading) {
    triggerBadgeText = "Analyzing...";
    triggerBadgeStyle = "bg-cyan-950/80 text-cyan-300 border border-cyan-800/50 animate-pulse";
  }

  return (
    <header
      className={`relative z-30 flex min-h-14 flex-wrap py-2 w-full shrink-0 items-center justify-between border-b border-white/[0.07] bg-[#090D16]/95 px-2 sm:px-4 backdrop-blur-md select-none overflow-visible gap-2 transition-all duration-700 ease-out ${
        theme === "fraud"
          ? "border-t-2 border-t-rose-500/80 shadow-[0_4px_20px_rgba(244,63,94,0.15)]"
          : ""
      }`}
    >
      {/* 1. Left Zone: Workbench Session Indicator */}
      <div className="hidden sm:flex items-center gap-2.5 shrink-0">
        <div className="flex items-center gap-2 rounded-lg border border-sky-500/20 bg-sky-950/40 px-2.5 py-1 text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-mono text-[11px] font-semibold text-sky-300">
            WORKBENCH
          </span>
        </div>
      </div>

      {/* 2. Center Zone: Stacking-Safe Case Selector Combobox Dropdown */}
      <div className="relative shrink-0" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => setIsDropdownOpen((prev) => !prev)}
          disabled={isLoading}
          className="group flex w-[210px] sm:w-[330px] items-center justify-between rounded-lg border border-white/[0.12] bg-[#0D1424] px-2.5 sm:px-3 py-1.5 text-xs text-slate-200 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:border-white/25 active:scale-[0.98]"
          title="Select investigation case (Shortcuts: 1-5)"
        >
          <div className="flex items-center gap-2 truncate">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">
              CASE:
            </span>
            <span className="truncate font-medium text-slate-100">
              {currentMeta.label}
            </span>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <span
              className={`rounded px-1.5 py-0.5 font-mono text-[9px] font-semibold transition-colors duration-300 ${triggerBadgeStyle}`}
            >
              {triggerBadgeText}
            </span>
            <ChevronDown
              className={`h-3.5 w-3.5 text-slate-400 transition-transform duration-150 ${
                isDropdownOpen ? "rotate-180" : ""
              }`}
            />
          </div>
        </button>

        {/* Dropdown Menu Panel with Glassmorphic Depth & z-[100] */}
        {isDropdownOpen && (
          <div className="absolute left-0 top-full mt-2 w-[340px] sm:w-[380px] z-[100] rounded-xl border border-white/15 bg-slate-950/95 p-2 shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between px-2.5 py-1 border-b border-white/[0.08] text-[10px] font-mono uppercase tracking-wider text-slate-400">
              <span>Preset Evidence Cases (1–5)</span>
              <span className="text-slate-500">Press 1-5 to switch</span>
            </div>
            <div className="space-y-1 mt-1.5">
              {demoSamples.map((sample, idx) => {
                const meta = SAMPLE_DETAILS[sample.id] || {
                  label: sample.title,
                  badge: `S${idx + 1}`,
                  color: "sky" as const,
                  desc: sample.scenario,
                };
                const isSelected = selectedSampleId === sample.id;

                let pillColorClass = "bg-sky-950 text-sky-300 border-sky-800/40";
                if (meta.color === "emerald") {
                  pillColorClass = "bg-emerald-950 text-emerald-300 border-emerald-800/40";
                } else if (meta.color === "amber") {
                  pillColorClass = "bg-amber-950 text-amber-300 border-amber-800/40";
                } else if (meta.color === "rose") {
                  pillColorClass = "bg-rose-950 text-rose-300 border-rose-800/40";
                }

                return (
                  <button
                    key={sample.id}
                    onClick={() => {
                      onSelectSample(sample.id);
                      setIsDropdownOpen(false);

                    }}
                    className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition-all ${
                      isSelected
                        ? "bg-sky-500/15 text-sky-100 border border-sky-500/40 shadow-sm"
                        : "hover:bg-white/[0.07] text-slate-300 border border-transparent"
                    }`}
                  >
                    <div className="truncate pr-2.5">
                      <div className="flex items-center gap-1.5">
                        <span className="rounded bg-white/[0.08] px-1.5 py-0.5 font-mono text-[9px] font-bold text-slate-300">
                          S{idx + 1}
                        </span>
                        <span className="font-medium truncate text-white">{meta.label}</span>
                      </div>
                      <span className="block text-[10px] text-slate-400 truncate mt-0.5">
                        {meta.desc}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span
                        className={`rounded border px-1.5 py-0.5 font-mono text-[9px] font-semibold ${pillColorClass}`}
                      >
                        {meta.badge}
                      </span>
                      {isSelected && <Check className="h-4 w-4 text-sky-400 shrink-0" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 3. Right Zone: Action Cluster */}
      <div className="flex max-w-full flex-wrap items-center gap-2 shrink-0 py-0.5">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/png,image/jpeg,image/webp,image/bmp,.png,.jpg,.jpeg,.webp,.bmp"
          className="hidden"
        />

        {/* Sliding Segmented Toggle: Simple | Forensic (motion-primitives layoutId) */}
        <div className="relative flex items-center rounded-lg border border-white/[0.08] bg-[#0A0F1D] p-0.5 text-xs font-mono">
          <button
            type="button"
            onClick={() => {
              if (isAdvancedMode) {
                onToggleAdvancedMode();
                toast("Switched to Simple Mode");
              }
            }}
            className={`relative z-10 px-2.5 py-1 text-[11px] font-medium transition-colors ${
              !isAdvancedMode ? "text-sky-300" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Simple
            {!isAdvancedMode && (
              <motion.div
                layoutId="activeViewModePill"
                className="absolute inset-0 z-[-1] rounded-md bg-sky-500/20 border border-sky-500/40 shadow-sm"
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              />
            )}
          </button>

          <button
            type="button"
            onClick={() => {
              if (!isAdvancedMode) {
                onToggleAdvancedMode();
                toast("Switched to Forensic Advanced Mode");
              }
            }}
            className={`relative z-10 px-2.5 py-1 text-[11px] font-medium transition-colors ${
              isAdvancedMode ? "text-sky-300" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Forensic
            {isAdvancedMode && (
              <motion.div
                layoutId="activeViewModePill"
                className="absolute inset-0 z-[-1] rounded-md bg-sky-500/20 border border-sky-500/40 shadow-sm"
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              />
            )}
          </button>
        </div>

        {/* Upload Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="flex items-center gap-1.5 rounded-lg border border-sky-500/30 bg-sky-500/10 px-3 py-1.5 text-xs font-medium text-sky-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)] transition-all hover:bg-sky-500/20 active:scale-[0.97]"
          title="Upload image evidence"
        >
          {isLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-sky-400" />
          ) : (
            <Upload className="h-3.5 w-3.5 text-sky-400" />
          )}
          <span>Upload Evidence</span>
        </button>

        <button type="button" onClick={onOpenMobileModal} className="action-button" title="Check mobile intake availability">Mobile intake</button>
        {/* WhatsApp Simulation */}
        <button
          type="button"
          disabled={!hasReport || isLoading} onClick={onOpenWhatsAppModal}

          className="flex items-center gap-1.5 rounded-lg border border-emerald-500/25 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-medium text-emerald-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:bg-emerald-500/20 active:scale-[0.97]"
          title="Simulate WhatsApp compression laundering"
        >
          <Share2 className="h-3.5 w-3.5 text-emerald-400" />
          <span className="hidden xl:inline">WhatsApp</span>
        </button>

        {/* Draft request Subpoena */}
        {onOpenSection91Modal && (
          <button
            type="button"
            disabled={!hasReport || isLoading} onClick={onOpenSection91Modal}

            className="flex items-center gap-1.5 rounded-lg border border-amber-500/25 bg-amber-500/10 px-2.5 py-1.5 text-xs font-medium text-amber-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:bg-amber-500/20 active:scale-[0.97]"
            title="Open preservation request draft"
          >
            <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
            <span className="hidden sm:inline">Draft request</span>
          </button>
        )}

        {/* What should I do next? / Response & Guidance */}
        {onOpenResponse && (
          <button
            type="button"
            disabled={!hasReport || isLoading} onClick={onOpenResponse}

            className="flex items-center gap-1.5 rounded-lg border border-sky-400/40 bg-gradient-to-r from-sky-500/20 to-indigo-500/20 px-3 py-1.5 text-xs font-semibold text-sky-200 shadow-sm transition-all hover:bg-sky-500/30 hover:text-white active:scale-[0.97]"
            title="What should I do next? Open Response & Guidance"
          >
            <LifeBuoy className="h-3.5 w-3.5 text-sky-400 animate-pulse" />
            <span className="hidden lg:inline">What should I do next?</span>
            <span className="lg:hidden">What Next?</span>
          </button>
        )}

        {/* Export Dossier */}
        <button
          type="button"
          disabled={!hasReport || isLoading} aria-label="Review Memo" onClick={onOpenReportModal}

          className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#162035] px-3 py-1.5 text-xs font-medium text-slate-100 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.15)] transition-all hover:bg-[#1E2B47] active:scale-[0.97]"
        >
          <FileText className="h-3.5 w-3.5 text-slate-300" />
          <span>Review Memo</span>
        </button>

        {/* Keyboard Shortcuts (?) */}
        {onOpenShortcutsModal && (
          <button
            type="button"
            onClick={onOpenShortcutsModal}
            className="rounded-lg border border-white/[0.08] bg-[#0A0F1D] p-1.5 text-slate-400 transition-all hover:bg-white/[0.06] hover:text-slate-200 active:scale-[0.95]"
            title="Keyboard shortcuts (?)"
            aria-label="Keyboard shortcuts"
          >
            <Keyboard className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </header>
  );
};
