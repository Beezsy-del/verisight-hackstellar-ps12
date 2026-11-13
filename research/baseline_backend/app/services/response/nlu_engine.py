import re
from datetime import datetime
from typing import Any

from app.services.response.models import (
    DynamicQuestion,
    ExtractedIncidentDetails,
    FinancialImpact,
    IncidentCategory,
    QuestionUrgency,
    UnderstandIncidentResponse,
)

# Multilingual keywords dictionary for categorisation & entity detection
MULTILINGUAL_KEYWORDS = {
    IncidentCategory.FAKE_PAYMENT_SCREENSHOT: [
        "fake screenshot", "fake payment", "fake receipt", "spoofed receipt",
        "showed screenshot", "sent screenshot", "payment screenshot", "fake upi",
        "नकली स्क्रीनशॉट", "फर्जी रसीद", "स्क्रीनशॉट भेजा", "पैसे नहीं आए",
        "ನಕಲಿ ಸ್ಕ್ರೀನ್‌ಶಾಟ್", "ಖಾತೆಗೆ ಬಂದಿಲ್ಲ", "ಹಣ ಬಂದಿಲ್ಲ", "ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ತೋರಿಸಿದ",
        "নকল স্ক্রিনশট", "পেমেন্ট আসেনি", "টাকা ঢোকেনি",
        "போலி ஸ்கிரீன்ஷாட்", "பணம் வரவில்லை", "ரசீது காண்பித்தார்",
        "నకిలీ స్క్రీన్‌షాట్", "డబ్బులు రాలేదు", "రశీదు చూపించాడు",
        "खोटा स्क्रीनशॉट", "पैसे जमा झाले नाहीत", "स्क्रीनशॉट दाखवला"
    ],
    IncidentCategory.QR_CODE_FRAUD: [
        "qr code", "qr scam", "scan to receive", "scan qr", "bar code",
        "क्यूआर कोड", "क्यूआर स्कैन", "स्कैन करने को कहा",
        "ಕ್ಯೂಆರ್ ಕೋಡ್", "ಸ್ಕ್ಯಾನ್ ಮಾಡಲು",
        "কিউআর কোড", "স্ক্যান করতে বলেছে",
        "க்யூஆர் குறியீடு", "ஸ்கேன் செய்ய சொன்னார்கள்",
        "క్యూఆర్ కోడ్", "స్కాన్ చేయమన్నారు",
        "क्युआर कोड", "स्कॅन करायला सांगितले"
    ],
    IncidentCategory.UPI_FRAUD: [
        "upi pin", "collect request", "entered pin", "pin enter", "requested money",
        "यूपीआई पिन", "पिन डाला", "कलेक्ट रिक्वेस्ट",
        "ಯುಪಿಐ ಪಿನ್", "ಪಿನ್ ನಮೂದಿಸಿದೆ",
        "ইউপিআই পিন", "পিন দিয়েছি",
        "யூபிஐ பின்", "பின் போட்டேன்",
        "యుపిఐ పిన్", "పిన్ ఎంటర్ చేశాను",
        "यूपीआय पिन", "पिन टाकला"
    ],
    IncidentCategory.UNAUTHORIZED_BANK_TRANSACTION: [
        "unauthorized", "auto debit", "money deducted without", "without otp", "compromised account",
        "अनधिकृत", "बिना ओटीपी", "अपने आप कट गए",
        "ಅನಧಿಕೃತ", "ಓಟಿಪಿ ಇಲ್ಲದೆ ಹಣ ಕಡಿತ",
        "অননুমোদিত", "ওটিপি ছাড়াই টাকা কাটা",
        "அங்கீகரிக்கப்படாத", "ஓடிபி இல்லாமல் பணம் பிடித்தம்",
        "అనధికారిక", "ఓటీపీ లేకుండా డబ్బు డెబిట్",
        "अनधिकृत व्यवहार", "ओटीपी शिवाय पैसे कापले"
    ],
    IncidentCategory.IMPERSONATION: [
        "pretending to be", "impersonator", "fake profile", "posing as", "fake officer", "army officer",
        "पहचान चुराई", "अधिकारी बनकर", "फर्जी प्रोफाइल", "आर्मी अफसर",
        "ಅಧಿಕಾರಿಯಂತೆ", "ನಕಲಿ ಪ್ರೊಫೈಲ್",
        "ছদ্মবেশী", "নকল অফিসার",
        "ஆள்மாறாட்டம்", "போலி அதிகாரி",
        "నకిలీ ప్రొఫైల్", "అధికారిగా నటిస్తూ",
        "तोतयागिरी", "बनावट अधिकारी"
    ],
    IncidentCategory.ONLINE_MARKETPLACE_FRAUD: [
        "olx", "quikr", "marketplace", "sold phone", "selling my", "buyer asked",
        "ओएलएक्स", "मार्केटप्लेस", "फोन बेचा", "खरीदार",
        "ಓಎಲ್ಎಕ್ಸ್", "ಮಾರ್ಕೆಟ್‌ಪ್ಲೇಸ್", "ಫೋನ್ ಮಾರಾಟ",
        "ওএলএক্স", "মার্কেটপ্লেস",
        "ஓஎல்எக்ஸ்", "பொருட்கள் விற்பனை",
        "ఓఎల్ఎక్స్", "మార్కెట్‌ప్లేస్",
        "ओएलएक्स", "फोन विकला"
    ],
    IncidentCategory.PHISHING_SOCIAL_ENGINEERING: [
        "apk", "anydesk", "teamviewer", "electricity bill", "kyc update", "phishing link",
        "केवाईसी अपडेट", "बिजली बिल", "लिंक पर क्लिक", "एपीके फाइल",
        "ಕೆವೈಸಿ ಅಪ್ಡೇಟ್", "ವಿದ್ಯುತ್ ಬಿಲ್", "ಲಿಂಕ್ ಕ್ಲಿಕ್",
        "কেওয়াইসি আপডেট", "বিদ্যুৎ বিল", "লিংকে ক্লিক",
        "கேஒய்சி புதுப்பிப்பு", "மின்சார கட்டணம்", "இணைப்பு",
        "కేవైసీ అప్‌డేట్", "కరెంట్ బిల్లు", "లింక్ క్లిక్",
        "केवायसी अपडेट", "वीज बिल", "लिंकवर क्लिक"
    ],
}

BANKS_AND_PSPS = [
    ("Google Pay", ["google pay", "gpay", "g-pay", "गूगल पे", "ಗೂಗಲ್ ಪೇ", "গুগল পে"]),
    ("PhonePe", ["phonepe", "phone pe", "फोनपे", "ಫೋನ್‌ಪೇ", "ফোনপে"]),
    ("Paytm", ["paytm", "पेटीएम", "ಪೇಟಿಎಂ", "পেটিএম"]),
    ("BHIM UPI", ["bhim", "भीम"]),
    ("State Bank of India (SBI)", ["sbi", "state bank", "एसबीआई", "ಎಸ್ ಬಿ ಐ", "এসবিআই"]),
    ("HDFC Bank", ["hdfc", "एचडीएफसी", "ಎಚ್‌ಡಿಎಫ್‌ಸಿ"]),
    ("ICICI Bank", ["icici", "आईसीआईसीआई", "ಐಸಿಐಸಿಐ"]),
    ("Axis Bank", ["axis bank", "एक्सिस बैंक", "ಆಕ್ಸಿಸ್"]),
    ("Punjab National Bank (PNB)", ["pnb", "punjab national", "पीएनबी"]),
    ("Kotak Mahindra Bank", ["kotak", "कोटक"]),
    ("Bank of Baroda", ["bob", "bank of baroda", "बैंक ऑफ बड़ौदा"]),
]

COMMUNICATION_CHANNELS = [
    ("WhatsApp", ["whatsapp", "wa chat", "व्हाट्सएप", "ವಾಟ್ಸಾಪ್", "হোয়াটসঅ্যাপ"]),
    ("Telegram", ["telegram", "tele", "टेलीग्राम", "ಟೆಲಿಗ್ರಾಂ"]),
    ("OLX", ["olx", "ओएलएक्स", "ಓಎಲ್ಎಕ್ಸ್"]),
    ("Instagram", ["instagram", "insta", "इंस्टाग्राम", "ಇನ್‌ಸ್ಟಾಗ್ರಾಂ"]),
    ("Phone Call", ["phone call", "called me", "mobile call", "फोन कॉल", "कॉल आया", "ಕರೆ"]),
    ("SMS", ["sms", "text message", "मैसेज", "ಸಂದೇಶ"]),
    ("Facebook", ["facebook", "fb", "फेसबुक"]),
]


def extract_financial_amount(text: str) -> tuple[float | None, str]:
    currency = "INR"
    patterns = [
        r"[₹]\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:rs\.?|inr|rupees?|रुपये?|रु\.?|ರೂಪಾಯಿ|টাকা|பணம்|రూపాయలు)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs\.?|inr|rupees?|रुपये?|रु\.?|ರೂಪಾಯಿ|টাকা|రూపాయలు)",
        r"(?:lost|paid|transferred|deducted|debited|of)\s+([\d,]+(?:\.\d{1,2})?)",
        r"\b([\d,]+(?:\.\d{1,2})?)\s*(?:का|की|/-|/)",
        r"(\d+)\s*k\b",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val_str = m.group(1).replace(",", "")
            try:
                val = float(val_str)
                if "k" in p:
                    val *= 1000
                return val, currency
            except ValueError:
                continue

    # Fallback: look for 3 to 8 digit numbers in text that are not phone numbers or years (2020-2030) or 12-digit UTRs
    for num_match in re.finditer(r"\b(\d{3,8})\b", text):
        num_str = num_match.group(1)
        if len(num_str) == 4 and (2020 <= int(num_str) <= 2035):
            continue
        # Check if preceded or followed by payment/screenshot/loss words
        start = max(0, num_match.start() - 30)
        end = min(len(text), num_match.end() + 30)
        window = text[start:end].lower()
        if any(w in window for w in ["screenshot", "screen shot", "स्क्रीनशॉट", "pay", "पे", "रुप", "हण", "loss", "sent", "credited"]):
            try:
                return float(num_str), currency
            except ValueError:
                pass

    return None, currency


def extract_utr_or_reference(text: str) -> str | None:
    # 12 digit standard Indian UPI UTR / RRN (e.g. 403218942311)
    utr_match = re.search(r"\b(\d{12})\b", text)
    if utr_match:
        return utr_match.group(1)
    # Generic UTR / Ref patterns (e.g. UTR: 123456789012, Ref 123456)
    ref_match = re.search(r"(?:utr|rrn|ref|reference|txn id|transaction id)[:\s#]*([a-zA-Z0-9]{8,18})", text, re.IGNORECASE)
    if ref_match:
        return ref_match.group(1)
    return None


def extract_vpa(text: str) -> str | None:
    vpa_pattern = r"\b([a-zA-Z0-9.\-_]{2,64}@[a-zA-Z]{2,32})\b"
    m = re.search(vpa_pattern, text)
    if m:
        candidate = m.group(1).lower()
        # Exclude typical email domains
        if not candidate.endswith(("@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com")):
            return candidate
    return None


def extract_phone(text: str) -> str | None:
    # Indian phone: +91 9876543210 or 9876543210
    phone_pattern = r"(?:\+91[\-\s]?)?([6-9]\d{9})\b"
    m = re.search(phone_pattern, text)
    if m:
        return m.group(1)
    return None


def extract_bank_or_psp(text: str) -> str | None:
    # Remove VPAs from matching text so e.g. 'fraudster@paytm' doesn't falsely classify the complainant's bank as Paytm
    clean_text = re.sub(r"\b[a-zA-Z0-9.\-_]{2,64}@[a-zA-Z]{2,32}\b", " ", text)
    clean_text_lower = clean_text.lower()

    # First check explicit complainant bank associations e.g. "from my SBI account", "in HDFC"
    for canonical_name, aliases in BANKS_AND_PSPS:
        for alias in aliases:
            al = alias.lower()
            pattern = rf"\b(?:from\s+my|in\s+my|my|account\s+in|with)\s+{re.escape(al)}\b"
            if re.search(pattern, clean_text_lower):
                return canonical_name

    # Second pass: check presence
    for canonical_name, aliases in BANKS_AND_PSPS:
        for alias in aliases:
            al = alias.lower()
            # If alias is non-ASCII (e.g. Devanagari, Kannada, Bengali)
            if any(ord(c) > 127 for c in al):
                if al in clean_text_lower:
                    return canonical_name
            else:
                if re.search(rf"\b{re.escape(al)}\b", clean_text_lower):
                    return canonical_name
    return None


def extract_communication_channel(text: str) -> str | None:
    text_lower = text.lower()
    for canonical_name, aliases in COMMUNICATION_CHANNELS:
        for alias in aliases:
            if alias.lower() in text_lower:
                return canonical_name
    return None


def classify_incident_and_impact(
    text: str, attached_forensic_report: dict[str, Any] | None = None
) -> tuple[IncidentCategory, FinancialImpact, str, float]:
    text_lower = text.lower()
    scores: dict[IncidentCategory, int] = {cat: 0 for cat in IncidentCategory}

    # 1. Check keyword triggers
    for cat, keywords in MULTILINGUAL_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[cat] += 2

    # 2. Check forensic findings context
    if attached_forensic_report:
        verdict = attached_forensic_report.get("verdict", "")
        tamper_score = attached_forensic_report.get("overall_tamper_score", 0)
        if tamper_score >= 25 or verdict in ("MANIPULATED_FORGERY", "CORROBORATED_ANOMALIES"):
            scores[IncidentCategory.FAKE_PAYMENT_SCREENSHOT] += 4
            scores[IncidentCategory.SUSPICIOUS_TRANSACTION_EVIDENCE] += 3

    # Fallback / additional rules
    if ("screenshot" in text_lower or "receipt" in text_lower or "payment slip" in text_lower) and ("fake" in text_lower or "forged" in text_lower or "spoofed" in text_lower or "tampered" in text_lower):
        scores[IncidentCategory.FAKE_PAYMENT_SCREENSHOT] += 5
    if "posing as" in text_lower or "fake profile" in text_lower or "using my photo" in text_lower or "using my name" in text_lower or "impersonat" in text_lower:
        scores[IncidentCategory.IMPERSONATION] += 5
    if "sold" in text_lower or "selling" in text_lower or "olx" in text_lower:
        scores[IncidentCategory.ONLINE_MARKETPLACE_FRAUD] += 3
        if "screenshot" in text_lower:
            scores[IncidentCategory.FAKE_PAYMENT_SCREENSHOT] += 3
    if "debited" in text_lower or "deducted" in text_lower or "कट गए" in text_lower:
        scores[IncidentCategory.UNAUTHORIZED_BANK_TRANSACTION] += 2

    best_cat = max(scores, key=lambda k: scores[k])
    confidence = min(0.95, 0.5 + (scores[best_cat] * 0.08)) if scores[best_cat] > 0 else 0.45

    if scores[best_cat] == 0:
        best_cat = IncidentCategory.OTHER_CYBERCRIME
        confidence = 0.5

    # Determine financial impact
    money_loss_keywords = [
        "lost money", "lost ₹", "lost rs", "debited", "deducted", "sent money", "transferred",
        "money is gone", "money gone", "deposited", "deposit", "scammed of", "cheated of",
        "पैसे कट गए", "नुकसान हुआ", "ಖಾತೆಯಿಂದ ಹಣ ಕಡಿತ", "ಹಣ ಕಳೆದುಕೊಂಡೆ", "பணம் போனது",
        "డబ్బులు పోయాయి", "कापले", "টাকা কেটেছে"
    ]
    no_loss_keywords = [
        "did not lose", "no money lost", "didn't send", "didn't give", "haven't lost", "zero loss",
        "zero money", "zero money was received", "no money arrived", "no money received", "no payment received",
        "did not hand over", "didn't hand over", "still have", "not handed over",
        "पैसे नहीं कटे", "कोई नुकसान नहीं", "ಯಾವುದೇ ನಷ್ಟವಿಲ್ಲ", "பணம் போகவில்லை", "డబ్బులు పోలేదు", "काही नुकसान नाही"
    ]
    received_dispute_keywords = ["disputed", "chargeback", "frozen account", "hold"]

    financial_impact = FinancialImpact.UNCERTAIN
    if any(k in text_lower for k in no_loss_keywords):
        financial_impact = FinancialImpact.NO_MONEY_LOST
    elif any(k in text_lower for k in money_loss_keywords):
        financial_impact = FinancialImpact.MONEY_LOST
    elif any(k in text_lower for k in received_dispute_keywords):
        financial_impact = FinancialImpact.RECEIVED_BUT_DISPUTED
    elif best_cat == IncidentCategory.FAKE_PAYMENT_SCREENSHOT and "sold" in text_lower:
        # User sold something but buyer showed fake screenshot
        financial_impact = FinancialImpact.NO_MONEY_LOST if "handed over" not in text_lower else FinancialImpact.MONEY_LOST

    category_labels = {
        IncidentCategory.FAKE_PAYMENT_SCREENSHOT: "Fake Payment Screenshot / Spliced Receipt Allegation",
        IncidentCategory.PAYMENT_FRAUD: "Digital Payment Fraud",
        IncidentCategory.UNAUTHORIZED_BANK_TRANSACTION: "Unauthorized Bank / Account Debit",
        IncidentCategory.UPI_FRAUD: "UPI Collect Request / PIN Manipulation Scam",
        IncidentCategory.QR_CODE_FRAUD: "Fraudulent QR Code 'Scan to Receive' Scam",
        IncidentCategory.IMPERSONATION: "Identity Theft & Authority Impersonation",
        IncidentCategory.IDENTITY_MISUSE: "Misuse of KYC & Personal Identity Documents",
        IncidentCategory.DIGITAL_PAYMENT_DISPUTE: "Digital Payment Technical Dispute / Glitch",
        IncidentCategory.SUSPICIOUS_TRANSACTION_EVIDENCE: "Suspicious Financial Digital Evidence",
        IncidentCategory.ONLINE_MARKETPLACE_FRAUD: "Online Marketplace Buyer/Seller Scam (OLX/Quikr)",
        IncidentCategory.PHISHING_SOCIAL_ENGINEERING: "Phishing / Remote Screen Access Social Engineering",
        IncidentCategory.OTHER_CYBERCRIME: "General Cybercrime Incident",
    }

    return best_cat, financial_impact, category_labels.get(best_cat, "Cyber Incident"), confidence


def determine_urgent_guidance(
    category: IncidentCategory,
    financial_impact: FinancialImpact,
    amount: float | None,
    text: str
) -> tuple[list[str], str]:
    alerts: list[str] = []
    text_lower = text.lower()

    # Differentiate actual financial loss vs fake screenshot with zero money lost
    if financial_impact in (FinancialImpact.MONEY_LOST, FinancialImpact.UNAUTHORIZED_DEBIT) or (amount and amount > 0 and financial_impact != FinancialImpact.NO_MONEY_LOST and financial_impact != FinancialImpact.UNCERTAIN):
        alerts.append("CRITICAL: Dial national cybercrime helpline 1930 immediately or visit cybercrime.gov.in.")
        alerts.append("Contact your bank fraud desk immediately to freeze beneficiary bank accounts within the 'Golden Hour' (first 2-4 hours).")
        pathway = "NATIONAL_CYBER_CRIME_PORTAL"
    elif category in (IncidentCategory.FAKE_PAYMENT_SCREENSHOT, IncidentCategory.ONLINE_MARKETPLACE_FRAUD) or financial_impact == FinancialImpact.NO_MONEY_LOST:
        alerts.append("PRESERVATION NOTICE: Do NOT hand over goods or refund any money without independently checking your bank statement.")
        alerts.append("Preserve original screenshots, uncompressed images, and chat logs for forensic verification.")
        pathway = "BANK_UPI_DISPUTE" if financial_impact == FinancialImpact.RECEIVED_BUT_DISPUTED else "NATIONAL_CYBER_CRIME_PORTAL"
    elif category in (IncidentCategory.PHISHING_SOCIAL_ENGINEERING, IncidentCategory.UPI_FRAUD):
        alerts.append("SECURITY ALERT: If you installed any remote desktop app (AnyDesk, TeamViewer) or entered your UPI PIN, disconnect internet and change your banking credentials immediately.")
        pathway = "NATIONAL_CYBER_CRIME_PORTAL"
    elif category == IncidentCategory.IMPERSONATION:
        alerts.append("PLATFORM ACTION: Report the impersonator profile directly to the platform and preserve message headers/phone numbers.")
        pathway = "PLATFORM_ABUSE"
    else:
        pathway = "NATIONAL_CYBER_CRIME_PORTAL"

    urgent_summary = alerts[0] if alerts else "Preserve all digital evidence and verify transaction records."
    return alerts, pathway


def generate_intelligent_follow_up(
    details: ExtractedIncidentDetails,
    conversation_history: list[str] | None = None
) -> DynamicQuestion | None:
    # Dynamic contextual questioning logic
    # Check 1: Fake screenshot scenario
    if details.incident_category in (IncidentCategory.FAKE_PAYMENT_SCREENSHOT, IncidentCategory.ONLINE_MARKETPLACE_FRAUD):
        if details.financial_impact == FinancialImpact.UNCERTAIN:
            return DynamicQuestion(
                id="q_bank_check",
                question="Did you independently log into your official bank or UPI app to confirm whether the money actually arrived in your account balance?",
                rationale="Determines whether actual financial loss has occurred or if this is an uncompleted fraudulent receipt presentation.",
                field_targeted="financial_impact",
                urgency=QuestionUrgency.URGENT_PROTECTIVE,
                options=[
                    "Yes, I checked my bank and NO money arrived",
                    "No, I only looked at their screenshot",
                    "Yes, money was debited from my account instead",
                    "Yes, money arrived but now account is frozen"
                ],
                suggested_actions=["Open your bank mobile app and check passbook balance directly"]
            )
        if "goods_delivered" not in details.available_evidence and "handover" not in details.narrative_description.lower():
            return DynamicQuestion(
                id="q_goods_handover",
                question="Did you already hand over the goods, phone, or deliver services before realizing the payment was not credited?",
                rationale="Clarifies whether physical goods or digital assets were transferred under false pretenses.",
                field_targeted="goods_handed_over",
                urgency=QuestionUrgency.STANDARD,
                options=[
                    "Yes, I already handed over the item",
                    "No, I still have the item with me",
                    "Services/digital goods were partially delivered"
                ]
            )

    # Check 2: Financial loss without UTR
    if details.financial_impact in (FinancialImpact.MONEY_LOST, FinancialImpact.UNAUTHORIZED_DEBIT):
        if not details.transaction_reference:
            return DynamicQuestion(
                id="q_utr_ref",
                question="Do you have the 12-digit UPI reference number (UTR) or bank transaction ID from your debit SMS or passbook?",
                rationale="The 12-digit UTR is required by police and banks on portal 1930 to trace and freeze the funds in the scammer's bank account.",
                field_targeted="transaction_reference",
                urgency=QuestionUrgency.URGENT_PROTECTIVE,
                options=[
                    "Yes, I have the 12-digit UTR from the SMS/app",
                    "I have the debit SMS but need to locate the UTR",
                    "No UTR visible yet, transaction is still pending"
                ]
            )
        if not details.suspected_vpa and not details.suspected_phone:
            return DynamicQuestion(
                id="q_suspect_contact",
                question="What is the UPI ID (VPA), phone number, or account details of the person or entity who sent or requested the payment?",
                rationale="Essential for identifying beneficiary accounts and freezing the fraudulent trail.",
                field_targeted="suspected_person_or_entity",
                urgency=QuestionUrgency.STANDARD,
                options=[
                    "I have their UPI ID / VPA (e.g., name@bank)",
                    "I have their mobile phone number",
                    "I have their bank account and IFSC",
                    "I only have their social media / marketplace profile"
                ]
            )

    # Check 3: Check missing bank/PSP provider
    if not details.bank_or_upi_provider:
        return DynamicQuestion(
            id="q_psp_provider",
            question="Which bank or payment app did this transaction involve (e.g. Google Pay, PhonePe, Paytm, SBI, HDFC)?",
            rationale="Identifies the appropriate grievance redressal desk and Payment Service Provider (PSP) nodal authority.",
            field_targeted="bank_or_upi_provider",
            urgency=QuestionUrgency.STANDARD,
            options=["Google Pay", "PhonePe", "Paytm", "BHIM", "State Bank of India (SBI)", "HDFC Bank", "ICICI Bank", "Other"]
        )

    # Check 4: Check communication channel
    if not details.communication_channel:
        return DynamicQuestion(
            id="q_comm_channel",
            question="Through which platform or app did the person communicate with you (e.g. WhatsApp, Telegram, Phone Call, OLX)?",
            rationale="Enables cyber forensic investigators to serve Section 91 notices and preserve digital chat evidence.",
            field_targeted="communication_channel",
            urgency=QuestionUrgency.STANDARD,
            options=["WhatsApp", "Telegram", "Phone Call", "SMS", "OLX", "Instagram", "Other"]
        )

    # All major fields answered
    return None


def parse_and_understand_incident(
    user_text: str,
    language: str = "en",
    existing_details: dict[str, Any] | None = None,
    attached_forensic_report: dict[str, Any] | None = None
) -> UnderstandIncidentResponse:
    # 1. Classification & Impact
    cat, impact, cat_label, conf = classify_incident_and_impact(user_text, attached_forensic_report)

    # 2. Extract Entities
    amount, currency = extract_financial_amount(user_text)
    utr = extract_utr_or_reference(user_text)
    vpa = extract_vpa(user_text)
    phone = extract_phone(user_text)
    bank_psp = extract_bank_or_psp(user_text)
    channel = extract_communication_channel(user_text)

    # Check date patterns (e.g., today, yesterday, 12 Nov, 12/11/2026)
    date_val = None
    time_val = None
    user_text_lower = user_text.lower()
    if "today" in user_text_lower or "आज" in user_text_lower or "ಇಂದು" in user_text_lower:
        date_val = datetime.now().strftime("%Y-%m-%d")
    elif "yesterday" in user_text_lower or "कल" in user_text_lower or "ನಿನ್ನೆ" in user_text_lower:
        from datetime import timedelta
        date_val = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    time_match = re.search(r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|hours|hrs)?)\b", user_text, re.IGNORECASE)
    if time_match:
        time_val = time_match.group(1)

    # Merge with existing details if provided
    merged = existing_details.copy() if existing_details else {}

    cat_to_use = cat if merged.get("incident_category") is None else IncidentCategory(merged["incident_category"])
    cat_label_to_use = cat_label if merged.get("incident_category_label") is None else merged["incident_category_label"]
    impact_to_use = impact if merged.get("financial_impact") is None else FinancialImpact(merged["financial_impact"])

    final_amount = amount if amount is not None else merged.get("financial_loss_amount")
    final_utr = utr if utr is not None else merged.get("transaction_reference")
    final_vpa = vpa if vpa is not None else merged.get("suspected_vpa")
    final_phone = phone if phone is not None else merged.get("suspected_phone")
    final_bank = bank_psp if bank_psp is not None else merged.get("bank_or_upi_provider")
    final_channel = channel if channel is not None else merged.get("communication_channel")
    final_date = date_val if date_val is not None else merged.get("incident_date", datetime.now().strftime("%Y-%m-%d"))
    final_time = time_val if time_val is not None else merged.get("approximate_time")

    # Available evidence checklist
    available_evidence = merged.get("available_evidence", [])
    if attached_forensic_report:
        if "VeriSight Forensic Screenshot Analysis" not in available_evidence:
            available_evidence.append("VeriSight Forensic Screenshot Analysis")
    if "screenshot" in user_text_lower or "रसीद" in user_text_lower:
        if "Digital Payment Screenshot" not in available_evidence:
            available_evidence.append("Digital Payment Screenshot")
    if final_channel:
        chat_item = f"{final_channel} Chat History & Export"
        if chat_item not in available_evidence:
            available_evidence.append(chat_item)
    if final_amount and final_amount > 0:
        if "Bank Account Debit Statement" not in available_evidence:
            available_evidence.append("Bank Account Debit Statement")

    # Urgent guidance
    urgent_alerts, rec_pathway = determine_urgent_guidance(cat_to_use, impact_to_use, final_amount, user_text)

    # Missing fields audit
    missing: list[str] = []
    if final_amount is None and impact_to_use != FinancialImpact.NO_MONEY_LOST:
        missing.append("financial_loss_amount")
    if not final_utr:
        missing.append("transaction_reference")
    if not final_bank:
        missing.append("bank_or_upi_provider")
    if not final_vpa and not final_phone:
        missing.append("suspected_entity_identifier")
    if not final_channel:
        missing.append("communication_channel")

    details = ExtractedIncidentDetails(
        incident_category=cat_to_use,
        incident_category_label=cat_label_to_use,
        financial_impact=impact_to_use,
        incident_date=final_date,
        approximate_time=final_time,
        financial_loss_amount=final_amount,
        currency=currency,
        payment_method="UPI / Digital Payment",
        bank_or_upi_provider=final_bank,
        transaction_reference=final_utr,
        suspected_person_or_entity=merged.get("suspected_person_or_entity"),
        suspected_vpa=final_vpa,
        suspected_phone=final_phone,
        complainant_name=merged.get("complainant_name", "Complainant"),
        complainant_contact=merged.get("complainant_contact"),
        communication_channel=final_channel,
        narrative_description=user_text.strip(),
        available_evidence=available_evidence,
        is_ongoing=merged.get("is_ongoing", False),
        account_at_risk=merged.get("account_at_risk", False),
        missing_fields=missing,
        confidence_score=conf,
        urgent_guidance=urgent_alerts[0] if urgent_alerts else None,
        recommended_pathway=rec_pathway
    )

    next_q = generate_intelligent_follow_up(details)

    rationale = f"Classified as '{cat_label_to_use}' with {impact_to_use.value} status based on stated statements, payment entities, and forensic context."

    return UnderstandIncidentResponse(
        extracted_details=details,
        original_text=user_text,
        language=language,
        urgent_alerts=urgent_alerts,
        next_question=next_q,
        classification_rationale=rationale
    )
