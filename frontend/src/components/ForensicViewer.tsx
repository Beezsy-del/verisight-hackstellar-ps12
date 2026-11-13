import React, { useState, useRef, useEffect } from "react";
import {
  Layers,
  Activity,
  Waves,
  Copy,
  Split,
  Grid,
  Eye,
  ZoomIn,
  ZoomOut,
  Move,
  Maximize2,
  PanelRightClose,
  PanelRightOpen,
  SlidersHorizontal,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ForensicAnalysisReport, BoundingBox } from "../types/forensic";
import { SynchronizedLoupe } from "./SynchronizedLoupe";
import { ComparisonSlider } from "./ComparisonSlider";
import { ForensicReticle } from "./ForensicReticle";
import { toast } from "sonner";
import { useVerdictTheme } from "./AmbientThreatBackground";

export type ViewMode =
  | "ORIGINAL"
  | "ELA"
  | "WAVELET"
  | "COPY_MOVE"
  | "SPLIT"
  | "LOUPE"
  | "QUAD";

interface ForensicViewerProps {
  report: ForensicAnalysisReport | null;
  selectedLocus: BoundingBox | null;
  onSelectLocus?: (box: BoundingBox | null) => void;
  isSidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
  isAdvancedMode?: boolean;
  viewMode?: ViewMode;
  onViewModeChange?: (mode: ViewMode) => void;
}

export const ForensicViewer: React.FC<ForensicViewerProps> = ({
  report,
  selectedLocus,
  onSelectLocus,
  isSidebarCollapsed = false,
  onToggleSidebar,
  isAdvancedMode = false,
  viewMode: controlledViewMode,
  onViewModeChange,
}) => {
  const [internalViewMode, setInternalViewMode] = useState<ViewMode>("ORIGINAL");
  const { borderClass, glowClass } = useVerdictTheme();
  const viewMode = controlledViewMode ?? internalViewMode;
  const setViewMode = (mode: ViewMode) => {
    setInternalViewMode(mode);
    onViewModeChange?.(mode);
  };

  const [showLasers, setShowLasers] = useState<boolean>(false);
  const [showBoxes, setShowBoxes] = useState<boolean>(false);
  const [showGrid, setShowGrid] = useState<boolean>(false);
  const [zoom, setZoom] = useState(1);
  const [nativeZoom, setNativeZoom] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [loadedSource, setLoadedSource] = useState<string | null>(null);
  useEffect(() => setImageError(false), [report?.file_sha256, viewMode]);
  const [isPanning, setIsPanning] = useState(false);
  const [viewportSize, setViewportSize] = useState({ width: 1280, height: 800 });

  // Laser scanline sweep trigger on report change
  const [isScanning, setIsScanning] = useState(false);

  // Loupe and Reticle coordinate tracking
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({
    x: 50,
    y: 50,
  });
  const [isHovering, setIsHovering] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);
  const panStartRef = useRef<{
    pointerId: number;
    clientX: number;
    clientY: number;
    scrollLeft: number;
    scrollTop: number;
  } | null>(null);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const updateSize = () =>
      setViewportSize({ width: viewport.clientWidth, height: viewport.clientHeight });
    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(viewport);
    return () => observer.disconnect();
  }, [Boolean(report)]);

  useEffect(() => {
    if (!nativeZoom && zoom === 1) viewportRef.current?.scrollTo(0,0);
  }, [viewportSize.width, viewportSize.height, nativeZoom, zoom, report?.file_sha256]);

  useEffect(() => {setShowLasers(isAdvancedMode);setShowBoxes(isAdvancedMode);},[isAdvancedMode]);
  useEffect(() => {if(selectedLocus)setShowBoxes(true);},[selectedLocus]);
  // Reset zoom and fire 450ms laser scanline sweep on evidence change
  useEffect(() => {
    setZoom(1); setNativeZoom(false); setImageError(false);
    if (report?.file_sha256) {
      setIsScanning(true);
      const timer = setTimeout(() => setIsScanning(false), 550);
      return () => clearTimeout(timer);
    }
  }, [report?.file_sha256]);

  if (!report) {
    return (
      <div className="flex min-h-[55dvh] w-full flex-1 flex-col items-center justify-center bg-transparent text-slate-500">
        <Layers className="mb-3 h-10 w-10 text-sky-500/40 animate-pulse stroke-[1.5]" />
        <p className="font-mono text-xs uppercase tracking-wider text-slate-400">
          Awaiting Forensic Screenshot Input
        </p>
        <p className="mt-1 text-[11px] text-slate-600">
          Select an investigation scenario above or drop an evidence screenshot
        </p>
      </div>
    );
  }

  const {
    image_width,
    image_height,
    original_image_b64,
    layer1,
    layer2,
    all_bounding_boxes,
  } = report;

  // Active channel image selection
  let currentLayerImg = original_image_b64;
  let layerLabel = "Original Evidence";

  if (viewMode === "ELA") {
    currentLayerImg = layer1.ela_b64;
    layerLabel = "Compression Analysis (Inferno Heatmap)";
  } else if (viewMode === "WAVELET") {
    currentLayerImg = layer1.wavelet_noise_b64;
    layerLabel = "Noise Consistency (Daubechies db4)";
  } else if (viewMode === "COPY_MOVE") {
    currentLayerImg = layer1.clone_b64;
    layerLabel = "Copy-Move Clones (ORB Keypoint Vectors)";
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const xPct = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
    const yPct = Math.max(0, Math.min(100, ((e.clientY - rect.top) / rect.height) * 100));
    setCursorPos({ x: xPct, y: yPct });
  };

  const clampZoom = (value: number) => Math.min(5, Math.max(0.25, value));

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    setZoom((current) => clampZoom(current + (e.deltaY < 0 ? 0.25 : -0.25)));
  };

  const handlePanStart = (e: React.PointerEvent<HTMLDivElement>) => {
    if (zoom <= 1 || e.button !== 0 || !viewportRef.current) return;
    if (
      (e.target as HTMLElement).closest("button") ||
      (e.target as HTMLElement).closest("[role='slider']")
    )
      return;
    panStartRef.current = {
      pointerId: e.pointerId,
      clientX: e.clientX,
      clientY: e.clientY,
      scrollLeft: viewportRef.current.scrollLeft,
      scrollTop: viewportRef.current.scrollTop,
    };
    e.currentTarget.setPointerCapture(e.pointerId);
    setIsPanning(true);
    e.preventDefault();
  };

  const handlePanMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const start = panStartRef.current;
    const viewport = viewportRef.current;
    if (!start || !viewport || start.pointerId !== e.pointerId) return;
    viewport.scrollLeft = start.scrollLeft - (e.clientX - start.clientX);
    viewport.scrollTop = start.scrollTop - (e.clientY - start.clientY);
  };

  const handlePanEnd = (e: React.PointerEvent<HTMLDivElement>) => {
    if (panStartRef.current?.pointerId !== e.pointerId) return;
    panStartRef.current = null;
    setIsPanning(false);
  };

  const PRIMARY_MODES: { id: ViewMode; label: string; icon: React.ReactNode }[] = [
    { id: "ORIGINAL", label: "Original", icon: <Eye className="h-3.5 w-3.5" /> },
    { id: "ELA", label: "Compression (ELA)", icon: <Activity className="h-3.5 w-3.5" /> },
    { id: "WAVELET", label: "Noise (Wavelet)", icon: <Waves className="h-3.5 w-3.5" /> },
    { id: "COPY_MOVE", label: "Clones (ORB)", icon: <Copy className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="relative flex h-[65dvh] shrink-0 md:h-full min-h-[360px] md:min-h-0 min-w-0 w-full md:flex-1 flex-col overflow-hidden bg-transparent select-none">
      {/* Sub-Toolbar (h-11 bg-[#0B101B] border-b border-white/[0.06]) */}
      <div className="flex min-h-11 flex-wrap gap-2 py-2 shrink-0 items-center justify-between border-b border-white/[0.06] bg-[#0B101B]/95 px-3 backdrop-blur text-xs">
        {/* Left: Sliding Segmented Primary View Tabs */}
        <div className="relative flex flex-wrap items-center rounded-lg border border-white/[0.07] bg-[#070B14] p-0.5 text-xs">
          {PRIMARY_MODES.map((tab) => {
            const isActive = viewMode === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => {
                  setViewMode(tab.id);
                  toast(`${tab.label} applied`);
                }}
                className={`relative z-10 flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium transition-colors ${
                  isActive ? "text-sky-200" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeForensicTab"
                    className="absolute inset-0 z-[-1] rounded-md bg-sky-500/20 border border-sky-500/40 shadow-sm"
                    transition={{ type: "spring", stiffness: 420, damping: 32 }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Center: Split Slider, Dual Loupe, Quad Matrix separated by 1px divider */}
        <div className="flex items-center gap-1.5">
          <div className="h-4 w-px bg-white/10" />

          <button
            type="button"
            onClick={() => {
              setViewMode("SPLIT");
              toast("Split Comparison Slider active");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all active:scale-[0.97] ${
              viewMode === "SPLIT"
                ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/50"
                : "text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 border border-transparent"
            }`}
            title="Interactive draggable before/after comparison slider (S)"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span>Split Slider</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setViewMode("LOUPE");
              toast("3X Dual Loupe active");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all active:scale-[0.97] ${
              viewMode === "LOUPE"
                ? "bg-purple-600/30 text-purple-300 border border-purple-500/50"
                : "text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 border border-transparent"
            }`}
            title="Synchronized 3X Dual Loupe (L)"
          >
            <Split className="h-3.5 w-3.5" />
            <span>Dual Loupe</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setViewMode("QUAD");
              toast("Quad-Spectral Matrix active");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all active:scale-[0.97] ${
              viewMode === "QUAD"
                ? "bg-emerald-600/30 text-emerald-300 border border-emerald-500/50"
                : "text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 border border-transparent"
            }`}
            title="4-Quadrant synchronized overview (Q)"
          >
            <Grid className="h-3.5 w-3.5" />
            <span>Quad Matrix</span>
          </button>
        </div>

        {/* Right: Custom Tactile Pill Switches (No raw browser checkboxes!) */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setShowBoxes((prev) => !prev);
              toast(!showBoxes ? "Anomaly Loci enabled" : "Anomaly Loci hidden");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2 py-0.5 font-mono text-[11px] transition-all border active:scale-[0.96] ${
              showBoxes
                ? "border-rose-500/40 bg-rose-500/15 text-rose-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)]"
                : "border-white/[0.07] bg-[#070B14] text-slate-500 hover:text-slate-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                showBoxes ? "bg-rose-400 shadow-[0_0_6px_#f43f5e]" : "bg-slate-600"
              }`}
            />
            <span>Anomaly Loci</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setShowLasers((prev) => !prev);
              toast(!showLasers ? "Baselines enabled" : "Baselines hidden");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2 py-0.5 font-mono text-[11px] transition-all border active:scale-[0.96] ${
              showLasers
                ? "border-sky-500/40 bg-sky-500/15 text-sky-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)]"
                : "border-white/[0.07] bg-[#070B14] text-slate-500 hover:text-slate-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                showLasers ? "bg-sky-400 shadow-[0_0_6px_#38bdf8]" : "bg-slate-600"
              }`}
            />
            <span>Baselines</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setShowGrid((prev) => !prev);
              toast(!showGrid ? "Calibration Grid enabled" : "Calibration Grid hidden");
            }}
            className={`flex items-center gap-1.5 rounded-md px-2 py-0.5 font-mono text-[11px] transition-all border active:scale-[0.96] ${
              showGrid
                ? "border-purple-500/40 bg-purple-500/15 text-purple-300 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)]"
                : "border-white/[0.07] bg-[#070B14] text-slate-500 hover:text-slate-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                showGrid ? "bg-purple-400 shadow-[0_0_6px_#c084fc]" : "bg-slate-600"
              }`}
            />
            <span>Grid</span>
          </button>

          {/* Toggle Sidebar Button */}
          {onToggleSidebar && (
            <button
              type="button"
              onClick={onToggleSidebar}
              className="flex items-center gap-1 rounded-md border border-white/[0.08] bg-[#070B14] px-2 py-0.5 text-[11px] text-slate-300 transition-colors hover:bg-white/[0.06] active:scale-[0.96]"
              title={
                isSidebarCollapsed
                  ? "Expand Risk Dossier panel ([)"
                  : "Collapse Risk Dossier to widen canvas ([)"
              }
            >
              {isSidebarCollapsed ? (
                <>
                  <PanelRightOpen className="h-3 w-3 text-sky-400" />
                  <span>Dossier</span>
                </>
              ) : (
                <>
                  <PanelRightClose className="h-3 w-3 text-sky-400" />
                  <span>Wide View</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Main Forensic Canvas */}
      {(() => {
        const availableWidth = Math.max(240, viewportSize.width - 32);
        const availableHeight = Math.max(100, viewportSize.height - 72);
        const quadWidth = Math.min(860, availableWidth, availableHeight * 0.9);
        const fitScale = Math.min(
          availableWidth / image_width,
          availableHeight / image_height,
          1,
        );
        const canvasWidth = Math.round(
          (viewMode === "QUAD" ? quadWidth : image_width * (nativeZoom ? 1 : fitScale)) * zoom,
        );
        const canvasHeight = Math.round(
          (viewMode === "QUAD" ? quadWidth * (10 / 9) : image_height * (nativeZoom ? 1 : fitScale)) * zoom,
        );

        return (
          <>
            <div
              ref={viewportRef}
              onWheel={handleWheel}
              onPointerDown={handlePanStart}
              onPointerMove={handlePanMove}
              onPointerUp={handlePanEnd}
              onPointerCancel={handlePanEnd}
              className="relative min-h-0 flex-1 touch-pan-x touch-pan-y overflow-auto p-3 md:p-5"
              aria-label="Zoomable forensic screenshot viewer"
            >
              <div
                className={`flex ${
                  canvasWidth > availableWidth ? "justify-start" : "justify-center"
                } ${canvasHeight > availableHeight ? "items-start" : "items-center"}`}
                style={{
                  width: Math.max(availableWidth, canvasWidth),
                  height: Math.max(availableHeight, canvasHeight),
                }}
              >
                {/* Mode A: Interactive Split Comparison Slider */}
                {viewMode === "SPLIT" ? (
                  <div
                    style={{ width: canvasWidth, height: canvasHeight }}
                    className="relative flex items-center justify-center w-full h-full"
                  >
                    <ComparisonSlider
                      originalSrc={original_image_b64}
                      elaSrc={layer1.ela_b64}
                      waveletSrc={layer1.wavelet_noise_b64}
                      cloneSrc={layer1.clone_b64}
                      aspectRatioWidth={image_width}
                      aspectRatioHeight={image_height}
                      className="h-full w-full"
                    />
                  </div>
                ) : viewMode === "QUAD" ? (
                  /* Mode B: 2x2 Synchronized Quad-Spectral Grid */
                  <div
                    className="grid grid-cols-2 gap-3.5 aspect-[9/10] w-full"
                    style={{ width: canvasWidth, height: canvasHeight }}
                  >
                    <div className="flex flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0C1222]/90 shadow-xl">
                      <div className="border-b border-white/[0.08] bg-[#070B14]/80 px-2.5 py-1.5 font-mono text-[10px] text-sky-400">
                        1. ORIGINAL EVIDENCE CAPTURE
                      </div>
                      <div className="flex flex-1 items-center justify-center p-2">
                        <img
                          src={original_image_b64}
                          alt="Original"
                          className="max-h-full object-contain rounded"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0C1222]/90 shadow-xl">
                      <div className="border-b border-white/[0.08] bg-[#070B14]/80 px-2.5 py-1.5 font-mono text-[10px] text-amber-400">
                        2. COMPRESSION ANALYSIS (ELA)
                      </div>
                      <div className="flex flex-1 items-center justify-center p-2">
                        <img
                          src={layer1.ela_b64}
                          alt="ELA"
                          className="max-h-full object-contain rounded"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0C1222]/90 shadow-xl">
                      <div className="border-b border-white/[0.08] bg-[#070B14]/80 px-2.5 py-1.5 font-mono text-[10px] text-cyan-400">
                        3. NOISE CONSISTENCY (WAVELET db4)
                      </div>
                      <div className="flex flex-1 items-center justify-center p-2">
                        <img
                          src={layer1.wavelet_noise_b64}
                          alt="Wavelet"
                          className="max-h-full object-contain rounded"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0C1222]/90 shadow-xl">
                      <div className="border-b border-white/[0.08] bg-[#070B14]/80 px-2.5 py-1.5 font-mono text-[10px] text-pink-400">
                        4. COPY-MOVE CLONED VECTORS (ORB)
                      </div>
                      <div className="flex flex-1 items-center justify-center p-2">
                        <img
                          src={layer1.clone_b64}
                          alt="Clone"
                          className="max-h-full object-contain rounded"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Mode C: Single Spectral Canvas with Laser Sweep & SVG Overlays */
                  <div
                    ref={containerRef}
                    onMouseEnter={() => setIsHovering(true)}
                    onMouseLeave={() => setIsHovering(false)}
                    onMouseMove={handleMouseMove}
                    className={`relative shrink-0 flex items-center justify-center rounded-xl overflow-hidden shadow-2xl bg-black/90 transition-colors duration-200 border ${borderClass} ${glowClass}`}
                    style={{
                      boxSizing: "content-box",
                      width: canvasWidth,
                      height: canvasHeight,
                      aspectRatio: `${image_width} / ${image_height}`,
                      cursor: zoom > 1 ? (isPanning ? "grabbing" : "grab") : "default",
                    }}
                  >
                    {!imageError && loadedSource !== currentLayerImg && <p role="status" className="absolute z-40 rounded bg-slate-950/90 p-3 text-xs text-sky-200">Loading evidence image…</p>}
                    {imageError && <p role="alert" className="absolute z-40 bg-slate-950 p-4 text-rose-300">Image preview could not load. Select the case again or re-upload.</p>}
                    {/* Base Image */}
                    <img
                      src={currentLayerImg}
                      alt={layerLabel}
                      onError={() => setImageError(true)}
                      onLoad={(event) => {setImageError(false); setLoadedSource(event.currentTarget.getAttribute("src"));}}
                      className="w-full h-full object-contain select-none pointer-events-none"
                    />

                    {/* Laser Scanline Sweep Animation (450ms on case change) */}
                    <AnimatePresence>
                      {isScanning && (
                        <motion.div
                          initial={{ top: "0%", opacity: 0.9 }}
                          animate={{ top: "100%", opacity: 0.9 }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 0.45, ease: "easeInOut" }}
                          className="pointer-events-none absolute left-0 right-0 z-30 h-[2px] bg-gradient-to-r from-transparent via-sky-400 to-transparent shadow-[0_0_12px_#38bdf8]"
                        />
                      )}
                    </AnimatePresence>

                    {/* Forensic Reticle & Coordinate HUD */}
                    <ForensicReticle
                      cursorPos={isHovering ? cursorPos : null}
                      imageWidth={image_width}
                      imageHeight={image_height}
                      zoom={zoom}
                    />

                    {/* Optional Coordinate Calibration Grid */}
                    {showGrid && (
                      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px] opacity-25" />
                    )}

                    {/* Interactive SVG Overlay (Lasers & Anomaly Reticles) */}
                    <svg
                      className="absolute inset-0 w-full h-full pointer-events-none"
                      viewBox={`0 0 ${image_width} ${image_height}`}
                      preserveAspectRatio="xMidYMid meet"
                    >
                      {/* Sub-pixel Horizontal Baseline Alignment Lasers */}
                      {showLasers &&
                        layer2.lasers.map((laser, idx) => {
                          const hasAlignmentCue = laser.is_tampered;
                          const x1 = laser.x_start ?? 40;
                          const x2 = laser.x_end ?? image_width - 40;
                          const y = laser.y_baseline;

                          return (
                            <g key={`laser-${idx}`}>
                              <line
                                x1={x1}
                                y1={y}
                                x2={x2}
                                y2={y}
                                stroke={hasAlignmentCue ? "#f43f5e" : "#38bdf8"}
                                strokeWidth={hasAlignmentCue ? "2.5" : "1.5"}
                                strokeDasharray={hasAlignmentCue ? "none" : "4 3"}
                                className={hasAlignmentCue ? "laser-critical" : "laser-aligned"}
                              />
                              <circle
                                cx={x1}
                                cy={y}
                                r={hasAlignmentCue ? 4 : 2.5}
                                fill={hasAlignmentCue ? "#f43f5e" : "#38bdf8"}
                              />
                              {hasAlignmentCue && laser.callout_text && (
                                <g transform={`translate(${x2 + 8}, ${y - 8})`}>
                                  <rect
                                    x="0"
                                    y="0"
                                    width="110"
                                    height="18"
                                    rx="3"
                                    fill="#f43f5e"
                                    stroke="#ffffff"
                                    strokeWidth="0.5"
                                  />
                                  <text
                                    x="5"
                                    y="13"
                                    fill="#ffffff"
                                    fontSize="11"
                                    fontWeight="bold"
                                    fontFamily="monospace"
                                  >
                                    {laser.callout_text}
                                  </text>
                                </g>
                              )}
                            </g>
                          );
                        })}

                      {/* Anomaly Bounding Box Reticles */}
                      {showBoxes &&
                        [...all_bounding_boxes, ...(selectedLocus?.anomaly_type === "OCR_REVIEW_REGION" ? [selectedLocus] : [])].map((box, bIdx) => {
                          const isLocus = box.anomaly_type === "CROSS_LAYER_SYNERGY_LOCUS";
                          const isSelected =
                            selectedLocus &&
                            selectedLocus.x === box.x &&
                            selectedLocus.y === box.y;

                          const strokeColor = box.anomaly_type === "OCR_REVIEW_REGION" ? "#38bdf8" : isLocus
                            ? "#f59e0b"
                            : box.layer === 1
                            ? "#ec4899"
                            : box.layer === 2
                            ? "#f43f5e"
                            : "#38bdf8";

                          return (
                            <g
                              key={`bbox-${bIdx}`}
                              className="cursor-pointer pointer-events-auto"
                              onClick={() => {
                                onSelectLocus?.(box);
                                toast(`Inspecting region: ${box.label}`);
                              }}
                            >
                              <rect
                                x={box.x}
                                y={box.y}
                                width={box.width}
                                height={box.height}
                                fill={
                                  isLocus
                                    ? "rgba(245, 158, 11, 0.15)"
                                    : box.anomaly_type === "OCR_REVIEW_REGION" ? "rgba(56, 189, 248, 0.08)" : "rgba(244, 63, 94, 0.08)"
                                }
                                stroke={strokeColor}
                                strokeWidth={isLocus || isSelected ? "3" : "1.8"}
                                strokeDasharray={isLocus ? "none" : "3 3"}
                              />
                              {/* Corner Reticles */}
                              <line
                                x1={box.x - 4}
                                y1={box.y}
                                x2={box.x + 8}
                                y2={box.y}
                                stroke={strokeColor}
                                strokeWidth="2.5"
                              />
                              <line
                                x1={box.x}
                                y1={box.y - 4}
                                x2={box.x}
                                y2={box.y + 8}
                                stroke={strokeColor}
                                strokeWidth="2.5"
                              />
                              <line
                                x1={box.x + box.width - 8}
                                y1={box.y}
                                x2={box.x + box.width + 4}
                                y2={box.y}
                                stroke={strokeColor}
                                strokeWidth="2.5"
                              />
                              <line
                                x1={box.x + box.width}
                                y1={box.y - 4}
                                x2={box.x + box.width}
                                y2={box.y + 8}
                                stroke={strokeColor}
                                strokeWidth="2.5"
                              />

                              {/* Header Label Badge */}
                              <g
                                transform={`translate(${box.x}, ${Math.max(16, box.y - 6)})`}
                              >
                                <rect
                                  x="0"
                                  y="-14"
                                  width={Math.min(box.width + 20, 240)}
                                  height="16"
                                  rx="2"
                                  fill={strokeColor}
                                />
                                <text
                                  x="4"
                                  y="-2"
                                  fill="#070b14"
                                  fontSize="10"
                                  fontWeight="bold"
                                  fontFamily="monospace"
                                >
                                  {box.label.slice(0, 32)}
                                </text>
                              </g>
                            </g>
                          );
                        })}
                    </svg>
                  </div>
                )}

                {/* 3x Synchronized Loupe (active in LOUPE view or hovering single view) */}
                <SynchronizedLoupe
                  visible={
                    viewMode === "LOUPE" ||
                    (isHovering && viewMode !== "QUAD" && viewMode !== "SPLIT")
                  }
                  x={cursorPos.x}
                  y={cursorPos.y}
                  originalImgSrc={original_image_b64}
                  spectralImgSrc={
                    viewMode !== "ORIGINAL" && viewMode !== "LOUPE" ? currentLayerImg : layer1.ela_b64
                  }
                  spectralLabel={
                    viewMode !== "ORIGINAL" && viewMode !== "LOUPE" ? layerLabel : "Compression Heatmap (ELA)"
                  }
                  imgWidth={image_width}
                  imgHeight={image_height}
                />
              </div>
            </div>

            {/* Precision Viewport Floating Controls */}
            <div className="absolute bottom-4 left-4 z-40 flex items-center gap-1 rounded-xl border border-white/10 bg-[#0C1222]/95 p-1.5 shadow-2xl backdrop-blur-md">
              <button
                type="button"
                onClick={() => setZoom((c) => clampZoom(c - 0.25))}
                disabled={zoom <= 0.25}
                title="Zoom out"
                aria-label="Zoom out"
                className="rounded-lg p-1.5 text-slate-300 hover:bg-white/[0.08] active:scale-[0.95] disabled:opacity-40"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </button>
              <span className="min-w-12 text-center font-mono text-[11px] text-sky-300 font-semibold">
                {Math.round(zoom * (nativeZoom ? 1 : fitScale) * 100)}%
              </span>
              <button
                type="button"
                onClick={() => setZoom((c) => clampZoom(c + 0.25))}
                disabled={zoom >= 5}
                title="Zoom in"
                aria-label="Zoom in"
                className="rounded-lg p-1.5 text-slate-300 hover:bg-white/[0.08] active:scale-[0.95] disabled:opacity-40"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </button>
              <span className="mx-1 h-4 w-px bg-white/10" />
              <button
                type="button"
                onClick={() => {
                  setZoom(1); setNativeZoom(false); viewportRef.current?.scrollTo(0,0);
                  toast("View fit to screen (F)");
                }}
                title="Fit screenshot to screen (F)"
                className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] text-slate-300 hover:bg-white/[0.08] active:scale-[0.96]"
              >
                <Maximize2 className="h-3 w-3" />
                <span>Fit</span>
              </button>
              <button type="button" className="px-2 py-1 text-xs" onClick={() => {setNativeZoom(true); setZoom(1);}}>1x</button>
              <button
                type="button"
                onClick={() => {
                  setZoom(2); setNativeZoom(true);
                  toast("200% Pixel Inspection Scale active");
                }}
                title="200% Pixel Detail"
                className="rounded-lg px-2 py-1 font-mono text-[11px] text-slate-400 hover:bg-white/[0.08] hover:text-slate-100 active:scale-[0.96]"
              >
                2X
              </button>
              <span className="hidden items-center gap-1 pl-2 pr-1 text-[10px] text-slate-500 xl:flex">
                <Move className="h-3 w-3" /> Drag to pan · Ctrl+Scroll
              </span>
            </div>
          </>
        );
      })()}
    </div>
  );
};
