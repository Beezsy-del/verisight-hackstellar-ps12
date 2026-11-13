import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.response.models import (
    CaseRecord,
    CaseStatus,
    ExtractedIncidentDetails,
    FinancialImpact,
    IncidentCategory,
    TimelineEvent,
)

import os
import sqlite3
from app.core.config import settings

STORE_FILE = Path(os.environ.get("VERISIGHT_CASE_DB", str(settings.BASE_DIR / ".local-data" / "response.sqlite3")))

def _connect():
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    conn = sqlite3.connect(STORE_FILE, timeout=10)
    conn.execute("CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    os.chmod(STORE_FILE, 0o600)
    return conn

def list_cases():
    with _connect() as conn:
        return sorted([CaseRecord.model_validate_json(row[0]) for row in conn.execute("SELECT payload FROM cases")], key=lambda c:c.updated_at, reverse=True)

def get_case(case_id):
    with _connect() as conn:
        row = conn.execute("SELECT payload FROM cases WHERE id=?", (case_id,)).fetchone()
        return CaseRecord.model_validate_json(row[0]) if row else None

def save_case(case):
    case.updated_at = datetime.now().isoformat()
    with _connect() as conn:
        conn.execute("INSERT INTO cases VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload", (case.case_id, case.model_dump_json()))
    return case

def create_case_from_details(
    details: ExtractedIncidentDetails,
    title: str | None = None,
    forensic_attachment: dict[str, Any] | None = None
) -> CaseRecord:
    now_iso = datetime.now().isoformat()
    case_num = uuid.uuid4().hex[:6].upper()
    cid = f"VS-CASE-{case_num}"

    t = title or f"{details.incident_category_label} ({details.incident_date or 'Recent'})"
    record = CaseRecord(
        case_id=cid,
        created_at=now_iso,
        updated_at=now_iso,
        title=t,
        category=details.incident_category,
        status=CaseStatus.DRAFTING,
        financial_loss=details.financial_loss_amount or 0.0,
        authority_destination=details.recommended_pathway,
        acknowledgement_number=None,
        submission_date=None,
        follow_up_date=None,
        notes=None,
        details=details,
        complaint_draft=None,
        forensic_attachment=forensic_attachment,
        timeline=[
            TimelineEvent(
                timestamp=now_iso,
                title="Incident Response Case Opened",
                description=f"Case initialized in VeriSight Response & Guidance with classification '{details.incident_category_label}'.",
                actor="SYSTEM"
            )
        ]
    )
    if forensic_attachment:
        record.timeline.append(
            TimelineEvent(
                timestamp=now_iso,
                title="Forensic Evidence Linked",
                description=f"Attached evidence hash SHA-256 {forensic_attachment.get('file_sha256', '')[:12]}... (Risk Score: {forensic_attachment.get('overall_tamper_score', 0):.1f}/100)",
                actor="SYSTEM"
            )
        )

    return save_case(record)
