import { IncidentCategory } from "../types/response";

export interface RealWorldFraudCase {
  id: string;
  headline: string;
  shortHeadline?: string;
  city: string;
  state: string;
  incidentMonthYear: string;
  scamCategory: string;
  categoryCode: IncidentCategory;
  reportedLoss: string;
  numericLoss?: number;
  summary: string;
  modusOperandi: string[];
  warningSigns: string[];
  preventionInsight: string;
  verisightRelevance: {
    forensicLayer: string;
    examination: string;
    userGuidance: string;
    responseFeature: string;
  };
  publisher: string;
  sourceUrl: string;
  sourceDate: string;
  mapCoordinates: { x: number; y: number };
  imageUrl: string;
  imageAlt: string;
  illustrationType: "digital-arrest" | "ipo-forgery" | "fake-gpay" | "reverse-qr" | "marketplace" | "soundbox" | "double-debit";
  accentColor: string;
}

export const REAL_WORLD_CASES: RealWorldFraudCase[] = [
  {
    id: "case-delhi-fake-gpay",
    headline: "Delhi man duped with fake UPI payment screenshot",
    shortHeadline: "Delhi man duped with fake UPI payment screenshot",
    city: "New Delhi",
    state: "Delhi",
    incidentMonthYear: "Aug 2026",
    scamCategory: "Fake UPI Screenshot Fraud",
    categoryCode: "FAKE_PAYMENT_SCREENSHOT",
    reportedLoss: "₹30.81 Lakh",
    numericLoss: 3081000,
    summary:
      "A fraudster allegedly showed a forged UPI payment confirmation to extort money from the victim. The perpetrator displayed a pixel-perfect payment success animation matching the merchant's exact VPA with simulated audio chime, claiming bank network latency was delaying SMS alerts.",
    modusOperandi: [
      "Buyer agreed to purchase high-value merchandise and scanned the retailer's merchant QR code.",
      "Instead of authorizing payment via official UPI apps, the fraudster opened a counterfeit generator APK ('Spoof Pay').",
      "The app rendered a pixel-perfect payment success animation matching the merchant's exact VPA with simulated audio chime.",
      "The fraudster displayed the screen for 5 seconds and hurried away, claiming bank network latency was delaying SMS alerts."
    ],
    warningSigns: [
      "Customer insisting on immediate handover of goods based on their own smartphone display without waiting for bank confirmation.",
      "Inconsistent font baseline alignment and non-native kerning on the amount text (e.g. ₹30.81 Lakh).",
      "Device clock in the screenshot header conflicting with the stated transaction timestamp."
    ],
    preventionInsight:
      "Always verify payment in your bank account, not just a screenshot.",
    verisightRelevance: {
      forensicLayer: "Layer 3: Sub-Pixel Laser Drift & Layer 4: Calibrated GBDT Risk Scoring",
      examination:
        "Detects a +3.8px vertical baseline drop on modified numbers and high-pass wavelet voids where synthetic text was rendered over clean background canvas.",
      userGuidance:
        "Instantly inspect suspicious screenshots: genuine receipts exhibit uniform camera/device sensor noise that synthetic APK generators cannot replicate.",
      responseFeature:
        "One-click Section 94 BNSS statutory summons notice ready to serve on the mobile network provider and IMEI tracking division."
    },
    publisher: "Hindustan Times",
    sourceUrl: "https://www.hindustantimes.com/cities/delhi-news",
    sourceDate: "August 12, 2026",
    mapCoordinates: { x: 147.9, y: 148.9 },
    imageUrl: "/images/cases/delhi-upi-phone.jpg",
    imageAlt: "Smartphone displaying fake UPI payment confirmation screen in New Delhi incident",
    illustrationType: "fake-gpay",
    accentColor: "#ef4444",
  },
  {
    id: "case-bengaluru-reverse-qr",
    headline: "Fake QR code fraud in Bengaluru",
    shortHeadline: "Fake QR code fraud in Bengaluru",
    city: "Bengaluru",
    state: "Karnataka",
    incidentMonthYear: "Jul 2026",
    scamCategory: "Deceptive QR Code Siphon",
    categoryCode: "QR_CODE_FRAUD",
    reportedLoss: "₹2.16 Cr",
    numericLoss: 21600000,
    summary:
      "Scammers used QR code to siphon funds from victim after initiating fake corporate advance orders. The victim was tricked into scanning a deceptive 'instant credit' QR code which was actually an outgoing collect debit request.",
    modusOperandi: [
      "Fraudster initiated contact via WhatsApp professing to place bulk corporate orders with advance deposits.",
      "Sent a doctored payment authorization QR code claiming: 'Scan this code to receive advance payment of ₹2.16 Cr into your linked account.'",
      "The QR was encoded as an outgoing UPI collect request rather than a payment address.",
      "When the victim scanned the code, the UPI app displayed an authorization prompt which the victim approved with their UPI PIN."
    ],
    warningSigns: [
      "Any statement or instruction claiming that entering your UPI PIN is necessary to receive or accept funds.",
      "QR codes received via chat with labels like 'Scan to Credit' or 'Cashback Receive Authorization'.",
      "UPI authorization prompts stating 'Pay' or 'Deduct' when you expect to receive money."
    ],
    preventionInsight:
      "Check the UPI ID before scanning.",
    verisightRelevance: {
      forensicLayer: "Layer 4: Protocol Semantic Consistency & Response Triage",
      examination:
        "Identifies malicious collect request payloads encoded inside innocent-looking promotional QR codes and highlights unauthorized debit protocols.",
      userGuidance:
        "Immediately distinguish between UPI Pay and Collect protocols. VeriSight Response provides clear, step-by-step visual guidance.",
      responseFeature:
        "Direct UPI reversal complaint generation for NPCI Dispute Resolution Mechanism (DRM) and bank grievance ombudsman escalation."
    },
    publisher: "Times of India",
    sourceUrl: "https://timesofindia.indiatimes.com/city/bengaluru",
    sourceDate: "July 20, 2026",
    mapCoordinates: { x: 146.1, y: 389.9 },
    imageUrl: "/images/cases/bengaluru-qr-scan.jpg",
    imageAlt: "Smartphone scanning malicious QR code in Bengaluru payment trap",
    illustrationType: "reverse-qr",
    accentColor: "#10b981",
  },
  {
    id: "case-mumbai-olx-military",
    headline: "Fake payment leads to loss",
    shortHeadline: "Fake payment leads to loss",
    city: "Mumbai",
    state: "Maharashtra",
    incidentMonthYear: "Jun 2026",
    scamCategory: "Marketplace & Spliced Transfer Slip",
    categoryCode: "ONLINE_MARKETPLACE_FRAUD",
    reportedLoss: "₹18,000",
    numericLoss: 18000,
    summary:
      "A seller was cheated with a fake UPI receipt. The scammer sent fabricated NEFT bank transfer screenshots and stolen identification cards, tricking the seller into parting with goods before payment confirmation arrived.",
    modusOperandi: [
      "Scammer contacted seller immediately after an online classified listing went live, agreeing to purchase items without negotiation.",
      "Shared stolen and doctored photographs of an official identification card and bank transfer receipt to foster credibility.",
      "Sent manipulated payment receipts showing funds had supposedly been sent via 'Army Welfare Fund Transfer'.",
      "Claimed that military transactions require the seller to send a matching deposit via UPI to verify civilian account compatibility."
    ],
    warningSigns: [
      "Buyers overly eager to prove their identity by immediately sending military cards without being asked.",
      "Refusal to meet in person or inspect goods physically prior to purchase.",
      "Demands for refundable 'registration fees' or 'verification charges' before payment can clear."
    ],
    preventionInsight:
      "Verify receipt with your bank.",
    verisightRelevance: {
      forensicLayer: "Layer 1: Multi-Spectral ELA & Layer 2: Copy-Move Feature Clustering",
      examination:
        "Pinpoints pasted headshots on military ID credentials with boundary quantization anomalies and reveals cloned text blocks on bank transfer receipts.",
      userGuidance:
        "Check image compression boundaries before accepting identification documents sent over social media or marketplace chats.",
      responseFeature:
        "Comprehensive formal cybercrime complaint draft with attached forensic dossier and OLX platform grievance takedown escalation."
    },
    publisher: "The Indian Express",
    sourceUrl: "https://indianexpress.com/article/cities/mumbai",
    sourceDate: "June 05, 2026",
    mapCoordinates: { x: 81.3, y: 293.0 },
    imageUrl: "/images/cases/mumbai-payment-app.jpg",
    imageAlt: "Smartphone showing payment transaction receipt in Mumbai marketplace incident",
    illustrationType: "marketplace",
    accentColor: "#38bdf8",
  },
  {
    id: "case-pune-ipo-forgery",
    headline: "Senior citizen defrauded of ₹6.80 Cr in fake institutional IPO allotment with forged vouchers",
    shortHeadline: "Fake institutional allotment vouchers",
    city: "Pune",
    state: "Maharashtra",
    incidentMonthYear: "Nov 2024",
    scamCategory: "Forged Institutional Banking Vouchers",
    categoryCode: "PAYMENT_FRAUD",
    reportedLoss: "₹6.80 Cr",
    numericLoss: 68000000,
    summary:
      "A retired corporate engineer in Pune lost ₹6.80 crore over three months after fraudsters provided manipulated bank deposit receipts, fake SEBI allotment vouchers, and fabricated trading dashboards displaying multi-crore returns.",
    modusOperandi: [
      "Victim was added to an elite investment advisory group purportedly managed by a recognized institutional asset management firm.",
      "The syndicate shared doctored institutional allotment letters and manipulated banking transaction receipts showing large-scale equity purchases.",
      "Victim deposited funds into 14 distinct mule current accounts, with fraudsters sending back falsified bank acknowledgement vouchers.",
      "When the victim attempted to withdraw his balance, fraudsters demanded an additional 20% in 'capital gains tax' before freezing communication."
    ],
    warningSigns: [
      "Promises of guaranteed 500%+ returns and exclusive institutional pre-IPO share allocations via WhatsApp.",
      "Payment instructions requiring transfers into commercial mule accounts rather than official SEBI-registered ASBA facilities.",
      "Presentation of high-contrast bank vouchers with missing or non-standard 12-digit UTR sequences."
    ],
    preventionInsight:
      "All legitimate IPO and equity applications in India are strictly processed via SEBI-mandated ASBA within your own bank.",
    verisightRelevance: {
      forensicLayer: "Layer 1: Error Level Analysis & Layer 2: Wavelet Residual Discontinuities",
      examination:
        "Exposes cloned transaction digits, artificial Gaussian smoothing around institutional logos, and mismatched quantization matrices on the fake banking vouchers.",
      userGuidance:
        "Examine banking voucher PDF/image metadata: authentic institutional receipts carry cryptographic timestamp signatures and genuine bank header hashes.",
      responseFeature:
        "Automated RBI CMS & Cyber Police formal complaint builder with chronological financial ledger breakdown across all 14 beneficiary accounts."
    },
    publisher: "The Indian Express",
    sourceUrl: "https://indianexpress.com/article/cities/pune/pune-cyber-crime-senior-citizen-cheated-of-over-rs-6-80-crore-in-online-share-trading-fraud-9669528/",
    sourceDate: "November 14, 2024",
    mapCoordinates: { x: 94.9, y: 302.4 },
    imageUrl: "/images/cases/pune-trading-voucher.jpg",
    imageAlt: "Institutional banking vouchers and investment portal displayed on tablet in Pune case",
    illustrationType: "ipo-forgery",
    accentColor: "#f59e0b",
  },
  {
    id: "case-hyderabad-reverse-qr",
    headline: "Hyderabad Merchant Loses ₹42,000 After Scanning 'Payment Receive' QR Code Sent on WhatsApp",
    shortHeadline: "Merchant tricked by reverse QR code",
    city: "Hyderabad",
    state: "Telangana",
    incidentMonthYear: "Mar 2024",
    scamCategory: "QR Code 'Scan to Receive' & Collect Request Trap",
    categoryCode: "QR_CODE_FRAUD",
    reportedLoss: "₹42,000",
    numericLoss: 42000,
    summary:
      "A boutique clothing designer in Jubilee Hills received a bulk order over WhatsApp. The buyer claimed corporate protocol required the merchant to scan a customized 'Instant Credit QR' to receive the ₹42,000 advance.",
    modusOperandi: [
      "Fraudster initiated contact via WhatsApp professing to buy corporate gifting apparel in bulk.",
      "Sent a doctored payment authorization QR code claiming: 'Scan this code to receive advance payment of ₹42,000 into your linked account.'",
      "The QR was encoded as an outgoing UPI collect request rather than a payment address.",
      "When the victim scanned the code, the UPI app displayed an authorization prompt which the merchant approved with her UPI PIN."
    ],
    warningSigns: [
      "Any statement or instruction claiming that entering your UPI PIN is necessary to receive or accept funds.",
      "QR codes received via chat with labels like 'Scan to Credit' or 'Cashback Receive Authorization'.",
      "UPI authorization prompts stating 'Pay' or 'Deduct' when you expect to receive money."
    ],
    preventionInsight:
      "A UPI PIN is used EXCLUSIVELY to debit money from your account. Receiving money never requires a PIN.",
    verisightRelevance: {
      forensicLayer: "Layer 4: Protocol Semantic Consistency & Response Triage",
      examination:
        "Identifies malicious collect request payloads encoded inside innocent-looking promotional QR codes and highlights unauthorized debit protocols.",
      userGuidance:
        "Immediately distinguish between UPI Pay and Collect protocols. VeriSight Response provides clear, step-by-step visual guidance.",
      responseFeature:
        "Direct UPI reversal complaint generation for NPCI Dispute Resolution Mechanism (DRM) and bank grievance ombudsman escalation."
    },
    publisher: "The Hindu & Cyberabad Police",
    sourceUrl: "https://www.thehindu.com/news/cities/Hyderabad/cyber-fraudsters-dupe-city-resident-of-money-using-qr-code/article67954120.ece",
    sourceDate: "March 15, 2024",
    mapCoordinates: { x: 160.9, y: 322.4 },
    imageUrl: "/images/cases/hyderabad-qr-terminal.jpg",
    imageAlt: "Payment terminal and QR code in retail outlet in Hyderabad incident",
    illustrationType: "reverse-qr",
    accentColor: "#a855f7",
  },
  {
    id: "case-jaipur-fake-soundbox",
    headline: "Jaipur wholesaler defrauded of ₹3.50 Lakh via muted soundbox & counterfeit audio alert",
    shortHeadline: "Wholesaler duped via spoofed audio alert",
    city: "Jaipur",
    state: "Rajasthan",
    incidentMonthYear: "Feb 2024",
    scamCategory: "Fabricated Merchant Audio Alert & Spliced Receipt",
    categoryCode: "PAYMENT_FRAUD",
    reportedLoss: "₹3.50 Lakh",
    numericLoss: 350000,
    summary:
      "A fabric wholesaler in Jaipur was targeted during rush hours when repeat buyers displayed counterfeit payment screenshots for ₹3.50 lakh. The perpetrators synchronized a portable Bluetooth speaker mimicking the chime of an official merchant soundbox.",
    modusOperandi: [
      "Perpetrators operated during crowded evening trading hours when the store experienced high counter volume.",
      "One accomplice positioned a small portable Bluetooth speaker near the store's soundbox while another initiated a bogus transfer.",
      "Fraudster played an authentic-sounding audio file announcing payment confirmation.",
      "Presented a doctored mobile receipt showing identical timestamp and retailer business name."
    ],
    warningSigns: [
      "Audio alert does not correlate with a new transaction logged in the official merchant application on the shopkeeper's phone.",
      "Transaction UTR number is either missing or contains fewer than 12 digits.",
      "Buyer creating intentional distractions during peak trading hours to bypass verification."
    ],
    preventionInsight:
      "Never rely exclusively on audio announcements. Reconcile transactions against real-time banking settlement records.",
    verisightRelevance: {
      forensicLayer: "Layer 3: Typographic Kerning & Viewport Aspect Ratio Inspection",
      examination:
        "Highlights cropped viewport coordinates (non-native screen dimensions) and irregular font kerning in the transaction confirmation banner.",
      userGuidance:
        "Examine the 12-digit UTR: genuine banking UTRs follow strict alphanumeric format and checksum standards.",
      responseFeature:
        "Section 94 BNSS statutory summons generation and cyber cell evidence preservation package."
    },
    publisher: "Dainik Bhaskar & Rajasthan Cyber Police",
    sourceUrl: "https://www.bhaskar.com/local/rajasthan/jaipur/news/fake-payment-app-sound-box-fraud-jaipur-police-investigation-132649021.html",
    sourceDate: "February 28, 2024",
    mapCoordinates: { x: 127.7, y: 174.3 },
    imageUrl: "/images/cases/jaipur-counter-retail.jpg",
    imageAlt: "Retail counter with payment soundbox and ledger in Jaipur wholesale market",
    illustrationType: "soundbox",
    accentColor: "#f97316",
  },
  {
    id: "case-chennai-double-debit",
    headline: "Chennai professional siphoned of ₹18,500 in 'failed transaction refund' phishing trap",
    shortHeadline: "Techie loses ₹18,500 in fake refund trap",
    city: "Chennai",
    state: "Tamil Nadu",
    incidentMonthYear: "Aug 2024",
    scamCategory: "Manipulated Payment Declined Screen & Phishing Trap",
    categoryCode: "PHISHING_SOCIAL_ENGINEERING",
    reportedLoss: "₹18,500",
    numericLoss: 18500,
    summary:
      "Following a failed food delivery payment of ₹450, a Chennai IT consultant sought assistance online and dialed a spoofed customer care number from Google Maps. The cybercriminal sent an altered 'Payment Declined' screenshot via WhatsApp with an embedded reverse-link, draining ₹18,500.",
    modusOperandi: [
      "Victim encountered a legitimate transaction error and searched online for customer support contact information.",
      "Called a fraudulently indexed mobile number appearing on search engine business listings.",
      "Fraudster sent an altered screenshot showing 'Transaction Failed — Tap to Claim Instant Refund' with a spoofed bank link.",
      "Victim tapped the link and entered net banking credentials, allowing fraudsters to execute unauthorized debits."
    ],
    warningSigns: [
      "Customer helpline phone numbers displayed as personal 10-digit mobile numbers (+91-9... or +91-7...).",
      "Customer support representatives asking users to download third-party APKs or tap external WhatsApp links for refunds.",
      "Screenshots of error messages sent from external phone numbers containing embedded URLs."
    ],
    preventionInsight:
      "Commercial banks and payment apps never maintain customer service over direct WhatsApp chats or personal mobile numbers.",
    verisightRelevance: {
      forensicLayer: "Voice Reporting Assistant & NLU Entity Extraction",
      examination:
        "Speech AI accurately parses the user's spoken narrative, extracts the UTR, bank name, and fake support phone number, and alerts the user to 1930 golden-hour freezing.",
      userGuidance:
        "Document the call logs, SMS headers, and fake screenshot. Preserve raw digital evidence without forwarding through compression channels.",
      responseFeature:
        "Formal Cybercrime 1930 incident report and RBI Integrated Ombudsman complaint PDF ready for immediate export."
    },
    publisher: "The New Indian Express",
    sourceUrl: "https://www.newindianexpress.com/cities/chennai/2024/Aug/14/chennai-techie-loses-money-after-calling-fake-customer-care-number-2735128.html",
    sourceDate: "August 14, 2024",
    mapCoordinates: { x: 185.9, y: 389.1 },
    imageUrl: "/images/cases/chennai-phone-error.jpg",
    imageAlt: "Smartphone displaying transaction declined error message in Chennai phishing incident",
    illustrationType: "double-debit",
    accentColor: "#06b6d4",
  },
];
