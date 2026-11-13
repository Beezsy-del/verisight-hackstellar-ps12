export type IncidentCategory =
  | "FAKE_PAYMENT_SCREENSHOT"
  | "PAYMENT_FRAUD"
  | "UNAUTHORIZED_BANK_TRANSACTION"
  | "UPI_FRAUD"
  | "QR_CODE_FRAUD"
  | "IMPERSONATION"
  | "IDENTITY_MISUSE"
  | "DIGITAL_PAYMENT_DISPUTE"
  | "SUSPICIOUS_TRANSACTION_EVIDENCE"
  | "ONLINE_MARKETPLACE_FRAUD"
  | "PHISHING_SOCIAL_ENGINEERING"
  | "OTHER_CYBERCRIME";

export type FinancialImpact =
  | "MONEY_LOST"
  | "NO_MONEY_LOST"
  | "RECEIVED_BUT_DISPUTED"
  | "TRANSACTION_PENDING"
  | "UNAUTHORIZED_DEBIT"
  | "UNCERTAIN";

export type CaseStatus =
  | "DRAFTING"
  | "READY_FOR_REVIEW"
  | "READY_TO_SUBMIT"
  | "SUBMITTED_BY_USER"
  | "ACKNOWLEDGEMENT_RECEIVED"
  | "FOLLOW_UP_REQUIRED"
  | "RESOLVED"
  | "CLOSED";

export type QuestionUrgency = "URGENT_PROTECTIVE" | "STANDARD" | "CLARIFICATION";

export interface DynamicQuestion {
  id: string;
  question: string;
  rationale: string;
  field_targeted: string;
  urgency: QuestionUrgency;
  options?: string[];
  suggested_actions?: string[];
}

export interface ExtractedIncidentDetails {
  incident_category: IncidentCategory;
  incident_category_label: string;
  financial_impact: FinancialImpact;
  incident_date?: string;
  approximate_time?: string;
  financial_loss_amount?: number;
  currency: string;
  payment_method?: string;
  bank_or_upi_provider?: string;
  transaction_reference?: string;
  suspected_person_or_entity?: string;
  suspected_vpa?: string;
  suspected_phone?: string;
  complainant_name?: string;
  complainant_contact?: string;
  communication_channel?: string;
  narrative_description: string;
  available_evidence: string[];
  is_ongoing: boolean;
  account_at_risk: boolean;
  missing_fields: string[];
  confidence_score: number;
  urgent_guidance?: string;
  recommended_pathway: string;
}

export interface UnderstandIncidentResponse {
  extracted_details: ExtractedIncidentDetails;
  original_text: string;
  language: string;
  urgent_alerts: string[];
  next_question?: DynamicQuestion;
  classification_rationale: string;
}

export interface StatementsBreakdown {
  personal_experience: string;
  counterparty_claims: string;
  screenshot_representation: string;
  forensic_observations: string;
  unverified_elements: string;
}

export interface FormalComplaint {
  id: string;
  title: string;
  destination_authority_name: string;
  destination_portal_url: string;
  complainant_name: string;
  complainant_contact: string;
  incident_date_time: string;
  incident_category: string;
  chronological_narrative: string;
  statements_breakdown: StatementsBreakdown;
  financial_details: {
    claimed_amount: number;
    currency: string;
    financial_impact: string;
    payment_method: string;
    bank_or_psp: string;
  };
  transaction_reference: string;
  suspected_entity: {
    name_or_alias: string;
    vpa: string;
    phone: string;
    channel: string;
  };
  communication_channel: string;
  evidence_inventory: string[];
  forensic_observations: string[];
  requested_action: string;
  supporting_document_index: string[];
  disclaimer: string;
  language: string;
}

export interface ReportingAuthority {
  id: string;
  name: string;
  category: "NATIONAL_PORTAL" | "BANK_UPI" | "REGULATOR_RBI" | "POLICE" | "PLATFORM";
  jurisdiction: string;
  type_of_complaint: string;
  official_website: string;
  contact_information: Record<string, string>;
  required_documents: string[];
  submission_procedure: string[];
  escalation_route: string;
  waiting_period_days?: number;
  prerequisites?: string[];
  last_verified_date: string;
  source_reference: string;
  disclaimer?: string;
}

export interface TimelineEvent {
  timestamp: string;
  title: string;
  description: string;
  actor: "USER" | "SYSTEM" | "AUTHORITY";
}

export interface CaseRecord {
  case_id: string;
  created_at: string;
  updated_at: string;
  title: string;
  category: IncidentCategory;
  status: CaseStatus;
  financial_loss: number;
  authority_destination: string;
  acknowledgement_number?: string;
  submission_date?: string;
  follow_up_date?: string;
  notes?: string;
  details: ExtractedIncidentDetails;
  complaint_draft?: FormalComplaint;
  forensic_attachment?: Record<string, any>;
  timeline: TimelineEvent[];
}

export interface AttachedForensicContext {
  case_id: string;
  filename: string;
  file_sha256: string;
  image_width: number;
  image_height: number;
  overall_tamper_score: number;
  verdict: string;
  findings: Array<{
    id: string;
    layer: number;
    title: string;
    description: string;
    severity: string;
    metric_name: string;
    metric_value: string;
  }>;
  synergy?: {
    synergy_multiplier_applied: boolean;
    multiplier_factor: number;
    synergy_explanation: string;
  };
  limitations?: string;
  thumbnail_b64?: string;
}
