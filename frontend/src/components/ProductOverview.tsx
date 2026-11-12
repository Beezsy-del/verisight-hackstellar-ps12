import { ReviewLimitations } from "./ReviewLimitations";
import React, { useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  Layers,
  Sparkles,
  Search,
  FileCheck2,
  Cpu,
  Fingerprint,
  Scale,
  Lock,
  Eye,
  AlertTriangle,
  Activity,
  Sliders,
  ChevronRight,
  HelpCircle,
  BarChart3,
  Terminal,
  Compass,
} from "lucide-react";
import { AppRoute } from "./NavigationHeader";
import { DemoSampleMeta } from "../types/forensic";

interface ProductOverviewProps {
  onNavigate: (route: AppRoute, query?: Record<string, string>) => void;
  demoSamples?: DemoSampleMeta[];
}

export const ProductOverview: React.FC<ProductOverviewProps> = ({
  onNavigate,
  demoSamples = [],
}) => {
  // Interactive Hero Preview state
  const [activePreviewLayer, setActivePreviewLayer] = useState<
    "ORIGINAL" | "ELA" | "WAVELET" | "LASER"
  >("ELA");

  const samples = demoSamples;

  return (
    <div className="relative min-h-[calc(100vh-3.5rem)] w-full overflow-y-auto bg-[#060911] text-slate-100 selection:bg-sky-500/30 selection:text-sky-200">
      {/* Background radial glow */}
      <div className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[600px] w-[1000px] -translate-x-1/2 rounded-full bg-gradient-to-b from-sky-500/10 via-indigo-500/5 to-transparent blur-[140px]" />

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {/* =========================================================================
            SECTION A: HERO NARRATIVE & DUAL CTA
        ========================================================================= */}
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12 lg:gap-8 pt-4 pb-16">
          <div className="lg:col-span-7 space-y-6">
            {/* Eyebrow badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-sky-500/30 bg-sky-950/40 px-3.5 py-1 text-xs font-mono font-medium text-sky-400 backdrop-blur-md">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500" />
              </span>
              <span>DIGITAL PAYMENT EVIDENCE FORENSICS</span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">v1.0 · heuristic</span>
            </div>

            {/* Headline */}
            <h1 className="text-3xl font-extrabold tracking-tight sm:text-5xl lg:text-5xl text-white leading-tight">
              Investigate the integrity of{" "}
              <span className="bg-gradient-to-r from-sky-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
                payment screenshots.
              </span>
            </h1>

            {/* Supporting paragraph */}
            <p className="text-base text-slate-300 sm:text-lg leading-relaxed max-w-2xl font-sans">Inspect pixel residuals, text-like geometry, metadata, and readable QR payloads. VeriSight provides review cues; it does not prove authenticity, detect every edit, or verify a payment.</p>

            <ReviewLimitations />

            {/* Dual CTAs */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => onNavigate("/workbench")}
                className="group flex items-center gap-2.5 rounded-lg border border-sky-400/40 bg-gradient-to-r from-sky-500 to-sky-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition-all hover:from-sky-400 hover:to-sky-500 hover:shadow-sky-500/30 active:scale-[0.98]"
              >
                <span>Launch Forensic Workbench</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>

              <a
                href="#demo-gallery"
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-[#0c1222] px-5 py-3 text-sm font-medium text-slate-200 shadow-sm transition-all hover:bg-white/[0.06] hover:text-white hover:border-white/20 active:scale-[0.98]"
              >
                <span>Explore Demonstration Cases</span>
                <ChevronRight className="h-4 w-4 text-slate-400" />
              </a>

              <button
                onClick={() => onNavigate("/evaluation")}
                className="flex items-center gap-1.5 px-3 py-3 text-xs font-mono text-slate-400 hover:text-sky-300 transition-colors"
              >
                <BarChart3 className="h-3.5 w-3.5" />
                <span>View Live Evaluation Telemetry</span>
              </button>
            </div>

            {/* Quick trust metrics */}
            <div className="pt-4 grid grid-cols-3 gap-4 border-t border-white/[0.08] text-xs font-mono">
              <div>
                <span className="block text-slate-400">Multi-Spectral</span>
                <span className="text-sm font-semibold text-white">4 Core Layers</span>
              </div>
              <div>
                <span className="block text-slate-400">Review Report</span>
                <span className="text-sm font-semibold text-emerald-400">Printable findings</span>
              </div>
              <div>
                <span className="block text-slate-400">Analysis Privacy</span>
                <span className="text-sm font-semibold text-sky-400">Optional summary saving</span>
              </div>
            </div>
          </div>

          {/* Interactive Live Preview Component */}
          <div className="lg:col-span-5">
            <div className="relative rounded-2xl border border-white/[0.12] bg-[#0A0F1D]/90 p-4 shadow-2xl backdrop-blur-xl">
              {/* Header bar of preview */}
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-rose-500 inline-block animate-pulse" />
                  <span className="font-mono text-xs font-semibold text-slate-200">
                    ILLUSTRATIVE LAYER PREVIEW
                  </span>
                </div>
                <span className="font-mono text-[10px] text-amber-400 bg-amber-950/60 border border-amber-800/40 px-2 py-0.5 rounded">
                  ILLUSTRATION · NOT A RESULT
                </span>
              </div>

              {/* Spectral layer tabs */}
              <div className="mt-3 flex gap-1 rounded-lg bg-[#060A14] p-1 border border-white/[0.06] text-[11px] font-mono">
                {[
                  { id: "ORIGINAL", label: "01 Original" },
                  { id: "ELA", label: "02 ELA Heatmap" },
                  { id: "WAVELET", label: "03 Wavelet HF" },
                  { id: "LASER", label: "04 Laser Drift" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActivePreviewLayer(tab.id as any)}
                    className={`flex-1 rounded py-1 text-center font-medium transition-all ${
                      activePreviewLayer === tab.id
                        ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm"
                        : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Visual viewport simulator */}
              <div className="relative mt-3 h-[290px] w-full overflow-hidden rounded-xl border border-white/[0.08] bg-[#03060C] flex flex-col items-center justify-center">
                {/* Simulated UPI Card */}
                <div className="relative w-[85%] max-w-[280px] rounded-lg border border-white/[0.12] bg-[#0E1526] p-4 shadow-xl">
                  {/* Top Bar */}
                  <div className="flex items-center justify-between border-b border-white/[0.06] pb-2 text-[10px] font-mono text-slate-400">
                    <span>Google Pay UPI</span>
                    <span>14:32 IST</span>
                  </div>

                  {/* Payment Body */}
                  <div className="mt-3 text-center space-y-1">
                    <p className="text-[11px] text-slate-400 font-sans">Payment to Merchant</p>
                    <p className="text-xs font-semibold text-slate-200">APOLLO PHARMACY PVT</p>

                    {/* Amount Block with Layer Overlays */}
                    <div className="relative my-3 inline-block rounded border px-3 py-1.5 transition-all">
                      {activePreviewLayer === "ORIGINAL" && (
                        <div className="border-transparent">
                          <span className="text-xl font-bold font-mono text-white">₹95,250.00</span>
                          <span className="block text-[9px] text-slate-400">Illustrative interface</span>
                        </div>
                      )}

                      {activePreviewLayer === "ELA" && (
                        <div className="relative rounded bg-rose-950/70 border border-rose-500/60 p-1 shadow-[0_0_15px_rgba(244,63,94,0.3)]">
                          <span className="text-xl font-bold font-mono text-rose-300">₹95,250.00</span>
                          <span className="block text-[9px] font-mono text-rose-400 font-semibold">
                            Illustrative residual overlay
                          </span>
                        </div>
                      )}

                      {activePreviewLayer === "WAVELET" && (
                        <div className="relative rounded bg-cyan-950/70 border border-cyan-500/60 p-1 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                          <span className="text-xl font-bold font-mono text-cyan-200">₹95,250.00</span>
                          <span className="block text-[9px] font-mono text-cyan-400 font-semibold">
                            db4 Wavelet High-Pass Void
                          </span>
                        </div>
                      )}

                      {activePreviewLayer === "LASER" && (
                        <div className="relative rounded bg-amber-950/70 border border-amber-500/60 p-1 shadow-[0_0_15px_rgba(245,158,11,0.3)]">
                          <span className="text-xl font-bold font-mono text-amber-200">₹95,250.00</span>
                          <span className="block text-[9px] font-mono text-amber-400 font-semibold">
                            Illustrative baseline overlay
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="text-[10px] font-mono text-emerald-400 flex items-center justify-center gap-1">
                      <ShieldCheck className="h-3 w-3" />
                      <span>Completed • UPI Ref 410293810294</span>
                    </div>
                  </div>
                </div>

                {/* Simulated scan line */}
                <div className="pointer-events-none absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-sky-400 to-transparent shadow-[0_0_10px_#38bdf8] opacity-70 animate-pulse" />
              </div>

              {/* Card Footer with Quick Action */}
              <div className="mt-3 flex items-center justify-between pt-1 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">
                  Illustration only: <strong className="text-rose-400">No measured result</strong>
                </span>
                <button
                  onClick={() => onNavigate("/workbench", { case: "sample_2" })}
                  className="inline-flex items-center gap-1 rounded bg-sky-500/20 px-2.5 py-1 text-[11px] font-mono font-medium text-sky-300 border border-sky-500/40 hover:bg-sky-500/30 transition-colors"
                >
                  <span>Inspect in Workbench</span>
                  <ExternalLink className="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION B: 4-LAYER FORENSIC ARCHITECTURE
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Corroboration Architecture
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white">
              Multi-Spectral Forensic Pipeline
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base">The pipeline combines pixel, geometry, metadata, and overlap rules. Compression, resizing, and ordinary interface design can affect all of these cues.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Layer 1: ELA */}
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6 shadow-lg hover:border-sky-500/40 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-950/60 text-sky-400 mb-4">
                <Activity className="h-5 w-5" />
              </div>
              <span className="font-mono text-xs font-semibold text-sky-400">PIXEL CUE 01</span>
              <h3 className="text-base font-bold text-white mt-1">Compression ELA</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Displays JPEG reconstruction residuals. Non-JPEG images receive no ELA anomaly score. Residual differences alone do not establish an edit.</p>
              <div className="mt-4 pt-4 border-t border-white/[0.06] text-[11px] font-mono text-slate-400">
                Cue: Reconstruction residuals
              </div>
            </div>

            {/* Layer 2: Wavelet */}
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6 shadow-lg hover:border-indigo-500/40 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-950/60 text-indigo-400 mb-4">
                <Cpu className="h-5 w-5" />
              </div>
              <span className="font-mono text-xs font-semibold text-indigo-400">PIXEL CUE 02</span>
              <h3 className="text-base font-bold text-white mt-1">Wavelet db4 Analysis</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Maps local variation in a db4 diagonal high-pass residual. Flat UI backgrounds and resampling can produce the same low-variation regions.</p>
              <div className="mt-4 pt-4 border-t border-white/[0.06] text-[11px] font-mono text-slate-400">
                Cue: Local residual variation
              </div>
            </div>

            {/* Layer 3: Spatial Copy-Move */}
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6 shadow-lg hover:border-teal-500/40 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-teal-500/30 bg-teal-950/60 text-teal-400 mb-4">
                <Fingerprint className="h-5 w-5" />
              </div>
              <span className="font-mono text-xs font-semibold text-teal-400">PIXEL CUE 03</span>
              <h3 className="text-base font-bold text-white mt-1">ORB Copy-Move Detection</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Groups matching ORB features into candidate repeated regions. Repeated text, logos, and interface elements can match without editing.</p>
              <div className="mt-4 pt-4 border-t border-white/[0.06] text-[11px] font-mono text-slate-400">
                Cue: Repeated features
              </div>
            </div>

            {/* Layer 4: Text Laser Baseline */}
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6 shadow-lg hover:border-amber-500/40 transition-all">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-amber-500/30 bg-amber-950/60 text-amber-400 mb-4">
                <Sliders className="h-5 w-5" />
              </div>
              <span className="font-mono text-xs font-semibold text-amber-400">GEOMETRY CUE</span>
              <h3 className="text-base font-bold text-white mt-1">Text Baseline Geometry</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Groups text-like components into rows and measures baseline differences. It does not recognize text or verify the displayed amount.</p>
              <div className="mt-4 pt-4 border-t border-white/[0.06] text-[11px] font-mono text-slate-400">
                Cue: Component baseline variation
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION C: 4-STAGE INVESTIGATIVE WORKFLOW
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Operational Protocol
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white">
              From Upload to Human Review
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base">A workflow for exploratory screenshot review.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            {/* Step 1 */}
            <div className="relative rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="font-mono text-3xl font-extrabold text-sky-400/30 mb-2">01</div>
              <h3 className="text-base font-bold text-white">Evidence Ingest</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Drag-and-drop raw PNG, JPG, or WhatsApp forwarded payment receipts. Mobile QR bridge
                allows officers to transfer evidence directly from field devices securely.
              </p>
              <div className="mt-3 font-mono text-[10px] text-sky-400">Hash SHA-256 logged</div>
            </div>

            {/* Step 2 */}
            <div className="relative rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="font-mono text-3xl font-extrabold text-sky-400/30 mb-2">02</div>
              <h3 className="text-base font-bold text-white">Multi-Layer Decomposition</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Computes pixel residuals, component geometry, metadata and QR cues, then combines configured rules.</p>
              <div className="mt-3 font-mono text-[10px] text-sky-400">Processing time depends on image size</div>
            </div>

            {/* Step 3 */}
            <div className="relative rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="font-mono text-3xl font-extrabold text-sky-400/30 mb-2">03</div>
              <h3 className="text-base font-bold text-white">Corroborated Inspection</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Examine suspicious regions with synchronized loupe (8x zoom), interactive split sliders,
                and quad-matrix views comparing original pixels against forensic heatmaps.
              </p>
              <div className="mt-3 font-mono text-[10px] text-sky-400">Interactive Canvas Loupe</div>
            </div>

            {/* Step 4 */}
            <div className="relative rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="font-mono text-3xl font-extrabold text-sky-400/30 mb-2">04</div>
              <h3 className="text-base font-bold text-white">Review Report Export</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Print a review report with the file hash, measurements, and limitations. No statutory notice generator or legal certification is active.</p>
              <div className="mt-3 font-mono text-[10px] text-emerald-400">Human review required</div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION D: VERIFIED CAPABILITIES VS REAL-WORLD BOUNDARIES
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Methodological Integrity
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white">
              Review Cues & Limitations
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base">A heuristic finding is a prompt for inspection. Neither a low score nor an overlapping region establishes authenticity or manipulation.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left: What We Verify */}
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/15 p-6 shadow-xl">
              <div className="flex items-center gap-3 border-b border-emerald-500/20 pb-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-emerald-200">Available Review Cues</h3>
                  <span className="text-xs font-mono text-emerald-400">Deterministic & Statistical Image Tests</span>
                </div>
              </div>

              <ul className="mt-4 space-y-3 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span>
                    <strong>Compression Quantization Inconsistencies:</strong> Displays JPEG reconstruction differences that can also arise from ordinary encoding.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span>
                    <strong>High-Frequency Wavelet Perturbations:</strong> Shows low residual variation; smooth UI backgrounds can produce similar patterns.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span>
                    <strong>Typographic Alignment & Baseline Drift:</strong> Measures component baseline differences; text recognition is unavailable.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span>
                    <strong>Cloned Transaction Digit Sequences:</strong> Finds repeated feature candidates, including ordinary repeated UI elements.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-2 shrink-0" />
                  <span>
                    <strong>Temporal & Viewport Sanity:</strong> Checks available metadata text and image dimensions; screenshot text is not OCR-verified.
                  </span>
                </li>
              </ul>
            </div>

            {/* Right: Explicit Limitations */}
            <div className="rounded-2xl border border-rose-500/30 bg-rose-950/15 p-6 shadow-xl">
              <div className="flex items-center gap-3 border-b border-rose-500/20 pb-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-rose-200">Forensic Limitations & Non-Claims</h3>
                  <span className="text-xs font-mono text-rose-400">Strict Operational Boundaries</span>
                </div>
              </div>

              <ul className="mt-4 space-y-3 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-400 mt-2 shrink-0" />
                  <span>
                    <strong>No Banking Ledger Access:</strong> VeriSight Pro does not access RBI, NPCI, or commercial bank databases. It does not verify whether fiat funds actually settled.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-400 mt-2 shrink-0" />
                  <span>
                    <strong>Does Not Prove Criminal Intent:</strong> Review cues do not establish editing or identify an author.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-400 mt-2 shrink-0" />
                  <span>
                    <strong>Extreme Laundering Degradation:</strong> If a screenshot is recompressed multiple times through lossy chat platforms at low resolution (&lt;480px), fine ELA evidence may degrade.
                  </span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-400 mt-2 shrink-0" />
                  <span>
                    <strong>Corroboration Tool, Not Sole Determiner:</strong> Confirm transaction status independently with the payment provider.
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION E: DEMONSTRATION CASE GALLERY (S1–S5)
        ========================================================================= */}
        <div id="demo-gallery" className="py-16 border-t border-white/[0.08]">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10 gap-4">
            <div>
              <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
                Golden Test Suite
              </span>
              <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white">
                Demonstration Case Catalog
              </h2>
              <p className="mt-2 text-slate-400 text-sm max-w-xl">Explore five synthetic regression fixtures. They demonstrate behavior, not accuracy on real screenshots.</p>
            </div>
            <div className="shrink-0">
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-amber-500/40 bg-amber-950/40 px-3 py-1.5 text-xs font-mono text-amber-300">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                <span>Synthetic development samples only</span>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {samples.map((sample, idx) => {
              const isManipulated =
                sample.expected_verdict !== "INCONCLUSIVE";

              return (
                <div
                  key={sample.id}
                  className="flex flex-col justify-between rounded-xl border border-white/[0.1] bg-[#0A0F1E] overflow-hidden shadow-lg hover:border-sky-500/50 hover:shadow-sky-500/10 transition-all group"
                >
                  {/* Mandatory Top Banner */}
                  <div className="bg-amber-950/80 border-b border-amber-800/50 px-3 py-1.5 text-center">
                    <span className="font-mono text-[9px] font-bold tracking-wider text-amber-300 uppercase">
                      SYNTHETIC DEMONSTRATION — NOT REAL PAYMENT EVIDENCE
                    </span>
                  </div>

                  {/* Body Content */}
                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-semibold text-sky-400">
                          SAMPLE S{idx + 1}
                        </span>
                        <span
                          className={`rounded px-2 py-0.5 font-mono text-[10px] font-semibold ${
                            isManipulated
                              ? "bg-rose-950/80 text-rose-300 border border-rose-800/50"
                              : "bg-emerald-950/80 text-emerald-300 border border-emerald-800/50"
                          }`}
                        >
                          {sample.expected_verdict}
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-white mt-2 group-hover:text-sky-300 transition-colors">
                        {sample.title}
                      </h3>

                      <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                        {sample.scenario}
                      </p>
                    </div>

                    <div className="space-y-3 pt-3 border-t border-white/[0.06]">
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-500">Expected Score:</span>
                        <span className={isManipulated ? "text-rose-400 font-bold" : "text-emerald-400 font-bold"}>
                          {sample.target_score_range || "N/A"}
                        </span>
                      </div>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-1.5">
                        {sample.tags?.map((tag) => (
                          <span
                            key={tag}
                            className="rounded bg-white/[0.04] px-2 py-0.5 text-[10px] font-mono text-slate-400 border border-white/[0.06]"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>

                      {/* Action Button */}
                      <button
                        onClick={() => onNavigate("/workbench", { case: sample.id })}
                        className="w-full mt-2 flex items-center justify-center gap-2 rounded-lg border border-sky-500/40 bg-sky-500/15 py-2 text-xs font-mono font-medium text-sky-300 hover:bg-sky-500/25 transition-all active:scale-[0.98]"
                      >
                        <span>Inspect in Workbench</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* =========================================================================
            SECTION F: RESEARCH & EVALUATION METHODOLOGY SUMMARY
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="rounded-2xl border border-white/[0.1] bg-[#0A0F1F] p-8 shadow-2xl">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-white/[0.08]">
              <div>
                <span className="font-mono text-xs font-semibold text-sky-400 uppercase tracking-wider">
                  Model Governance & Empirical Rigor
                </span>
                <h2 className="text-xl sm:text-3xl font-bold text-white mt-1">
                  Deterministic heuristic analyzer
                </h2>
                <p className="text-xs sm:text-sm text-slate-300 mt-2 max-w-2xl font-sans">The deployed analyzer combines deterministic rules. No trained classifier, calibration corpus, or held-out accuracy evaluation is configured.</p>
              </div>

              <button
                onClick={() => onNavigate("/evaluation")}
                className="shrink-0 flex items-center gap-2 rounded-lg border border-sky-500/40 bg-sky-500/20 px-4 py-2.5 text-xs font-mono font-semibold text-sky-300 hover:bg-sky-500/30 transition-all active:scale-[0.98]"
              >
                <span>Full Evaluation Dashboard</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Mandatory Academic & Scientific Disclosure */}
            <div className="my-6 rounded-lg border border-amber-500/40 bg-amber-950/30 p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-200/90 leading-relaxed">
                  <strong className="text-amber-200 uppercase font-mono block mb-1">
                    Mandatory Benchmark Disclosure:
                  </strong>
                  Only five synthetic regression fixtures are bundled. No independent authenticity labels, held-out accuracy metrics, or calibrated probabilities are available.
                </div>
              </div>
            </div>

            {/* Telemetry Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              <div className="rounded-lg border border-white/[0.06] bg-[#070B16] p-4 text-center">
                <span className="font-mono text-[11px] text-slate-400 block">ROC-AUC</span>
                <span className="font-mono text-2xl font-bold text-sky-400 mt-1 block">Unavailable</span>
                <span className="font-mono text-[10px] text-slate-500 mt-1 block">No held-out evaluation</span>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#070B16] p-4 text-center">
                <span className="font-mono text-[11px] text-slate-400 block">Brier Score</span>
                <span className="font-mono text-2xl font-bold text-emerald-400 mt-1 block">Unavailable</span>
                <span className="font-mono text-[10px] text-slate-500 mt-1 block">Not calibrated</span>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#070B16] p-4 text-center">
                <span className="font-mono text-[11px] text-slate-400 block">Benchmark Corpus</span>
                <span className="font-mono text-2xl font-bold text-white mt-1 block">5 Fixtures</span>
                <span className="font-mono text-[10px] text-slate-500 mt-1 block">Synthetic regression only</span>
              </div>

              <div className="rounded-lg border border-white/[0.06] bg-[#070B16] p-4 text-center">
                <span className="font-mono text-[11px] text-slate-400 block">Calibration Model</span>
                <span className="font-mono text-sm font-bold text-indigo-300 mt-2 block">
                  None deployed
                </span>
                <span className="font-mono text-[10px] text-slate-500 mt-1 block">No calibration dataset</span>
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION G: PRIVACY, DATA RETENTION & STATUTORY COMPLIANCE
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Judicial & Data Safeguards
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white">
              Data Handling & Report Scope
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base">Case-summary saving is off by default and requires the operator to opt in. Each result reports whether its summary was saved, unavailable, or failed; a connected database alone does not mean a case was saved.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-950/60 text-sky-400 mb-4">
                <Lock className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">Temporary previews & saved summaries</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Analysis can create private preview files on this server. Preview links expire after 10 minutes. Opt-in summaries carry a 7-day retention policy; cleanup is attempted while the server is running and the database is reachable. Signed-upload files are removed after consumption, with best-effort cleanup of abandoned uploads after 24 hours. These are prototype policies, not a cloud deletion guarantee.</p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-950/60 text-emerald-400 mb-4">
                <Scale className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">Technical Review Reports</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">Reports summarize measurements for human review. The prototype does not issue legal notices or certify evidentiary admissibility.</p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-950/60 text-indigo-400 mb-4">
                <FileCheck2 className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">Uploaded File SHA-256</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">SHA-256 identifies the uploaded bytes. The hash does not prove capture origin, payment settlement, or a complete chain of custody.</p>
            </div>
          </div>
        </div>

        {/* =========================================================================
            SECTION H: HONEST FAQ & FORENSIC FOOTER
        ========================================================================= */}
        <div className="py-16 border-t border-white/[0.08]">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Investigator Q&A
            </span>
            <h2 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="max-w-3xl mx-auto space-y-4">
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="h-4 w-4 text-sky-400 shrink-0" />
                <span>Can VeriSight prove who committed the forgery?</span>
              </h3>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed pl-6">No. The system cannot establish who created or changed a screenshot, and its review cues do not prove that an edit occurred.</p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="h-4 w-4 text-sky-400 shrink-0" />
                <span>Why does WhatsApp compression make forensics difficult?</span>
              </h3>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed pl-6">Lossy encoding can remove useful detail and create residual patterns. The simulator uses a fixed JPEG transform; it is not a verified reproduction of any current messaging app.</p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="h-4 w-4 text-sky-400 shrink-0" />
                <span>Does VeriSight issue legal notices?</span>
              </h3>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed pl-6">No. The printable report is a technical review aid. Legal notice generation is not implemented in this analyzer.</p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="h-4 w-4 text-sky-400 shrink-0" />
                <span>Does VeriSight connect to NPCI or bank servers?</span>
              </h3>
              <p className="mt-2 text-xs text-slate-300 leading-relaxed pl-6">No. Confirm payment status through the payment provider or bank. Screenshot pixels and QR payloads cannot verify settlement.</p>
            </div>
          </div>
        </div>

        {/* =========================================================================
            FOOTER
        ========================================================================= */}
        <footer className="mt-16 border-t border-white/[0.08] pt-8 pb-12 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 font-mono gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-sky-400" />
            <span className="font-semibold text-slate-400">VERISIGHT PRO FORENSIC SUITE</span>
            <span>•</span>
            <span>v1.0 · heuristic</span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => onNavigate("/")}
              className="hover:text-slate-300 transition-colors"
            >
              Overview
            </button>
            <button
              onClick={() => onNavigate("/workbench")}
              className="hover:text-slate-300 transition-colors"
            >
              Workbench
            </button>
            <button
              onClick={() => onNavigate("/evaluation")}
              className="hover:text-slate-300 transition-colors"
            >
              Evaluation
            </button>
          </div>

          <div>
            <span>Heuristic review prototype</span>
          </div>
        </footer>
      </div>
    </div>
  );
};
