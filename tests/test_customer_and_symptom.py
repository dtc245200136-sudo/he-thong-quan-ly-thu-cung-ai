import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app
from backend.services.ai_service import AIService

client = TestClient(app)

def test_ai_symptom_checker_emergency():
    res = AIService.check_symptoms(
        species="Chó",
        breed="Poodle",
        symptoms=["co giật", "sùi bọt mép"],
        symptom_description="Bé ăn nhầm bả thuốc chuột ngoài sân",
        duration="30 phút"
    )
    assert res["risk_level"] == "EMERGENCY"
    assert res["risk_color"] == "red"
    assert res["should_see_vet"] is True
    assert len(res["first_aid_and_care"]) > 0

def test_ai_symptom_checker_medium_risk():
    res = AIService.check_symptoms(
        species="Mèo",
        breed="Mèo Anh",
        symptoms=["ngứa", "gãi nhiều", "rụng lông"],
        symptom_description="Bé gãi tai liên tục, da có vảy gàu",
        duration="3 ngày"
    )
    assert res["risk_level"] == "MEDIUM"
    assert len(res["recommended_services"]) > 0

def test_api_symptom_checker_endpoint():
    response = client.post("/api/v1/ai/symptom-checker", json={
        "species": "Chó",
        "breed": "Corgi",
        "symptoms": ["ngứa da"],
        "symptom_description": "Lông hơi xơ rối và rụng lông nhẹ",
        "duration": "1 tuần"
    })
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data
    assert "recommended_services" in data

def test_customer_lookup_and_booking():
    # 1. Lookup phone 0912345678 (seeded owner)
    lookup_res = client.get("/api/v1/customer/lookup?phone=0912345678")
    assert lookup_res.status_code == 200
    data = lookup_res.json()
    assert "owner" in data
    assert "loyalty" in data["owner"]
    assert "pets" in data
    assert len(data["pets"]) > 0

    # 2. Book appointment online
    booking_time = (datetime.now() + timedelta(days=2)).replace(microsecond=0).isoformat()
    book_res = client.post("/api/v1/customer/book-appointment", json={
        "owner_name": "Nguyễn Thị Thảo",
        "phone": "0988999888",
        "pet_name": "Bé Miu Xinh",
        "species": "Mèo",
        "breed": "Mèo Ba Tư",
        "service_id": 1,
        "appointment_time": booking_time,
        "notes": "Cần tắm sấy nhẹ nhàng"
    })
    assert book_res.status_code == 200
    book_data = book_res.json()
    assert book_data["success"] is True
