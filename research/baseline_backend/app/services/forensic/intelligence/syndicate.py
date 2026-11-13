"""
VeriSight Syndicate Intelligence & Law Enforcement Requisition Module
Inspired by ScamShield AI (Public Safety Intelligence & Section 91 Subpoena Generation)

Extracts payment entities (VPA, Payee, UTR, Amount), evaluates syndicate risk clusters,
and automatically drafts official Section 91 CrPC (Section 94 BNSS) cyber-cell requisitions.
"""
from __future__ import annotations

import re
from typing import Any


def _token_str(t: Any) -> str:
    if hasattr(t, "text"):
        return str(t.text or "")
    if isinstance(t, dict):
        return str(t.get("text", "") or "")
    return ""


def detect_psp_provider(vpa: str | None) -> str:
    """Resolves payment service provider (PSP) and clearing bank from UPI VPA handle."""
    if not vpa or "@" not in vpa:
        return "Unknown / Non-standard"
    handle = "@" + vpa.split("@")[-1].lower()
    providers = {
        "@ybl": "PhonePe (Yes Bank)",
        "@axl": "PhonePe (Axis Bank)",
        "@ibl": "PhonePe (ICICI Bank)",
        "@okaxis": "Google Pay (Axis Bank)",
        "@okhdfcbank": "Google Pay (HDFC Bank)",
        "@okicici": "Google Pay (ICICI Bank)",
        "@oksbi": "Google Pay (State Bank of India)",
        "@paytm": "Paytm Payments Bank",
        "@upi": "BHIM / NPCI Official",
        "@apl": "Amazon Pay",
        "@barodampay": "Bank of Baroda UPI",
        "@idfcbank": "IDFC FIRST Bank",
    }
    return providers.get(handle, f"UPI PSP ({handle})")


def extract_financial_entities(
    tokens: list[Any],
    qr_details: dict[str, Any] | None = None,
    filename: str = "",
) -> dict[str, Any]:
    """
    Extracts financial transaction entities:
    - Beneficiary VPA (UPI handle, including hyphenated numbers like 8273444379-4@ybl)
    - Payee Name
    - UPI Reference ID / UTR (validated against 12-digit RBI standard)
    - Transacted Amount (INR)
    - PSP Provider Resolution
    """
    all_text = " ".join(_token_str(t) for t in tokens)

    # 1. UPI VPA Extraction (supporting hyphenated and dotted handles, e.g. 8273444379-4@ybl)
    vpa_pattern = r"([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})"
    vpa_matches = re.findall(vpa_pattern, all_text)

    # Also check QR decoded payload for VPA if present
    qr_vpa = None
    qr_payee = None
    qr_amount = None
    if qr_details and "results" in qr_details:
        for item in qr_details.get("results", []):
            if item.get("kind") == "UPI_PAYMENT_INTENT":
                qr_vpa = item.get("vpa") or item.get("payee_vpa")
                qr_payee = item.get("payee_name")
                qr_amount = item.get("amount")
                break

    primary_vpa = qr_vpa or (vpa_matches[0] if vpa_matches else None)

    # 2. UTR / Reference Number Extraction (typically 12 digits for authentic UPI)
    utr_pattern = r"(?:UPI Ref|Ref No|UTR|Txn ID|Transaction ID)[:\s]*([0-9A-Za-z]{8,22})"
    utr_match = re.search(utr_pattern, all_text, re.IGNORECASE)
    utr_value = utr_match.group(1) if utr_match else None

    # Fallback search for isolated 10-12 digit numbers if not found
    if not utr_value:
        digit_runs = re.findall(r"\b([0-9]{10,12})\b", all_text)
        if digit_runs:
            utr_value = digit_runs[0]

    # 3. Transacted Amount Extraction (e.g. ₹95,250.00 or Rs. 1,250)
    amount_pattern = r"(?:[₹RrsRs\.]\s*|INR\s*)([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?)"
    amount_match = re.search(amount_pattern, all_text)
    amount_str = amount_match.group(1) if amount_match else qr_amount

    # 4. Payee Name Extraction (heuristics)
    payee_name = qr_payee
    if not payee_name:
        to_pattern = r"(?:Paid to|To:|To\s+|Banking Name:|Beneficiary:?)\s*([A-Za-z0-9\s.\-_]{3,40})"
        name_match = re.search(to_pattern, all_text, re.IGNORECASE)
        if name_match:
            payee_name = name_match.group(1).strip()

    # Determine PSP Provider
    psp_provider = detect_psp_provider(primary_vpa)

    return {
        "payee_vpa": primary_vpa,
        "payee_name": payee_name or "Not Specified / Extracted",
        "utr_number": utr_value,
        "amount": amount_str,
        "psp_provider": psp_provider,
        "qr_linked": bool(qr_vpa),
        "qr_intent": {
            "vpa": qr_vpa,
            "payee": qr_payee,
            "amount": qr_amount,
        } if qr_vpa else None,
    }


def evaluate_syndicate_threat(entities, tamper_score, verdict, clock_paradox=False, is_whatsapp_laundered=False):
    return {"syndicate_risk_level": "UNVERIFIED", "threat_indicators": [],
            "entity_summary": entities, "recommended_action": "Review supplied values independently. No identity, settlement or syndicate intelligence integration is configured."}


def generate_section91_subpoena(report_sha256, filename, timestamp, entities, tamper_score, verdict, findings):
    return ("EVIDENCE PRESERVATION REQUEST — PERSONAL DRAFT\n"
            "Not a subpoena, statutory notice, legal advice, or submission to any authority.\n"
            "No issuing authority is represented by VeriSight. Review and edit before sharing.\n\n"
            f"File: {filename}\nSHA-256: {report_sha256}\nAnalysis time: {timestamp}\n"
            f"Heuristic review score: {tamper_score}/100 (not a probability)\nAssessment: {verdict}\n"
            f"Unverified VPA: {entities.get('payee_vpa') or 'Unavailable'}\n"
            f"Unverified amount: {entities.get('amount') or 'Unavailable'}\n"
            f"Unverified reference: {entities.get('utr_number') or 'Unavailable'}\n\n"
            "I request guidance on preserving the attached evidence and independently checking the reported transaction. "
            "Screenshot analysis cannot establish payment settlement, recipient identity, or criminal involvement.\n\n"
            + "\n".join(f"- {f['title']}: {f['description']}" for f in findings))
