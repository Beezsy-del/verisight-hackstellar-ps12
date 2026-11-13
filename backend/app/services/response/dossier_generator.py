import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.response.models import FormalComplaint


def generate_complaint_pdf(complaint: FormalComplaint) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,  # Center
    )
    subhead_style = ParagraphStyle(
        "SubheadStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )
    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
    )
    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )

    story = []

    # Title & Subhead
    story.append(Paragraph(complaint.title, header_style))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            f"Prepared for: <b>{complaint.destination_authority_name}</b> | Ref: {complaint.id}",
            subhead_style,
        )
    )
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceBefore=2, spaceAfter=8))

    # Meta Table
    meta_data = [
        [
            Paragraph("Complainant:", meta_label),
            Paragraph(complaint.complainant_name, meta_val),
            Paragraph("Incident Date/Time:", meta_label),
            Paragraph(complaint.incident_date_time, meta_val),
        ],
        [
            Paragraph("Contact / Phone:", meta_label),
            Paragraph(complaint.complainant_contact, meta_val),
            Paragraph("Incident Category:", meta_label),
            Paragraph(complaint.incident_category, meta_val),
        ],
        [
            Paragraph("Claimed Amount:", meta_label),
            Paragraph(
                f"{complaint.financial_details.get('currency', 'INR')} {complaint.financial_details.get('claimed_amount', 0):,}",
                meta_val,
            ),
            Paragraph("Payment Method:", meta_label),
            Paragraph(
                str(complaint.financial_details.get("payment_method", "UPI")),
                meta_val,
            ),
        ],
        [
            Paragraph("Txn / UTR Ref:", meta_label),
            Paragraph(complaint.transaction_reference, meta_val),
            Paragraph("Suspected Entity / VPA:", meta_label),
            Paragraph(
                f"{complaint.suspected_entity.get('name_or_alias', 'N/A')} ({complaint.suspected_entity.get('vpa') or complaint.suspected_entity.get('phone') or 'N/A'})",
                meta_val,
            ),
        ],
    ]
    t = Table(meta_data, colWidths=[1.3 * inch, 2.3 * inch, 1.4 * inch, 2.3 * inch])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(t)
    story.append(Spacer(1, 10))

    # Narrative Section
    story.append(Paragraph("Chronological Factual Statement & Details", section_title))
    paragraphs = complaint.chronological_narrative.split("\n\n")
    for p in paragraphs:
        if p.strip():
            story.append(Paragraph(p.strip().replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 4))

    # Supporting Document Index
    if complaint.supporting_document_index:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Index of Supporting Evidence & Annexures", section_title))
        for doc_item in complaint.supporting_document_index:
            story.append(Paragraph(f"• {doc_item}", body_style))
            story.append(Spacer(1, 2))

    # Requested Actions
    story.append(Spacer(1, 6))
    story.append(Paragraph("Relief & Investigation Requested", section_title))
    story.append(Paragraph(complaint.requested_action, body_style))

    # Disclaimer Footer
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(complaint.disclaimer, disclaimer_style))

    doc.build(story)
    return buffer.getvalue()


def generate_evidence_dossier_pdf(report: dict[str, Any], complaint_ref: str | None = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0284c7"),
        alignment=1,
    )
    subhead_style = ParagraphStyle(
        "SubheadStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
    )
    mono_style = ParagraphStyle(
        "MonoStyle",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0f172a"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )

    file_sha = report.get("file_sha256", "UNKNOWN")
    case_id = f"VS-EVD-{file_sha[:10].upper()}"
    tamper_score = report.get("overall_tamper_score", 0.0)
    verdict = report.get("verdict", "INCONCLUSIVE")

    story = []

    # Header
    story.append(Paragraph("VERISIGHT DIGITAL FORENSIC EVIDENCE DOSSIER", header_style))
    story.append(
        Paragraph(
            f"Case Dossier Ref: <b>{case_id}</b> | Complaint Linked: <b>{complaint_ref or 'UNLINKED'}</b> | Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            subhead_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0ea5e9"), spaceBefore=4, spaceAfter=8))

    # Summary Table
    summary_data = [
        [
            Paragraph("<b>Forensic Verdict:</b>", body_style),
            Paragraph(f"<b>{verdict}</b>", body_style),
            Paragraph("<b>Heuristic review score:</b>", body_style),
            Paragraph(f"<b>{tamper_score:.1f} / 100</b>", body_style),
        ],
        [
            Paragraph("<b>Original File:</b>", body_style),
            Paragraph(report.get("filename", "unknown.png"), body_style),
            Paragraph("<b>Image Dimensions:</b>", body_style),
            Paragraph(f"{report.get('image_width', 0)} x {report.get('image_height', 0)} px", body_style),
        ],
        [
            Paragraph("<b>Cryptographic Hash:</b>", body_style),
            Paragraph(f"SHA-256: {file_sha}", mono_style),
            Paragraph("<b>Channel Detected:</b>", body_style),
            Paragraph(report.get("channel_detected", "UNKNOWN_CHANNEL"), body_style),
        ],
    ]
    t = Table(summary_data, colWidths=[1.4 * inch, 2.3 * inch, 1.4 * inch, 2.3 * inch])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )
    story.append(t)
    story.append(Spacer(1, 6))

    # Multi-Layer Findings
    findings = report.get("findings", [])
    story.append(Paragraph(f"1. Detected Multi-Layer Forensic Signal Anomalies ({len(findings)} Review Cues)", section_title))
    if findings:
        finding_rows = [["Layer", "Severity", "Finding Title & Forensic Description", "Metric Value"]]
        for f in findings:
            finding_rows.append([
                f"L{f.get('layer', 1)}",
                f.get("severity", "INFO"),
                f"{f.get('title', 'Anomaly')}: {f.get('description', '')}",
                f"{f.get('metric_name', '')}: {f.get('metric_value', '')}",
            ])
        ft = Table(finding_rows, colWidths=[0.5 * inch, 0.8 * inch, 4.6 * inch, 1.5 * inch])
        ft.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ])
        )
        story.append(ft)
    else:
        story.append(Paragraph("No strong review cues detected; authenticity and payment settlement remain unverified.", body_style))

    # Cross-Layer Synergy
    synergy = report.get("synergy", {})
    if synergy.get("synergy_multiplier_applied"):
        story.append(Spacer(1, 4))
        story.append(Paragraph("2. Cross-Layer Geometric Synergy Convergence", section_title))
        story.append(
            Paragraph(
                f"Boost Factor: <b>{synergy.get('multiplier_factor', 1.0)}x</b> — {synergy.get('synergy_explanation', '')}",
                body_style,
            )
        )

    # Methodology & Limitations
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Forensic Methodology & Scientific Framework", section_title))
    story.append(
        Paragraph(
            "VeriSight executes a 4-layer forensic inspection model: "
            "(L1) Signal & Pixel Compression Physics (Error Level Analysis ELA, Wavelet High-Frequency Decomposition, ORB Copy-Move Clones); "
            "(L2) Typography & Geometric Precision (Sub-pixel Baseline Laser, Font Kerning / CIELAB Color Space Continuity); "
            "(L3) Structural Metadata & Transaction Protocols (Exif Stripping Detection, Viewport Ratio Consistency, Temporal Status Bar Clock Consistency, NPCI 12-digit UTR Checksum); "
            "(L4) Heuristic Multi-Spectral Ensemble Calibration (HistGradientBoosting / Logistic Model Fusion).",
            body_style,
        )
    )

    story.append(Spacer(1, 4))
    story.append(Paragraph("4. Technical Limitations & Chain-of-Custody Safeguards", section_title))
    story.append(
        Paragraph(
            "Observations reflect statistical and physical signal variations in digital image containers. Lossy compression, screen re-encoding (e.g. WhatsApp / MMS forwarding), or third-party camera re-photography can introduce non-fraudulent noise outliers. This report must be evaluated in conjunction with verified bank account statements, banking switch logs (NPCI), and telecommunications provider records under legal process.",
            body_style,
        )
    )

    # Footer Disclaimer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=4, spaceAfter=6))
    story.append(
        Paragraph(
            "LEGAL DISCLAIMER: This document is an automated technical forensic summary generated by VeriSight. It does not constitute a certified expert testimony, a judicial determination, or an official police FIR. VeriSight is an independent forensic analysis system.",
            disclaimer_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()
