import uuid
from datetime import datetime
from typing import Any

from app.services.response.models import (
    ExtractedIncidentDetails,
    FormalComplaint,
    GenerateComplaintRequest,
)

TRANSLATIONS = {
    "hi": {
        "title_prefix": "औपचारिक साइबर अपराध शिकायत",
        "to_authority": "सेवा में, नोडल अधिकारी / साइबर अपराध जांच प्रभाग",
        "subject_prefix": "विषय: डिजिटल वित्तीय धोखाधड़ी एवं संदिग्ध भुगतान रसीद की औपचारिक शिकायत",
        "sir_madam": "महोदय / महोदया,",
        "personal_exp": "शिकायतकर्ता का प्रत्यक्ष विवरण",
        "counterparty_claims": "प्रतिवादी/संदिग्ध द्वारा किए गए दावे",
        "screenshot_obs": "प्रस्तुत स्क्रीनशॉट का दृश्य विवरण",
        "forensic_obs": "वेरीसाइट (VeriSight) फोरेंसिक विश्लेषण एवं तकनीकी अवलोकन",
        "financial_details": "वित्तीय एवं लेन-देन विवरण",
        "suspected_entity": "संदिग्ध व्यक्ति अथवा संस्था का विवरण",
        "requested_actions": "प्रार्थना एवं अपेक्षित विधिक कार्रवाई",
        "action_freeze": "1. संदिग्ध लाभार्थी बैंक खाते / यूपीआई आईडी (VPA) को तत्काल फ्रीज किया जाए।",
        "action_sec91": "2. संबंधित सेवा प्रदाता को धारा 91 सीआरपीसी / धारा 94 बीएनएसएस के तहत डिजिटल साक्ष्य सुरक्षित रखने का नोटिस भेजा जाए।",
        "action_investigate": "3. आईपी लॉग, आईएमईआई एवं संबंधित बैंक लेन-देन की गहन जांच की जाए।",
        "disclaimer_text": "अस्वीकरण: यह तकनीकी सारांश वेरीसाइट फोरेंसिक प्लेटफॉर्म द्वारा साक्ष्य संगठन के उद्देश्य से तैयार किया गया है। यह कोई आधिकारिक पुलिस रिपोर्ट या न्यायिक निर्णय नहीं है।"
    },
    "kn": {
        "title_prefix": "ಔಪಚಾರಿಕ ಸೈಬರ್ ಕ್ರೈಮ್ ದೂರು",
        "to_authority": "ಮಾನ್ಯ ನೊಡಲ್ ಅಧಿಕಾರಿ / ಸೈಬರ್ ಕ್ರೈಮ್ ತನಿಖಾ ವಿಭಾಗ",
        "subject_prefix": "ವಿಷಯ: ಡಿಜಿಟಲ್ ಪಾವತಿ ವಂಚನೆ ಮತ್ತು ನಕಲಿ ರಶೀದಿಯ ಕುರಿತು ದೂರು",
        "sir_madam": "ಮಾನ್ಯರೇ,",
        "personal_exp": "ದೂರುದಾರರ ವೈಯಕ್ತಿಕ ಅನುಭವ ಮತ್ತು ಘಟನೆ ವಿವರ",
        "counterparty_claims": "ಎದುರುದಾರರು / ಶಂಕಿತರು ನೀಡಿದ ಹೇಳಿಕೆಗಳು",
        "screenshot_obs": "ಪಾವತಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ನ ದೃಶ್ಯ ಪರಿಶೀಲನೆ ವಿವರ",
        "forensic_obs": "ವೆರಿಸೈಟ್ (VeriSight) ಫೋರೆನ್ಸಿಕ್ ತಾಂತ್ರಿಕ ವೀಕ್ಷಣೆಗಳು",
        "financial_details": "ಹಣಕಾಸು ಮತ್ತು ವಹಿವಾಟು ವಿವರಗಳು",
        "suspected_entity": "ಶಂಕಿತ ವ್ಯಕ್ತಿ ಅಥವಾ ಸಂಸ್ಥೆಯ ವಿವರಗಳು",
        "requested_actions": "ಕೋರಿಕೊಂಡಿರುವ ತನಿಖಾ ಕ್ರಮಗಳು",
        "action_freeze": "1. ಶಂಕಿತರ ಫಲಾನುಭವಿ ಬ್ಯಾಂಕ್ ಖಾತೆ / ಯುಪಿಐ ಐಡಿಯನ್ನು ತಕ್ಷಣವೇ ಸ್ಥಗಿತಗೊಳಿಸುವುದು (ಫ್ರೀಜ್).",
        "action_sec91": "2. ಡಿಜಿಟಲ್ ಸಂವಹನ ಲಾಗ್‌ಗಳನ್ನು ಸಂರಕ್ಷಿಸಲು ಸಂಬಂಧಿತ ಕಂಪನಿಗೆ ನೋಟಿಸ್ ನೀಡುವುದು.",
        "action_investigate": "3. ಹಣ ವರ್ಗಾವಣೆಯ ಮೂಲ ಹಾಗೂ ಐಪಿ ವಿಳಾಸದ ತನಿಖೆ ನಡೆಸುವುದು.",
        "disclaimer_text": "ಹಕ್ಕುತ್ಯಾಗ: ಈ ತಾಂತ್ರಿಕ ವರದಿಯು ವೆರಿಸೈಟ್ ಫೋರೆನ್ಸಿಕ್ ವ್ಯವಸ್ಥೆಯಿಂದ ಸಿದ್ಧಪಡಿಸಲಾದ ಮಾಹಿತಿ ಸಂಗ್ರಹವಾಗಿದ್ದು, ಇದು ನ್ಯಾಯಾಲಯದ ಪ್ರಮಾಣೀಕರಣ ಅಥವಾ ಅಧಿಕೃತ ಪೊಲೀಸ್ ವರದಿಯಲ್ಲ."
    },
    "bn": {
        "title_prefix": "আনুষ্ঠানিক সাইবার অপরাধের অভিযোগ",
        "to_authority": "মাননীয় নোডাল অফিসার / সাইবার ক্রাইম তদন্ত বিভাগ",
        "subject_prefix": "বিষয়: ডিজিটাল আর্থিক প্রতারণা ও জাল পেমেন্ট স্ক্রিনশটের অভিযোগ",
        "sir_madam": "মহাশয় / মহাশয়া,",
        "personal_exp": "অভিযোগকারীর প্রত্যক্ষ বিবরণ",
        "counterparty_claims": "সন্দেহভাজন ব্যক্তির দাবি",
        "screenshot_obs": "পেমেন্ট স্ক্রিনশটের দৃশ্যমান বিবরণ",
        "forensic_obs": "ভ্যারিসাইট (VeriSight) ফরেনসিক পর্যবেক্ষণ",
        "financial_details": "আর্থিক ও লেনদেনের বিবরণ",
        "suspected_entity": "সন্দেহভাজন ব্যক্তি বা সংস্থার বিবরণ",
        "requested_actions": "প্রয়োজনীয় আইনি ব্যবস্থা গ্রহণের আবেদন",
        "action_freeze": "১. সন্দেহভাজন ব্যক্তির সুবিধাভোগী ব্যাংক অ্যাকাউন্ট ও ইউপিআই আইডি দ্রুত ফ্রিজ করা হোক।",
        "action_sec91": "২. ডিজিটাল প্রমাণ সংরক্ষণের জন্য সংশ্লিষ্ট প্ল্যাটফর্মকে নোটিশ পাঠানো হোক।",
        "action_investigate": "৩. আর্থিক প্রতারণার ঘটনার পূর্ণাঙ্গ তদন্ত করে অর্থ পুনরুদ্ধারের নির্দেশ দেওয়া হোক।",
        "disclaimer_text": "দাবিত্যাগ: এই প্রযুক্তিগত ফরেনসিক সারাংশটি ভ্যারিসাইট সিস্টেম দ্বারা প্রমাণ সংগঠনের জন্য তৈরি, এটি কোনও আনুষ্ঠানিক পুলিশ রিপোর্ট নয়।"
    },
    "ta": {
        "title_prefix": "முறையான இணையவழி குற்றப் புகார்",
        "to_authority": "மதிப்பிற்குரிய சைபர் குற்றப் பிரிவு ஆய்வாளர் அவர்களுக்கு",
        "subject_prefix": "பொருள்: டிஜிட்டல் பண மோசடி மற்றும் போலி ரசீது தொடர்பான புகார்",
        "sir_madam": "மதிப்பிற்குரிய ஐயா / அம்மா,",
        "personal_exp": "புகார்தாரரின் நேரடி அனுபவ விவரம்",
        "counterparty_claims": "எதிர் தரப்பினர் கூறிய தகவல்கள்",
        "screenshot_obs": "காட்டப்பட்ட ரசீது குறித்த விவரம்",
        "forensic_obs": "வெரிசைட் (VeriSight) தடயவியல் தொழில்நுட்பக் குறிப்புகள்",
        "financial_details": "நிதி மற்றும் பரிவர்த்தனை விவரங்கள்",
        "suspected_entity": "சந்தேகத்திற்குரிய நபர் / நிறுவனம்",
        "requested_actions": "கோரப்படும் சட்ட நடவடிக்கைகள்",
        "action_freeze": "1. சந்தேகத்திற்குரிய பயனாளியின் வங்கி கணக்கு / UPI ஐடியை உடனடியாக முடக்கவும்.",
        "action_sec91": "2. டிஜிட்டல் சான்றுகளைப் பாதுகாக்க சம்பந்தப்பட்ட நிறுவனத்திற்கு நோட்டீஸ் அனுப்பவும்.",
        "action_investigate": "3. இழந்த தொகையை மீட்க விரைவான விசாரணை மேற்கொள்ள வேண்டுகிறேன்.",
        "disclaimer_text": "பொறுப்புத் துறப்பு: இது வெரிசைட் தடயவியல் தளத்தால் சான்றுகளை ஒழுங்கமைக்க உருவாக்கப்பட்ட தொழில்நுட்ப அறிக்கை மட்டுமே; இது நீதிமன்ற உத்தரவு அல்ல."
    },
    "te": {
        "title_prefix": "అధికారిక సైబర్ క్రైమ్ ఫిర్యాదు",
        "to_authority": "గౌరవనీయ సైబర్ క్రైమ్ ఇన్వెస్టిగేషన్ అధికారి గారికి",
        "subject_prefix": "విషయం: డిజిటల్ ఆర్థిక మోసం మరియు నకిలీ రశీదుపై అధికారిక ఫిర్యాదు",
        "sir_madam": "అయ్యా / అమ్మా,",
        "personal_exp": "ఫిర్యాదుదారుడి ప్రత్యక్ష వివరణ",
        "counterparty_claims": "అనుమానితుడు చేసిన ప్రకటనలు",
        "screenshot_obs": "చెల్లింపు స్క్రీన్‌షాట్ పరిశీలన",
        "forensic_obs": "వెరిసైట్ (VeriSight) ఫోరెన్సిక్ సాంకేతిక విశ్లేషణ",
        "financial_details": "ఆర్థిక మరియు లావాదేవీల వివరాలు",
        "suspected_entity": "అనుమానిత వ్యక్తి లేదా సంస్థ వివరాలు",
        "requested_actions": "అభ్యర్థించిన దర్యాప్తు చర్యలు",
        "action_freeze": "1. అనుమానితుడి లబ్ధిదారు బ్యాంక్ ఖాతా / UPI ఐడీని తక్షణమే స్తంభింపజేయాలి (ఫ్రీజ్).",
        "action_sec91": "2. డిజిటల్ ఆధారాలను భద్రపరచడానికి నోటీసు జారీ చేయాలి.",
        "action_investigate": "3. సైబర్ నేరంపై తగిన విచారణ జరిపి న్యాయం చేయాలని కోరుతున్నాను.",
        "disclaimer_text": "గమనిక: ఈ నివేదిక వెరిసైట్ ఫోరెన్సిక్ సిస్టమ్ ద్వారా ఆధారాల కోసం రూపొందించబడింది, ఇది అధికారిక పోలీసు లేదా న్యాయపరమైన ధృవీకరణ కాదు."
    },
    "mr": {
        "title_prefix": "औपचारिक सायबर गुन्हे तक्रार",
        "to_authority": "मा. सायबर गुन्हे अन्वेषण अधिकारी,",
        "subject_prefix": "विषय: डिजिटल पेमेंट फसवणूक आणि बनावट पावतीबाबत तक्रार",
        "sir_madam": "महोदय / महोदया,",
        "personal_exp": "तक्रारदाराचा थेट अनुभव आणि घटनाक्रम",
        "counterparty_claims": "संशयित व्यक्तीने केलेले दावे",
        "screenshot_obs": "पेमेंट स्क्रीनशॉटचे दृश्य निरीक्षण",
        "forensic_obs": "व्हेरीसाईट (VeriSight) फॉरेन्सिक तांत्रिक निरीक्षणे",
        "financial_details": "आर्थिक आणि व्यवहार तपशील",
        "suspected_entity": "संशयित व्यक्ती किंवा खात्याचा तपशील",
        "requested_actions": "मागणी केलेली कायदेशीर कारवाई",
        "action_freeze": "१. संशयिताचे लाभार्थी बँक खाते / यूपीआय त्वरित गोठवण्यात (फ्रीझ) यावे.",
        "action_sec91": "२. डिजिटल पुरावे सुरक्षित ठेवण्यासाठी संबंधित कंपनीला नोटीस बजावण्यात यावी.",
        "action_investigate": "३. सायबर फसवणुकीची सखोल चौकशी करून गमावलेली रक्कम परत मिळवून द्यावी.",
        "disclaimer_text": "अस्वीकरण: हा तांत्रिक सारांश व्हेरीसाईट फॉरेन्सिक प्लॅटफॉर्मद्वारे पुरावा संकलनासाठी तयार केला आहे, हा न्यायालयीन निकाल नाही."
    },
    "en": {
        "title_prefix": "FORMAL CYBERCRIME INCIDENT REPORT",
        "to_authority": "To: The Investigating Officer / Cyber Crime Police Station / Nodal Grievance Officer",
        "subject_prefix": "SUBJECT: Formal Complaint Regarding Financial Cyber Incident & Fraudulent Digital Evidence",
        "sir_madam": "Respected Officer / Grievance Authority,",
        "personal_exp": "1. Complainant's Personal Direct Experience",
        "counterparty_claims": "2. Statements & Representations Made by Counterparty",
        "screenshot_obs": "3. Visual Representation of Disputed Screenshot",
        "forensic_obs": "4. VeriSight Multi-Spectral Forensic Observations",
        "financial_details": "5. Financial Impact & Transaction Specifics",
        "suspected_entity": "6. Suspected Entity & Counterparty Identifiers",
        "requested_actions": "7. Requested Law Enforcement & Protective Actions",
        "action_freeze": "1. Immediate lien marking / debit freezing of the suspect beneficiary bank account and associated UPI VPA under Section 106 BNSS / Section 102 CrPC.",
        "action_sec91": "2. Issuance of preservation and disclosure orders under Section 94 BNSS / Section 91 CrPC to the concerned Payment Service Provider and messaging platform.",
        "action_investigate": "3. Verification of telecommunication subscriber records (CDRs), IP log history, and bank branch KYC records.",
        "disclaimer_text": "DISCLAIMER: This technical forensic dossier is prepared through the VeriSight forensic system to assist the complainant in presenting structured evidence. VeriSight risk metrics represent signal analysis and do not constitute a legal conclusion or police investigation certificate."
    }
}


def build_forensic_observations_text(report: dict[str, Any] | None) -> list[str]:
    if not report:
        return [
            "No automated forensic screenshot analysis has been attached to this complaint.",
            "Add only evidence you actually possess; no submission has been made."
        ]

    obs: list[str] = []
    file_hash = report.get("file_sha256", "N/A")
    tamper_score = report.get("overall_tamper_score", 0.0)
    verdict = report.get("verdict", "UNKNOWN")
    width = report.get("image_width", 0)
    height = report.get("image_height", 0)

    obs.append(f"File identification: SHA-256 {file_hash} (Image Dimensions: {width}x{height}px).")
    obs.append(f"Heuristic Review Score (not a probability): {tamper_score:.1f}/100 (Classification: {verdict}).")

    findings = report.get("findings", [])
    if findings:
        obs.append(f"Detected Anomaly Count: {len(findings)} review cues identified across signal layers:")
        for idx, f in enumerate(findings[:4], 1):
            title = f.get("title", "Anomaly")
            desc = f.get("description", "")
            metric = f.get("metric_name", "")
            val = f.get("metric_value", "")
            obs.append(f"  • Flag {idx} [{f.get('severity', 'HIGH')}]: {title} — {desc} ({metric}: {val}).")

    synergy = report.get("synergy", {})
    if synergy.get("synergy_multiplier_applied"):
        obs.append(f"Multi-Signal Convergence: {synergy.get('synergy_explanation', 'Spatial intersection confirmed across independent compression and typography layers.')}")

    obs.append("Forensic Limitation: Image compression (such as WhatsApp forwarding) can introduce secondary artifacts; observations reflect mathematical signal anomalies.")
    return obs


def generate_formal_complaint(request: GenerateComplaintRequest) -> FormalComplaint:
    d = request.details
    lang = request.language if request.language in TRANSLATIONS else "en"
    t = dict(TRANSLATIONS[lang])
    t["action_freeze"] = "1. Please advise on appropriate protective steps for the incident described above."
    t["action_sec91"] = "2. Please advise how to preserve and provide relevant evidence through an authorized channel."
    t["action_investigate"] = "3. Please review the reported facts independently. No outcome or recovery is guaranteed."

    comp_id = f"VS-CMP-{uuid.uuid4().hex[:8].upper()}"

    # Destination mapping
    auth_destinations = {
        "NATIONAL_CYBER_CRIME_PORTAL": (
            "National Cyber Crime Reporting Portal (NCRP) / 1930 Helpline",
            "https://cybercrime.gov.in"
        ),
        "BANK_UPI_PSP": (
            f"Bank Grievance Redressal / {d.bank_or_upi_provider or 'Payment Service Provider'}",
            "https://www.npci.org.in"
        ),
        "RBI_CMS_OMBUDSMAN": (
            "Reserve Bank of India (RBI) Integrated Ombudsman / CMS",
            "https://cms.rbi.org.in"
        ),
        "POLICE_CYBER_CELL": (
            "District Cyber Crime Police Station / Jurisdictional Police Station",
            "https://cybercrime.gov.in"
        ),
        "PLATFORM_ABUSE": (
            f"{d.communication_channel or 'Platform'} Cyber Grievance Officer",
            "https://gac.gov.in"
        ),
    }

    auth_name, auth_url = auth_destinations.get(
        request.authority_destination,
        ("National Cyber Crime Reporting Portal (NCRP)", "https://cybercrime.gov.in")
    )

    # Chronological breakdown
    forensic_obs = build_forensic_observations_text(request.attached_forensic_report)

    # Personal direct experience
    personal_exp = (
        request.custom_narrative_edits or
        f"I, {d.complainant_name or 'the complainant'}, state that on {d.incident_date or 'the date of incident'} "
        f"at approximately {d.approximate_time or 'the stated time'}, I experienced the following cyber incident: "
        f"{d.narrative_description}"
    )

    # Never invent a bank balance check, counterparty statement, or evidence capture.
    counterparty_claims = "Review and describe the counterparty's actual statements in your own words. No statement is independently verified by VeriSight."
    screenshot_obs = (
        f"An image analysis is attached with SHA-256 {request.attached_forensic_report.get('file_sha256', 'unavailable')}. "
        "Its review cues do not verify payment settlement."
        if request.attached_forensic_report else "No image analysis is attached. List only evidence actually available to you."
    )

    # Narrative synthesis
    chronological = f"""{t['sir_madam']}

{t['subject_prefix']} - {d.incident_category_label}

{t['personal_exp']}:
{personal_exp}

{t['counterparty_claims']}:
{counterparty_claims}

{t['screenshot_obs']}:
{screenshot_obs}

{t['forensic_obs']}:
{chr(10).join(forensic_obs)}

{t['requested_actions']}:
{t['action_freeze']}
{t['action_sec91']}
{t['action_investigate']}

Sincerely,
{d.complainant_name or 'Complainant'}
Contact: {d.complainant_contact or 'Provided with identity proof'}
Date: {datetime.now().strftime('%d %B %Y')}
"""

    financial_info = {
        "claimed_amount": d.financial_loss_amount or 0.0,
        "currency": d.currency,
        "financial_impact": d.financial_impact.value,
        "payment_method": d.payment_method or "UPI",
        "bank_or_psp": d.bank_or_upi_provider or "Unspecified",
    }

    suspected_info = {
        "name_or_alias": d.suspected_person_or_entity or "Unknown",
        "vpa": d.suspected_vpa or "N/A",
        "phone": d.suspected_phone or "N/A",
        "channel": d.communication_channel or "Digital Messaging",
    }

    evidence_docs = [
        "Suggested annexure A (if available): Original screenshot of the disputed payment / communication.",
        "Annexure B: Bank account statement, if available; confirm its contents independently.",
        "Suggested annexure C (if available): Unedited messaging transcript (WhatsApp / Telegram / SMS).",
    ]
    if request.attached_forensic_report:
        evidence_docs.append("Annexure D: VeriSight Forensic Integrity Audit & Multi-Spectral Signal Report.")

    return FormalComplaint(
        id=comp_id,
        title=f"DRAFT — {t['title_prefix']} — {comp_id}",
        destination_authority_name=auth_name,
        destination_portal_url=auth_url,
        complainant_name=d.complainant_name or "Complainant",
        complainant_contact=d.complainant_contact or "Confidential / On File",
        incident_date_time=f"{d.incident_date or 'Recent'} {d.approximate_time or ''}".strip(),
        incident_category=d.incident_category_label,
        chronological_narrative=chronological.strip(),
        statements_breakdown={
            "personal_experience": personal_exp,
            "counterparty_claims": counterparty_claims,
            "screenshot_representation": screenshot_obs,
            "forensic_observations": "\n".join(forensic_obs),
            "unverified_elements": "Identity of counterparty and authenticity of remote server logs remain subject to law enforcement discovery.",
        },
        financial_details=financial_info,
        transaction_reference=d.transaction_reference or "NOT_SUPPLIED",
        suspected_entity=suspected_info,
        communication_channel=d.communication_channel or "Unspecified",
        evidence_inventory=d.available_evidence,
        forensic_observations=forensic_obs,
        requested_action=f"{t['action_freeze']} {t['action_sec91']} {t['action_investigate']}",
        supporting_document_index=evidence_docs,
        disclaimer="PERSONAL DRAFT — review and edit every statement. Not submitted, signed, certified or issued by any authority. Screenshot analysis does not verify payment settlement. " + t["disclaimer_text"],
        language=lang,
    )
