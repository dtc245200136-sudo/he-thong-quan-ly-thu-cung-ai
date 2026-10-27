from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Appointment, Pet, Owner, Service, User
from ..schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

def serialize_appointment(a: Appointment) -> AppointmentResponse:
    resp = AppointmentResponse.model_validate(a)
    if a.pet:
        resp.pet_name = a.pet.name
        resp.pet_species = a.pet.species
        resp.pet_breed = a.pet.breed
    if a.owner:
        resp.owner_name = a.owner.name
        resp.owner_phone = a.owner.phone
    if a.service:
        resp.service_name = a.service.name
        resp.service_price = a.service.price
    if a.staff:
        resp.staff_name = a.staff.full_name
    resp.has_care_record = (a.care_record is not None)
    resp.has_invoice = (a.invoice is not None)
    return resp

def check_appointment_conflict(
    db: Session,
    appointment_date: str,
    appointment_time: str,
    pet_id: int,
    staff_id: Optional[int] = None,
    exclude_id: Optional[int] = None
):
    """
    KT2 Algorithm: Check slot conflicts.
    1. Pet cannot have two overlapping active appointments at the exact same slot.
    2. Staff cannot be assigned two appointments at the exact same slot.
    """
    active_statuses = ["pending", "confirmed", "in_progress"]

    # Check pet conflict
    pet_conflict = db.query(Appointment).filter(
        Appointment.pet_id == pet_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(active_statuses)
    )
    if exclude_id:
        pet_conflict = pet_conflict.filter(Appointment.id != exclude_id)
    if pet_conflict.first():
        raise HTTPException(
            status_code=400,
            detail=f"Trùng lịch: Thú cưng này đã có lịch hẹn vào lúc {appointment_time} ngày {appointment_date}!"
        )

    # Check staff conflict if staff is designated
    if staff_id:
        staff_conflict = db.query(Appointment).filter(
            Appointment.staff_id == staff_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_(active_statuses)
        )
        if exclude_id:
            staff_conflict = staff_conflict.filter(Appointment.id != exclude_id)
        existing = staff_conflict.first()
        if existing:
            staff_user = db.query(User).filter(User.id == staff_id).first()
            staff_name = staff_user.full_name if staff_user else "Nhân viên"
            raise HTTPException(
                status_code=400,
                detail=f"Trùng lịch: Kỹ thuật viên {staff_name} đã có lịch hẹn phục vụ vào {appointment_time} ngày {appointment_date}!"
            )

@router.get("", response_model=List[AppointmentResponse])
def get_appointments(
    date: Optional[str] = Query(None, description="Filter by YYYY-MM-DD"),
    status: Optional[str] = Query(None),
    pet_id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    staff_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)
    if date:
        query = query.filter(Appointment.appointment_date == date)
    if status:
        query = query.filter(Appointment.status == status)
    if pet_id:
        query = query.filter(Appointment.pet_id == pet_id)
    if owner_id:
        query = query.filter(Appointment.owner_id == owner_id)
    if staff_id:
        query = query.filter(Appointment.staff_id == staff_id)

    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).all()
    return [serialize_appointment(a) for a in appointments]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")
    return serialize_appointment(a)

@router.post("", response_model=AppointmentResponse)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    # Validate pet
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=400, detail="Thú cưng không tồn tại!")

    # Validate service
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=400, detail="Dịch vụ không tồn tại!")

    # Check conflict
    check_appointment_conflict(
        db=db,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        pet_id=data.pet_id,
        staff_id=data.staff_id
    )

    appointment = Appointment(
        pet_id=data.pet_id,
        owner_id=data.owner_id,
        service_id=data.service_id,
        staff_id=data.staff_id,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        notes=data.notes,
        status="confirmed"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return serialize_appointment(appointment)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")

    update_dict = data.model_dump(exclude_unset=True)
    
    # Check if rescheduling (date or time changed)
    target_date = update_dict.get("appointment_date", a.appointment_date)
    target_time = update_dict.get("appointment_time", a.appointment_time)
    target_staff = update_dict.get("staff_id", a.staff_id)

    if target_date != a.appointment_date or target_time != a.appointment_time or target_staff != a.staff_id:
        check_appointment_conflict(
            db=db,
            appointment_date=target_date,
            appointment_time=target_time,
            pet_id=a.pet_id,
            staff_id=target_staff,
            exclude_id=a.id
        )

    for k, v in update_dict.items():
        setattr(a, k, v)

    db.commit()
    db.refresh(a)
    return serialize_appointment(a)

@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int, reason: Optional[str] = "Khách hàng báo bận", db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")
    a.status = "cancelled"
    a.cancel_reason = reason
    db.commit()
    db.refresh(a)
    return serialize_appointment(a)

@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")
    a.status = "completed"
    db.commit()
    db.refresh(a)
    return serialize_appointment(a)

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn!")
    db.delete(a)
    db.commit()
    return {"message": "Đã xóa lịch hẹn thành công."}
