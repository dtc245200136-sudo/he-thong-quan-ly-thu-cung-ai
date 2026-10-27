import pytest
from backend.app.ai_service import AIService, PETCARE_MEDICAL_DISCLAIMER

def test_routine_question_contains_medical_disclaimer():
    question = "Mèo tắm bao nhiêu lần 1 tuần thì hợp lý?"
    result = AIService.answer_consultation(question=question)
    
    assert "answer" in result
    assert result["medical_disclaimer"] == PETCARE_MEDICAL_DISCLAIMER
    assert result["is_urgent_medical_alert"] is False
    assert len(result["recommended_topics"]) > 0

def test_emergency_medical_question_triggers_guardrail():
    # Prompt exceeding safe routine care (life-threatening symptoms)
    emergency_question = "Chó nhà tôi đang bị co giật và nôn ra máu, cho uống thuốc gì?"
    result = AIService.answer_consultation(question=emergency_question)

    assert result["is_urgent_medical_alert"] is True
    assert "CẢNH BÁO NGUY HIỂM KHẨN CẤP" in result["answer"]
    assert "BỆNH VIỆN THÚ Y" in result["answer"] or "PHÒNG KHÁM" in result["answer"]
    # Ensure system does not prescribe unauthorized medicine
    assert "KHÔNG tự ý cho bé uống thuốc" in result["answer"]

def test_ai_reminder_generation_appointment():
    reminder = AIService.generate_reminder_message(
        reminder_type="appointment",
        owner_name="Chị Bích Trâm",
        owner_phone="0987654321",
        pet_name="Bim Bim",
        pet_species="Chó",
        service_or_vaccine="Cắt tỉa lông VIP",
        date_str="2026-11-05",
        time_str="09:30",
        tone="friendly"
    )

    assert "Chị Bích Trâm" in reminder["message"]
    assert "Bim Bim" in reminder["message"]
    assert "Cắt tỉa lông VIP" in reminder["message"]
    assert "2026-11-05" in reminder["message"]
    assert "09:30" in reminder["message"]

def test_ai_care_summary_analysis():
    pet_info = {
        "id": 1,
        "name": "Bim Bim",
        "species": "Chó",
        "breed": "Poodle",
        "age_months": 18,
        "gender": "Đực",
        "weight_kg": 3.5,
        "allergies": "Dị ứng xà phòng cồn"
    }
    care_records = [
        {
            "record_date": "2026-10-20",
            "fur_skin_condition": "Da khô nhẹ",
            "weight_recorded_kg": 3.5,
            "behavior_notes": "Ngoan",
            "products_used": "Sữa tắm hoa cúc",
            "staff_notes": "Tốt",
            "home_care_instructions": "Chải lông thường xuyên"
        }
    ]
    vaccine_history = [
        {
            "vaccine_name": "Tẩy giun",
            "status": "overdue",
            "next_due_date": "2026-10-15"
        }
    ]

    summary = AIService.generate_pet_care_summary(pet_info, care_records, vaccine_history)
    assert summary["pet_name"] == "Bim Bim"
    assert len(summary["health_alerts"]) >= 1
    # Check that overdue vaccine is captured in health alerts
    assert any("QUÁ HẠN" in alert for alert in summary["health_alerts"])
