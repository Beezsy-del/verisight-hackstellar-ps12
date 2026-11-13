import React, { useState } from "react";
import {
  PhoneCall,
  ShieldAlert,
  AlertTriangle,
  Mic,
  FileText,
  Search,
  Clock,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  CreditCard,
  QrCode,
  UserX,
  HelpCircle,
  ShoppingBag,
  Link2,
  Copy,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { CaseRecord, IncidentCategory } from "../../types/response";
import { RealWorldCaseShowcase } from "../RealWorldCaseShowcase";

interface IncidentCentreProps {
  onNavigateTab: (tab: string, initialCategory?: IncidentCategory) => void;
  cases: CaseRecord[];
  hasAttachedForensicContext: boolean;
}

const CATEGORIES: Array<{
  id: IncidentCategory;
  name: string;
  tagline: string;
  destination: string;
  urgency: "CRITICAL" | "HIGH" | "ADVISORY";
  icon: React.ElementType;
}> = [
  {
    id: "FAKE_PAYMENT_SCREENSHOT",
    name: "Fake Payment Screenshot",
    tagline: "Counterparty showed a forged UPI / bank confirmation screenshot but zero money was credited.",
    destination: "NCRP 1930 / Bank Dispute",
    urgency: "HIGH",
    icon: FileText,
  },
  {
    id: "UNAUTHORIZED_BANK_TRANSACTION",
    name: "Unauthorized Bank Debit",
    tagline: "Money was debited from your savings/current account or card without your authorization or OTP.",
    destination: "1930 Helpline + Issuing Bank",
    urgency: "CRITICAL",
    icon: CreditCard,
  },
  {
    id: "UPI_FRAUD",
    name: "UPI Collect Request / PIN Scam",
    tagline: "Tricked into entering your UPI PIN under the pretense of receiving money or unlocking cashback.",
    destination: "1930 Helpline + NPCI Portal",
    urgency: "CRITICAL",
    icon: ShieldAlert,
  },
  {
    id: "QR_CODE_FRAUD",
    name: "QR Code 'Scan to Receive' Scam",
    tagline: "Scammed into scanning a fraudulent QR code which debited your account instead of crediting funds.",
    destination: "1930 Helpline + Issuing Bank",
    urgency: "CRITICAL",
    icon: QrCode,
  },
  {
    id: "ONLINE_MARKETPLACE_FRAUD",
    name: "Marketplace Fraud (OLX / Quikr)",
    tagline: "Buyer/Seller scam on peer-to-peer marketplaces involving advance fees or fake courier receipts.",
    destination: "NCRP + Platform Support",
    urgency: "HIGH",
    icon: ShoppingBag,
  },
  {
    id: "PHISHING_SOCIAL_ENGINEERING",
    name: "Phishing & Remote App Scam",
    tagline: "Deceived into installing remote access APKs (AnyDesk, TeamViewer) or clicking electricity/KYC links.",
    destination: "1930 + Device Disconnect",
    urgency: "CRITICAL",
    icon: Link2,
  },
  {
    id: "IMPERSONATION",
    name: "Authority Impersonation",
    tagline: "Scammer posed as police, customs, bank manager, or defense personnel demanding funds.",
    destination: "Cyber Police + Platform",
    urgency: "HIGH",
    icon: UserX,
  },
  {
    id: "DIGITAL_PAYMENT_DISPUTE",
    name: "Digital Payment Dispute",
    tagline: "Transaction debited but pending at merchant; lack of refund within statutory NPCI turnaround time.",
    destination: "Bank Nodal Officer / RBI CMS",
    urgency: "ADVISORY",
    icon: Clock,
  },
  {
    id: "IDENTITY_MISUSE",
    name: "Identity & KYC Misuse",
    tagline: "Aadhaar, PAN, or personal documents used to fraudulently open SIM cards or digital loan accounts.",
    destination: "NCRP + UIDAI / DoT Sanchar Saathi",
    urgency: "HIGH",
    icon: ShieldCheck,
  },
  {
    id: "SUSPICIOUS_TRANSACTION_EVIDENCE",
    name: "Suspicious Payment Evidence",
    tagline: "Evaluating doubtful digital receipts, altered transaction IDs, or non-standard font baselines.",
    destination: "Forensic Workbench / Review",
    urgency: "ADVISORY",
    icon: AlertTriangle,
  },
  {
    id: "PAYMENT_FRAUD",
    name: "Other Payment Fraud",
    tagline: "Investment group, work-from-home task scam, or crypto deposit deception.",
    destination: "NCRP 1930 + Cyber Police",
    urgency: "CRITICAL",
    icon: CreditCard,
  },
  {
    id: "OTHER_CYBERCRIME",
    name: "Other Cyber Incident",
    tagline: "Cyberstalking, unauthorized account takeover, social media impersonation, or data breach.",
    destination: "NCRP Portal (cybercrime.gov.in)",
    urgency: "HIGH",
    icon: HelpCircle,
  },
];

export const IncidentCentre: React.FC<IncidentCentreProps> = ({
  onNavigateTab,
  cases,
  hasAttachedForensicContext,
}) => {
  const [copiedHelpline, setCopiedHelpline] = useState(false);

  const handleCopyHelpline = () => {
    navigator.clipboard.writeText("1930");
    setCopiedHelpline(true);
    toast.success("Cybercrime Helpline 1930 copied to clipboard");
    setTimeout(() => setCopiedHelpline(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* 1. Emergency Golden Hour Triage Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-rose-500/40 bg-gradient-to-r from-rose-950/60 via-[#130d1b]/80 to-[#0e1628]/80 p-5 shadow-2xl backdrop-blur-md">
        <div className="relative z-10 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-1.5 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500" />
              </span>
              <span className="font-mono text-xs font-bold tracking-wider uppercase text-rose-300">
                CRITICAL FINANCIAL CYBER FRAUD TRIAGE
              </span>
              <span className="rounded bg-rose-900/80 px-2 py-0.5 font-mono text-[10px] text-rose-200 border border-rose-700/60 font-semibold">
                REPORT PROMPTLY
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white font-sans">
              Have you suffered an unauthorized financial debit in India?
            </h2>
            <p className="text-xs leading-relaxed text-slate-300 font-sans">
              Report suspected financial cybercrime promptly through the official channels below and contact your bank. Reporting does not guarantee that funds can be frozen or recovered.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <button
              onClick={handleCopyHelpline}
              className="flex items-center gap-2 rounded-xl border border-rose-500/50 bg-rose-500/20 px-4 py-2.5 font-mono text-xs font-semibold text-rose-200 transition-all hover:bg-rose-500/30 active:scale-[0.98] shadow-md shadow-rose-950/40"
              title="Copy Helpline 1930"
            >
              <PhoneCall className="h-4 w-4 text-rose-400" />
              <span>DIAL 1930</span>
              {copiedHelpline ? (
                <Check className="h-3.5 w-3.5 text-emerald-400" />
              ) : (
                <Copy className="h-3.5 w-3.5 text-rose-300 opacity-70" />
              )}
            </button>

            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 rounded-xl border border-white/15 bg-white/10 px-4 py-2.5 font-mono text-xs font-medium text-slate-200 transition-all hover:bg-white/15 hover:text-white active:scale-[0.98]"
            >
              <span>cybercrime.gov.in</span>
              <ExternalLink className="h-3.5 w-3.5 text-slate-400" />
            </a>
          </div>
        </div>
      </div>

      {/* 2. Fast Navigation Entry Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Pillar 1: Voice Reporting Assistant */}
        <div
          onClick={() => onNavigateTab("voice")}
          className="group relative cursor-pointer overflow-hidden rounded-xl border border-sky-500/30 bg-[#0B1224]/80 p-5 transition-all hover:border-sky-400 hover:bg-[#0E172E] hover:shadow-xl active:scale-[0.99]"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-sky-500/40 bg-sky-500/20 text-sky-400 shadow-sm group-hover:scale-105 transition-transform">
              <Mic className="h-5 w-5" />
            </div>
            <span className="font-mono text-[10px] text-sky-300 font-semibold bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800/40">
              MULTILINGUAL SPEECH
            </span>
          </div>
          <h3 className="text-sm font-semibold text-white group-hover:text-sky-300 transition-colors">
            Voice Incident Assistant
          </h3>
          <p className="mt-1 text-xs text-slate-400 leading-relaxed font-sans">
            Explain what happened in your own words (English, Hindi, Kannada, Bengali, Tamil, Telugu, Marathi). VeriSight extracts structured evidence and asks smart follow-ups.
          </p>
          <div className="mt-4 flex items-center gap-1 font-mono text-[11px] text-sky-400 group-hover:translate-x-1 transition-transform">
            <span>Start Voice Intake</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </div>
        </div>

        {/* Pillar 2: Complaint Builder */}
        <div
          onClick={() => onNavigateTab("builder")}
          className="group relative cursor-pointer overflow-hidden rounded-xl border border-amber-500/30 bg-[#16120B]/80 p-5 transition-all hover:border-amber-400 hover:bg-[#1C170E] hover:shadow-xl active:scale-[0.99]"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-amber-500/40 bg-amber-500/20 text-amber-400 shadow-sm group-hover:scale-105 transition-transform">
              <FileText className="h-5 w-5" />
            </div>
            <span className="font-mono text-[10px] text-amber-300 font-semibold bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/40">
              FORMAL DRAFTING
            </span>
          </div>
          <h3 className="text-sm font-semibold text-white group-hover:text-amber-300 transition-colors">
            Complaint Builder
          </h3>
          <p className="mt-1 text-xs text-slate-400 leading-relaxed font-sans">
            Generate an editable, factual complaint formatted for NCRP, Bank Nodal Officers, or RBI Ombudsman. Attach forensic image hashes and download print-ready PDF.
          </p>
          <div className="mt-4 flex items-center gap-1 font-mono text-[11px] text-amber-400 group-hover:translate-x-1 transition-transform">
            <span>Open Document Editor</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </div>
        </div>

        {/* Pillar 3: Official Reporting Directory */}
        <div
          onClick={() => onNavigateTab("directory")}
          className="group relative cursor-pointer overflow-hidden rounded-xl border border-emerald-500/30 bg-[#0B1A14]/80 p-5 transition-all hover:border-emerald-400 hover:bg-[#0E221A] hover:shadow-xl active:scale-[0.99]"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-500/40 bg-emerald-500/20 text-emerald-400 shadow-sm group-hover:scale-105 transition-transform">
              <Search className="h-5 w-5" />
            </div>
            <span className="font-mono text-[10px] text-emerald-300 font-semibold bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/40">
              VERIFIED PORTALS
            </span>
          </div>
          <h3 className="text-sm font-semibold text-white group-hover:text-emerald-300 transition-colors">
            Reporting Directory
          </h3>
          <p className="mt-1 text-xs text-slate-400 leading-relaxed font-sans">
            Search verified helplines and submission requirements across NCRP 1930, Bank Grievance Cells, NPCI, RBI Integrated Ombudsman, and Zero FIR police guidelines.
          </p>
          <div className="mt-4 flex items-center gap-1 font-mono text-[11px] text-emerald-400 group-hover:translate-x-1 transition-transform">
            <span>Explore Directory</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </div>
        </div>
      </div>

      {/* 3. Active Tracked Incidents Mini-Widget */}
      {cases.length > 0 && (
        <div className="rounded-xl border border-white/[0.08] bg-[#0A0E1A]/80 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-sky-400" />
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
                Active Incident Response Cases ({cases.length})
              </h3>
            </div>
            <button
              onClick={() => onNavigateTab("tracking")}
              className="font-mono text-[11px] text-sky-400 hover:text-sky-300 flex items-center gap-1"
            >
              <span>View All Cases</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {cases.slice(0, 2).map((c) => (
              <div
                key={c.case_id}
                onClick={() => onNavigateTab("tracking")}
                className="cursor-pointer rounded-lg border border-white/[0.07] bg-[#0C1222] p-3 transition-colors hover:border-white/20"
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
                <h4 className="text-xs font-semibold text-slate-200 truncate">
                  {c.title}
                </h4>
                <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>
                    Loss: {c.financial_loss > 0 ? `₹${c.financial_loss.toLocaleString()}` : "Zero loss (Prevented)"}
                  </span>
                  <span>{c.updated_at.slice(0, 10)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. Incident Category Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100 font-sans">
              Select Incident Classification to Begin
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              Choose the category that matches what happened to receive tailored guidance and question flow.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isCritical = cat.urgency === "CRITICAL";
            const isHigh = cat.urgency === "HIGH";

            return (
              <div
                key={cat.id}
                onClick={() => onNavigateTab("voice", cat.id)}
                className="group cursor-pointer rounded-xl border border-white/[0.08] bg-[#0A0F1D]/80 p-3.5 transition-all hover:border-sky-500/40 hover:bg-[#0E1528] active:scale-[0.99] flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-slate-300 group-hover:text-sky-400 group-hover:border-sky-500/30 transition-colors">
                      <Icon className="h-3.5 w-3.5" />
                    </div>
                    <span
                      className={`rounded px-1.5 py-0.2 font-mono text-[8px] font-bold tracking-wider uppercase ${
                        isCritical
                          ? "bg-rose-950/80 text-rose-300 border border-rose-800/40"
                          : isHigh
                          ? "bg-amber-950/80 text-amber-300 border border-amber-800/40"
                          : "bg-slate-800 text-slate-300 border border-slate-700"
                      }`}
                    >
                      {cat.urgency}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-200 group-hover:text-sky-300 transition-colors">
                    {cat.name}
                  </h4>
                  <p className="mt-1 text-[11px] leading-relaxed text-slate-400 font-sans line-clamp-2">
                    {cat.tagline}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-white/[0.05] flex items-center justify-between font-mono text-[9px] text-slate-400">
                  <span className="truncate max-w-[170px]" title={cat.destination}>
                    {cat.destination}
                  </span>
                  <span className="text-sky-400 group-hover:translate-x-0.5 transition-transform flex items-center">
                    Report <ChevronRight className="h-3 w-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. Real-World Documented Fraud Cases Showcase */}
      <div className="pt-6 border-t border-white/[0.08]">
        <RealWorldCaseShowcase
          onNavigateResponse={(cat) => onNavigateTab("voice", cat as any)}
        />
      </div>
    </div>
  );
};
