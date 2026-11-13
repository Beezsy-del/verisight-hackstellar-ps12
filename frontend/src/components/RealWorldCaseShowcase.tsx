import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  ChevronLeft,
  ChevronRight,
  MapPin,
  Calendar,
  ArrowRight,
  ExternalLink,
  Lightbulb,
  Search,
  ShieldCheck,
  FileCheck2,
  Zap,
} from "lucide-react";
import { REAL_WORLD_CASES, RealWorldFraudCase } from "../data/realWorldCases";
import { DottedIndiaMap } from "./common/DottedIndiaMap";
import { CaseInvestigationModal } from "./CaseInvestigationModal";

interface RealWorldCaseShowcaseProps {
  onNavigateWorkbench?: () => void;
  onNavigateResponse?: (category?: string) => void;
  className?: string;
}

export const RealWorldCaseShowcase: React.FC<RealWorldCaseShowcaseProps> = ({
  onNavigateWorkbench,
  onNavigateResponse,
  className = "",
}) => {
  const [activeCaseIndex, setActiveCaseIndex] = useState<number>(0);
  const [investigatingCase, setInvestigatingCase] = useState<RealWorldFraudCase | null>(null);

  // Swipe & drag state
  const [dragStartX, setDragStartX] = useState<number | null>(null);
  const [dragCurrentX, setDragCurrentX] = useState<number | null>(null);
  const isDraggingRef = useRef<boolean>(false);
  const carouselContainerRef = useRef<HTMLDivElement | null>(null);

  const cases = REAL_WORLD_CASES;
  const totalCases = cases.length;

  const handlePrev = useCallback(() => {
    setActiveCaseIndex((prev) => (prev > 0 ? prev - 1 : totalCases - 1));
  }, [totalCases]);

  const handleNext = useCallback(() => {
    setActiveCaseIndex((prev) => (prev < totalCases - 1 ? prev + 1 : 0));
  }, [totalCases]);

  const handleSelectCaseById = useCallback(
    (caseId: string) => {
      const idx = cases.findIndex((c) => c.id === caseId);
      if (idx !== -1) {
        setActiveCaseIndex(idx);
      }
    },
    [cases]
  );

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") {
        handlePrev();
      } else if (e.key === "ArrowRight") {
        handleNext();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handlePrev, handleNext]);

  // Touch handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    setDragStartX(e.touches[0].clientX);
    setDragCurrentX(e.touches[0].clientX);
    isDraggingRef.current = false;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (dragStartX === null) return;
    const currentX = e.touches[0].clientX;
    setDragCurrentX(currentX);
    if (Math.abs(currentX - dragStartX) > 8) {
      isDraggingRef.current = true;
    }
  };

  const handleTouchEnd = () => {
    if (dragStartX !== null && dragCurrentX !== null) {
      const deltaX = dragCurrentX - dragStartX;
      if (deltaX > 45) {
        handlePrev();
      } else if (deltaX < -45) {
        handleNext();
      }
    }
    setDragStartX(null);
    setDragCurrentX(null);
    setTimeout(() => {
      isDraggingRef.current = false;
    }, 50);
  };

  // Mouse drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    // Only drag with primary left mouse button
    if (e.button !== 0) return;
    setDragStartX(e.clientX);
    setDragCurrentX(e.clientX);
    isDraggingRef.current = false;
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragStartX === null) return;
    const currentX = e.clientX;
    setDragCurrentX(currentX);
    if (Math.abs(currentX - dragStartX) > 8) {
      isDraggingRef.current = true;
    }
  };

  const handleMouseUp = () => {
    if (dragStartX !== null && dragCurrentX !== null) {
      const deltaX = dragCurrentX - dragStartX;
      if (deltaX > 45) {
        handlePrev();
      } else if (deltaX < -45) {
        handleNext();
      }
    }
    setDragStartX(null);
    setDragCurrentX(null);
    setTimeout(() => {
      isDraggingRef.current = false;
    }, 50);
  };

  const handleMouseLeave = () => {
    if (dragStartX !== null) {
      handleMouseUp();
    }
  };

  // Get index with wrapping
  const getIndex = (offset: number) => {
    return (activeCaseIndex + offset + totalCases) % totalCases;
  };

  const activeCase = cases[activeCaseIndex];
  const prevCase = cases[getIndex(-1)];
  const nextCase = cases[getIndex(1)];

  return (
    <section
      id="real-world-cases"
      className={`relative w-full overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-b from-[#080E1C] via-[#050B14] to-[#03060C] p-6 sm:p-10 lg:p-12 shadow-2xl ${className}`}
    >
      {/* Background ambient lighting */}
      <div className="pointer-events-none absolute -top-40 left-10 h-96 w-96 rounded-full bg-emerald-500/10 blur-[140px]" />
      <div className="pointer-events-none absolute -bottom-40 right-10 h-96 w-96 rounded-full bg-cyan-500/10 blur-[140px]" />

      {/* Main Grid: Left Column (40%) & Right Column (60%) */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
        {/* =========================================================================
            LEFT COLUMN: EDITORIAL STORYTELLING & DOTTED INDIA MAP
        ========================================================================= */}
        <div className="lg:col-span-5 space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Section Eyebrow Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-3.5 py-1 text-xs font-mono font-bold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>VERISIGHT INTELLIGENCE</span>
            </div>

            {/* Headline matching user's visual reference */}
            <h2 className="text-3xl sm:text-4xl lg:text-[42px] font-extrabold text-white leading-[1.15] tracking-tight font-sans">
              It happened to them.
              <br />
              Learn to recognize it
              <br />
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                before it happens to you.
              </span>
            </h2>

            {/* Introductory Narrative Prose */}
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-sans max-w-lg">
              Explore real UPI fraud cases, fake payment screenshots and digital deception across India.
              Understand the patterns, learn the warning signs, and see how Verisight helps investigate
              suspicious evidence.
            </p>
          </div>

          {/* Authentic Dotted India Map */}
          <div className="pt-2">
            <DottedIndiaMap
              cases={cases}
              activeCaseId={activeCase.id}
              onSelectCase={handleSelectCaseById}
            />
          </div>
        </div>

        {/* =========================================================================
            RIGHT COLUMN: LAYERED 3D DECK CAROUSEL (SCAMSHIELD & DESIGN SPEC)
        ========================================================================= */}
        <div
          ref={carouselContainerRef}
          className="lg:col-span-7 flex flex-col justify-center select-none"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
        >
          {/* Layered Cards Stage Container */}
          <div className="relative w-full h-[540px] sm:h-[580px] flex items-center justify-center overflow-hidden">
            {/* ================= LEFT CARD (PEEKING PREVIOUS) ================= */}
            <div
              onClick={() => handlePrev()}
              className="absolute left-0 sm:left-4 w-[280px] sm:w-[320px] rounded-3xl bg-white text-slate-900 shadow-2xl overflow-hidden border border-slate-100 transition-all duration-500 ease-out z-10 opacity-40 scale-[0.84] -translate-x-[45%] sm:-translate-x-[30%] pointer-events-auto cursor-pointer hover:opacity-70"
            >
              <div className="relative h-44 w-full bg-slate-800 overflow-hidden">
                <img
                  src={prevCase.imageUrl}
                  alt={prevCase.imageAlt}
                  className="w-full h-full object-cover filter brightness-95"
                />
              </div>
              <div className="p-4 space-y-2 text-left">
                <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-500">
                  <MapPin className="h-3 w-3 text-slate-400" />
                  <span>
                    {prevCase.city}, {prevCase.state}
                  </span>
                </div>
                <div className="font-mono text-xl font-black text-[#dc2626]">
                  {prevCase.reportedLoss}
                </div>
                <h4 className="text-sm font-bold text-slate-900 line-clamp-1">
                  {prevCase.headline}
                </h4>
                <p className="text-[11px] text-slate-600 line-clamp-2">
                  {prevCase.summary}
                </p>
                <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2 text-[10px] text-emerald-900">
                  💡 {prevCase.preventionInsight}
                </div>
                <div className="text-[10px] text-slate-400 pt-1">
                  Source: {prevCase.publisher}
                </div>
              </div>
            </div>

            {/* ================= ACTIVE CENTER CARD ================= */}
            <div className="relative w-[320px] sm:w-[380px] rounded-3xl bg-white text-slate-900 shadow-[0_25px_60px_rgba(0,0,0,0.8),0_0_35px_rgba(16,185,129,0.16)] overflow-hidden border border-slate-200 transition-all duration-300 z-20 scale-100">
              {/* Featured Top Editorial Image (~40% of card) */}
              <div className="relative h-48 sm:h-56 w-full bg-slate-900 overflow-hidden">
                <img
                  src={activeCase.imageUrl}
                  alt={activeCase.imageAlt}
                  className="w-full h-full object-cover"
                />

                {/* Tilted Red Rubber Stamp Badge */}
                <div className="absolute top-4 right-4 z-10 transform -rotate-12 select-none pointer-events-none rounded border-2 border-red-500 bg-red-950/90 px-3 py-1 font-mono text-xs font-black tracking-widest text-red-400 shadow-xl backdrop-blur-md uppercase">
                  REPORTED CASE
                </div>
              </div>

              {/* Card Body */}
              <div className="p-5 sm:p-6 space-y-3 text-left">
                {/* Location and Date */}
                <div className="flex items-center gap-3 text-xs font-semibold text-slate-500 font-sans">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-slate-700" />
                    <span>
                      {activeCase.city}, {activeCase.state}
                    </span>
                  </div>
                  <span className="text-slate-300">|</span>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <span>{activeCase.incidentMonthYear}</span>
                  </div>
                </div>

                {/* Huge Financial Loss Figure in Bold Red */}
                <div className="font-mono text-3xl sm:text-4xl font-black text-[#dc2626] tracking-tight">
                  {activeCase.reportedLoss}
                </div>

                {/* Headline */}
                <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug font-sans">
                  {activeCase.headline}
                </h3>

                {/* Narrative Summary */}
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-sans line-clamp-2">
                  {activeCase.summary}
                </p>

                {/* What Could Have Helped Prevent It Box */}
                <div className="rounded-xl border border-emerald-300 bg-[#ecfdf5] p-3">
                  <div className="text-[10px] font-bold tracking-wider text-emerald-800 uppercase flex items-center gap-1.5 font-mono">
                    <Lightbulb className="h-3.5 w-3.5 text-emerald-700" />
                    <span>WHAT COULD HAVE HELPED PREVENT IT?</span>
                  </div>
                  <p className="mt-1 text-xs text-emerald-950 font-medium leading-relaxed font-sans">
                    {activeCase.preventionInsight}
                  </p>
                </div>

                {/* Card Bottom: Source Attribution & Read Full Report Link */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                  <span className="text-slate-400 font-medium">
                    Source: {activeCase.publisher}
                  </span>

                  <button
                    type="button"
                    onClick={(e) => {
                      if (!isDraggingRef.current) {
                        e.stopPropagation();
                        setInvestigatingCase(activeCase);
                      }
                    }}
                    className="font-bold text-slate-900 hover:text-emerald-600 flex items-center gap-1 transition-colors"
                  >
                    <span>Read Full Report</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* ================= RIGHT CARD (PEEKING NEXT) ================= */}
            <div
              onClick={() => handleNext()}
              className="absolute right-0 sm:right-4 w-[280px] sm:w-[320px] rounded-3xl bg-white text-slate-900 shadow-2xl overflow-hidden border border-slate-100 transition-all duration-500 ease-out z-10 opacity-40 scale-[0.84] translate-x-[45%] sm:translate-x-[30%] pointer-events-auto cursor-pointer hover:opacity-70"
            >
              <div className="relative h-44 w-full bg-slate-800 overflow-hidden">
                <img
                  src={nextCase.imageUrl}
                  alt={nextCase.imageAlt}
                  className="w-full h-full object-cover filter brightness-95"
                />
              </div>
              <div className="p-4 space-y-2 text-left">
                <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-500">
                  <MapPin className="h-3 w-3 text-slate-400" />
                  <span>
                    {nextCase.city}, {nextCase.state}
                  </span>
                </div>
                <div className="font-mono text-xl font-black text-[#dc2626]">
                  {nextCase.reportedLoss}
                </div>
                <h4 className="text-sm font-bold text-slate-900 line-clamp-1">
                  {nextCase.headline}
                </h4>
                <p className="text-[11px] text-slate-600 line-clamp-2">
                  {nextCase.summary}
                </p>
                <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2 text-[10px] text-emerald-900">
                  💡 {nextCase.preventionInsight}
                </div>
                <div className="text-[10px] text-slate-400 pt-1">
                  Source: {nextCase.publisher}
                </div>
              </div>
            </div>

            {/* Left & Right Circular Glass Buttons */}
            <button
              type="button"
              onClick={handlePrev}
              className="absolute left-2 sm:left-12 top-1/2 -translate-y-1/2 z-30 h-11 w-11 rounded-full border border-white/20 bg-slate-900/80 text-white flex items-center justify-center hover:bg-slate-800 hover:scale-105 transition-all shadow-xl backdrop-blur-md"
              aria-label="Previous case"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>

            <button
              type="button"
              onClick={handleNext}
              className="absolute right-2 sm:right-12 top-1/2 -translate-y-1/2 z-30 h-11 w-11 rounded-full border border-white/20 bg-slate-900/80 text-white flex items-center justify-center hover:bg-slate-800 hover:scale-105 transition-all shadow-xl backdrop-blur-md"
              aria-label="Next case"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>

          {/* Dots Pagination & Counter */}
          <div className="mt-4 flex items-center justify-between px-6">
            <div className="flex items-center gap-1.5">
              {cases.map((c, i) => (
                <button
                  key={c.id}
                  onClick={() => setActiveCaseIndex(i)}
                  className={`h-1.5 rounded-full transition-all ${
                    i === activeCaseIndex
                      ? "w-8 bg-emerald-400"
                      : "w-2 bg-slate-700 hover:bg-slate-500"
                  }`}
                  aria-label={`Go to case ${i + 1}: ${c.city}`}
                />
              ))}
            </div>

            <span className="font-mono text-xs text-slate-400 font-semibold">
              {activeCaseIndex + 1} / {totalCases}
            </span>
          </div>
        </div>
      </div>

      {/* =========================================================================
          BOTTOM BAR: HOW VERISIGHT HELPS IN SUCH CASES (FULL WIDTH)
      ========================================================================= */}
      <div className="mt-12 rounded-2xl border border-white/10 bg-[#071322]/90 p-4 sm:p-5 backdrop-blur-md shadow-xl flex flex-col lg:flex-row items-center justify-between gap-4">
        {/* Left Indicator Label */}
        <div className="flex items-center gap-2 text-sm sm:text-base font-bold text-white shrink-0 self-start lg:self-center">
          <span className="h-5 w-1 bg-cyan-400 rounded-full" />
          <span>How Verisight helps in such cases:</span>
        </div>

        {/* 4 Forensic Pillars */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 w-full lg:w-auto flex-1 lg:ml-6">
          {/* Pillar 1 */}
          <div
            onClick={onNavigateWorkbench}
            className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-white/[0.03] px-3.5 py-2.5 hover:border-cyan-500/30 hover:bg-cyan-500/10 transition-colors cursor-pointer group"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400 group-hover:bg-cyan-500/25 transition-colors shrink-0">
              <Search className="h-4 w-4" />
            </div>
            <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
              Examine suspicious evidence
            </span>
          </div>

          {/* Pillar 2 */}
          <div
            onClick={onNavigateWorkbench}
            className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-white/[0.03] px-3.5 py-2.5 hover:border-emerald-500/30 hover:bg-emerald-500/10 transition-colors cursor-pointer group"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400 group-hover:bg-emerald-500/25 transition-colors shrink-0">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
              Analyze for forgery indicators
            </span>
          </div>

          {/* Pillar 3 */}
          <div
            onClick={() => onNavigateResponse?.()}
            className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-white/[0.03] px-3.5 py-2.5 hover:border-sky-500/30 hover:bg-sky-500/10 transition-colors cursor-pointer group"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/15 text-sky-400 group-hover:bg-sky-500/25 transition-colors shrink-0">
              <FileCheck2 className="h-4 w-4" />
            </div>
            <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
              Prepare an evidence dossier
            </span>
          </div>

          {/* Pillar 4 */}
          <div
            onClick={() => onNavigateResponse?.()}
            className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-white/[0.03] px-3.5 py-2.5 hover:border-emerald-500/30 hover:bg-emerald-500/10 transition-colors cursor-pointer group"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400 group-hover:bg-emerald-500/25 transition-colors shrink-0">
              <Zap className="h-4 w-4" />
            </div>
            <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
              Get guided response & reporting
            </span>
          </div>
        </div>
      </div>

      {/* Expandable Case Investigation Modal */}
      <CaseInvestigationModal
        caseItem={investigatingCase}
        isOpen={!!investigatingCase}
        onClose={() => setInvestigatingCase(null)}
        onNavigateWorkbench={onNavigateWorkbench}
        onNavigateResponse={onNavigateResponse}
      />
    </section>
  );
};
