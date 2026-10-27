from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.vaccination import VaccinationSchedule, VaccinationStatus
from backend.models.pet import Pet
from backend.schemas.appointment_dto import VaccinationCreate, VaccinationUpdate, VaccinationResponse

router = APIRouter(prefix="/vaccinations", tags=["Lịch Tiêm phòng & Nhắc bệnh (Vaccinations)"])

def enrich_vaccination_response(v: VaccinationSchedule) -> dict:
    pet = v.pet
    owner = pet.owner if pet else None
    
    return {
        "id": v.id,
        "pet_id": v.pet_id,
        "vaccine_name": v.vaccine_name,
        "dose_number": getattr(v, "dose_number", None),
        "manufacturer": getattr(v, "manufacturer", None),
        "batch_number": getattr(v, "batch_number", None),
        "administered_date": v.administered_date,
        "next_due_date": v.next_due_date,
        "status": v.effective_status,
        "status_display": v.status_display,
        "is_overdue": v.is_overdue,
        "days_until_due": v.days_until_due,
        "administered_by_id": getattr(v, "administered_by_id", None),
        "reaction_notes": getattr(v, "reaction_notes", None),
        "notes": v.notes,
        "reminder_sent": v.reminder_sent,
        "created_at": v.created_at,
        "updated_at": getattr(v, "updated_at", None),
        "pet_name": pet.name if pet else None,
        "owner_name": owner.full_name if owner else None,
        "owner_phone": owner.phone if owner else None
    }

@router.get("/core-protocols", description="Lấy danh mục phác đồ tiêm chủng chuẩn y khoa cho Chó và Mèo")
def get_core_vaccine_protocols():
    return {
        "dog_core": VaccinationSchedule.CORE_VACCINES_DOG,
        "cat_core": VaccinationSchedule.CORE_VACCINES_CAT
    }

@router.get("", response_model=List[VaccinationResponse])
def list_vaccinations(
    pet_id: Optional[int] = Query(None, description="Lọc theo Pet ID"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái"),
    upcoming_days: Optional[int] = Query(None, description="Lọc lịch tiêm trong N ngày tới"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(VaccinationSchedule)
    if pet_id:
        query = query.filter(VaccinationSchedule.pet_id == pet_id)
    if status:
        query = query.filter(VaccinationSchedule.status == status)
    if upcoming_days:
        from datetime import timedelta
        target_date = date.today() + timedelta(days=upcoming_days)
        query = query.filter(
            VaccinationSchedule.next_due_date >= date.today(),
            VaccinationSchedule.next_due_date <= target_date
        )
        
    vaccs = query.order_by(VaccinationSchedule.next_due_date.asc()).all()
    return [enrich_vaccination_response(v) for v in vaccs]

@router.post("", response_model=VaccinationResponse)
def create_vaccination(
    data: VaccinationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng")
        
    vac = VaccinationSchedule(**data.model_dump())
    db.add(vac)
    db.commit()
    db.refresh(vac)
    return enrich_vaccination_response(vac)

@router.put("/{vac_id}", response_model=VaccinationResponse)
def update_vaccination(
    vac_id: int,
    data: VaccinationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vac = db.query(VaccinationSchedule).filter(VaccinationSchedule.id == vac_id).first()
    if not vac:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin lịch tiêm")
        
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vac, key, value)
        
    db.commit()
    db.refresh(vac)
    return enrich_vaccination_response(vac)

@router.delete("/{vac_id}")
def delete_vaccination(
    vac_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vac = db.query(VaccinationSchedule).filter(VaccinationSchedule.id == vac_id).first()
    if not vac:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin lịch tiêm")
        
    db.delete(vac)
    db.commit()
    return {"message": "Đã xóa lịch tiêm phòng thành công"}
