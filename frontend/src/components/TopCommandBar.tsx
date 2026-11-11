import React, { useRef, useState, useEffect } from "react";
import {
  ShieldCheck,
  Upload,
  ChevronDown,
  Check,
  Share2,
  QrCode,
  FileText,
  Loader2,
  ShieldAlert,
  Keyboard,
} from "lucide-react";
import { motion } from "framer-motion";
import { DemoSampleMeta } from "../types/forensic";
import { toast } from "sonner";

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
  isAdvancedMode: boolean;
  onToggleAdvancedMode: () => void;
  isLoading: boolean;
}

const SAMPLE_DETAILS: Record<
  string,
  { label: string; badge: string; color: string; desc: string }
> = {
  sample_1: {
    label: "Clean Synthetic UPI",
    badge: "Synthetic",
    color: "emerald",
    desc: "Clean baseline reference receipt",
  },
  sample_2: {
    label: "Synthetic ₹95,250 Edit",
    badge: "Amount Edit",
    color: "rose",
    desc: "Digital text insertion & font drift",
  },
  sample_3: {
    label: "Clock Paradox UPI",
    badge: "Time Drift",
    color: "amber",
    desc: "Status bar vs transaction mismatch",
  },
  sample_4: {
    label: "WhatsApp Recompressed",
    badge: "Recompressed",
    color: "amber",
    desc: "Compression laundering artifact",
  },
  sample_5: {
    label: "ORB Cloned Icons",
    badge: "Copy-Move",
    color: "rose",
    desc: "Duplicated bank badge keypoints",
  },
};

export const TopCommandBar: React.FC<TopCommandBarProps> = ({
  databaseStatus,
  demoSamples,
  selectedSampleId,
  onSelectSample,
  onFileUpload,
  onOpenWhatsAppModal,
  onOpenMobileModal,
  onOpenReportModal,
  onOpenSection91Modal,
  onOpenShortcutsModal,
  isAdvancedMode,
  onToggleAdvancedMode,
  isLoading,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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
        color: "sky",
        desc: "Custom uploaded screenshot",
      }
    : {
        label: "Custom Screenshot",
        badge: "Custom Upload",
        color: "sky",
        desc: "Active forensic artifact",
      };

  return (
    <header className="relative z-30 flex h-14 w-full shrink-0 items-center justify-between border-b border-white/[0.07] bg-[#090D16]/95 px-2 sm:px-4 backdrop-blur-md select-none overflow-x-auto no-scrollbar gap-2">
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

      {/* 2. Center Zone: Sleek Case Selector Combobox Dropdown */}
      <div className="relative shrink-0" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => setIsDropdownOpen((prev) => !prev)}
          disabled={isLoading}
          className="group flex w-[200px] sm:w-[310px] items-center justify-between rounded-lg border border-white/[0.08] bg-[#0D1424] px-2.5 sm:px-3 py-1.5 text-xs text-slate-200 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:border-white/20 active:scale-[0.98]"
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
              className={`rounded px-1.5 py-0.5 font-mono text-[9px] font-semibold ${
                currentMeta.color === "emerald"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800/50"
                  : currentMeta.color === "amber"
                  ? "bg-amber-950/80 text-amber-300 border border-amber-800/50"
                  : "bg-rose-950/80 text-rose-300 border border-rose-800/50"
              }`}
            >
              {currentMeta.badge}
            </span>
            <ChevronDown
              className={`h-3.5 w-3.5 text-slate-400 transition-transform duration-150 ${
                isDropdownOpen ? "rotate-180" : ""
              }`}
            />
          </div>
        </button>

        {/* Dropdown Menu */}
        {isDropdownOpen && (
          <div className="absolute left-0 top-full mt-1.5 w-[310px] z-50 rounded-xl border border-white/10 bg-[#0C1222]/98 p-1.5 shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-100">
            <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-slate-500">
              Preset Evidence Samples (1–5)
            </div>
            <div className="space-y-1 mt-1">
              {demoSamples.map((sample, idx) => {
                const meta = SAMPLE_DETAILS[sample.id] || {
                  label: sample.title,
                  badge: `S${idx + 1}`,
                  color: "sky",
                  desc: sample.scenario,
                };
                const isSelected = selectedSampleId === sample.id;

                return (
                  <button
                    key={sample.id}
                    onClick={() => {
                      onSelectSample(sample.id);
                      setIsDropdownOpen(false);
                      toast.success(`Loaded case: ${meta.label}`);
                    }}
                    className={`flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-left text-xs transition-colors ${
                      isSelected
                        ? "bg-sky-500/15 text-sky-200 border border-sky-500/30"
                        : "hover:bg-white/[0.06] text-slate-300"
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-[10px] font-bold text-slate-400">
                          S{idx + 1}
                        </span>
                        <span className="font-medium truncate">{meta.label}</span>
                      </div>
                      <span className="block text-[10px] text-slate-500 truncate">
                        {meta.desc}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <span
                        className={`rounded px-1.5 py-0.5 font-mono text-[9px] ${
                          meta.color === "emerald"
                            ? "bg-emerald-950 text-emerald-300 border border-emerald-800/40"
                            : meta.color === "amber"
                            ? "bg-amber-950 text-amber-300 border border-amber-800/40"
                            : "bg-rose-950 text-rose-300 border border-rose-800/40"
                        }`}
                      >
                        {meta.badge}
                      </span>
                      {isSelected && <Check className="h-3.5 w-3.5 text-sky-400" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 3. Right Zone: Sliding Segmented Mode Toggle + Fixed Action Cluster (ZERO SCROLLBARS) */}
      <div className="flex items-center gap-2.5 shrink-0">
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

        {/* WhatsApp Simulation */}
        <button
          type="button"
          onClick={onOpenWhatsAppModal}
          disabled={isLoading}
          className="flex items-center gap-1.5 rounded-lg border border-emerald-500/25 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-medium text-emerald-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:bg-emerald-500/20 active:scale-[0.97]"
          title="Simulate WhatsApp compression laundering"
        >
          <Share2 className="h-3.5 w-3.5 text-emerald-400" />
          <span className="hidden xl:inline">WhatsApp</span>
        </button>

        {/* Section 91 Subpoena */}
        {onOpenSection91Modal && (
          <button
            type="button"
            onClick={onOpenSection91Modal}
            disabled={isLoading}
            className="flex items-center gap-1.5 rounded-lg border border-amber-500/25 bg-amber-500/10 px-2.5 py-1.5 text-xs font-medium text-amber-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] transition-all hover:bg-amber-500/20 active:scale-[0.97]"
            title="Open Section 91 Subpoena Notice"
          >
            <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
            <span className="hidden sm:inline">Section 91</span>
          </button>
        )}

        {/* Export Dossier */}
        <button
          type="button"
          onClick={onOpenReportModal}
          disabled={isLoading}
          className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#162035] px-3 py-1.5 text-xs font-medium text-slate-100 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.15)] transition-all hover:bg-[#1E2B47] active:scale-[0.97]"
        >
          <FileText className="h-3.5 w-3.5 text-slate-300" />
          <span className="hidden md:inline">Export</span>
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
