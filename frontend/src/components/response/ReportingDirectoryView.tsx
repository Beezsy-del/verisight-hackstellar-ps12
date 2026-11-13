import React, { useState, useEffect } from "react";
import {
  Search,
  Building2,
  ExternalLink,
  PhoneCall,
  Mail,
  ShieldCheck,
  FileCheck,
  Clock,
  ChevronRight,
  Filter,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { ReportingAuthority } from "../../types/response";
import { fetchReportingDirectory } from "../../services/api";

const CATEGORY_TABS = [
  { id: "ALL", label: "All Pathways" },
  { id: "NATIONAL_PORTAL", label: "National Cyber Portal (1930)" },
  { id: "BANK_UPI", label: "Banks & UPI PSPs" },
  { id: "REGULATOR_RBI", label: "RBI Ombudsman (CMS)" },
  { id: "POLICE", label: "Cyber Police & Zero FIR" },
  { id: "PLATFORM", label: "Platform Abuse" },
];

export const ReportingDirectoryView: React.FC = () => {
  const [authorities, setAuthorities] = useState<ReportingAuthority[]>([]);
  const [activeCategory, setActiveCategory] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAuthority, setSelectedAuthority] = useState<ReportingAuthority | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    void loadAuthorities();
  }, [activeCategory, searchQuery]);

  const loadAuthorities = async () => {
    setIsLoading(true);
    try {
      const data = await fetchReportingDirectory(activeCategory, searchQuery);
      setAuthorities(data);
      if (data.length > 0 && !selectedAuthority) {
        setSelectedAuthority(data[0]);
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to load directory.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    toast.success(`Copied: ${text}`);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-5 shadow-xl backdrop-blur-md">
        <div>
          <h2 className="text-base font-bold text-white font-sans flex items-center gap-2">
            <Building2 className="h-5 w-5 text-sky-400" />
            Verified Indian Cybercrime & Financial Reporting Directory
          </h2>
          <p className="mt-0.5 text-xs text-slate-400 font-sans">
            Current statutory submission procedures, helplines, waiting periods, and escalation routes across India.
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by bank, portal, or fraud type..."
            className="w-full rounded-xl border border-white/10 bg-[#060911] pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:border-sky-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-white/[0.08] pb-3">
        {CATEGORY_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveCategory(tab.id)}
            className={`rounded-lg px-3 py-1.5 font-mono text-xs transition-all ${
              activeCategory === tab.id
                ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Directory Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Authority List (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          {isLoading ? (
            <div className="p-8 text-center font-mono text-xs text-slate-500">
              Loading verified reporting directory...
            </div>
          ) : authorities.length === 0 ? (
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0E1A]/80 p-6 text-center font-mono text-xs text-slate-500">
              No authorities found matching "{searchQuery}".
            </div>
          ) : (
            authorities.map((auth) => {
              const isSelected = selectedAuthority?.id === auth.id;

              return (
                <div
                  key={auth.id}
                  onClick={() => setSelectedAuthority(auth)}
                  className={`group cursor-pointer rounded-xl border p-4 transition-all ${
                    isSelected
                      ? "border-sky-500/50 bg-[#0E172E] shadow-lg ring-1 ring-sky-500/30"
                      : "border-white/[0.08] bg-[#0A0E1A]/80 hover:border-white/20 hover:bg-[#0C1222]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="rounded bg-sky-950/80 px-2 py-0.5 font-mono text-[9px] font-semibold text-sky-300 border border-sky-800/40">
                      {auth.category.replace(/_/g, " ")}
                    </span>
                    <span className="font-mono text-[10px] text-slate-400">
                      Verified {auth.last_verified_date}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-white group-hover:text-sky-300 transition-colors">
                    {auth.name}
                  </h3>

                  <p className="mt-1 text-xs text-slate-400 font-sans line-clamp-2">
                    {auth.type_of_complaint}
                  </p>

                  <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-slate-500">
                    <span className="truncate max-w-[200px]">{auth.jurisdiction}</span>
                    <span className="text-sky-400 flex items-center gap-0.5">
                      View Guide <ChevronRight className="h-3 w-3" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Detailed Authority Dossier (7 cols) */}
        <div className="lg:col-span-7">
          {selectedAuthority ? (
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/95 p-6 shadow-2xl backdrop-blur-md space-y-5">
              {/* Header */}
              <div className="border-b border-white/[0.06] pb-4 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-sky-400">
                    {selectedAuthority.category.replace(/_/g, " ")}
                  </span>
                  <a
                    href={selectedAuthority.official_website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 font-mono text-xs text-sky-400 hover:text-sky-300 hover:underline"
                  >
                    <span>Visit Official Portal</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>

                <h2 className="text-lg font-bold text-white font-sans">
                  {selectedAuthority.name}
                </h2>

                <div className="text-xs text-slate-300 font-sans">
                  Jurisdiction: <span className="text-white font-medium">{selectedAuthority.jurisdiction}</span>
                </div>
              </div>

              {/* Verified Contact Details Grid */}
              <div className="space-y-2">
                <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Verified Contact Information
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-xs">
                  {Object.entries(selectedAuthority.contact_information).map(([key, val]) => (
                    <div
                      key={key}
                      onClick={() => handleCopy(val, key)}
                      className="group cursor-pointer rounded-lg border border-white/[0.06] bg-[#0C1222] p-2.5 transition-colors hover:border-sky-500/30"
                      title="Click to copy contact details"
                    >
                      <div className="flex items-center justify-between text-[9px] text-slate-500 uppercase mb-0.5">
                        <span>{key.replace(/_/g, " ")}</span>
                        {copiedKey === key ? (
                          <Check className="h-3 w-3 text-emerald-400" />
                        ) : (
                          <Copy className="h-3 w-3 text-slate-500 group-hover:text-sky-300 transition-colors" />
                        )}
                      </div>
                      <span className="text-slate-200 font-medium truncate block">
                        {val}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Step-by-Step Submission Procedure */}
              <div className="space-y-2">
                <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Statutory Submission Procedure
                </h4>
                <div className="space-y-2">
                  {selectedAuthority.submission_procedure.map((step, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-white/[0.05] bg-[#070B16] p-3 text-xs leading-relaxed text-slate-300 font-sans"
                    >
                      {step}
                    </div>
                  ))}
                </div>
              </div>

              {/* Required Documents Checklist */}
              <div className="space-y-2">
                <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Required Evidence & Documents Checklist
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {selectedAuthority.required_documents.map((doc, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2 rounded-lg border border-white/[0.04] bg-[#0C1222] p-2.5 text-xs text-slate-300 font-sans"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{doc}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Escalation Route & Prerequisites */}
              <div className="space-y-2 rounded-xl border border-white/[0.06] bg-[#070B16] p-4 text-xs font-sans space-y-2">
                <div className="text-slate-200">
                  <strong className="text-white font-mono uppercase text-[10px] block mb-1">
                    Applicable Escalation Route:
                  </strong>
                  <span className="text-slate-300">{selectedAuthority.escalation_route}</span>
                </div>

                {selectedAuthority.prerequisites && (
                  <div className="pt-2 border-t border-white/[0.05] text-slate-300">
                    <strong className="text-amber-400 font-mono uppercase text-[10px] block mb-1">
                      Statutory Prerequisites & Waiting Period:
                    </strong>
                    <ul className="list-disc pl-4 space-y-1 text-slate-400">
                      {selectedAuthority.prerequisites.map((req, i) => (
                        <li key={i}>{req}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Source Reference & Official Disclaimer */}
              <div className="pt-2 border-t border-white/[0.06] text-[10px] text-slate-500 font-mono space-y-1">
                <div>Source: {selectedAuthority.source_reference}</div>
                {selectedAuthority.disclaimer && (
                  <div className="italic text-slate-400 font-sans">
                    {selectedAuthority.disclaimer}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex h-96 items-center justify-center rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 text-slate-500 font-mono text-xs">
              Select an authority from the directory to view its submission guide.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
