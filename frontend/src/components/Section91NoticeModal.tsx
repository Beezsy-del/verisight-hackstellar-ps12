import React, { useState } from "react";
import {
  X,
  Copy,
  Check,
  Download,
  Printer,
  ShieldAlert,
  AlertTriangle,
  Building,
  CreditCard,
  Hash,
} from "lucide-react";
import { ForensicAnalysisReport } from "../types/forensic";

interface Section91NoticeModalProps {
  report: ForensicAnalysisReport;
  onClose: () => void;
}

export const Section91NoticeModal: React.FC<Section91NoticeModalProps> = ({
  report,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const syndicate = report.syndicate_intelligence;
  const entities = syndicate?.entity_summary;
  const noticeText = report.section91_notice || "Notice not generated for this artifact.";

  const handleCopy = () => {
    navigator.clipboard.writeText(noticeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([noticeText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `SECTION_91_SUBPOENA_VERISIGHT_${report.file_sha256.substring(0, 10).toUpperCase()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    const printWindow = window.open("", "_blank");
    if (!printWindow) return;
    printWindow.document.write(`
      <html>
        <head>
          <title>Section 91 Statutory Requisition - VeriSight</title>
          <style>
            body { font-family: 'Courier New', monospace; padding: 40px; color: #111; line-height: 1.4; font-size: 13px; }
            pre { white-space: pre-wrap; word-wrap: break-word; }
            @page { margin: 20mm; }
          </style>
        </head>
        <body>
          <pre>${noticeText.replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char] || char))}</pre>
          <script>window.onload = function() { window.print(); window.close(); }</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-[#0b1120] border border-[#1e293b] rounded-2xl shadow-2xl flex flex-col overflow-hidden text-[#f1f5f9]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1e293b] bg-[#070b14]/90">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold tracking-tight text-[#f1f5f9]">
                  Section 91 Cr.P.C. / Section 94 BNSS Statutory Notice
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded-full bg-rose-950 text-rose-300 border border-rose-800">
                  1930 Cyber-Cell Ready
                </span>
              </div>
              <p className="text-xs text-[#94a3b8] mt-0.5">
                Automated legal requisition for Emergency Account Freeze & Evidence Preservation
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[#1e293b] text-[#94a3b8] hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Intelligence Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 px-6 py-3 bg-[#070b14]/50 border-b border-[#1e293b] text-xs">
          <div className="bg-[#0b1120] p-2.5 rounded-lg border border-[#1e293b]">
            <div className="flex items-center space-x-1.5 text-[#94a3b8] mb-1 font-mono text-[10px]">
              <CreditCard className="w-3.5 h-3.5 text-amber-400" />
              <span>TARGET VPA</span>
            </div>
            <div className="font-mono font-medium text-white truncate" title={entities?.payee_vpa || "Not extracted"}>
              {entities?.payee_vpa || "N/A"}
            </div>
          </div>

          <div className="bg-[#0b1120] p-2.5 rounded-lg border border-[#1e293b]">
            <div className="flex items-center space-x-1.5 text-[#94a3b8] mb-1 font-mono text-[10px]">
              <Building className="w-3.5 h-3.5 text-sky-400" />
              <span>REPORTED PAYEE</span>
            </div>
            <div className="font-medium text-white truncate" title={entities?.payee_name || "N/A"}>
              {entities?.payee_name || "N/A"}
            </div>
          </div>

          <div className="bg-[#0b1120] p-2.5 rounded-lg border border-[#1e293b]">
            <div className="flex items-center space-x-1.5 text-[#94a3b8] mb-1 font-mono text-[10px]">
              <Hash className="w-3.5 h-3.5 text-emerald-400" />
              <span>REFERENCE UTR</span>
            </div>
            <div className="font-mono font-medium text-white truncate">
              {entities?.utr_number || "Fictitious / Non-standard"}
            </div>
          </div>

          <div className="bg-[#0b1120] p-2.5 rounded-lg border border-[#1e293b]">
            <div className="flex items-center space-x-1.5 text-[#94a3b8] mb-1 font-mono text-[10px]">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>SYNDICATE LEVEL</span>
            </div>
            <div className="font-semibold text-rose-300 truncate">
              {syndicate?.syndicate_risk_level?.replace(/_/g, " ") || "REVIEW REQUIRED"}
            </div>
          </div>
        </div>

        {/* Notice Content */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-xs leading-relaxed bg-[#070b14]/70">
          <div className="relative p-5 rounded-xl bg-[#070b14] border border-[#1e293b] shadow-inner">
            <pre className="text-[#cbd5e1] whitespace-pre-wrap select-all font-mono">
              {noticeText}
            </pre>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-6 py-4 border-t border-[#1e293b] bg-[#070b14]/90">
          <div className="flex items-center space-x-2 text-xs text-[#94a3b8]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Cryptographic Proof: <code className="text-[#f1f5f9] font-mono">{report.file_sha256.substring(0, 16)}...</code></span>
          </div>

          <div className="flex items-center space-x-2.5 w-full sm:w-auto">
            <button
              onClick={handleCopy}
              className="flex-1 sm:flex-none flex items-center justify-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium bg-[#1e293b] hover:bg-[#334155] text-white transition-colors border border-[#334155]"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? "Copied" : "Copy Subpoena"}</span>
            </button>

            <button
              onClick={handleDownload}
              className="flex-1 sm:flex-none flex items-center justify-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium bg-[#1e293b] hover:bg-[#334155] text-white transition-colors border border-[#334155]"
            >
              <Download className="w-4 h-4" />
              <span>Download (.txt)</span>
            </button>

            <button
              onClick={handlePrint}
              className="flex-1 sm:flex-none flex items-center justify-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black shadow-md shadow-amber-500/20 transition-all"
            >
              <Printer className="w-4 h-4 text-black" />
              <span>Print Notice</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
