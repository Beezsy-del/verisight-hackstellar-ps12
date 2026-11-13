export interface AnalysisGate {
  state: "PASS" | "WARNING" | "BLOCK";
  processing_status: "COMPLETE" | "INCOMPLETE" | "FAILED";
  policy_version: string;
  reasons: { code: string; state: "PASS" | "WARNING" | "BLOCK"; message: string; evidence_ids: string[] }[];
  allowed_actions: { view_report: boolean; automated_approval: false };
  settlement_verified: false;
}

export type PersistenceStatus = "DISABLED" | "NOT_CONFIGURED" | "FAILED" | "SAVED" | "NOT_REQUESTED";

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  points?: number[][];
  label: string;
  confidence: number;
  layer: number;
  anomaly_type: string;
  details?: Record<string, any>;
}

export interface BaselineLaser {
  row_index: number;
  y_baseline: number;
  slope: number;
  tokens_count: number;
  delta_y_max: number;
  is_tampered: boolean;
  status: "ALIGNED_CYAN" | "CRITICAL_RED";
  callout_text?: string;
  token_indices: number[];
  x_start?: number;
  x_end?: number;
}

export interface Layer1SignalResult {
  ela_score: number;
  ela_b64: string;
  wavelet_noise_score: number;
  wavelet_noise_b64: string;
  clone_detected: boolean;
  clone_count: number;
  clone_b64: string;
  anomalous_blocks_count: number;
  layer_score: number;
  bounding_boxes: BoundingBox[];
  details: Record<string, any>;
}

export interface Layer2GeometryResult {
  baseline_drift_score: number;
  max_baseline_drift_px: number;
  max_delta_e: number;
  cielab_patch_anomaly: boolean;
  sharpness_z_anomaly: boolean;
  layer_score: number;
  lasers: BaselineLaser[];
  bounding_boxes: BoundingBox[];
  details: Record<string, any>;
}

export interface Layer3MetadataResult {
  channel_detected: string;
  is_whatsapp_laundered: boolean;
  exif_stripped: boolean;
  software_signature?: string;
  c2pa_present: boolean;
  c2pa_status: string;
  viewport_aspect_ratio: string;
  is_non_native_viewport: boolean;
  clock_paradox_detected: boolean;
  status_bar_clock?: string;
  transaction_time?: string;
  upi_utr_valid?: boolean;
  upi_utr_value?: string;
  layer_score: number;
  bounding_boxes: BoundingBox[];
  details: Record<string, any>;
}

export interface Layer4SemanticResult {
  vlm_used: boolean;
  vlm_provider?: string;
  semantic_inconsistency: boolean;
  layer_score: number;
  findings: string[];
  details: Record<string, any>;
}

export interface CrossLayerSynergy {
  region_overlap_found: boolean;
  primary_review_locus?: BoundingBox | null;
  max_iou: number;
  synergy_multiplier_applied: boolean;
  multiplier_factor: number;
  primary_forgery_locus?: BoundingBox;
  synergy_explanation: string;
}

export interface ForensicFinding {
  id: string;
  layer: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
  title: string;
  description: string;
  metric_name: string;
  metric_value: string;
  bounding_box?: BoundingBox;
}

export interface SyndicateIntelligence {
  syndicate_risk_level: "CRITICAL_SYNDICATE_THREAT" | "MODERATE_REVIEW_REQUIRED" | "LOW" | string;
  threat_indicators: string[];
  entity_summary: {
    payee_vpa?: string | null;
    payee_name?: string | null;
    utr_number?: string | null;
    amount?: string | null;
    psp_provider?: string | null;
    qr_linked?: boolean;
    qr_intent?: {
      vpa?: string | null;
      payee?: string | null;
      amount?: string | null;
    } | null;
  };
  recommended_action: string;
}

export interface ForensicAnalysisReport {
  analysis_gate?: AnalysisGate;
  persistence_status?: PersistenceStatus;
  media_urls?: Record<string,string>;
  intelligence?: ReviewIntelligence;
  schema_version: string;
  case_id: string;
  sample_id: string | null;
  source_kind: string;
  processing_status: "COMPLETE";
  ai_origin_status: string;
  ai_origin?: {summary: string; signals: {id: string; label: string; status: string; evidence: string; limitation: string}[]};
  payment_status: string;
  limitations: string[];
  file_sha256: string;
  filename?: string;
  timestamp: string;
  image_width: number;
  image_height: number;
  overall_tamper_score: number;
  confidence_score: number | null;
  verdict:
    | "INCONCLUSIVE"
    | "REVIEW_REQUIRED"
    | "CORROBORATED_ANOMALIES"
    | string;
  channel_detected: string;
  layer1: Layer1SignalResult;
  layer2: Layer2GeometryResult;
  layer3: Layer3MetadataResult;
  layer4: Layer4SemanticResult;
  synergy: CrossLayerSynergy;
  findings: ForensicFinding[];
  all_bounding_boxes: BoundingBox[];
  original_image_b64: string;
  syndicate_intelligence?: SyndicateIntelligence;
  section91_notice?: string;
}

export interface DemoSampleMeta {
  id: string;
  filename: string;
  title: string;
  scenario: string;
  expected_verdict: string;
  target_score_range: string;
  description: string;
  tags: string[];
  url: string;
}

export interface WhatsAppSimulationResponse {
  original_size_bytes: number;
  simulated_size_bytes: number;
  compression_ratio: number;
  original_dimensions: number[];
  simulated_dimensions: number[];
  simulated_image_b64: string;
  diff_heatmap_b64: string;
  reanalysis: ForensicAnalysisReport;
}

export interface NetworkInfo {
  local_ip: string;
  frontend_port: number;
  backend_port: number;
  mobile_upload_url: string;
}

export interface ReviewIntelligence {
 semantic_checks?:Array<{kind:string;state:string;explanation:string;box?:{x:number;y:number;width:number;height:number}|null}>;
 version:string;
 acquisition:{estimated_profile:string;compression_condition:string;pixel_cue_reliability:number};
 ocr:{status:string;reason?:string|null;fields:Array<{kind:string;text:string;confidence:number;box:{x:number;y:number;width:number;height:number}}>;
 tokens:Array<{id:string;text:string;confidence:number;readable:boolean;box:{x:number;y:number;width:number;height:number}}>};
 candidate_score:number;
 evidence:Array<{id:string;family:string;availability:string;direction:string;explanation:string;box?:{x:number;y:number;width:number;height:number}|null}>;
}
