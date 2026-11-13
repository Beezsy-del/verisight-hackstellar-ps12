import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_reporting_directory():
    res = client.get("/api/response/reporting-directory")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    # Verify NCRP is present
    ids = [d["id"] for d in data]
    assert "ncrp-1930" in ids
    assert "bank-upi-psp" in ids
    assert "rbi-cms-ombudsman" in ids


def test_reporting_directory_filter():
    res = client.get("/api/response/reporting-directory?category=BANK_UPI")
    assert res.status_code == 200
    data = res.json()
    assert all(d["category"] == "BANK_UPI" for d in data)


def test_understand_fake_screenshot_scenario():
    payload = {
        "user_text": "I sold a phone on OLX and the buyer showed me a screenshot saying they paid ₹18,000 via Google Pay, but no money arrived in my bank.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]
    assert details["incident_category"] in ("FAKE_PAYMENT_SCREENSHOT", "ONLINE_MARKETPLACE_FRAUD")
    assert details["financial_loss_amount"] == 18000.0
    assert details["bank_or_upi_provider"] == "Google Pay"
    assert data["next_question"] is not None
    assert len(data["urgent_alerts"]) > 0


def test_understand_unauthorized_debit_scenario():
    payload = {
        "user_text": "₹25,000 debited from my SBI account without OTP. The message had UTR 403218942311 and went to fraudster@paytm.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]
    assert details["incident_category"] == "UNAUTHORIZED_BANK_TRANSACTION"
    assert details["financial_loss_amount"] == 25000.0
    assert details["transaction_reference"] == "403218942311"
    assert details["suspected_vpa"] == "fraudster@paytm"
    assert details["bank_or_upi_provider"] == "State Bank of India (SBI)"
    assert details["financial_impact"] in ("MONEY_LOST", "UNAUTHORIZED_DEBIT")
    # Immediate 1930 guidance must be present
    assert any("1930" in a for a in data["urgent_alerts"])


def test_multilingual_hindi_understanding():
    payload = {
        "user_text": "ओएलएक्स पर फोन बेचा, खरीदार ने गूगल पे पर 15000 का नकली स्क्रीनशॉट भेजा, पैसे नहीं आए।",
        "language": "hi"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]
    assert details["financial_loss_amount"] == 15000.0
    assert details["bank_or_upi_provider"] == "Google Pay"
    assert details["incident_category"] in ("FAKE_PAYMENT_SCREENSHOT", "ONLINE_MARKETPLACE_FRAUD")


def test_generate_complaint_and_pdf():
    understand_res = client.post("/api/response/understand", json={
        "user_text": "Sold laptop on OLX, buyer sent fake receipt of ₹45,000 via PhonePe with UTR 492019283712 to user@ybl. No money credited.",
        "language": "en"
    })
    assert understand_res.status_code == 200
    details = understand_res.json()["extracted_details"]

    complaint_res = client.post("/api/response/generate-complaint", json={
        "details": details,
        "authority_destination": "NATIONAL_CYBER_CRIME_PORTAL",
        "language": "en"
    })
    assert complaint_res.status_code == 200
    complaint = complaint_res.json()
    assert "FORMAL CYBERCRIME" in complaint["title"]
    assert complaint["transaction_reference"] == "492019283712"
    assert "₹45,000" in complaint["chronological_narrative"] or "45000" in complaint["chronological_narrative"]
    assert len(complaint["supporting_document_index"]) >= 3

    # Export PDF test
    pdf_res = client.post("/api/response/export-complaint-pdf", json=complaint)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Valid non-empty PDF


def test_cases_store_endpoints(tmp_path, monkeypatch):
    from app.services.response import case_store
    monkeypatch.setattr(case_store, "STORE_FILE", tmp_path / "cases.sqlite3")
    # List cases
    res = client.get("/api/response/cases")
    assert res.status_code == 200
    cases = res.json()
    assert cases == []
    details = client.post("/api/response/understand", json={"user_text":"I received a suspicious payment screenshot."}).json()["extracted_details"]
    created = client.post("/api/response/cases/create", json={"details":details}).json()
    case_id = created["case_id"]
    single_res = client.get(f"/api/response/cases/{case_id}")
    assert single_res.status_code == 200
    assert single_res.json()["case_id"] == case_id


def test_transcribe_audio_endpoint():
    # Test valid audio upload
    dummy_wav = b"RIFF" + b"\x00" * 40 + b"DATA" + b"\x01\x02\x03\x04" * 100
    files = {"file": ("recording.wav", dummy_wav, "audio/wav")}
    data = {"language": "en-IN"}
    res = client.post("/api/response/transcribe-audio", files=files, data=data)
    assert res.status_code == 501
    assert "transcript" not in res.json()

    # Test empty audio upload
    empty_files = {"file": ("empty.wav", b"", "audio/wav")}
    res_empty = client.post("/api/response/transcribe-audio", files=empty_files, data=data)
    assert res_empty.status_code == 400
