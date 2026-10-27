from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.care_record import CareRecord
from backend.models.pet import Pet
from backend.models.appointment import Appointment
from backend.schemas.care_record_dto import CareRecordCreate, CareRecordUpdate, CareRecordResponse

router = APIRouter(prefix="/care-records", tags=["Hồ sơ Chăm sóc Thú cưng (Care Records)"])

def enrich_care_record_response(rec: CareRecord) -> dict:
    pet = rec.pet
    owner = pet.owner if pet else None
    return {
        "id": rec.id,
        "pet_id": rec.pet_id,
        "appointment_id": rec.appointment_id,
        "staff_id": rec.staff_id,
        "record_date": rec.record_date,
        "weight_kg": rec.weight_kg,
        "coat_skin_condition": rec.coat_skin_condition,
        "ears_eyes_teeth": rec.ears_eyes_teeth,
        "behavior_mood": rec.behavior_mood,
        "services_performed": rec.services_performed,
        "notes": rec.notes,
        "before_photo_url": rec.before_photo_url,
        "after_photo_url": rec.after_photo_url,
        "created_at": rec.created_at,
        "pet_name": pet.name if pet else None,
        "pet_species": pet.species if pet else None,
        "pet_breed": pet.breed if pet else None,
        "owner_name": owner.full_name if owner else None,
        "owner_phone": owner.phone if owner else None,
        "staff_name": rec.staff.full_name if rec.staff else "Nhân viên chăm sóc"
    }

@router.get("", response_model=List[CareRecordResponse])
def list_care_records(
    pet_id: Optional[int] = Query(None, description="Lọc theo Pet ID"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(CareRecord)
    if pet_id:
        query = query.filter(CareRecord.pet_id == pet_id)
    records = query.order_by(CareRecord.record_date.desc()).offset(skip).limit(limit).all()
    return [enrich_care_record_response(r) for r in records]

@router.get("/{record_id}", response_model=CareRecordResponse)
def get_care_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    rec = db.query(CareRecord).filter(CareRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chăm sóc")
    return enrich_care_record_response(rec)

@router.post("", response_model=CareRecordResponse)
def create_care_record(
    data: CareRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng")
        
    record = CareRecord(**data.model_dump())
    if not record.staff_id:
        record.staff_id = current_user.id
    if not record.record_date:
        record.record_date = datetime.now()
        
    # Cập nhật cân nặng mới nhất cho thú cưng nếu có
    if data.weight_kg:
        pet.weight_kg = data.weight_kg
        
    db.add(record)
    db.commit()
    db.refresh(record)
    return enrich_care_record_response(record)

@router.put("/{record_id}", response_model=CareRecordResponse)
def update_care_record(
    record_id: int,
    data: CareRecordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    rec = db.query(CareRecord).filter(CareRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chăm sóc")
        
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rec, key, value)
        
    if data.weight_kg and rec.pet:
        rec.pet.weight_kg = data.weight_kg
        
    db.commit()
    db.refresh(rec)
    return enrich_care_record_response(rec)

@router.delete("/{record_id}")
def delete_care_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    rec = db.query(CareRecord).filter(CareRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chăm sóc")
        
    db.delete(rec)
    db.commit()
    return {"message": "Đã xóa hồ sơ chăm sóc thành công"}
