import React from "react";
import { Cpu, CheckCircle2, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface SkillStage {
  id: string;
  name: string;
  layer: number;
  shortDesc: string;
}

export const FORENSIC_SKILLS: SkillStage[] = [
  {
    id: "pixel_forensics_skill",
    layer: 1,
    name: "Pixel Forensics",
    shortDesc: "Compression ELA & Wavelet Noise",
  },
  {
    id: "typography_alignment_skill",
    layer: 2,
    name: "Typography Geometry",
    shortDesc: "Sub-Pixel Baseline Lasers & Kerning",
  },
  {
    id: "clone_splice_skill",
    layer: 3,
    name: "Clone & Splicing",
    shortDesc: "ORB Keypoints & Copy-Move Vectors",
  },
  {
    id: "upi_entity_syndicate_skill",
    layer: 4,
    name: "UPI Syndicate Resolution",
    shortDesc: "VPA, UTR & Section 91 Subpoena",
  },
];

interface SkillPipelineHUDProps {
  activeStageIndex: number; // 0 to 4 (4 = complete)
  isRunning: boolean;
}

export const SkillPipelineHUD: React.FC<SkillPipelineHUDProps> = ({
  activeStageIndex,
  isRunning,
}) => {
  if (!isRunning && activeStageIndex >= 4) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: "auto" }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.2 }}
        className="w-full bg-[#080d1a]/95 border-b border-cyan-500/25 px-4 py-2 z-40 backdrop-blur-md shadow-lg select-none"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 max-w-7xl mx-auto">
          {/* Status Title */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              {isRunning ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Cpu className="h-3.5 w-3.5" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] font-bold text-cyan-200 uppercase tracking-wider">
                  Active Forensic Skill Orchestrator
                </span>
                <span className="rounded bg-cyan-950 px-1.5 py-0.2 font-mono text-[9px] font-semibold text-cyan-400 border border-cyan-800">
                  {isRunning ? `RUNNING STAGE ${Math.min(activeStageIndex + 1, 4)}/4` : "PIPELINE SYNCHRONIZED"}
                </span>
              </div>
            </div>
          </div>

          {/* 4 Skill Pills */}
          <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 font-mono text-[10px]">
            {FORENSIC_SKILLS.map((skill, idx) => {
              const isPast = idx < activeStageIndex;
              const isCurrent = idx === activeStageIndex && isRunning;
              const isPending = idx > activeStageIndex;

              return (
                <div
                  key={skill.id}
                  className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 border transition-all ${
                    isCurrent
                      ? "border-cyan-400 bg-cyan-500/20 text-cyan-100 shadow-[0_0_12px_rgba(6,182,212,0.4)] animate-pulse"
                      : isPast
                      ? "border-emerald-500/40 bg-emerald-950/50 text-emerald-300"
                      : "border-white/[0.08] bg-[#0c1322] text-slate-500 opacity-60"
                  }`}
                >
                  {isCurrent ? (
                    <Loader2 className="h-3 w-3 animate-spin text-cyan-400 shrink-0" />
                  ) : isPast ? (
                    <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                  ) : (
                    <div className="h-2 w-2 rounded-full bg-slate-600 shrink-0" />
                  )}
                  <div className="truncate">
                    <span className="font-semibold block truncate">
                      L{skill.layer}: {skill.name}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
