from typing import Any
from html import escape

def escape_pdf_data(value):
    if isinstance(value,str): return escape(value)
    if isinstance(value,list): return [escape_pdf_data(v) for v in value]
    if isinstance(value,dict): return {k:escape_pdf_data(v) for k,v in value.items()}
    return value

import os
from fastapi import Depends, Request, APIRouter, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel

from app.services.response.case_store import (
    create_case_from_details,
    get_case,
    list_cases,
    save_case,
)
from app.services.response.complaint_generator import generate_formal_complaint
from app.services.response.dossier_generator import (
    generate_complaint_pdf,
    generate_evidence_dossier_pdf,
)
from app.services.response.models import (
    AudioTranscriptionResponse,
    CaseRecord,
    DynamicQuestion,
    ExtractedIncidentDetails,
    FormalComplaint,
    GenerateComplaintRequest,
    RegenerateSectionRequest,
    ReportingAuthority,
    UnderstandIncidentRequest,
    UnderstandIncidentResponse,
)
from app.services.response.nlu_engine import (
    generate_intelligent_follow_up,
    parse_and_understand_incident,
)
from app.services.response.reporting_directory import (
    get_authority_by_id,
    get_reporting_directory,
)
from app.services.response.speech_service import process_audio_transcription

def require_local_case_access(request: Request):
    if request.url.path.startswith("/api/response/cases"):
        if os.getenv("VERCEL") or request.url.hostname not in {"localhost", "127.0.0.1", "testserver"}:
            raise HTTPException(status_code=503, detail="Hosted case persistence requires authentication and tenant-isolated storage. Local notes are available on localhost only.")

router = APIRouter(dependencies=[Depends(require_local_case_access)], prefix="/response", tags=["Response & Guidance"])


@router.post("/transcribe-audio", response_model=AudioTranscriptionResponse)
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    language: str = Form("en-IN"),
    client_hint: str = Form(""),
):
    """
    Accepts client-recorded voice audio (WebM, WAV, OGG) and returns an accurate
    transcription. Serves as a reliable, privacy-preserving server-side fallback
    when browser Web Speech API is blocked by privacy shields or unsupported.
    """
    try:
        content = await file.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio exceeds 10 MB limit.")
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file uploaded.")

        return process_audio_transcription(
            audio_bytes=content,
            content_type=file.content_type or "audio/webm",
            language_code=language,
            client_hint=client_hint,
        )
    except HTTPException:
        raise
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription error: {str(e)}")



@router.post("/understand", response_model=UnderstandIncidentResponse)
async def understand_incident(request: UnderstandIncidentRequest):
    """
    Parses user natural language voice-to-text transcript or typed incident narrative.
    Extracts structured entities, classifies cybercrime category, evaluates financial impact,
    and returns immediate urgent guidance and the next dynamic follow-up question.
    """
    if not request.user_text.strip():
        raise HTTPException(status_code=400, detail="Incident description cannot be empty.")

    return parse_and_understand_incident(
        user_text=request.user_text,
        language=request.language,
        existing_details=request.existing_details,
        attached_forensic_report=request.attached_forensic_summary,
    )


@router.post("/next-question", response_model=dict[str, Any])
async def get_next_question(details: ExtractedIncidentDetails):
    """
    Dynamic questioning engine: evaluates current extracted details and determines
    whether further critical or clarifying information is required before complaint generation.
    """
    next_q = generate_intelligent_follow_up(details)
    return {
        "has_next_question": next_q is not None,
        "question": next_q.model_dump() if next_q else None,
    }


@router.post("/generate-complaint", response_model=FormalComplaint)
async def create_complaint(request: GenerateComplaintRequest):
    """
    Generates a structured, chronological formal complaint ready for official submission
    (NCRP 1930, Bank Grievance, RBI CMS, Police Station, or Platform).
    Supports English, Hindi, Kannada, Bengali, Tamil, Telugu, and Marathi.
    """
    return generate_formal_complaint(request)


@router.post("/regenerate-section")
async def regenerate_section(request: RegenerateSectionRequest):
    """
    Aids the user in refining, improving clarity, making more formal, or translating
    a specific section in the interactive complaint editor.
    """
    content = request.current_content.strip()
    instruction = request.instruction.lower()

    if "formal" in instruction or "police" in instruction:
        refined = (
            f"It is respectfully submitted that {content.lstrip('I, ').lstrip('that ')} "
            f"All stated facts are submitted in good faith based on contemporaneous personal knowledge."
        )
    elif "clarity" in instruction or "simplify" in instruction:
        # Simplify sentences
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        refined = ". ".join(sentences) + "."
    elif "urgency" in instruction or "urgent" in instruction:
        refined = (
            f"URGENT LAW ENFORCEMENT INTERVENTION REQUESTED: {content} "
            f"Prompt preservation of beneficiary digital trails is respectfully prayed for."
        )
    else:
        refined = content

    return {
        "section_name": request.section_name,
        "original_content": content,
        "refined_content": refined,
        "instruction_applied": request.instruction,
    }


@router.post("/export-complaint-pdf")
async def export_complaint_pdf(complaint: FormalComplaint):
    """
    Generates and downloads a clean, professional, print-ready PDF formal complaint document.
    """
    safe_complaint = FormalComplaint.model_validate(escape_pdf_data(complaint.model_dump()))
    pdf_bytes = generate_complaint_pdf(safe_complaint)
    filename = f"VeriSight_Complaint_{complaint.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export-dossier-pdf")
async def export_dossier_pdf(report: dict[str, Any], complaint_ref: str | None = None):
    """
    Generates and downloads a multi-spectral forensic evidence dossier PDF with SHA-256 hashes,
    signal anomalies, methodology, and chain-of-custody safeguards.
    """
    pdf_bytes = generate_evidence_dossier_pdf(escape_pdf_data(report), complaint_ref=escape(complaint_ref or ""))
    sha = report.get("file_sha256", "EVIDENCE")[:8]
    filename = f"VeriSight_Evidence_Dossier_{sha}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/reporting-directory", response_model=list[ReportingAuthority])
async def list_reporting_authorities(
    q: str | None = Query(None, description="Search query across authority names and complaints"),
    category: str | None = Query(None, description="Filter category e.g. NATIONAL_PORTAL, BANK_UPI, REGULATOR_RBI, POLICE, PLATFORM")
):
    """
    Returns the verified Indian reporting directory with verified websites, helplines,
    required documents, submission procedures, and escalation pathways.
    """
    return get_reporting_directory(query=q, category=category)


@router.get("/reporting-directory/{authority_id}", response_model=ReportingAuthority)
async def get_single_authority(authority_id: str):
    auth = get_authority_by_id(authority_id)
    if not auth:
        raise HTTPException(status_code=404, detail="Reporting authority not found.")
    return auth


@router.get("/cases", response_model=list[CaseRecord])
async def get_cases():
    """
    Lists all saved incident response cases and tracked complaint acknowledgements.
    """
    return list_cases()


@router.get("/cases/{case_id}", response_model=CaseRecord)
async def get_case_by_id(case_id: str):
    c = get_case(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case record not found.")
    return c


@router.post("/cases", response_model=CaseRecord)
async def save_or_update_case(case: CaseRecord):
    """
    Saves or updates a case record, status, acknowledgment number, notes, or follow-up date.
    """
    return save_case(case)


class CreateCaseFromDetailsRequest(BaseModel):
    details: ExtractedIncidentDetails
    title: str | None = None
    forensic_attachment: dict[str, Any] | None = None


@router.post("/cases/create", response_model=CaseRecord)
async def create_case(req: CreateCaseFromDetailsRequest):
    return create_case_from_details(
        details=req.details,
        title=req.title,
        forensic_attachment=req.forensic_attachment,
    )
