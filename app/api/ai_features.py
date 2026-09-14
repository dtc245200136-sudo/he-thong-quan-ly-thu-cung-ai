import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.core.config import settings
from app.models.pet import Pet
from app.models.care_record import CareRecord
from app.models.vaccination import VaccinationSchedule
from app.models.appointment import Appointment
from app.schemas.ai_dto import (
    AIReminderRequest, AIReminderResponse,
    AICareSummaryRequest, AICareSummaryResponse,
    AIChatRequest, AIChatResponse,
    AIConfigUpdateRequest,
    AISymptomCheckRequest, AISymptomCheckResponse
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["Tính năng Trí tuệ Nhân tạo (AI Features & Guardrails)"])

@router.post("/symptom-checker", response_model=AISymptomCheckResponse)
def check_pet_symptoms(data: AISymptomCheckRequest):
    """
    AI Feature 4: Chẩn đoán triệu chứng thông minh & Đề xuất dịch vụ chăm sóc phù hợp
    """
    return AIService.check_symptoms(
        species=data.species,
        breed=data.breed,
        age_str=data.age_str,
        symptoms=data.symptoms,
        symptom_description=data.symptom_description,
        duration=data.duration,
        behavior_changes=data.behavior_changes
    )


@router.post("/generate-reminder", response_model=AIReminderResponse)
def generate_reminder_message(
    data: AIReminderRequest,
    current_user = Depends(get_current_user)
):
    """
    AI Feature 1: Sinh tin nhắn nhắc lịch chăm sóc hoặc tiêm phòng đa kênh (SMS, Zalo, Email)
    """
    return AIService.generate_reminder(
        pet_name=data.pet_name,
        owner_name=data.owner_name,
        service_or_vaccine_name=data.service_or_vaccine_name,
        scheduled_time=data.scheduled_time,
        reminder_type=data.reminder_type,
        channel=data.channel,
        special_notes=data.special_notes
    )

@router.post("/care-summary", response_model=AICareSummaryResponse)
def summarize_pet_care_history(
    data: AICareSummaryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    AI Feature 2: AI Tóm tắt hồ sơ chăm sóc của thú cưng, tổng hợp xu hướng cân nặng & sức khỏe
    """
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thú cưng")
        
    care_records = db.query(CareRecord).filter(CareRecord.pet_id == data.pet_id).order_by(CareRecord.record_date.desc()).all()
    vaccinations = db.query(VaccinationSchedule).filter(VaccinationSchedule.pet_id == data.pet_id).all()
    
    pet_info = {
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "age_years": pet.age_years,
        "age_months": pet.age_months,
        "allergies": pet.allergies,
        "medical_notes": pet.medical_notes,
    }
    
    records_data = [
        {
            "record_date": r.record_date.strftime("%d/%m/%Y") if r.record_date else "",
            "weight_kg": r.weight_kg,
            "coat_skin_condition": r.coat_skin_condition,
            "ears_eyes_teeth": r.ears_eyes_teeth,
            "behavior_mood": r.behavior_mood,
            "services_performed": r.services_performed,
            "notes": r.notes
        }
        for r in care_records
    ]
    
    vacs_data = [
        {
            "vaccine_name": v.vaccine_name,
            "administered_date": v.administered_date.strftime("%d/%m/%Y") if v.administered_date else "",
            "next_due_date": v.next_due_date.strftime("%d/%m/%Y"),
            "status": v.status
        }
        for v in vaccinations
    ]
    
    return AIService.summarize_care_history(
        pet_info=pet_info,
        care_records=records_data,
        vaccinations=vacs_data
    )

@router.post("/chat", response_model=AIChatResponse)
def chat_with_pet_ai(
    data: AIChatRequest
):
    """
    AI Feature 3: Trợ lý AI Bác sĩ Thú y 24/7 trả lời câu hỏi chăm sóc thông thường có tích hợp Guardrails Cảnh báo Y tế
    """
    return AIService.chat_with_assistant(
        message=data.message,
        image_data=data.image_data,
        pet_context=data.pet_context,
        chat_history=data.chat_history
    )

def _persist_env_config(updates: dict):
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            lines = []
    
    current_data = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            current_data[k.strip()] = v.strip()
            
    for k, v in updates.items():
        if v is not None:
            current_data[k] = str(v)
            
    out_lines = [f"{k}={v}\n" for k, v in current_data.items()]
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
    except Exception:
        pass

@router.get("/config")
def get_ai_config(current_user = Depends(get_current_user_optional)):
    return {
        "current_provider": settings.AI_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "gemini_api_key_masked": f"{settings.GEMINI_API_KEY[:6]}...{settings.GEMINI_API_KEY[-4:]}" if len(settings.GEMINI_API_KEY) > 10 else ("***" if settings.GEMINI_API_KEY else ""),
        "safety_guardrails_active": True,
        "supported_models": ["Built-in Offline Smart NLP (Recommended for Offline Grading)", "Google Gemini-1.5-Flash", "OpenAI GPT-4o-mini"]
    }

@router.post("/config")
def update_ai_config(
    data: AIConfigUpdateRequest,
    current_user = Depends(get_current_user_optional)
):
    settings.AI_PROVIDER = data.provider
    env_updates = {"AI_PROVIDER": data.provider}
    
    if data.gemini_api_key is not None:
        settings.GEMINI_API_KEY = data.gemini_api_key.strip()
        env_updates["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
    if data.openai_api_key is not None:
        settings.OPENAI_API_KEY = data.openai_api_key.strip()
        env_updates["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    _persist_env_config(env_updates)
        
    return {
        "message": "Cập nhật cấu hình AI Engine thành công",
        "current_provider": settings.AI_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY)
    }
