import { loadSimulationSource } from "./services/simulationSource";
import React, { useEffect, useState, useCallback, useRef } from "react";
import { NavigationHeader, AppRoute } from "./components/NavigationHeader";
import { ProductOverview } from "./components/ProductOverview";
import { EvaluationDashboard } from "./components/EvaluationDashboard";
import { WhyVerisight } from "./components/WhyVerisight";
import { ResponseModule } from "./components/response/ResponseModule";
import { AttachedForensicContext } from "./types/response";
import { TopCommandBar } from "./components/TopCommandBar";
import { ForensicViewer, ViewMode } from "./components/ForensicViewer";
import { RiskDossierSidebar } from "./components/RiskDossierSidebar";
import { AmbientThreatBackground } from "./components/AmbientThreatBackground";
import { WhatsAppSimulatorModal } from "./components/WhatsAppSimulatorModal";
import { MobileUploadModal } from "./components/MobileUploadModal";
import { MobileUploadView } from "./components/MobileUploadView";
import { ForensicReportModal } from "./components/ForensicReportModal";
import { Section91NoticeModal } from "./components/Section91NoticeModal";
import { KeyboardShortcutsModal } from "./components/KeyboardShortcutsModal";
import { SkillPipelineHUD } from "./components/SkillPipelineHUD";
import { Toaster, toast } from "sonner";
import { UploadCloud } from "lucide-react";
import {
  ForensicAnalysisReport,
  DemoSampleMeta,
  WhatsAppSimulationResponse,
  BoundingBox,
} from "./types/forensic";
import {
  fetchDemoSamples,
  analyzeDemoSample,
  analyzeUpload,
  simulateWhatsApp,
  fetchHealth,
} from "./services/api";

const getRouteFromLocation = (): AppRoute => {
  const path = window.location.pathname;
  if (path === "/workbench") return "/workbench";
  if (path === "/evaluation") return "/evaluation";
  if (path === "/why-verisight" || path === "/guide") return "/guide";
  if (path === "/response") return "/response";
  return "/";
};

export const App: React.FC = () => {
  const isMobileMode =
    new URLSearchParams(window.location.search).get("mode") === "mobile";

  if (isMobileMode) {
    return <MobileUploadView />;
  }

  return <MainProductApplication />;
};

const MainProductApplication: React.FC = () => {
  // Routing State
  const [currentRoute, setCurrentRoute] = useState<AppRoute>(getRouteFromLocation);

  // Shared Data State
  const [demoSamples, setDemoSamples] = useState<DemoSampleMeta[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(() => {
    return new URLSearchParams(window.location.search).get("case") || "sample_clean";
  });
  const [report, setReport] = useState<ForensicAnalysisReport | null>(null);
  const [appError, setAppError] = useState<string | null>(null);
  const [selectedLocus, setSelectedLocus] = useState<BoundingBox | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [databaseStatus, setDatabaseStatus] = useState<
    "CHECKING" | "HEALTHY" | "UNAVAILABLE" | "NOT_CONFIGURED"
  >("CHECKING");
  const [demoLoadFailed, setDemoLoadFailed] = useState(false);
  const [demoRetry, setDemoRetry] = useState(0);

  // Workstation Ergonomics State
  const [isAdvancedMode, setIsAdvancedMode] = useState<boolean>(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<ViewMode>("ORIGINAL");
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState<boolean>(false);

  // Drag and drop overlay state
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  const dragCounter = useRef(0);

  // Modals state
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState<boolean>(false);
  const [isWhatsAppLoading, setIsWhatsAppLoading] = useState<boolean>(false);
  const [whatsAppData, setWhatsAppDat] = useState<WhatsAppSimulationResponse | null>(null);
  const [isMobileModalOpen, setIsMobileModalOpen] = useState<boolean>(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);
  const [isSection91ModalOpen, setIsSection91ModalOpen] = useState<boolean>(false);
  const [pipelineStage, setPipelineStage] = useState<number>(4);
  const [isPipelineRunning, setIsPipelineRunning] = useState<boolean>(false);

  // Response & Guidance Linked Forensic Context
  const [attachedForensicContext, setAttachedForensicContext] = useState<AttachedForensicContext | null>(null);

  const originalUpload = useRef<File | null>(null);
  const activeRequest = useRef<{ id: number; controller: AbortController | null }>({ id: 0, controller: null });
  const [backendStatus, setBackendStatus] = useState<"CHECKING" | "HEALTHY" | "UNAVAILABLE" | "DEGRADED">("CHECKING");
  const beginAnalysis = useCallback(() => {
    originalUpload.current = null;
    activeRequest.current.controller?.abort();
    const controller = new AbortController();
    const id = activeRequest.current.id + 1;
    activeRequest.current = { id, controller };
    setReport(null); setSelectedLocus(null); setWhatsAppDat(null);
    setIsReportModalOpen(false); setIsSection91ModalOpen(false); setIsWhatsAppModalOpen(false);
    setAttachedForensicContext(null); setViewMode("ORIGINAL");
    setIsLoading(true); setAppError(null);
    return { id, controller };
  }, []);
  const handleSelectSample = useCallback(async (sampleId: string) => {
    const { id, controller } = beginAnalysis();
    setSelectedSampleId(sampleId);
    try {
      const result = await analyzeDemoSample(sampleId, controller.signal);
      if (activeRequest.current.id === id) setReport(result);
    } catch (err) {
      if (activeRequest.current.id === id && !controller.signal.aborted)
        setAppError(`Sample analysis failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      if (activeRequest.current.id === id) setIsLoading(false);
    }
  }, [beginAnalysis]);
  useEffect(() => () => activeRequest.current.controller?.abort(), []);

  // Synchronized Client-Side Navigation
  const handleNavigate = useCallback(
    (route: AppRoute, query?: Record<string, string>) => {
      let resolvedRoute = route;
      if (route === "/why-verisight") resolvedRoute = "/guide";
      let targetUrl = resolvedRoute;
      if (query && Object.keys(query).length > 0) {
        const params = new URLSearchParams(query);
        targetUrl += `?${params.toString()}`;
      }
      window.history.pushState({}, "", targetUrl);
      setCurrentRoute(resolvedRoute);

      if (query?.case) {
        void handleSelectSample(query.case);
      }
    },
    [handleSelectSample]
  );

  // Contextual handoff to Response & Guidance with active investigation facts preserved
  const handleOpenResponseGuidance = useCallback(
    (targetReport: ForensicAnalysisReport) => {
      setAttachedForensicContext({
        case_id: `VS-CASE-${targetReport.file_sha256.slice(0, 8).toUpperCase()}`,
        filename: targetReport.filename || "screenshot.png",
        file_sha256: targetReport.file_sha256,
        image_width: targetReport.image_width,
        image_height: targetReport.image_height,
        overall_tamper_score: targetReport.overall_tamper_score,
        verdict: targetReport.verdict,
        findings: targetReport.findings,
        synergy: targetReport.synergy,
        limitations: "Observations reflect statistical signal anomalies in image containers.",
      });
      handleNavigate("/response");
      toast("Context preserved: Entered Response & Guidance");
    },
    [handleNavigate]
  );

  // Listen to browser Back/Forward buttons
  useEffect(() => {
    const handlePopState = () => {
      setCurrentRoute(getRouteFromLocation());
      const queryCase = new URLSearchParams(window.location.search).get("case");
      if (queryCase && queryCase !== selectedSampleId) {
        void handleSelectSample(queryCase);
      }
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [handleSelectSample, selectedSampleId]);

  // Request catalog and initial sample in parallel
  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((health) => {
        if (active) { setDatabaseStatus(health.database || "NOT_CONFIGURED"); setBackendStatus(health.status === "HEALTHY" ? "HEALTHY" : "DEGRADED"); }
      })
      .catch(() => {
        if (active) { setDatabaseStatus("UNAVAILABLE"); setBackendStatus("UNAVAILABLE"); }
      });

    const catalogRequest = fetchDemoSamples()
      .then((samples) => {
        if (!active) return;
        setDemoSamples(samples);
        setDemoLoadFailed(false);
        if (samples.length === 0) {
          setAppError("The demo sample list is empty.");
        }
      })
      .catch((err) => {
        if (!active) return;
        setDemoLoadFailed(true);
        setAppError(`Could not load demo samples: ${err.message}`);
      });
    void catalogRequest;

    // Load initial sample
    const initCase = new URLSearchParams(window.location.search).get("case") || "sample_clean";
    void handleSelectSample(initCase);

    return () => {
      active = false;
    };
  }, [demoRetry, handleSelectSample]);

  useEffect(() => {
    let active=true;
    const interval=window.setInterval(()=>fetchHealth().then(health=>{
      if(active){setBackendStatus(health.status === "HEALTHY" ? "HEALTHY" : "DEGRADED");setDatabaseStatus(health.database || "NOT_CONFIGURED");}
    }).catch(()=>{if(active)setBackendStatus("UNAVAILABLE");}),30000);
    return()=>{active=false;window.clearInterval(interval);};
  },[]);

  // Global Keyboard Navigation Shortcuts Handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      // Sample 1 - 5 shortcuts
      if (["1", "2", "3", "4", "5"].includes(e.key)) {
        e.preventDefault();
        const sampleId = `sample_${e.key}`;
        if (currentRoute !== "/workbench") {
          handleNavigate("/workbench", { case: sampleId });
        } else {
          void handleSelectSample(sampleId);
        }
        return;
      }

      // View Modes (only when on workbench)
      if (currentRoute === "/workbench") {
        const key = e.key.toLowerCase();
        if (key === "o") {
          e.preventDefault();
          setViewMode("ORIGINAL");
          toast("Original View applied");
        } else if (key === "e") {
          e.preventDefault();
          setViewMode("ELA");
          toast("Compression (ELA) Heatmap applied");
        } else if (key === "w") {
          e.preventDefault();
          setViewMode("WAVELET");
          toast("Noise (Wavelet) applied");
        } else if (key === "c") {
          e.preventDefault();
          setViewMode("COPY_MOVE");
          toast("Clones (ORB) applied");
        } else if (key === "s") {
          e.preventDefault();
          setViewMode("SPLIT");
          toast("Split Comparison Slider active");
        } else if (key === "l") {
          e.preventDefault();
          setViewMode("LOUPE");
          toast("Dual Loupe active");
        } else if (key === "q") {
          e.preventDefault();
          setViewMode("QUAD");
          toast("Quad-Spectral Matrix active");
        } else if (e.key === "[") {
          e.preventDefault();
          setIsSidebarCollapsed((prev) => !prev);
        } else if (key === "m") {
          e.preventDefault();
          setIsAdvancedMode((prev) => !prev);
          toast(`Mode switched: ${!isAdvancedMode ? "Forensic Advanced" : "Simple"}`);
        } else if (e.key === "?") {
          e.preventDefault();
          setIsShortcutsModalOpen((prev) => !prev);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleSelectSample, isAdvancedMode, currentRoute, handleNavigate]);

  const handleFileUpload = async (file: File) => {
    const { id, controller } = beginAnalysis();
    setSelectedSampleId(null);
    if (currentRoute !== "/workbench") handleNavigate("/workbench");
    try {
      if (file.size > 20 * 1024 * 1024) throw new Error("Choose an image under 20 MB.");
      const result = await analyzeUpload(file, controller.signal);
      if (activeRequest.current.id === id) { originalUpload.current = file; setReport(result); toast.success(`Analyzed ${file.name}`); }
    } catch (err) {
      if (activeRequest.current.id === id && !controller.signal.aborted)
        setAppError(`Upload failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      if (activeRequest.current.id === id) setIsLoading(false);
    }
  };

  // Full window drag-and-drop support
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current += 1;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDraggingFile(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      setIsDraggingFile(false);
      dragCounter.current = 0;
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingFile(false);
    dragCounter.current = 0;
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        void handleFileUpload(file);
      } else {
        toast.error("Please drop an image file (PNG, JPG, WebP, BMP)");
      }
    }
  };

  // Handle WhatsApp simulation on current screenshot
  const handleTriggerWhatsAppSimulation = async () => {
    if (!report) return;
    const simulationRequestId = activeRequest.current.id;
    setIsWhatsAppModalOpen(true);
    setIsWhatsAppLoading(true);

    try {
      const blob = await loadSimulationSource(originalUpload.current, demoSamples.find(sample => sample.id === selectedSampleId)?.url, report.original_image_b64);
      const simRes = await simulateWhatsApp(
        blob,
        report.filename || "screenshot.png"
      );
      if (simulationRequestId !== activeRequest.current.id) return;
      setWhatsAppDat(simRes);
      toast.success("WhatsApp simulation completed");
    } catch (err) {
      setAppError(
        `WhatsApp simulation failed: ${err instanceof Error ? err.message : "Unknown error"}`
      );
      toast.error("WhatsApp simulation failed");
    } finally {
      setIsWhatsAppLoading(false);
    }
  };

  // Handle stage judge live mobile upload arrival
  const handleMobileUploadReceived = (newReport: ForensicAnalysisReport) => {
    beginAnalysis();
    setSelectedSampleId(null);
    setSelectedLocus(null);
    setReport(newReport);
    setIsLoading(false);
    if (currentRoute !== "/workbench") {
      handleNavigate("/workbench");
    }
    toast.success("Live mobile screenshot received");
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="flex h-[100dvh] min-h-[100dvh] w-full flex-col overflow-hidden bg-[#060911] text-slate-100"
    >
      {/* 1. Global Unified Navigation Header */}
      <NavigationHeader
        currentRoute={currentRoute}
        onNavigate={handleNavigate}
        databaseStatus={databaseStatus}
        backendStatus={backendStatus}
      />

      {/* 2. Main Routed View Area */}
      <div className="relative flex-1 min-h-0 flex flex-col overflow-hidden">
        {/* Experience A: Product Overview */}
        {currentRoute === "/" && (
          <ProductOverview
            onNavigate={handleNavigate}
            demoSamples={demoSamples}
          />
        )}

        {/* Experience B: Forensic Workbench */}
        {currentRoute === "/workbench" && (
          <AmbientThreatBackground
            threatScore={report?.overall_tamper_score || 0}
            verdict={report?.verdict}
            isLoading={isLoading}
          >
            {/* Top Workbench Command Bar */}
            <TopCommandBar
              databaseStatus={databaseStatus}
              demoSamples={demoSamples}
              selectedSampleId={selectedSampleId}
              onSelectSample={handleSelectSample}
              onFileUpload={handleFileUpload}
              onOpenWhatsAppModal={handleTriggerWhatsAppSimulation}
              onOpenMobileModal={() => setIsMobileModalOpen(true)}
              onOpenReportModal={() => setIsReportModalOpen(true)}
              onOpenSection91Modal={() => setIsSection91ModalOpen(true)}
              onOpenShortcutsModal={() => setIsShortcutsModalOpen(true)}
              onOpenResponse={() => report && handleOpenResponseGuidance(report)}
              isAdvancedMode={isAdvancedMode}
              onToggleAdvancedMode={() => setIsAdvancedMode((prev) => !prev)}
              isLoading={isLoading}
              hasReport={!!report}
            />

            {/* Active 4-Skill Telemetry HUD */}
            {isLoading && <div role="status" className="px-4 py-2 text-sm text-sky-300">Analyzing image… Waiting for measured results.</div>}

            {/* Error Banner */}
            {appError && (
              <div
                role="alert"
                className="flex items-center justify-between border-b border-rose-800 bg-rose-950/80 px-4 py-2 text-xs text-rose-200 z-30 shrink-0"
              >
                <span>{appError}</span>
                <div className="ml-4 flex shrink-0 items-center gap-3">
                  {demoLoadFailed && (
                    <button
                      onClick={() => setDemoRetry((n) => n + 1)}
                      className="text-rose-100 underline hover:text-white"
                    >
                      Retry
                    </button>
                  )}
                  <button
                    onClick={() => setAppError(null)}
                    className="text-rose-100 hover:text-white"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}

            {/* Main Forensic Workspace: Multi-Spectral Viewer + Collapsible Risk Dossier */}
            <main className="flex min-h-0 flex-1 flex-col overflow-y-auto md:flex-row md:overflow-hidden relative z-10">
              <ForensicViewer
                report={report}
                selectedLocus={selectedLocus}
                onSelectLocus={(box) => setSelectedLocus(box)}
                isSidebarCollapsed={isSidebarCollapsed}
                onToggleSidebar={() => setIsSidebarCollapsed((prev) => !prev)}
                isAdvancedMode={isAdvancedMode}
                viewMode={viewMode}
                onViewModeChange={(m) => setViewMode(m)}
              />
              <RiskDossierSidebar
                report={report}
                selectedLocus={selectedLocus}
                onSelectLocus={(box) => setSelectedLocus(box)}
                isCollapsed={isSidebarCollapsed}
                onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
                isAdvancedMode={isAdvancedMode}
                onOpenReport={() => setIsReportModalOpen(true)}
                onOpenSection91={() => setIsSection91ModalOpen(true)}
                onOpenResponseGuidance={handleOpenResponseGuidance}
              />
            </main>
          </AmbientThreatBackground>
        )}

        {/* Experience C: Research & Evaluation Dashboard */}
        {currentRoute === "/evaluation" && (
          <EvaluationDashboard
            onNavigateWorkbench={() => handleNavigate("/workbench")}
          />
        )}

        {/* Experience D: Why VeriSight & Competitive Benchmarks */}
        {currentRoute === "/guide" && (
          <WhyVerisight
            onNavigateWorkbench={() => handleNavigate("/workbench")}
          />
        )}

        {/* Experience E: Response & Guidance (Native Module) */}
        {currentRoute === "/response" && (
          <ResponseModule
            onNavigateWorkbench={() => handleNavigate("/workbench")}
            attachedForensicContext={attachedForensicContext}
            onClearForensicContext={() => setAttachedForensicContext(null)}
          />
        )}
      </div>

      {/* Drag & Drop Overlay */}
      {isDraggingFile && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#070b16]/90 backdrop-blur-md border-4 border-dashed border-sky-400 p-8 text-center animate-in fade-in duration-200 pointer-events-none">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-sky-500/20 text-sky-400 mb-4 border border-sky-400/40 shadow-xl">
            <UploadCloud className="h-10 w-10 animate-bounce" />
          </div>
          <p className="text-xl font-bold font-mono text-white tracking-wide">
            RELEASE EVIDENCE TO INGEST
          </p>
          <p className="text-xs font-mono text-sky-300 mt-2">
            Supports PNG, JPG, WebP, BMP up to 20MB
          </p>
        </div>
      )}

      {/* Modals */}
      <WhatsAppSimulatorModal
        originalSrc={report?.original_image_b64 || ""}
        isOpen={isWhatsAppModalOpen}
        onClose={() => setIsWhatsAppModalOpen(false)}
        simulationData={whatsAppData}
        isLoading={isWhatsAppLoading}
        onApplyLaunderedImage={handleMobileUploadReceived}
      />

      <MobileUploadModal
        isOpen={isMobileModalOpen}
        onClose={() => setIsMobileModalOpen(false)}
        onMobileUploadReceived={handleMobileUploadReceived}
      />

      <ForensicReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        report={report}
      />

      {isSection91ModalOpen && report && (
        <Section91NoticeModal
          report={report}
          onClose={() => setIsSection91ModalOpen(false)}
        />
      )}

      <KeyboardShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => setIsShortcutsModalOpen(false)}
      />

      {/* Tactile Toaster (`ask-sonner` forensic theme) */}
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: "rgba(13, 19, 34, 0.96)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            color: "#e2e8f0",
            fontFamily: "ui-monospace, monospace",
            fontSize: "12px",
            boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(12px)",
          },
        }}
      />
    </div>
  );
};
