from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CareRecord, Pet, User, Appointment
from ..schemas import CareRecordCreate, CareRecordResponse

router = APIRouter(prefix="/api/care-records", tags=["Care Records"])

def serialize_care_record(cr: CareRecord) -> CareRecordResponse:
    resp = CareRecordResponse.model_validate(cr)
    if cr.pet:
        resp.pet_name = cr.pet.name
    if cr.staff:
        resp.staff_name = cr.staff.full_name
    return resp

@router.get("", response_model=List[CareRecordResponse])
def get_care_records(
    pet_id: Optional[int] = Query(None),
    staff_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(CareRecord)
    if pet_id:
        query = query.filter(CareRecord.pet_id == pet_id)
    if staff_id:
        query = query.filter(CareRecord.staff_id == staff_id)
    records = query.order_by(CareRecord.record_date.desc(), CareRecord.id.desc()).all()
    return [serialize_care_record(r) for r in records]

@router.get("/{record_id}", response_model=CareRecordResponse)
def get_care_record(record_id: int, db: Session = Depends(get_db)):
    cr = db.query(CareRecord).filter(CareRecord.id == record_id).first()
    if not cr:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chăm sóc!")
    return serialize_care_record(cr)

@router.post("", response_model=CareRecordResponse)
def create_care_record(data: CareRecordCreate, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=400, detail="Thú cưng không tồn tại!")

    # If weight is recorded, also update current weight of pet
    if data.weight_recorded_kg:
        pet.weight_kg = data.weight_recorded_kg

    record = CareRecord(**data.model_dump())
    db.add(record)

    # If linked to appointment, set appointment to completed if not already
    if data.appointment_id:
        apt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
        if apt:
            apt.status = "completed"

    db.commit()
    db.refresh(record)
    return serialize_care_record(record)

@router.delete("/{record_id}")
def delete_care_record(record_id: int, db: Session = Depends(get_db)):
    cr = db.query(CareRecord).filter(CareRecord.id == record_id).first()
    if not cr:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chăm sóc!")
    db.delete(cr)
    db.commit()
    return {"message": "Đã xóa hồ sơ chăm sóc thành công."}
