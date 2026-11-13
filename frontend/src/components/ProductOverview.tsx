import { analyzeDemoSample } from "../services/api";
import { ForensicAnalysisReport } from "../types/forensic";
import React, { useState, useEffect } from "react";
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
  Award,
  Mic,
  LifeBuoy,
  FileText,
  CheckCircle2,
  Clock,
  Landmark,
  Users,
  ArrowUpRight,
  PhoneCall,
  History,
  FolderLock,
  BookOpen,
} from "lucide-react";
import { motion, AnimatePresence, useReducedMotion, type Variants } from "framer-motion";
import { AppRoute } from "./NavigationHeader";
import { DemoSampleMeta } from "../types/forensic";
import { WhyVerisight } from "./WhyVerisight";
import { RealWorldCaseShowcase } from "./RealWorldCaseShowcase";

interface ProductOverviewProps {
  onNavigate: (route: AppRoute, query?: Record<string, string>) => void;
  demoSamples?: DemoSampleMeta[];
}

export const ProductOverview: React.FC<ProductOverviewProps> = ({
  onNavigate,
  demoSamples = [],
}) => {
  const [preview, setPreview] = useState<ForensicAnalysisReport | null>(null);
  const [previewError,setPreviewError] = useState("");
  useEffect(()=>{ const controller=new AbortController(); analyzeDemoSample("sample_2",controller.signal).then(setPreview).catch(e=>{if(!controller.signal.aborted)setPreviewError(e.message);}); return()=>controller.abort();},[]);
  const shouldReduceMotion = useReducedMotion();

  // Interactive Hero Preview state
  const [activePreviewLayer, setActivePreviewLayer] = useState<
    "ORIGINAL" | "ELA" | "WAVELET" | "LASER"
  >("ELA");

  // Fallback demo samples if not passed from parent
  const samples = demoSamples;

  // Motion variants according to Emil Kowalski / Apple motion design principles
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.08,
        delayChildren: shouldReduceMotion ? 0 : 0.05,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 14 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: shouldReduceMotion ? 0 : 0.45,
        ease: "easeOut",
      },
    },
  };

  const sectionVariants: Variants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: shouldReduceMotion ? 0 : 0.5,
        ease: "easeOut",
      },
    },
  };

  return (
    <div className="relative min-h-[calc(100vh-3.5rem)] w-full overflow-y-auto bg-[#060911] text-slate-100 selection:bg-sky-500/30 selection:text-sky-200">
      {/* Background ambient radial glow */}
      <motion.div
        animate={
          shouldReduceMotion
            ? undefined
            : {
                opacity: [0.65, 0.85, 0.65],
                scale: [0.98, 1.02, 0.98],
              }
        }
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[600px] w-[1000px] -translate-x-1/2 rounded-full bg-gradient-to-b from-sky-500/12 via-indigo-500/6 to-transparent blur-[140px]"
      />

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-16">
        {/* =========================================================================
            SECTION 1: HERO NARRATIVE & POSITIONING (DUAL PRIMARY ACTIONS)
        ========================================================================= */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 items-center gap-12 lg:grid-cols-12 lg:gap-8 pt-4 pb-8"
        >
          <div className="lg:col-span-7 space-y-6">
            {/* Platform Eyebrow Badge */}
            <motion.div
              variants={itemVariants}
              className="inline-flex items-center gap-2 rounded-full border border-sky-500/30 bg-sky-950/40 px-3.5 py-1 text-xs font-mono font-medium text-sky-300 backdrop-blur-md"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500" />
              </span>
              <span>INTELLIGENT EVIDENCE FORENSICS & RESPONSE PLATFORM</span>
              <span className="text-slate-500">|</span>
              <span className="text-emerald-400 font-semibold">v1.3.0 UNIFIED</span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={itemVariants}
              className="text-3xl font-extrabold tracking-tight sm:text-5xl lg:text-5xl text-white leading-tight font-sans"
            >
              From suspicious evidence{" "}
              <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-sky-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
                to informed action.
              </span>
            </motion.h1>

            {/* Sub-headline */}
            <motion.p
              variants={itemVariants}
              className="text-base text-slate-300 sm:text-lg leading-relaxed max-w-2xl font-sans"
            >
              VeriSight bridges the gap between deep digital image forensics and active incident response.
              Inspect screenshot review cues, describe what happened by voice or text, and prepare editable complaint drafts and evidence summaries.
            </motion.p>

            {/* Dual Primary Action CTAs */}
            <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-3 pt-2">
              <motion.button
                whileHover={shouldReduceMotion ? undefined : { scale: 1.015 }}
                whileTap={shouldReduceMotion ? undefined : { scale: 0.985 }}
                onClick={() => onNavigate("/workbench")}
                className="group flex items-center gap-2.5 rounded-xl border border-sky-400/40 bg-gradient-to-r from-sky-500 to-sky-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-500/25 transition-all hover:from-sky-400 hover:to-sky-500"
              >
                <Layers className="h-4 w-4" />
                <span>Launch Forensic Workbench</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </motion.button>

              <motion.button
                whileHover={shouldReduceMotion ? undefined : { scale: 1.015 }}
                whileTap={shouldReduceMotion ? undefined : { scale: 0.985 }}
                onClick={() => onNavigate("/response")}
                className="group flex items-center gap-2.5 rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-600 to-teal-700 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 transition-all hover:from-emerald-500 hover:to-teal-600"
              >
                <Mic className="h-4 w-4 text-emerald-200" />
                <span>Report an Incident</span>
                <ChevronRight className="h-4 w-4 text-emerald-200 transition-transform group-hover:translate-x-1" />
              </motion.button>

              <a
                href="#why-verisight"
                className="flex items-center gap-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs font-mono text-amber-300 hover:bg-amber-500/20 transition-all"
              >
                <Award className="h-3.5 w-3.5 text-amber-400" />
                <span>Review methods & limitations ↓</span>
              </a>
            </motion.div>

            {/* Trust Metrics Strip */}
            <motion.div
              variants={itemVariants}
              className="pt-4 grid grid-cols-3 gap-4 border-t border-white/[0.08] text-xs font-mono"
            >
              <div>
                <span className="block text-slate-400">Forensic Engine</span>
                <span className="text-sm font-semibold text-white">4-Layer Multi-Spectral</span>
              </div>
              <div>
                <span className="block text-slate-400">Voice Intelligence</span>
                <span className="text-sm font-semibold text-emerald-400">Browser-dependent speech</span>
              </div>
              <div>
                <span className="block text-slate-400">Drafting guidance</span>
                <span className="text-sm font-semibold text-sky-400">Editable personal drafts</span>
              </div>
            </motion.div>
          </div>

          {/* Interactive Live Preview Component */}
          <motion.div variants={itemVariants} className="lg:col-span-5">
            <div className="relative rounded-2xl border border-white/[0.12] bg-[#0A0F1D]/90 p-4 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-rose-500 inline-block animate-pulse" />
                  <span className="font-mono text-xs font-semibold text-slate-200">
                    INTERACTIVE MULTI-SPECTRAL PREVIEW
                  </span>
                </div>
                <span className="font-mono text-[10px] text-amber-400 bg-amber-950/60 border border-amber-800/40 px-2 py-0.5 rounded">
                  SYNTHETIC SAMPLE S2
                </span>
              </div>

              {/* Spectral layer tabs */}
              <div className="mt-3 flex gap-1 rounded-lg bg-[#060A14] p-1 border border-white/[0.06] text-[11px] font-mono">
                {[
                  { id: "ORIGINAL", label: "01 Original" },
                  { id: "ELA", label: "02 ELA Heatmap" },
                  { id: "WAVELET", label: "03 Wavelet HF" },

                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActivePreviewLayer(tab.id as any)}
                    className={`flex-1 rounded py-1 text-center font-medium transition-all ${
                      activePreviewLayer === tab.id
                        ? "bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm font-bold"
                        : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="mt-4 h-80 flex items-center justify-center overflow-hidden bg-slate-950 rounded-lg">
                {preview ? <img className="w-full h-full object-contain" alt="Measured synthetic sample preview" src={activePreviewLayer === "ELA" ? preview.layer1.ela_b64 : activePreviewLayer === "WAVELET" ? preview.layer1.wavelet_noise_b64 : preview.original_image_b64}/> : <p role="status" className="text-sm p-4">{previewError || "Loading actual analysis preview…"}</p>}
              </div><p className="mt-3 text-xs text-slate-400">Actual synthetic fixture and analysis views. For geometry overlays, open the workbench.</p>
            </div>
          </motion.div>
        </motion.div>

        <section className="panel my-8"><h2>Product demonstration</h2><p>Recorded demonstration of the earlier workbench. Current labels and capabilities may differ.</p><video controls preload="metadata" className="w-full rounded-lg mt-4" aria-label="VeriSight product demo"><source src="/demo/verisight-demo.mp4" type="video/mp4"/></video></section>
        {/* =========================================================================
            SECTION 2: THE PROBLEM (PAYMENT FRAUD & VICTIM CONFUSION)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-rose-400">
              The Critical Challenge
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
              The Digital Payment Fraud Crisis
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
              Fraudsters can exploit manipulated screenshots,
              counterfeit receipt APKs, and psychological urgency to defraud merchants and consumers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 p-6 space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-rose-500/30 bg-rose-950/40 text-rose-400">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">Manipulated Payment Receipts</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Subtle pixel splices alter transaction amounts from ₹10 to ₹10,000. Counterfeit generator APKs
                mimic PhonePe, Google Pay, and Paytm UI templates to trick counter staff and vendors.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 p-6 space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-950/40 text-amber-400">
                <Clock className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">The "Golden Hour" Void</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Victims waste precious hours unsure whether a payment failed or was stolen. By the time they
                reach official portals, fraud syndicates have laundered the funds across mule accounts.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/80 p-6 space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-sky-500/30 bg-sky-950/40 text-sky-400">
                <Scale className="h-5 w-5" />
              </div>
              <h3 className="text-base font-bold text-white">Bureaucratic Reporting Friction</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Organizing an incident narrative and supporting evidence can be difficult. Editable drafts help users prepare information for independent review.
              </p>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 2.5: REAL-WORLD FRAUD CASES (SCAMSHIELD-INSPIRED SHOWCASE)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="pt-4 pb-8"
        >
          <RealWorldCaseShowcase
            onNavigateWorkbench={() => onNavigate("/workbench")}
            onNavigateResponse={(cat) =>
              onNavigate("/response", cat ? { category: cat } : undefined)
            }
          />
        </motion.div>

        {/* =========================================================================
            SECTION 3: HOW VERISIGHT WORKS (4-STEP WORKFLOW)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              End-to-End Pipeline
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
              How VeriSight Solves the Crisis
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
              A synchronized 4-stage journey that transforms raw suspicion into structured evidence review.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-6 relative">
              <span className="font-mono text-3xl font-extrabold text-sky-500/30 block mb-2">01</span>
              <h3 className="text-base font-bold text-white">Ingest & Detect</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Upload suspect screenshot. The 4-layer engine instantly runs multi-spectral ELA, wavelet residual
                checks, typography baseline lasers, and heuristic evidence aggregation.
              </p>
              <div className="mt-4 font-mono text-[10px] text-sky-400">SHA-256 File Identification</div>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-6 relative">
              <span className="font-mono text-3xl font-extrabold text-indigo-500/30 block mb-2">02</span>
              <h3 className="text-base font-bold text-white">Contextual Handoff</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                When review cues are detected, click "What should I do next?". Your forensic report facts,
                tamper scores, and file hash automatically bind into the Response Module.
              </p>
              <div className="mt-4 font-mono text-[10px] text-indigo-400">Zero Manual Data Re-entry</div>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-6 relative">
              <span className="font-mono text-3xl font-extrabold text-emerald-500/30 block mb-2">03</span>
              <h3 className="text-base font-bold text-white">Voice Incident Intake</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Speak what happened in Hindi, Kannada, Tamil, Telugu, Bengali, Marathi, or English.
                Browser speech recognition, where supported, supplies editable text. Rules extract candidate fields for your review.
              </p>
              <div className="mt-4 font-mono text-[10px] text-emerald-400">Browser speech or typed input</div>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-6 relative">
              <span className="font-mono text-3xl font-extrabold text-teal-500/30 block mb-2">04</span>
              <h3 className="text-base font-bold text-white">Complaint & Evidence Drafts</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Export an editable complaint draft and evidence summary. No submission or statutory notice is issued by VeriSight.
              </p>
              <div className="mt-4 font-mono text-[10px] text-teal-400">Editable Draft PDF Export</div>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 4: FORENSIC WORKBENCH (4-LAYER SIGNAL ARCHITECTURE & S1-S5)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
            <div>
              <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
                Core Science
              </span>
              <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
                Forensic Workbench Architecture
              </h2>
              <p className="mt-2 text-slate-400 text-sm max-w-xl">
                Four stages of image, geometry, metadata and evidence review.
              </p>
            </div>
            <motion.button
              whileHover={shouldReduceMotion ? undefined : { scale: 1.02 }}
              whileTap={shouldReduceMotion ? undefined : { scale: 0.98 }}
              onClick={() => onNavigate("/workbench")}
              className="flex items-center gap-2 rounded-xl border border-sky-500/40 bg-sky-500/20 px-4 py-2.5 text-xs font-mono font-semibold text-sky-300 hover:bg-sky-500/30 transition-all self-start md:self-auto"
            >
              <span>Launch Full Workbench</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </motion.button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5 shadow-lg">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-950/60 text-sky-400 mb-3">
                <Layers className="h-4 w-4" />
              </div>
              <span className="font-mono text-[11px] font-semibold text-sky-400">LAYER 01</span>
              <h3 className="text-sm font-bold text-white mt-1">Multi-Scale ELA</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Evaluates Error Level Analysis across Q75, Q85, and Q95 quantization matrices to expose modified patches.
              </p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5 shadow-lg">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-950/60 text-cyan-400 mb-3">
                <Activity className="h-4 w-4" />
              </div>
              <span className="font-mono text-[11px] font-semibold text-cyan-400">LAYER 02</span>
              <h3 className="text-sm font-bold text-white mt-1">Wavelet Residuals</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Wavelet-derived local variation highlights smooth and textured regions for inspection.
              </p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5 shadow-lg">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-amber-500/30 bg-amber-950/60 text-amber-400 mb-3">
                <Sliders className="h-4 w-4" />
              </div>
              <span className="font-mono text-[11px] font-semibold text-amber-400">LAYER 03</span>
              <h3 className="text-sm font-bold text-white mt-1">Typography & Laser Drift</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Text-like component geometry and CIELAB color differences flag review cues without recognizing words.
              </p>
            </div>

            <div className="rounded-xl border border-white/[0.08] bg-[#0A0F1E] p-5 shadow-lg">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-purple-500/30 bg-purple-950/60 text-purple-400 mb-3">
                <Cpu className="h-4 w-4" />
              </div>
              <span className="font-mono text-[11px] font-semibold text-purple-400">LAYER 04</span>
              <h3 className="text-sm font-bold text-white mt-1">Fusion GBDT v1.2.1</h3>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed font-sans">
                Combines measured image cues for review. Experimental fusion checkpoints remain research assets; no validated probability is displayed.
              </p>
            </div>
          </div>

          {/* Golden Demonstration Sample Grid */}
          <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A]/90 p-6">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-4 mb-5">
              <div>
                <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
                  Synthetic Demonstration Samples (S1 – S5)
                </h3>
                <span className="text-xs text-slate-400">
                  Click any benchmark case to load it directly into the Forensic Workbench.
                </span>
              </div>
              <span className="rounded bg-sky-950 px-2 py-1 font-mono text-[10px] text-sky-300 border border-sky-800">
                Software fixtures
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {samples.map((s, idx) => {
                const isManipulated =
                  s.expected_verdict?.includes("MANIPULATED") ||
                  s.expected_verdict?.includes("FORGERY");
                return (
                  <button
                    key={s.id}
                    onClick={() => onNavigate("/workbench", { case: s.id })}
                    className="flex flex-col justify-between rounded-xl border border-white/[0.08] bg-[#060911] p-3 text-left hover:border-sky-500/50 hover:bg-[#080E1C] transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between text-[10px] font-mono mb-1">
                        <span className="text-sky-400 font-bold">S{idx + 1}</span>
                        <span
                          className={`rounded px-1.5 py-0.2 font-semibold ${
                            isManipulated
                              ? "bg-rose-950 text-rose-300 border border-rose-800/40"
                              : "bg-emerald-950 text-emerald-300 border border-emerald-800/40"
                          }`}
                        >
                          {s.tags[0] || "Unverified"}
                        </span>
                      </div>
                      <h4 className="text-xs font-semibold text-white group-hover:text-sky-300 transition-colors line-clamp-1">
                        {s.title}
                      </h4>
                      <p className="mt-1 text-[11px] text-slate-400 line-clamp-2 font-sans">
                        {s.scenario}
                      </p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-white/[0.06] flex items-center justify-between font-mono text-[10px]">
                      <span className="text-slate-500">{s.target_score_range}</span>
                      <ArrowRight className="h-3 w-3 text-sky-400 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </motion.div>

        <section className="panel my-8"><h2>Evaluation & Research</h2><p>Real-world accuracy and calibrated confidence are unavailable. The bundled examples are synthetic software fixtures. Experimental checkpoints are not used to certify authenticity.</p><button className="action-button mt-4" onClick={()=>onNavigate("/evaluation")}>View evaluation status</button></section>
        {/* =========================================================================
            SECTION 6: RESPONSE & GUIDANCE (THE 6 SUBMODULES)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
            <div>
              <span className="font-mono text-xs font-semibold uppercase tracking-wider text-emerald-400">
                Action Module
              </span>
              <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
                Response & Guidance System
              </h2>
              <p className="mt-2 text-slate-400 text-sm max-w-xl">
                6 integrated submodules assisting victims and investigators from immediate containment to judicial resolution.
              </p>
            </div>
            <motion.button
              whileHover={shouldReduceMotion ? undefined : { scale: 1.02 }}
              whileTap={shouldReduceMotion ? undefined : { scale: 0.98 }}
              onClick={() => onNavigate("/response")}
              className="flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/20 px-4 py-2.5 text-xs font-mono font-semibold text-emerald-300 hover:bg-emerald-500/30 transition-all self-start md:self-auto"
            >
              <span>Launch Response & Guidance</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </motion.button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Submodule 1 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-950 border border-sky-800 text-sky-400 font-mono text-xs font-bold">
                  01
                </div>
                <h3 className="text-sm font-bold text-white">Incident Centre</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Immediate triage wizard evaluating financial loss and incident category. Delivers urgent golden-hour advice (1930 call, UPI freeze, SIM deactivation).
              </p>
            </div>

            {/* Submodule 2 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-400 font-mono text-xs font-bold">
                  02
                </div>
                <h3 className="text-sm font-bold text-white">Voice Reporting Assistant</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Select a browser speech language where supported, or type your statement. Review candidate fields extracted by rules.
              </p>
            </div>

            {/* Submodule 3 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-950 border border-indigo-800 text-indigo-400 font-mono text-xs font-bold">
                  03
                </div>
                <h3 className="text-sm font-bold text-white">Formal Complaint Builder</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Generates complete chronological formal complaint drafts customized for NCRP 1930, Bank Grievance, RBI Ombudsman, or Local Police Stations.
              </p>
            </div>

            {/* Submodule 4 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-950 border border-purple-800 text-purple-400 font-mono text-xs font-bold">
                  04
                </div>
                <h3 className="text-sm font-bold text-white">Evidence Dossier Organizer</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Organizes available workbench findings and SHA-256 identification into a review memo. No digital signature or legal certification is provided.
              </p>
            </div>

            {/* Submodule 5 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-950 border border-teal-800 text-teal-400 font-mono text-xs font-bold">
                  05
                </div>
                <h3 className="text-sm font-bold text-white">Indian Reporting Directory</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Curated statutory escalation paths with working links, nodal email templates, and escalation timelines for 10+ major Indian banks and payment apps.
              </p>
            </div>

            {/* Submodule 6 */}
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0E1A] p-5 space-y-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-950 border border-amber-800 text-amber-400 font-mono text-xs font-bold">
                  06
                </div>
                <h3 className="text-sm font-bold text-white">Complaint Tracking & Follow-up</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Local-first case management recording NCRP acknowledgement numbers, timeline events, statutory 30-day escalation deadlines, and notes.
              </p>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 7: VOICE-TO-COMPLAINT INTELLIGENCE DEEP DIVE
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7 space-y-4">
              <span className="font-mono text-xs font-semibold uppercase tracking-wider text-teal-400">
                Voice-assisted Intake
              </span>
              <h2 className="text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
                Voice-to-Complaint Intelligence
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed font-sans">
                When people experience fraud, typing complex legal details is intimidating.
                VeriSight enables victims to explain what occurred naturally in their mother tongue.
              </p>

              <div className="space-y-3 pt-2">
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-lg bg-teal-950 border border-teal-800 flex items-center justify-center shrink-0 text-teal-400 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Seven selectable language settings</h4>
                    <p className="text-xs text-slate-400 font-sans">
                      English (India), हिन्दी (Hindi), ಕನ್ನಡ (Kannada), বাংলা (Bengali), தமிழ் (Tamil), తెలుగు (Telugu), and मराठी (Marathi). Recognition support depends on the browser and provider; language accuracy is not validated.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-lg bg-teal-950 border border-teal-800 flex items-center justify-center shrink-0 text-teal-400 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Browser Speech and Typed Input</h4>
                    <p className="text-xs text-slate-400 font-sans">
                      Browser Web Speech API with editable interim text. If unsupported or denied, type your statement; server transcription is unavailable.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-lg bg-teal-950 border border-teal-800 flex items-center justify-center shrink-0 text-teal-400 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Rule-Based Candidate Field Extraction</h4>
                    <p className="text-xs text-slate-400 font-sans">
                      Pattern rules suggest reported amounts, references and contact details. Review and correct every field before using the personal complaint draft.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:col-span-5 rounded-2xl border border-teal-500/30 bg-[#0A1220] p-5 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-teal-500/20 pb-3">
                <span className="font-mono text-xs font-bold text-teal-300">LIVE AUDIO RECOGNITION</span>
                <span className="font-mono text-[9px] text-teal-400 bg-teal-950 px-2 py-0.5 rounded border border-teal-800">
                  REAL-TIME ASR
                </span>
              </div>

              <div className="rounded-xl border border-white/[0.06] bg-[#060911] p-3 font-mono text-xs text-slate-300 space-y-2">
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                  <Mic className="h-3 w-3 text-rose-400 animate-pulse" />
                  <span>"मुझे Google Pay पर ₹18,500 का फर्जी स्क्रीनशॉट भेजा गया..."</span>
                </div>
                <div className="rounded bg-teal-950/40 p-2 text-[11px] text-teal-200 border border-teal-800/40">
                  <strong className="block text-white mb-0.5">Extracted Structured Facts:</strong>
                  • Category: Fake Payment Screenshot<br />
                  • Amount: ₹18,500.00<br />
                  • Channel: UPI / Google Pay<br />
                  • Urgency: 1930 Golden Hour Alert Triggered
                </div>
              </div>

              <button
                onClick={() => onNavigate("/response")}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-teal-600 hover:bg-teal-500 py-2.5 font-mono text-xs font-semibold text-white transition-all shadow-md"
              >
                <span>Try Voice Reporting Assistant</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 8: EVIDENCE-TO-ACTION WORKFLOW
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Connected Continuity
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
              The Evidence-to-Action Bridge
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
              Forensic inspection and reporting are no longer fragmented across disconnected tools.
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-6 lg:p-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
              <div className="rounded-xl border border-white/[0.06] bg-[#070B16] p-4 space-y-2">
                <span className="font-mono text-[10px] text-sky-400 font-bold uppercase">Phase 1: Workbench</span>
                <h4 className="text-sm font-bold text-white">Detection & Scoring</h4>
                <p className="text-slate-400 leading-relaxed font-sans">
                  The user inspects an image and its measured review cues. The heuristic score is not a fraud probability.
                </p>
              </div>

              <div className="rounded-xl border border-white/[0.06] bg-[#070B16] p-4 space-y-2">
                <span className="font-mono text-[10px] text-emerald-400 font-bold uppercase">Phase 2: One-Click Handoff</span>
                <h4 className="text-sm font-bold text-white">Contextual Transfer</h4>
                <p className="text-slate-400 leading-relaxed font-sans">
                  Clicking "What should I do next?" transfers the filename, SHA-256 hash, verdict, and findings directly into the Voice Assistant.
                </p>
              </div>

              <div className="rounded-xl border border-white/[0.06] bg-[#070B16] p-4 space-y-2">
                <span className="font-mono text-[10px] text-indigo-400 font-bold uppercase">Phase 3: Formal Output</span>
                <h4 className="text-sm font-bold text-white">Draft for Independent Review</h4>
                <p className="text-slate-400 leading-relaxed font-sans">
                  The complaint builder binds the user's spoken narrative with the cryptographic forensic findings into an editable evidence summary.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 9: WHY VERISIGHT (EMBEDDED BENCHMARK & COMPARATIVE SANDBOX)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="pt-12 border-t border-white/[0.08]"
        >
          {/* Seamlessly embed the complete WhyVerisight interactive suite */}
          <WhyVerisight
            onNavigateWorkbench={() => onNavigate("/workbench")}
          />
        </motion.div>

        {/* =========================================================================
            SECTION 10: WHO BENEFITS (STAKEHOLDER IMPACT)
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="font-mono text-xs font-semibold uppercase tracking-wider text-sky-400">
              Ecosystem Utility
            </span>
            <h2 className="mt-2 text-2xl sm:text-4xl font-bold tracking-tight text-white font-sans">
              Who Benefits from VeriSight
            </h2>
            <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
              Purpose-built for multiple stakeholders across the cybercrime prevention and judicial lifecycle.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-5 space-y-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-950 border border-sky-800 text-sky-400">
                <Users className="h-4 w-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Fraud Victims & Citizens</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Structured screenshot review, incident intake, and editable complaint drafts. Verify transactions through your bank.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-5 space-y-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-400">
                <Landmark className="h-4 w-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Merchants & Business Owners</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Review suspicious receipt images and check payment status independently before releasing goods.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-5 space-y-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-950 border border-indigo-800 text-indigo-400">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Police Cyber-Cells & Investigators</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Internal review memos and personal preservation-request drafts with SHA-256 file identification. These do not issue summons or freeze funds.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.08] bg-[#0A0F1E] p-5 space-y-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-950 border border-purple-800 text-purple-400">
                <Scale className="h-4 w-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Fintech & Bank Compliance</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Rapid triage of customer payment dispute claims with deterministic physical and typography anomaly detection.
              </p>
            </div>
          </div>
        </motion.div>

        {/* =========================================================================
            SECTION 11: CALL TO ACTION & PLATFORM FOOTER
        ========================================================================= */}
        <motion.div
          variants={sectionVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="py-12 border-t border-white/[0.08]"
        >
          {/* Main CTA Card */}
          <div className="relative rounded-3xl border border-sky-500/30 bg-gradient-to-b from-[#0B152A] to-[#070D1B] p-8 sm:p-12 text-center overflow-hidden shadow-2xl">
            <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 h-48 w-96 rounded-full bg-sky-500/20 blur-[90px]" />

            <div className="relative z-10 max-w-2xl mx-auto space-y-4">
              <span className="font-mono text-xs font-bold uppercase tracking-wider text-sky-400 bg-sky-950/70 px-3 py-1 rounded-full border border-sky-800/50 inline-block">
                START INVESTIGATING OR REPORTING
              </span>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-white font-sans">
                Take Informed Action Against Digital Evidence Tampering
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                Explore our Golden Benchmark catalog or launch the Voice Reporting Assistant to prepare your formal complaint.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-3 pt-3">
                <button
                  onClick={() => onNavigate("/workbench")}
                  className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-sky-600 px-6 py-3 font-mono text-xs font-semibold text-white shadow-lg shadow-sky-500/25 hover:from-sky-400 hover:to-sky-500 transition-all active:scale-[0.98]"
                >
                  <Layers className="h-4 w-4" />
                  <span>Launch Forensic Workbench</span>
                </button>

                <button
                  onClick={() => onNavigate("/response")}
                  className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-3 font-mono text-xs font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-500 transition-all active:scale-[0.98]"
                >
                  <Mic className="h-4 w-4" />
                  <span>Report an Incident</span>
                </button>
              </div>
            </div>
          </div>

          {/* Unified Platform Footer */}
          <footer className="mt-12 pt-8 border-t border-white/[0.08] flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 font-mono gap-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-sky-400" />
              <span className="font-semibold text-slate-300">VERISIGHT PLATFORM</span>
              <span>•</span>
              <span>Intelligent Digital Evidence Forensics & Response</span>
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
              <button
                onClick={() => onNavigate("/response")}
                className="text-emerald-400 hover:text-emerald-300 font-semibold transition-colors"
              >
                Response & Guidance
              </button>
            </div>

            <div>
              <span>Personal drafting & reporting guidance</span>
            </div>
          </footer>
        </motion.div>
      </div>
    </div>
  );
};
