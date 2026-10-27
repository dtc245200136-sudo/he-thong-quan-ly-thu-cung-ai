from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import VaccineReminder, Pet
from ..schemas import VaccineReminderCreate, VaccineReminderUpdate, VaccineReminderResponse

router = APIRouter(prefix="/api/vaccines", tags=["Vaccine Reminders"])

def serialize_vaccine(v: VaccineReminder) -> VaccineReminderResponse:
    resp = VaccineReminderResponse.model_validate(v)
    if v.pet:
        resp.pet_name = v.pet.name
        if v.pet.owner:
            resp.owner_name = v.pet.owner.name
            resp.owner_phone = v.pet.owner.phone
    return resp

@router.get("", response_model=List[VaccineReminderResponse])
def get_vaccine_reminders(
    pet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    upcoming_days: Optional[int] = Query(None, description="Reminders due within N days"),
    db: Session = Depends(get_db)
):
    query = db.query(VaccineReminder)
    if pet_id:
        query = query.filter(VaccineReminder.pet_id == pet_id)
    if status:
        query = query.filter(VaccineReminder.status == status)

    today = datetime.date.today()
    if upcoming_days is not None:
        target_date = (today + datetime.timedelta(days=upcoming_days)).strftime("%Y-%m-%d")
        query = query.filter(VaccineReminder.next_due_date <= target_date, VaccineReminder.status != "completed")

    reminders = query.order_by(VaccineReminder.next_due_date.asc()).all()

    # Dynamic status update: if due date passed and not completed, mark as overdue
    for r in reminders:
        if r.status == "pending" and r.next_due_date < today.strftime("%Y-%m-%d"):
            r.status = "overdue"
    db.commit()

    return [serialize_vaccine(r) for r in reminders]

@router.post("", response_model=VaccineReminderResponse)
def create_vaccine_reminder(data: VaccineReminderCreate, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=400, detail="Thú cưng không tồn tại!")

    reminder = VaccineReminder(**data.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return serialize_vaccine(reminder)

@router.put("/{reminder_id}", response_model=VaccineReminderResponse)
def update_vaccine_reminder(reminder_id: int, data: VaccineReminderUpdate, db: Session = Depends(get_db)):
    r = db.query(VaccineReminder).filter(VaccineReminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch nhắc tiêm!")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return serialize_vaccine(r)

@router.patch("/{reminder_id}/complete", response_model=VaccineReminderResponse)
def mark_vaccine_completed(reminder_id: int, db: Session = Depends(get_db)):
    r = db.query(VaccineReminder).filter(VaccineReminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch nhắc tiêm!")
    r.status = "completed"
    r.administered_date = datetime.date.today().strftime("%Y-%m-%d")
    db.commit()
    db.refresh(r)
    return serialize_vaccine(r)

@router.delete("/{reminder_id}")
def delete_vaccine_reminder(reminder_id: int, db: Session = Depends(get_db)):
    r = db.query(VaccineReminder).filter(VaccineReminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch nhắc tiêm!")
    db.delete(r)
    db.commit()
    return {"message": "Đã xóa lịch nhắc tiêm thành công."}
