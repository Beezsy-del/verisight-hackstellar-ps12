from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class IncidentCategory(str, Enum):
    FAKE_PAYMENT_SCREENSHOT = "FAKE_PAYMENT_SCREENSHOT"
    PAYMENT_FRAUD = "PAYMENT_FRAUD"
    UNAUTHORIZED_BANK_TRANSACTION = "UNAUTHORIZED_BANK_TRANSACTION"
    UPI_FRAUD = "UPI_FRAUD"
    QR_CODE_FRAUD = "QR_CODE_FRAUD"
    IMPERSONATION = "IMPERSONATION"
    IDENTITY_MISUSE = "IDENTITY_MISUSE"
    DIGITAL_PAYMENT_DISPUTE = "DIGITAL_PAYMENT_DISPUTE"
    SUSPICIOUS_TRANSACTION_EVIDENCE = "SUSPICIOUS_TRANSACTION_EVIDENCE"
    ONLINE_MARKETPLACE_FRAUD = "ONLINE_MARKETPLACE_FRAUD"
    PHISHING_SOCIAL_ENGINEERING = "PHISHING_SOCIAL_ENGINEERING"
    OTHER_CYBERCRIME = "OTHER_CYBERCRIME"


class FinancialImpact(str, Enum):
    MONEY_LOST = "MONEY_LOST"
    NO_MONEY_LOST = "NO_MONEY_LOST"
    RECEIVED_BUT_DISPUTED = "RECEIVED_BUT_DISPUTED"
    TRANSACTION_PENDING = "TRANSACTION_PENDING"
    UNAUTHORIZED_DEBIT = "UNAUTHORIZED_DEBIT"
    UNCERTAIN = "UNCERTAIN"


class CaseStatus(str, Enum):
    DRAFTING = "DRAFTING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    READY_TO_SUBMIT = "READY_TO_SUBMIT"
    SUBMITTED_BY_USER = "SUBMITTED_BY_USER"
    ACKNOWLEDGEMENT_RECEIVED = "ACKNOWLEDGEMENT_RECEIVED"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class QuestionUrgency(str, Enum):
    URGENT_PROTECTIVE = "URGENT_PROTECTIVE"
    STANDARD = "STANDARD"
    CLARIFICATION = "CLARIFICATION"


class DynamicQuestion(BaseModel):
    id: str
    question: str
    rationale: str
    field_targeted: str
    urgency: QuestionUrgency = QuestionUrgency.STANDARD
    options: Optional[list[str]] = None
    suggested_actions: Optional[list[str]] = None


class ExtractedIncidentDetails(BaseModel):
    incident_category: IncidentCategory = IncidentCategory.OTHER_CYBERCRIME
    incident_category_label: str = "Other Cyber Incident"
    financial_impact: FinancialImpact = FinancialImpact.UNCERTAIN
    incident_date: Optional[str] = None
    approximate_time: Optional[str] = None
    financial_loss_amount: Optional[float] = None
    currency: str = "INR"
    payment_method: Optional[str] = None
    bank_or_upi_provider: Optional[str] = None
    transaction_reference: Optional[str] = None
    suspected_person_or_entity: Optional[str] = None
    suspected_vpa: Optional[str] = None
    suspected_phone: Optional[str] = None
    complainant_name: Optional[str] = None
    complainant_contact: Optional[str] = None
    communication_channel: Optional[str] = None
    narrative_description: str = ""
    available_evidence: list[str] = Field(default_factory=list)
    is_ongoing: bool = False
    account_at_risk: bool = False
    missing_fields: list[str] = Field(default_factory=list)
    confidence_score: float = 0.8
    urgent_guidance: Optional[str] = None
    recommended_pathway: str = "NATIONAL_CYBER_CRIME_PORTAL"


class UnderstandIncidentRequest(BaseModel):
    user_text: str
    language: str = "en"
    existing_details: Optional[dict[str, Any]] = None
    attached_forensic_case_id: Optional[str] = None
    attached_forensic_summary: Optional[dict[str, Any]] = None
    user_consent_granted: bool = True


class UnderstandIncidentResponse(BaseModel):
    extracted_details: ExtractedIncidentDetails
    original_text: str
    language: str
    urgent_alerts: list[str] = Field(default_factory=list)
    next_question: Optional[DynamicQuestion] = None
    classification_rationale: str


class GenerateComplaintRequest(BaseModel):
    details: ExtractedIncidentDetails
    authority_destination: str = "NATIONAL_CYBER_CRIME_PORTAL"
    language: str = "en"  # "en", "hi", "kn", "bn", "ta", "te", "mr"
    complainant_address: Optional[str] = None
    attached_forensic_report: Optional[dict[str, Any]] = None
    custom_narrative_edits: Optional[str] = None


class FormalComplaint(BaseModel):
    id: str
    title: str
    destination_authority_name: str
    destination_portal_url: str
    complainant_name: str
    complainant_contact: str
    incident_date_time: str
    incident_category: str
    chronological_narrative: str
    statements_breakdown: dict[str, str] = Field(
        default_factory=lambda: {
            "personal_experience": "",
            "counterparty_claims": "",
            "screenshot_representation": "",
            "forensic_observations": "",
            "unverified_elements": "",
        }
    )
    financial_details: dict[str, Any]
    transaction_reference: str
    suspected_entity: dict[str, Any]
    communication_channel: str
    evidence_inventory: list[str]
    forensic_observations: list[str] = Field(default_factory=list)
    requested_action: str
    supporting_document_index: list[str]
    disclaimer: str
    language: str


class RegenerateSectionRequest(BaseModel):
    section_name: str
    current_content: str
    instruction: str  # e.g. "make_more_formal", "simplify", "add_details", "translate"
    target_language: Optional[str] = "en"
    context: Optional[dict[str, Any]] = None


class ReportingAuthority(BaseModel):
    id: str
    name: str
    category: str  # "NATIONAL_PORTAL", "BANK_UPI", "REGULATOR_RBI", "POLICE", "PLATFORM"
    jurisdiction: str
    type_of_complaint: str
    official_website: str
    contact_information: dict[str, str]
    required_documents: list[str]
    submission_procedure: list[str]
    escalation_route: str
    waiting_period_days: Optional[int] = None
    prerequisites: Optional[list[str]] = None
    last_verified_date: str
    source_reference: str
    disclaimer: Optional[str] = None


class TimelineEvent(BaseModel):
    timestamp: str
    title: str
    description: str
    actor: str = "USER"  # "USER", "SYSTEM", "AUTHORITY"


class CaseRecord(BaseModel):
    case_id: str
    created_at: str
    updated_at: str
    title: str
    category: IncidentCategory
    status: CaseStatus = CaseStatus.DRAFTING
    financial_loss: float = 0.0
    authority_destination: str = "NATIONAL_CYBER_CRIME_PORTAL"
    acknowledgement_number: Optional[str] = None
    submission_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    details: ExtractedIncidentDetails
    complaint_draft: Optional[FormalComplaint] = None
    forensic_attachment: Optional[dict[str, Any]] = None
    timeline: list[TimelineEvent] = Field(default_factory=list)


class AudioTranscriptionResponse(BaseModel):
    transcript: str
    confidence: float = 0.95
    detected_language: str = "en-IN"
    duration_seconds: float = 0.0
    engine: str = "VeriSight Audio Processor"
    client_action_needed: bool = False
