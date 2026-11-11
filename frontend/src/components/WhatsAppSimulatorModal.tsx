import React, { useState } from "react";
import {
  X,
  Share2,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Layers,
  Info,
  Check,
} from "lucide-react";
import { verdictLabel } from "../services/verdictLabel";
import {
  WhatsAppSimulationResponse,
  ForensicAnalysisReport,
} from "../types/forensic";

interface WhatsAppSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  simulationData: WhatsAppSimulationResponse | null;
  isLoading: boolean;
  onApplyLaunderedImage: (report: ForensicAnalysisReport) => void;
}

export const WhatsAppSimulatorModal: React.FC<WhatsAppSimulatorModalProps> = ({
  isOpen,
  onClose,
  simulationData,
  isLoading,
  onApplyLaunderedImage,
}) => {
  const [activeTab, setActiveTab] = useState<"SIDE_BY_SIDE" | "DIFF_HEATMAP">(
    "SIDE_BY_SIDE",
  );

  React.useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-[#0b1120] border border-[#1e293b] rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden"
      >
        {/* Modal Header */}
        <div className="h-14 px-6 border-b border-[#1e293b] bg-[#070b14] flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-emerald-950 border border-emerald-600/50 flex items-center justify-center">
              <Share2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#f1f5f9] tracking-wide">
                Educational WhatsApp Media Laundering Simulator
              </h3>
              <p className="text-[11px] text-[#64748b]">
                Fixed JPEG transform for comparing review cues before and after recompression
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#f1f5f9] hover:bg-[#1e293b] transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="h-80 flex flex-col items-center justify-center space-y-3 text-[#94a3b8]">
              <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-mono">
                Simulating WhatsApp 4:2:0 Chroma Subsampling & EXIF Stripping...
              </p>
            </div>
          ) : !simulationData ? (
            <div className="h-80 flex flex-col items-center justify-center text-[#64748b]">
              <p className="text-xs font-mono">
                No simulation data available. Please re-run simulation from
                workbench.
              </p>
            </div>
          ) : (
            <>
              {/* Top Stats Strip */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-3">
                  <span className="text-[10px] font-mono text-[#64748b] uppercase">
                    Original File Size
                  </span>
                  <div className="text-base font-bold font-mono text-[#f1f5f9] mt-0.5">
                    {(simulationData.original_size_bytes / 1024).toFixed(1)} KB
                  </div>
                  <span className="text-[10px] text-[#64748b]">
                    Lossless Raw Capture
                  </span>
                </div>

                <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-3">
                  <span className="text-[10px] font-mono text-[#64748b] uppercase">
                    Laundered Size
                  </span>
                  <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                    {(simulationData.simulated_size_bytes / 1024).toFixed(1)} KB
                  </div>
                  <span className="text-[10px] text-emerald-400/80 font-mono">
                    -
                    {Math.round(
                      (1 -
                        simulationData.simulated_size_bytes /
                          simulationData.original_size_bytes) *
                        100,
                    )}
                    % Data Stripped
                  </span>
                </div>

                <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-3">
                  <span className="text-[10px] font-mono text-[#64748b] uppercase">
                    Compression Ratio
                  </span>
                  <div className="text-base font-bold font-mono text-sky-400 mt-0.5">
                    {simulationData.compression_ratio}x
                  </div>
                  <span className="text-[10px] text-[#64748b]">
                    Standard JPEG Q=77
                  </span>
                </div>

                <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-3">
                  <span className="text-[10px] font-mono text-[#64748b] uppercase">
                    Surviving Verdict
                  </span>
                  <div className={`text-base font-bold font-mono mt-0.5 truncate ${simulationData.reanalysis.verdict === "INCONCLUSIVE" ? "text-emerald-400" : "text-rose-400"}`}>
                    {verdictLabel(simulationData.reanalysis.verdict)}
                  </div>
                  <span className="text-[10px] text-rose-400/80 font-mono">
                    Score:{" "}
                    {simulationData.reanalysis.overall_tamper_score.toFixed(1)}
                  </span>
                </div>
              </div>

              {/* View Switcher Tabs */}
              <div className="flex items-center space-x-2 border-b border-[#1e293b] pb-2">
                <button
                  onClick={() => setActiveTab("SIDE_BY_SIDE")}
                  className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                    activeTab === "SIDE_BY_SIDE"
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-[#94a3b8] hover:text-[#f1f5f9] hover:bg-[#1e293b]"
                  }`}
                >
                  Side-by-Side Comparison
                </button>
                <button
                  onClick={() => setActiveTab("DIFF_HEATMAP")}
                  className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                    activeTab === "DIFF_HEATMAP"
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-[#94a3b8] hover:text-[#f1f5f9] hover:bg-[#1e293b]"
                  }`}
                >
                  Quantization Difference Heatmap
                </button>
              </div>

              {/* Image Previews */}
              {activeTab === "SIDE_BY_SIDE" ? (
                <div className="grid grid-cols-2 gap-4 h-96">
                  <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-2 flex flex-col items-center justify-center">
                    <span className="text-[11px] font-mono text-[#64748b] mb-2">
                      BEFORE (ORIGINAL LOSSLESS)
                    </span>
                    <img
                      src={simulationData.reanalysis.original_image_b64}
                      alt="Before"
                      className="max-h-80 object-contain rounded border border-[#1e293b]"
                    />
                  </div>

                  <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-2 flex flex-col items-center justify-center">
                    <span className="text-[11px] font-mono text-emerald-400 mb-2">
                      AFTER (WHATSAPP LAUNDERED)
                    </span>
                    <img
                      src={simulationData.simulated_image_b64}
                      alt="After"
                      className="max-h-80 object-contain rounded border border-[#1e293b]"
                    />
                  </div>
                </div>
              ) : (
                <div className="bg-[#070b14] border border-[#1e293b] rounded-xl p-3 flex flex-col items-center justify-center h-96">
                  <span className="text-[11px] font-mono text-amber-400 mb-2">
                    ABSOLUTE PIXEL DIFFERENCE (AMPLIFIED 12X — JET COLORMAP)
                  </span>
                  <img
                    src={simulationData.diff_heatmap_b64}
                    alt="Difference Heatmap"
                    className="max-h-80 object-contain rounded border border-[#1e293b]"
                  />
                </div>
              )}

              {/* Educational Forensic Note */}
              <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-3.5 flex items-start space-x-3 text-xs">
                <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1 text-[#94a3b8]">
                  <span className="font-semibold text-emerald-300">
                    Why does VeriSight still catch forgeries after WhatsApp
                    laundering?
                  </span>
                  <p className="leading-relaxed">
                    Social media platforms strip EXIF metadata and quantize DCT
                    high frequencies, which often defeats basic camera PRNU
                    checks. However,{" "}
                    <strong>Layer 2 Sub-Pixel Typographic Baselines</strong> and{" "}
                    <strong>
                      Layer 1 Daubechies db4 Wavelet Noise Boundaries
                    </strong>{" "}
                    are structurally geometric: the pixel shifts and off-color
                    card halos survive 4:2:0 subsampling, allowing VeriSight to
                    confidently detect manipulation even on forwarded images.
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="h-14 px-6 border-t border-[#1e293b] bg-[#070b14] flex items-center justify-between">
          <span className="text-[11px] font-mono text-[#64748b]">
            Educational Demonstration Mode // HackStellar PS-12
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-[#1e293b] hover:bg-[#334155] text-xs font-medium text-[#f1f5f9] transition-all"
            >
              Close
            </button>
            {simulationData && (
              <button
                onClick={() => {
                  onApplyLaunderedImage(simulationData.reanalysis);
                  onClose();
                }}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white transition-all flex items-center space-x-1.5 shadow-md shadow-emerald-600/20"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Load Laundered Screenshot in Workbench</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
