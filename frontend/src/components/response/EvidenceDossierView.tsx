import React, { useState } from "react";
import {
  Fingerprint,
  Download,
  Printer,
  Copy,
  Layers,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Check,
  Info,
  Maximize2,
} from "lucide-react";
import { toast } from "sonner";
import { AttachedForensicContext } from "../../types/response";
import { downloadDossierPdfBlob } from "../../services/api";

interface EvidenceDossierViewProps {
  attachedForensicContext?: AttachedForensicContext | null;
  onNavigateWorkbench?: () => void;
}

export const EvidenceDossierView: React.FC<EvidenceDossierViewProps> = ({
  attachedForensicContext,
  onNavigateWorkbench,
}) => {
  const [copiedHash, setCopiedHash] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleCopyHash = () => {
    if (!attachedForensicContext) return;
    navigator.clipboard.writeText(attachedForensicContext.file_sha256);
    setCopiedHash(true);
    toast.success("SHA-256 Hash copied to clipboard");
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleDownloadDossierPdf = async () => {
    if (!attachedForensicContext) return;
    setIsDownloading(true);
    try {
      const blob = await downloadDossierPdfBlob(attachedForensicContext);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `VeriSight_Evidence_Dossier_${attachedForensicContext.file_sha256.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Evidence Dossier PDF downloaded");
    } catch (err: any) {
      toast.error(err.message || "Failed to download Dossier PDF");
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (!attachedForensicContext) {
    return (
      <div className="flex min-h-[460px] flex-col items-center justify-center rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 p-8 text-center space-y-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-500">
          <Fingerprint className="h-7 w-7" />
        </div>
        <div className="space-y-1 max-w-md">
          <h3 className="text-base font-semibold text-slate-200 font-sans">
            No Forensic Workbench Screenshot Attached
          </h3>
          <p className="text-xs text-slate-400 font-sans leading-relaxed">
            To generate a cryptographic evidence dossier with ELA, wavelet noise, and baseline laser measurements, analyze a screenshot in the Forensic Workbench and click "What should I do next?".
          </p>
        </div>
        {onNavigateWorkbench && (
          <button
            type="button"
            onClick={onNavigateWorkbench}
            className="flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 font-mono text-xs font-semibold text-white shadow-md shadow-sky-600/30 hover:bg-sky-500 active:scale-[0.98]"
          >
            <span>Open Forensic Workbench</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    );
  }

  const {
    case_id,
    filename,
    file_sha256,
    image_width,
    image_height,
    overall_tamper_score,
    verdict,
    findings,
    synergy,
  } = attachedForensicContext;

  const isHighRisk = overall_tamper_score >= 25 || verdict === "MANIPULATED_FORGERY";

  return (
    <div className="space-y-6">
      {/* Dossier Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-4 shadow-xl backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-sky-500/30 bg-sky-950/60 text-sky-400">
            <Fingerprint className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Cryptographic Forensic Evidence Dossier
              </h3>
              <span className="rounded bg-sky-950 px-1.5 py-0.2 font-mono text-[9px] text-sky-300 border border-sky-800">
                {case_id}
              </span>
            </div>
            <span className="font-mono text-[10px] text-slate-400">
              Chain-of-Custody Protected • Algorithmically Corroborated
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyHash}
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#0C1222] px-3 py-1.5 text-xs font-mono text-slate-300 hover:bg-white/10 active:scale-[0.98]"
            title="Copy SHA-256 Hash"
          >
            {copiedHash ? (
              <Check className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Copy className="h-3.5 w-3.5 text-slate-400" />
            )}
            <span>Copy Hash</span>
          </button>

          <button
            type="button"
            onClick={handlePrint}
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#0C1222] px-3 py-1.5 text-xs font-mono text-slate-300 hover:bg-white/10 active:scale-[0.98]"
            title="Print evidence dossier"
          >
            <Printer className="h-3.5 w-3.5 text-slate-400" />
            <span>Print</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadDossierPdf}
            disabled={isDownloading}
            className="flex items-center gap-1.5 rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-mono font-semibold text-white hover:bg-sky-500 shadow-md shadow-sky-600/30 active:scale-[0.98]"
          >
            <Download className="h-3.5 w-3.5" />
            <span>{isDownloading ? "Generating PDF..." : "Download Dossier PDF"}</span>
          </button>
        </div>
      </div>

      {/* Main Dossier Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Chain-of-Custody & Findings Inventory (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Verdict Overview Card */}
          <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                FORENSIC ASSESSMENT
              </span>
              <span
                className={`rounded border px-2 py-0.5 font-mono text-[10px] font-bold ${
                  isHighRisk
                    ? "border-rose-500/50 bg-rose-500/20 text-rose-300"
                    : "border-emerald-500/50 bg-emerald-500/20 text-emerald-300"
                }`}
              >
                {verdict}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div
                className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border font-mono text-2xl font-bold shadow-lg ${
                  isHighRisk
                    ? "border-rose-500/50 bg-rose-950/80 text-rose-300 shadow-rose-950/50"
                    : "border-emerald-500/50 bg-emerald-950/80 text-emerald-300 shadow-emerald-950/50"
                }`}
              >
                {overall_tamper_score.toFixed(0)}%
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">
                  Calibrated Algorithmic Tamper Risk Score
                </h4>
                <p className="mt-0.5 text-xs text-slate-400 font-sans leading-relaxed">
                  {isHighRisk
                    ? "Multi-spectral signal divergence detected across compression, typography, and metadata."
                    : "Consistent with uniform sensor capture; no digital splicing detected."}
                </p>
              </div>
            </div>

            {/* Cryptographic Hash Bar */}
            <div className="space-y-1 rounded-xl border border-white/[0.06] bg-[#060911] p-3 font-mono text-xs">
              <div className="text-[10px] text-slate-500 uppercase">
                SHA-256 Cryptographic Integrity Digest
              </div>
              <div className="text-sky-300 break-all select-all text-[11px]">
                {file_sha256}
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-white/[0.04]">
                <span>Dimensions: {image_width} × {image_height} px</span>
                <span>Filename: {filename}</span>
              </div>
            </div>
          </div>

          {/* Detailed Findings Inventory */}
          <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
              <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
                Corroborated Signal Findings ({findings.length})
              </h4>
              <span className="font-mono text-[10px] text-slate-400">
                Multi-Layer Physical Inspection
              </span>
            </div>

            {findings.length > 0 ? (
              <div className="space-y-2.5">
                {findings.map((f, i) => (
                  <div
                    key={f.id || i}
                    className="rounded-xl border border-white/[0.06] bg-[#0C1222] p-3 space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-200">
                        {f.title}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.2 font-mono text-[9px] font-bold ${
                          f.severity === "CRITICAL"
                            ? "bg-rose-950 text-rose-300 border border-rose-800/40"
                            : f.severity === "HIGH"
                            ? "bg-amber-950 text-amber-300 border border-amber-800/40"
                            : "bg-sky-950 text-sky-300 border border-sky-800/40"
                        }`}
                      >
                        {f.severity}
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed text-slate-400 font-sans">
                      {f.description}
                    </p>
                    <div className="flex items-center justify-between font-mono text-[10px] text-slate-500 pt-1">
                      <span>Layer {f.layer} Signal</span>
                      <span className="text-sky-400">
                        {f.metric_name}: {f.metric_value}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-500 font-mono">
                No anomalous signal flags detected in this screenshot.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Scientific Methodology & Legal Safeguards (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Methodology */}
          <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl space-y-3 font-sans">
            <div className="flex items-center gap-2 border-b border-white/[0.06] pb-2.5">
              <Layers className="h-4 w-4 text-sky-400" />
              <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
                Forensic Methodology
              </h4>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              VeriSight executes a four-pillar multi-spectral inspection pipeline designed specifically for digital financial transaction screenshots:
            </p>
            <ul className="text-[11px] text-slate-400 space-y-2 leading-relaxed">
              <li>
                <strong className="text-slate-200">Layer 1 (Pixel Physics):</strong> Error Level Analysis (ELA) identifies differential JPEG recompression; 2D Discrete Wavelet Transform (DWT) reveals high-frequency noise voids.
              </li>
              <li>
                <strong className="text-slate-200">Layer 2 (Typography & Geometry):</strong> Sub-pixel baseline laser scans detect micro-vertical displacement (+3px) and font glyph bounding box kerning anomalies.
              </li>
              <li>
                <strong className="text-slate-200">Layer 3 (Metadata & Protocols):</strong> Evaluates EXIF quantization matrices, native device aspect ratios, and validates 12-digit UPI UTR checksum compliance.
              </li>
              <li>
                <strong className="text-slate-200">Layer 4 (Evidence aggregation):</strong> Heuristic cues and spatial overlaps prioritize review. No calibrated authenticity probability is available.
              </li>
            </ul>
          </div>

          {/* Legal Limitations & Safeguards */}
          <div className="rounded-2xl border border-amber-500/30 bg-amber-950/20 p-5 shadow-xl space-y-3 font-sans">
            <div className="flex items-center gap-2 text-amber-300">
              <Info className="h-4 w-4 text-amber-400" />
              <h4 className="font-mono text-xs font-semibold uppercase tracking-wider">
                Technical Limitations & Legal Safeguards
              </h4>
            </div>
            <p className="text-xs text-amber-200/90 leading-relaxed">
              Digital image analysis measures probabilistic physical signal artifacts. Image laundering (e.g. repeated WhatsApp or Telegram forwarding) re-encodes images at quality 77 and subsamples chroma (4:2:0), which may obscure subtle manipulation.
            </p>
            <div className="rounded-lg border border-amber-800/40 bg-amber-950/60 p-2.5 text-[10px] font-mono text-amber-300">
              NOTICE: This dossier is an automated technical summary. It must be corroborated by official bank account statements, banking switch logs, and appropriate independent review.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
