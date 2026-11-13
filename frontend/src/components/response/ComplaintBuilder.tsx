import React, { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Printer,
  Copy,
  Save,
  Languages,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  Building2,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Check,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";
import {
  ExtractedIncidentDetails,
  FormalComplaint,
  AttachedForensicContext,
} from "../../types/response";
import {
  generateComplaint,
  downloadComplaintPdfBlob,
  regenerateComplaintSection,
  createCaseRecord,
} from "../../services/api";

interface ComplaintBuilderProps {
  initialDetails?: ExtractedIncidentDetails | null;
  attachedForensicContext?: AttachedForensicContext | null;
  onSavedToCaseTracker?: (caseId: string) => void;
}

const AUTHORITIES = [
  {
    id: "NATIONAL_CYBER_CRIME_PORTAL",
    name: "National Cyber Crime Reporting Portal (NCRP) / 1930 Helpline",
    url: "https://cybercrime.gov.in",
    tag: "Recommended for Financial Cyber Fraud & Forgery",
  },
  {
    id: "BANK_UPI_PSP",
    name: "Bank Grievance Redressal & UPI Service Provider",
    url: "https://www.npci.org.in",
    tag: "Required within 72 hrs for Zero-Liability Protection",
  },
  {
    id: "RBI_CMS_OMBUDSMAN",
    name: "RBI Complaint Management System (CMS) — Banking Ombudsman",
    url: "https://cms.rbi.org.in",
    tag: "Escalation after 30 days of unresolved bank dispute",
  },
  {
    id: "POLICE_CYBER_CELL",
    name: "District Cyber Crime Police Station (Zero FIR / Section 173 BNSS)",
    url: "https://cybercrime.gov.in",
    tag: "Criminal investigation & evidence subpoena",
  },
  {
    id: "PLATFORM_ABUSE",
    name: "Platform Abuse & Grievance Officer (WhatsApp, Telegram, OLX)",
    url: "https://gac.gov.in",
    tag: "Account takedown & profile preservation",
  },
];

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी (Hindi)" },
  { code: "kn", label: "ಕನ್ನಡ (Kannada)" },
  { code: "bn", label: "বাংলা (Bengali)" },
  { code: "ta", label: "தமிழ் (Tamil)" },
  { code: "te", label: "తెలుగు (Telugu)" },
  { code: "mr", label: "मराठी (Marathi)" },
];

export const ComplaintBuilder: React.FC<ComplaintBuilderProps> = ({
  initialDetails,
  attachedForensicContext,
  onSavedToCaseTracker,
}) => {
  // Complainant & Incident Form States
  const [authorityDestination, setAuthorityDestination] = useState("NATIONAL_CYBER_CRIME_PORTAL");
  const [language, setLanguage] = useState("en");
  const [complainantName, setComplainantName] = useState(initialDetails?.complainant_name || "");
  const [complainantContact, setComplainantContact] = useState(initialDetails?.complainant_contact || "");
  const [complainantAddress, setComplainantAddress] = useState("");
  const [customNarrative, setCustomNarrative] = useState(initialDetails?.narrative_description || "");
  const [includeForensicEvidence, setIncludeForensicEvidence] = useState(true);

  // Generated Complaint State
  const [complaint, setComplaint] = useState<FormalComplaint | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [copiedText, setCopiedText] = useState(false);
  const [isSavingCase, setIsSavingCase] = useState(false);

  // Auto-generate complaint draft when initialDetails change
  useEffect(() => {
    if (initialDetails) {
      void handleBuildDraft();
    }
  }, [initialDetails, authorityDestination, language, includeForensicEvidence]);

  const handleBuildDraft = async () => {
    if (!initialDetails && !customNarrative.trim()) return;

    setIsGenerating(true);
    try {
      const detailsToUse: ExtractedIncidentDetails = initialDetails || {
        incident_category: "OTHER_CYBERCRIME",
        incident_category_label: "Cyber Incident",
        financial_impact: "UNCERTAIN",
        currency: "INR",
        narrative_description: customNarrative,
        available_evidence: ["Screenshot / Communication Record"],
        is_ongoing: false,
        account_at_risk: false,
        missing_fields: [],
        confidence_score: 0.8,
        recommended_pathway: authorityDestination,
      };

      // Apply complainant name/contact updates
      detailsToUse.complainant_name = complainantName || detailsToUse.complainant_name;
      detailsToUse.complainant_contact = complainantContact || detailsToUse.complainant_contact;

      const generated = await generateComplaint({
        details: detailsToUse,
        authority_destination: authorityDestination,
        language: language,
        complainant_address: complainantAddress,
        attached_forensic_report:
          includeForensicEvidence && attachedForensicContext
            ? {
                file_sha256: attachedForensicContext.file_sha256,
                filename: attachedForensicContext.filename,
                overall_tamper_score: attachedForensicContext.overall_tamper_score,
                verdict: attachedForensicContext.verdict,
                image_width: attachedForensicContext.image_width,
                image_height: attachedForensicContext.image_height,
                findings: attachedForensicContext.findings,
                synergy: attachedForensicContext.synergy,
              }
            : undefined,
        custom_narrative_edits: customNarrative || undefined,
      });

      setComplaint(generated);
    } catch (err: any) {
      toast.error(err.message || "Failed to generate formal complaint draft.");
    } finally {
      setIsGenerating(false);
    }
  };

  // Section refinement helper
  const handleRefineNarrative = async (instruction: string) => {
    if (!customNarrative.trim()) return;
    try {
      const res = await regenerateComplaintSection({
        section_name: "narrative",
        current_content: customNarrative,
        instruction: instruction,
        target_language: language,
      });
      setCustomNarrative(res.refined_content);
      toast.success(`Narrative refined: ${instruction}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to refine section");
    }
  };

  // Download PDF
  const handleDownloadPdf = async () => {
    if (!complaint) return;
    setIsDownloadingPdf(true);
    try {
      const blob = await downloadComplaintPdfBlob(complaint);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `VeriSight_Complaint_${complaint.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Formal complaint PDF downloaded");
    } catch (err: any) {
      toast.error(err.message || "Failed to download PDF");
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  // Print
  const handlePrint = () => {
    window.print();
  };

  // Copy Complaint Text
  const handleCopyText = () => {
    if (!complaint) return;
    navigator.clipboard.writeText(complaint.chronological_narrative);
    setCopiedText(true);
    toast.success("Complaint text copied to clipboard");
    setTimeout(() => setCopiedText(false), 2000);
  };

  // Save to Case Tracker
  const handleSaveToCaseTracker = async () => {
    if (!initialDetails && !complaint) return;
    setIsSavingCase(true);
    try {
      const detailsToUse = initialDetails || {
        incident_category: "OTHER_CYBERCRIME",
        incident_category_label: "Cyber Incident",
        financial_impact: "UNCERTAIN",
        currency: "INR",
        narrative_description: customNarrative,
        available_evidence: [],
        is_ongoing: false,
        account_at_risk: false,
        missing_fields: [],
        confidence_score: 0.8,
        recommended_pathway: authorityDestination,
      };

      const newCase = await createCaseRecord({
        details: detailsToUse,
        title: `${detailsToUse.incident_category_label} (${complaint?.id || "Draft"})`,
        forensic_attachment: attachedForensicContext
          ? {
              file_sha256: attachedForensicContext.file_sha256,
              filename: attachedForensicContext.filename,
              overall_tamper_score: attachedForensicContext.overall_tamper_score,
              verdict: attachedForensicContext.verdict,
            }
          : undefined,
      });

      toast.success(`Saved to Case Tracker: ${newCase.case_id}`);
      if (onSavedToCaseTracker) {
        onSavedToCaseTracker(newCase.case_id);
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to save case record");
    } finally {
      setIsSavingCase(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* ------------------------------------------------------------- */}
      {/* Left Column: Complaint Configuration & Complainant Details (5 cols) */}
      {/* ------------------------------------------------------------- */}
      <div className="lg:col-span-5 space-y-4">
        <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-sky-400" />
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-100">
                Destination Authority
              </h3>
            </div>
            <span className="font-mono text-[10px] text-slate-400">
              Jurisdiction: India
            </span>
          </div>

          {/* Authority Radio Selection */}
          <div className="space-y-2">
            {AUTHORITIES.map((auth) => (
              <label
                key={auth.id}
                className={`flex cursor-pointer flex-col rounded-xl border p-3 transition-all ${
                  authorityDestination === auth.id
                    ? "border-sky-500/50 bg-sky-950/30 text-white ring-1 ring-sky-500/30"
                    : "border-white/[0.06] bg-[#070B16] text-slate-300 hover:border-white/20"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="authority"
                      value={auth.id}
                      checked={authorityDestination === auth.id}
                      onChange={(e) => setAuthorityDestination(e.target.value)}
                      className="text-sky-500 focus:ring-0"
                    />
                    <span className="text-xs font-semibold">{auth.name}</span>
                  </div>
                </div>
                <span className="ml-5 mt-1 text-[10px] text-slate-400 font-sans">
                  {auth.tag}
                </span>
              </label>
            ))}
          </div>

          {/* Language Selection */}
          <div className="space-y-1.5 pt-2 border-t border-white/[0.06]">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Languages className="h-3.5 w-3.5 text-sky-400" />
                Draft Language:
              </span>
            </div>
            <div className="grid grid-cols-3 gap-1.5">
              {LANGUAGES.map((l) => (
                <button
                  key={l.code}
                  type="button"
                  onClick={() => setLanguage(l.code)}
                  className={`rounded-lg border px-2 py-1.5 font-mono text-[11px] transition-all ${
                    language === l.code
                      ? "border-sky-500/50 bg-sky-500/20 text-sky-200 font-semibold"
                      : "border-white/[0.06] bg-[#070B16] text-slate-400 hover:text-slate-200 hover:bg-white/5"
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          {/* Complainant Identity Details */}
          <div className="space-y-2.5 pt-2 border-t border-white/[0.06]">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              Complainant Information
            </span>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-400 font-mono mb-1">
                  FULL LEGAL NAME
                </label>
                <input
                  type="text"
                  value={complainantName}
                  onChange={(e) => setComplainantName(e.target.value)}
                  placeholder="e.g. Ramesh Kumar"
                  className="w-full rounded-lg border border-white/10 bg-[#060911] px-2.5 py-1.5 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 font-mono mb-1">
                  PHONE / CONTACT
                </label>
                <input
                  type="text"
                  value={complainantContact}
                  onChange={(e) => setComplainantContact(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="w-full rounded-lg border border-white/10 bg-[#060911] px-2.5 py-1.5 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 font-mono mb-1">
                RESIDENCE ADDRESS / JURISDICTION (OPTIONAL)
              </label>
              <input
                type="text"
                value={complainantAddress}
                onChange={(e) => setComplainantAddress(e.target.value)}
                placeholder="e.g. Indiranagar, Bengaluru, Karnataka"
                className="w-full rounded-lg border border-white/10 bg-[#060911] px-2.5 py-1.5 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Narrative Editor & Refinement */}
          <div className="space-y-1.5 pt-2 border-t border-white/[0.06]">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                Chronological Narrative
              </span>
              <div className="flex items-center gap-1 text-[10px] text-slate-400">
                <button
                  type="button"
                  onClick={() => handleRefineNarrative("make_more_formal")}
                  className="rounded px-1.5 py-0.5 hover:bg-white/10 text-sky-400"
                  title="Rewrite in formal legal-evidentiary tone"
                >
                  Formalize
                </button>
                <span>•</span>
                <button
                  type="button"
                  onClick={() => handleRefineNarrative("clarity")}
                  className="rounded px-1.5 py-0.5 hover:bg-white/10 text-sky-400"
                  title="Improve sentence clarity and chronology"
                >
                  Clarity
                </button>
              </div>
            </div>

            <textarea
              value={customNarrative}
              onChange={(e) => setCustomNarrative(e.target.value)}
              placeholder="State exactly what occurred chronologically..."
              rows={4}
              className="w-full rounded-xl border border-white/10 bg-[#060911] p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:border-sky-500 focus:outline-none font-sans"
            />
          </div>

          {/* Forensic Attachment Toggle */}
          {attachedForensicContext && (
            <div className="rounded-xl border border-sky-500/30 bg-sky-950/20 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-semibold uppercase tracking-wider text-sky-300">
                  Forensic Workbench Evidence
                </span>
                <label className="flex items-center gap-1.5 text-[11px] font-mono text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeForensicEvidence}
                    onChange={(e) => setIncludeForensicEvidence(e.target.checked)}
                    className="rounded text-sky-500 focus:ring-0"
                  />
                  <span>Attach to Complaint</span>
                </label>
              </div>
              <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
                Includes SHA-256 hash <code className="text-sky-300">{attachedForensicContext.file_sha256.slice(0, 12)}...</code>,
                heuristic review score ({attachedForensicContext.overall_tamper_score.toFixed(1)}/100), and baseline laser / wavelet anomalies in Annexure.
              </p>
            </div>
          )}

          {/* Manual Rebuild Button */}
          <button
            type="button"
            onClick={handleBuildDraft}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-white/5 py-2 font-mono text-xs font-semibold text-slate-200 hover:bg-white/10 active:scale-[0.98]"
          >
            <RotateCcw className="h-3.5 w-3.5 text-slate-400" />
            <span>{isGenerating ? "Synthesizing Complaint..." : "Update Complaint Draft"}</span>
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* Right Column: Live Formal Document Preview Workspace (7 cols) */}
      {/* ------------------------------------------------------------- */}
      <div className="lg:col-span-7 space-y-4">
        {/* Document Action Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-3.5 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="rounded bg-sky-950/80 px-2 py-0.5 font-mono text-[10px] font-bold text-sky-300 border border-sky-800/40">
              DRAFT PREVIEW
            </span>
            <span className="font-mono text-xs text-slate-300">
              {complaint ? complaint.id : "Generating..."}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyText}
              disabled={!complaint}
              className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#0C1222] px-3 py-1.5 text-xs font-mono text-slate-300 hover:bg-white/10 active:scale-[0.98]"
              title="Copy formatted complaint text"
            >
              {copiedText ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5 text-slate-400" />
                  <span>Copy</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={handlePrint}
              disabled={!complaint}
              className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#0C1222] px-3 py-1.5 text-xs font-mono text-slate-300 hover:bg-white/10 active:scale-[0.98]"
              title="Print complaint or save via browser PDF"
            >
              <Printer className="h-3.5 w-3.5 text-slate-400" />
              <span>Print</span>
            </button>

            <button
              type="button"
              onClick={handleDownloadPdf}
              disabled={!complaint || isDownloadingPdf}
              className="flex items-center gap-1.5 rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-mono font-semibold text-white hover:bg-sky-500 shadow-md shadow-sky-600/30 active:scale-[0.98]"
              title="Download complaint draft PDF"
            >
              <Download className="h-3.5 w-3.5" />
              <span>{isDownloadingPdf ? "Building PDF..." : "Download PDF"}</span>
            </button>

            <button
              type="button"
              onClick={handleSaveToCaseTracker}
              disabled={!complaint || isSavingCase}
              className="flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/20 px-3 py-1.5 text-xs font-mono font-semibold text-emerald-300 hover:bg-emerald-500/30 active:scale-[0.98]"
              title="Save to Case Tracker to record acknowledgement numbers"
            >
              <Save className="h-3.5 w-3.5" />
              <span>{isSavingCase ? "Saving..." : "Save Case"}</span>
            </button>
          </div>
        </div>

        {/* The Formal Document Paper Sheet Preview */}
        <div className="rounded-2xl border border-white/[0.08] bg-[#0E1528]/95 p-6 shadow-2xl backdrop-blur-md space-y-5 text-slate-100 min-h-[580px] font-sans">
          {complaint ? (
            <div className="space-y-5">
              {/* Document Header */}
              <div className="border-b border-white/10 pb-4 text-center space-y-1">
                <span className="font-mono text-[9px] tracking-widest text-sky-400 uppercase font-semibold">
                  PERSONAL COMPLAINT DRAFT — REVIEW BEFORE USE
                </span>
                <h2 className="text-lg font-bold text-white tracking-wide">
                  {complaint.title}
                </h2>
                <div className="text-[11px] text-slate-400 font-mono">
                  Destination: <strong className="text-slate-200">{complaint.destination_authority_name}</strong> • Language: {complaint.language.toUpperCase()}
                </div>
              </div>

              {/* Metadata Key Details Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 rounded-xl border border-white/[0.08] bg-[#0A0F1F] p-3 text-xs font-mono">
                <div>
                  <span className="text-[9px] text-slate-500 block">COMPLAINANT</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {complaint.complainant_name || "Complainant"}
                  </span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-500 block">REPORTED AMOUNT</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {complaint.financial_details.claimed_amount > 0
                      ? `₹${complaint.financial_details.claimed_amount.toLocaleString()}`
                      : "₹0.00 (Zero loss)"}
                  </span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-500 block">TXN REF / UTR</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {complaint.transaction_reference}
                  </span>
                </div>
                <div>
                  <span className="text-[9px] text-slate-500 block">SUSPECT ENTITY</span>
                  <span className="font-semibold text-slate-200 truncate block">
                    {complaint.suspected_entity.name_or_alias}
                  </span>
                </div>
              </div>

              {/* Narrative Content */}
              <div className="space-y-4 text-xs leading-relaxed text-slate-200 font-sans whitespace-pre-line bg-[#090D1A] p-4 rounded-xl border border-white/[0.05]">
                {complaint.chronological_narrative}
              </div>

              {/* Annexure Inventory */}
              {complaint.supporting_document_index.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-white/10">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                    Annexure & Evidence Inventory
                  </h4>
                  <ul className="space-y-1 text-xs text-slate-400 font-mono">
                    {complaint.supporting_document_index.map((ann, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-sky-400" />
                        <span>{ann}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Disclaimer */}
              <div className="pt-3 border-t border-white/[0.08] text-[10px] leading-relaxed text-slate-500 italic font-sans text-center">
                {complaint.disclaimer}
              </div>
            </div>
          ) : (
            <div className="flex h-96 flex-col items-center justify-center text-center text-slate-500 space-y-2">
              <FileText className="h-10 w-10 stroke-[1.2] text-slate-600 animate-pulse" />
              <span className="font-mono text-xs">
                Drafting formal complaint from incident facts...
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
