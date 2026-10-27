from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Appointment, VaccineReminder, Pet, CareRecord, AISessionLog
from ..schemas import (
    AIReminderRequest, AIReminderResponse,
    AISummaryRequest, AISummaryResponse,
    AIConsultationRequest, AIConsultationResponse,
    AISettings
)
from ..ai_service import AIService
from ..config import settings

router = APIRouter(prefix="/api/ai", tags=["AI Features"])

@router.post("/reminder", response_model=AIReminderResponse)
def generate_reminder(data: AIReminderRequest, db: Session = Depends(get_db)):
    """
    AI Feature 1: Sinh tin nhắn nhắc lịch chăm sóc hoặc lịch tiêm nhắc.
    """
    owner_name = "Quý khách"
    owner_phone = "0987654321"
    pet_name = "Thú cưng"
    pet_species = "Chó"
    service_name = "Dịch vụ chăm sóc"
    date_str = ""
    time_str = None

    if data.reminder_type == "appointment":
        if not data.appointment_id:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp appointment_id!")
        apt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
        if not apt:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")
        owner_name = apt.owner.name if apt.owner else owner_name
        owner_phone = apt.owner.phone if apt.owner else owner_phone
        pet_name = apt.pet.name if apt.pet else pet_name
        pet_species = apt.pet.species if apt.pet else pet_species
        service_name = apt.service.name if apt.service else service_name
        date_str = apt.appointment_date
        time_str = apt.appointment_time
    else: # vaccine
        if not data.vaccine_reminder_id:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp vaccine_reminder_id!")
        vac = db.query(VaccineReminder).filter(VaccineReminder.id == data.vaccine_reminder_id).first()
        if not vac:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch nhắc tiêm!")
        if vac.pet and vac.pet.owner:
            owner_name = vac.pet.owner.name
            owner_phone = vac.pet.owner.phone
        if vac.pet:
            pet_name = vac.pet.name
            pet_species = vac.pet.species
        service_name = vac.vaccine_name
        date_str = vac.next_due_date

    result = AIService.generate_reminder_message(
        reminder_type=data.reminder_type,
        owner_name=owner_name,
        owner_phone=owner_phone,
        pet_name=pet_name,
        pet_species=pet_species,
        service_or_vaccine=service_name,
        date_str=date_str,
        time_str=time_str,
        tone=data.tone,
        custom_note=data.custom_note
    )

    # Log AI session
    log = AISessionLog(
        feature_type=f"reminder_{data.reminder_type}",
        pet_id=data.appointment_id or data.vaccine_reminder_id,
        user_prompt=f"Tone: {data.tone}, Custom Note: {data.custom_note}",
        ai_response=result["message"],
        model_name=result["model_used"]
    )
    db.add(log)
    db.commit()

    return AIReminderResponse(**result)

@router.post("/summary", response_model=AISummaryResponse)
def generate_pet_summary(data: AISummaryRequest, db: Session = Depends(get_db)):
    """
    AI Feature 2: Tóm tắt hồ sơ chăm sóc của thú cưng.
    """
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng!")

    # Fetch care records
    records = db.query(CareRecord).filter(CareRecord.pet_id == data.pet_id).order_by(CareRecord.record_date.desc()).all()
    care_records_data = [
        {
            "record_date": r.record_date,
            "fur_skin_condition": r.fur_skin_condition,
            "weight_recorded_kg": r.weight_recorded_kg,
            "behavior_notes": r.behavior_notes,
            "products_used": r.products_used,
            "staff_notes": r.staff_notes,
            "home_care_instructions": r.home_care_instructions
        }
        for r in records
    ]

    # Fetch vaccine history
    vaccines = db.query(VaccineReminder).filter(VaccineReminder.pet_id == data.pet_id).all()
    vaccine_data = [
        {
            "vaccine_name": v.vaccine_name,
            "dose_number": v.dose_number,
            "administered_date": v.administered_date,
            "next_due_date": v.next_due_date,
            "status": v.status
        }
        for v in vaccines
    ]

    pet_info = {
        "id": pet.id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "age_months": pet.age_months,
        "gender": pet.gender,
        "weight_kg": pet.weight_kg,
        "allergies": pet.allergies,
        "medical_history": pet.medical_history
    }

    result = AIService.generate_pet_care_summary(
        pet_info=pet_info,
        care_records=care_records_data,
        vaccine_history=vaccine_data
    )

    # Log AI session
    log = AISessionLog(
        feature_type="pet_summary",
        pet_id=pet.id,
        user_prompt=f"Yêu cầu tóm tắt hồ sơ bé {pet.name} (ID: {pet.id})",
        ai_response=result["summary_markdown"],
        model_name=result["model_used"]
    )
    db.add(log)
    db.commit()

    return AISummaryResponse(**result)

@router.post("/consultation", response_model=AIConsultationResponse)
def chat_consultation(data: AIConsultationRequest, db: Session = Depends(get_db)):
    """
    AI Feature 3: Trả lời câu hỏi chăm sóc thông thường có cảnh báo y tế thú y.
    """
    pet_info = None
    if data.pet_id:
        pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
        if pet:
            pet_info = {
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "age_months": pet.age_months,
                "weight_kg": pet.weight_kg
            }

    result = AIService.answer_consultation(
        question=data.question,
        pet_info=pet_info,
        chat_history=data.chat_history
    )

    # Log AI session
    log = AISessionLog(
        feature_type="consultation",
        pet_id=data.pet_id,
        user_prompt=data.question,
        ai_response=result["answer"],
        has_disclaimer=True,
        model_name=result["model_used"]
    )
    db.add(log)
    db.commit()

    return AIConsultationResponse(**result)

@router.get("/settings", response_model=AISettings)
def get_ai_settings():
    return AISettings(
        provider=settings.DEFAULT_AI_PROVIDER,
        has_gemini_key=bool(settings.GEMINI_API_KEY),
        has_openai_key=bool(settings.OPENAI_API_KEY)
    )

@router.post("/settings")
def update_ai_settings(
    provider: Optional[str] = Body(None),
    gemini_key: Optional[str] = Body(None),
    openai_key: Optional[str] = Body(None)
):
    if provider:
        settings.DEFAULT_AI_PROVIDER = provider
    if gemini_key is not None:
        settings.GEMINI_API_KEY = gemini_key.strip()
    if openai_key is not None:
        settings.OPENAI_API_KEY = openai_key.strip()

    return {
        "message": "Cập nhật cấu hình AI thành công!",
        "provider": settings.DEFAULT_AI_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY)
    }

@router.get("/logs")
def get_ai_logs(db: Session = Depends(get_db)):
    logs = db.query(AISessionLog).order_by(AISessionLog.id.desc()).limit(20).all()
    return logs
