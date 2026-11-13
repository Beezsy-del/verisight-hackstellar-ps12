import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_scenario_1_fake_payment_screenshot():
    """
    Scenario 1: Fake payment screenshot.
    A seller receives a screenshot claiming payment was completed but receives no money.
    """
    payload = {
        "user_text": "I was selling my second hand DSLR camera on OLX. A buyer named Vicky messaged on WhatsApp, showed a fake Google Pay screenshot of ₹32,000 with UTR 481920394812, but when I opened my HDFC mobile banking app, zero money was received. I did not hand over the camera yet.",
        "language": "en",
        "attached_forensic_summary": {
            "file_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "filename": "camera_payment_gpay.png",
            "overall_tamper_score": 93.4,
            "verdict": "MANIPULATED_FORGERY",
            "findings": [
                {"id": "f1", "layer": 2, "title": "Baseline Laser Drop", "severity": "CRITICAL", "metric_name": "Drift", "metric_value": "+3.4px"}
            ]
        }
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]

    # Verify category
    assert details["incident_category"] in ("FAKE_PAYMENT_SCREENSHOT", "ONLINE_MARKETPLACE_FRAUD")
    assert details["financial_loss_amount"] == 32000.0
    assert details["financial_impact"] == "NO_MONEY_LOST"
    assert details["transaction_reference"] == "481920394812"
    assert details["communication_channel"] == "WhatsApp"
    assert any("Preserve" in a or "hand over" in a for a in data["urgent_alerts"])

    # Generate complaint
    comp_res = client.post("/api/response/generate-complaint", json={
        "details": details,
        "authority_destination": "NATIONAL_CYBER_CRIME_PORTAL",
        "language": "en"
    })
    assert comp_res.status_code == 200
    comp = comp_res.json()
    assert "FORMAL CYBERCRIME" in comp["title"]
    assert "₹32,000" in comp["chronological_narrative"] or "32000" in comp["chronological_narrative"]


def test_scenario_2_financial_cyber_fraud():
    """
    Scenario 2: Actual financial cyber fraud.
    A person transfers money to a scammer.
    """
    payload = {
        "user_text": "I was deceived by an investment group on Telegram. They asked me to deposit ₹50,000 to merchant@icici with UTR 412093849102 promising high returns, and now they blocked me and my money is gone.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]

    assert details["financial_loss_amount"] == 50000.0
    assert details["financial_impact"] == "MONEY_LOST"
    assert details["transaction_reference"] == "412093849102"
    assert details["suspected_vpa"] == "merchant@icici"
    assert details["communication_channel"] == "Telegram"

    # Must immediately display urgent 1930 helpline guidance
    assert any("1930" in a for a in data["urgent_alerts"])
    assert any("Golden Hour" in a for a in data["urgent_alerts"])


def test_scenario_3_unauthorized_transaction():
    """
    Scenario 3: Unauthorized transaction.
    A person notices an unauthorized debit.
    """
    payload = {
        "user_text": "Unauthorized transaction on my State Bank of India account. ₹12,500 was debited at 3:15 AM without any OTP or alert. Reference number 409182374612.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]

    assert details["incident_category"] == "UNAUTHORIZED_BANK_TRANSACTION"
    assert details["financial_loss_amount"] == 12500.0
    assert details["bank_or_upi_provider"] == "State Bank of India (SBI)"
    assert details["transaction_reference"] == "409182374612"
    assert details["financial_impact"] in ("MONEY_LOST", "UNAUTHORIZED_DEBIT")
    assert any("1930" in a for a in data["urgent_alerts"])


def test_scenario_4_impersonation():
    """
    Scenario 4: Impersonation.
    Someone creates a fake account or poses as authority using another's identity.
    """
    payload = {
        "user_text": "Someone is posing as an army officer on Facebook and OLX using my photo and name to sell fake goods and scam people.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]

    assert details["incident_category"] in ("IMPERSONATION", "ONLINE_MARKETPLACE_FRAUD")
    assert details["recommended_pathway"] in ("PLATFORM_ABUSE", "NATIONAL_CYBER_CRIME_PORTAL")


def test_scenario_5_incomplete_voice_description():
    """
    Scenario 5: Incomplete voice description.
    A person provides a vague or incomplete explanation.
    """
    payload = {
        "user_text": "Someone showed me a receipt for something, not sure what happened.",
        "language": "en"
    }
    res = client.post("/api/response/understand", json=payload)
    assert res.status_code == 200
    data = res.json()
    details = data["extracted_details"]

    # Must extract what is known, not invent missing fields
    assert details["financial_loss_amount"] is None
    assert details["transaction_reference"] is None
    assert "transaction_reference" in details["missing_fields"]

    # Must generate an intelligent targeted follow-up question
    assert data["next_question"] is not None
    assert len(data["next_question"]["question"]) > 10
