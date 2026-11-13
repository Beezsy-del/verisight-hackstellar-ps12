import {
  ForensicAnalysisReport,
  DemoSampleMeta,
  WhatsAppSimulationResponse,
  NetworkInfo,
} from "../types/forensic";

const API_BASE = "/api";
const MEDIA_QUERY = ["localhost", "127.0.0.1"].includes(window.location.hostname) ? "?media=urls" : "";

async function fetchStartupData(path: string): Promise<Response> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 8000);
  try {
    return await fetch(`${API_BASE}${path}`, { signal: controller.signal });
  } finally {
    window.clearTimeout(timeout);
  }
}

async function responseError(res: Response, fallback: string): Promise<Error> {
  if (res.status === 413) {
    return new Error("This screenshot is too large to upload. Choose an image under 20 MB.");
  }
  const data = await res.json().catch(() => null);
  const detail = typeof data?.detail === "string" ? data.detail : fallback;
  return new Error(detail);
}

export async function fetchHealth(): Promise<{
  status: string;
  service: string;
  database: "HEALTHY" | "UNAVAILABLE" | "NOT_CONFIGURED";
  upload_mode?: "signed" | "direct";
}> {
  const res = await fetchStartupData("/health");
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchDemoSamples(): Promise<DemoSampleMeta[]> {
  const res = await fetchStartupData("/demo-samples");
  if (!res.ok) throw new Error("Failed to fetch demo samples");
  return res.json();
}

export async function analyzeDemoSample(
  sampleId: string,
  signal?: AbortSignal,
): Promise<ForensicAnalysisReport> {
  const res = await fetch(`${API_BASE}/analyze-sample/${encodeURIComponent(sampleId)}${MEDIA_QUERY}`, {
    method: "POST", signal,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || "Sample analysis failed");
  }
  return resolveAnalysisMedia(await res.json());
}

export async function analyzeUpload(
  file: File,
  signal?: AbortSignal,
): Promise<ForensicAnalysisReport> {
  const health = await fetchHealth();
  if (health.upload_mode === "signed" && file.size > 4 * 1024 * 1024) {
    const { session_id } = await uploadFileToPrivateStorage(file);
    const result = await fetch(`${API_BASE}/analyze-upload-session/${session_id}`, { method: "POST", signal });
    if (!result.ok) throw await responseError(result, "Screenshot analysis failed.");
    return resolveAnalysisMedia(await result.json());
  }
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/analyze${MEDIA_QUERY}`, {
    method: "POST", signal,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || "Screenshot analysis failed. Choose a PNG, JPG, WebP, or BMP image.");
  }
  return resolveAnalysisMedia(await res.json());
}

async function uploadFileToPrivateStorage(file: File, sessionId?: string) {
  if (file.size > 20 * 1024 * 1024) {
    throw new Error("Choose an image smaller than 20 MB.");
  }
  const extension = file.name.split(".").pop()?.toLowerCase();
  const contentType = file.type || ({
    png: "image/png",
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    webp: "image/webp",
    bmp: "image/bmp",
  } as Record<string, string>)[extension || ""] || "application/octet-stream";
  const sessionRes = await fetch(`${API_BASE}/upload-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filename: file.name,
      content_type: contentType,
      size: file.size,
      ...(sessionId ? { session_id: sessionId } : {}),
    }),
  });
  if (!sessionRes.ok) {
    throw await responseError(sessionRes, "Could not prepare secure screenshot upload.");
  }

  const { session_id, upload_url, storage_key } = await sessionRes.json();
  const uploadRes = await fetch(upload_url, {
    method: "PUT",
    headers: {
      "Content-Type": contentType,
      apikey: storage_key,
      Authorization: `Bearer ${storage_key}`,
      "x-upsert": "false",
      "cache-control": "max-age=3600",
    },
    body: file,
  });
  if (!uploadRes.ok) {
    const detail = await uploadRes.json().catch(() => null);
    throw new Error(
      typeof detail?.message === "string"
        ? detail.message
        : "Secure upload failed. Check your connection and try again.",
    );
  }

  return { session_id: session_id as string };
}

export async function simulateWhatsApp(
  file: File | Blob,
  filename = "screenshot.png",
): Promise<WhatsAppSimulationResponse> {
  const formData = new FormData();
  formData.append("file", file, filename);
  const res = await fetch(`${API_BASE}/simulate-whatsapp${MEDIA_QUERY}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "WhatsApp simulation failed" }));
    throw new Error(err.detail || "WhatsApp simulation failed");
  }
  const data = await res.json();
  return {...data, reanalysis: resolveAnalysisMedia(data.reanalysis)};
}

export async function fetchNetworkInfo(): Promise<NetworkInfo> {
  const res = await fetch(`${API_BASE}/network-info`);
  if (!res.ok) throw new Error("Failed to fetch network info");
  return res.json();
}

export async function fetchLatestMobileUpload(
  sessionId: string,
): Promise<ForensicAnalysisReport | null> {
  const query = new URLSearchParams({ session_id: sessionId });
  const res = await fetch(`${API_BASE}/latest-mobile-upload?${query}`);
  if (!res.ok) return null;
  const data = await res.json();
  return data.report || null;
}

export async function uploadMobile(
  file: File,
  sessionId: string,
): Promise<void> {
  await uploadFileToPrivateStorage(file, sessionId);
}

export interface ModelStatus {
  active_model_id: string;
  active_model_version: string;
  architecture: string;
  calibration_status: string;
  promotion_status: string;
  available_models: any[];
  ml_environment_ready: boolean;
}

export interface RocOperatingPoint {
  threshold: number;
  fpr: number;
  tpr: number;
  sensitivity: number;
  specificity: number;
  precision: number;
  tp: number;
  fp: number;
  tn: number;
  fn: number;
}

export interface RocCurveDataset {
  name: string;
  sample_count: number;
  positive_count: number;
  negative_count: number;
  roc_auc: number;
  brier_score?: number;
  dataset_type: string;
  leakage_status: string;
  fpr?: number[];
  tpr?: number[];
  thresholds?: number[];
  operating_points?: RocOperatingPoint[];
}

export interface ModelEvaluationReport {
  dataset_summary: {
    total_samples: number;
    dev_samples: number;
    held_out_test_samples: number;
    authentic_reference: number;
    manipulated_reference: number;
    features_extracted: number;
    feature_schema_version: string;
    feature_names: string[];
    held_out_test_ids: string[];
  };
  models: Record<string, any>;
  data_leakage_audit?: Record<string, any>;
  scientific_assessment?: Record<string, any>;
  roc_evaluation?: {
    benchmark_held_out?: RocCurveDataset;
    user_supplied_external?: RocCurveDataset;
    dev_oof_cv?: RocCurveDataset;
  };
  status?: string;
  message?: string;
}

export async function fetchModelStatus(): Promise<ModelStatus> {
  const res = await fetchStartupData("/model/status");
  if (!res.ok) throw new Error("Failed to fetch model status");
  return res.json();
}

export async function fetchModelEvaluation(): Promise<ModelEvaluationReport> {
  const res = await fetchStartupData("/model/evaluation");
  if (!res.ok) throw new Error("Failed to fetch model evaluation");
  return res.json();
}

// ---------------------------------------------------------------------------
// RESPONSE & GUIDANCE API CLIENT
// ---------------------------------------------------------------------------
import type {
  ExtractedIncidentDetails,
  UnderstandIncidentResponse,
  FormalComplaint,
  ReportingAuthority,
  CaseRecord,
} from "../types/response";

export async function understandIncident(payload: {
  user_text: string;
  language?: string;
  existing_details?: any;
  attached_forensic_summary?: any;
}): Promise<UnderstandIncidentResponse> {
  const res = await fetch(`${API_BASE}/response/understand`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_text: payload.user_text,
      language: payload.language || "en",
      existing_details: payload.existing_details,
      attached_forensic_summary: payload.attached_forensic_summary,
      user_consent_granted: true,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "NLU analysis failed" }));
    throw new Error(err.detail || "Failed to process incident statement");
  }
  return res.json();
}

export async function fetchNextQuestion(
  details: ExtractedIncidentDetails
): Promise<{ has_next_question: boolean; question: any }> {
  const res = await fetch(`${API_BASE}/response/next-question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(details),
  });
  if (!res.ok) throw new Error("Failed to get follow-up question");
  return res.json();
}

export async function generateComplaint(payload: {
  details: ExtractedIncidentDetails;
  authority_destination?: string;
  language?: string;
  attached_forensic_report?: any;
  custom_narrative_edits?: string;
  complainant_address?: string;
}): Promise<FormalComplaint> {
  const res = await fetch(`${API_BASE}/response/generate-complaint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      details: payload.details,
      authority_destination: payload.authority_destination || "NATIONAL_CYBER_CRIME_PORTAL",
      language: payload.language || "en",
      attached_forensic_report: payload.attached_forensic_report,
      custom_narrative_edits: payload.custom_narrative_edits,
      complainant_address: payload.complainant_address,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Complaint generation failed" }));
    throw new Error(err.detail || "Failed to generate complaint");
  }
  return res.json();
}

export async function regenerateComplaintSection(payload: {
  section_name: string;
  current_content: string;
  instruction: string;
  target_language?: string;
}): Promise<{ section_name: string; original_content: string; refined_content: string }> {
  const res = await fetch(`${API_BASE}/response/regenerate-section`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to regenerate section");
  return res.json();
}

export async function fetchReportingDirectory(
  category?: string,
  query?: string
): Promise<ReportingAuthority[]> {
  const params = new URLSearchParams();
  if (category && category !== "ALL") params.append("category", category);
  if (query) params.append("q", query);

  const res = await fetch(`${API_BASE}/response/reporting-directory?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to load reporting directory");
  return res.json();
}

export async function fetchCases(): Promise<CaseRecord[]> {
  const res = await fetch(`${API_BASE}/response/cases`);
  if (!res.ok) throw new Error("Failed to fetch cases");
  return res.json();
}

export async function fetchCase(caseId: string): Promise<CaseRecord> {
  const res = await fetch(`${API_BASE}/response/cases/${caseId}`);
  if (!res.ok) throw new Error("Failed to fetch case");
  return res.json();
}

export async function saveCaseRecord(caseRecord: CaseRecord): Promise<CaseRecord> {
  const res = await fetch(`${API_BASE}/response/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(caseRecord),
  });
  if (!res.ok) throw new Error("Failed to save case");
  return res.json();
}

export async function createCaseRecord(payload: {
  details: ExtractedIncidentDetails;
  title?: string;
  forensic_attachment?: any;
}): Promise<CaseRecord> {
  const res = await fetch(`${API_BASE}/response/cases/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create case");
  return res.json();
}

export async function downloadComplaintPdfBlob(complaint: FormalComplaint): Promise<Blob> {
  const res = await fetch(`${API_BASE}/response/export-complaint-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(complaint),
  });
  if (!res.ok) throw new Error("Failed to generate complaint PDF");
  return res.blob();
}

export async function downloadDossierPdfBlob(
  report: any,
  complaintRef?: string
): Promise<Blob> {
  const params = complaintRef ? `?complaint_ref=${encodeURIComponent(complaintRef)}` : "";
  const res = await fetch(`${API_BASE}/response/export-dossier-pdf${params}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  if (!res.ok) throw new Error("Failed to generate dossier PDF");
  return res.blob();
}

export interface AudioTranscriptionResponse {
  transcript: string;
  confidence: number;
  detected_language: string;
  duration_seconds: number;
  engine: string;
  client_action_needed: boolean;
}

export async function transcribeAudioFile(
  audioBlob: Blob,
  language = "en-IN",
  clientHint = ""
): Promise<AudioTranscriptionResponse> {
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.webm");
  formData.append("language", language);
  if (clientHint) formData.append("client_hint", clientHint);

  const res = await fetch(`${API_BASE}/response/transcribe-audio`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Audio transcription failed" }));
    throw new Error(err.detail || "Audio transcription failed");
  }
  return res.json();
}



function resolveAnalysisMedia(report: ForensicAnalysisReport): ForensicAnalysisReport {
  const urls = report.media_urls;
  if (!urls?.original) return report;
  return {...report, original_image_b64: urls.original, layer1: {...report.layer1,
    ela_b64: urls.ela, wavelet_noise_b64: urls.wavelet, clone_b64: urls.clone}};
}
