from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.appointment import Appointment, AppointmentStatus
from app.models.pet import Pet
from app.models.service import Service
from app.models.user import User
from app.schemas.appointment_dto import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.appointment_service import calculate_end_time, check_appointment_conflict

router = APIRouter(prefix="/appointments", tags=["Quản lý Đặt lịch & Lịch hẹn (Appointments)"])

def enrich_appointment_response(appt: Appointment) -> dict:
    return {
        "id": appt.id,
        "pet_id": appt.pet_id,
        "owner_id": appt.owner_id,
        "service_id": appt.service_id,
        "staff_id": appt.staff_id,
        "appointment_time": appt.appointment_time,
        "end_time": appt.end_time,
        "status": appt.status,
        "notes": appt.notes,
        "reminder_sent": appt.reminder_sent,
        "created_at": appt.created_at,
        "pet_name": appt.pet.name if appt.pet else None,
        "pet_species": appt.pet.species if appt.pet else None,
        "owner_name": appt.owner.full_name if appt.owner else None,
        "owner_phone": appt.owner.phone if appt.owner else None,
        "service_name": appt.service.name if appt.service else None,
        "service_price": appt.service.price if appt.service else None,
        "staff_name": appt.staff.full_name if appt.staff else "Chưa phân công"
    }

@router.get("", response_model=List[AppointmentResponse])
def list_appointments(
    date_str: Optional[str] = Query(None, description="Lọc theo ngày (YYYY-MM-DD)"),
    status_filter: Optional[str] = Query(None, description="Lọc theo trạng thái"),
    pet_id: Optional[int] = Query(None, description="Lọc theo thú cưng"),
    staff_id: Optional[int] = Query(None, description="Lọc theo nhân viên"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Appointment)
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_dt = datetime.combine(target_date, datetime.min.time())
            end_dt = datetime.combine(target_date, datetime.max.time())
            query = query.filter(Appointment.appointment_time >= start_dt, Appointment.appointment_time <= end_dt)
        except ValueError:
            pass
            
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if pet_id:
        query = query.filter(Appointment.pet_id == pet_id)
    if staff_id:
        query = query.filter(Appointment.staff_id == staff_id)
        
    appts = query.order_by(Appointment.appointment_time.asc()).all()
    return [enrich_appointment_response(a) for a in appts]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
    return enrich_appointment_response(appt)

@router.post("", response_model=AppointmentResponse)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng")
        
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
        
    duration = service.duration_minutes or 60
    end_time = calculate_end_time(data.appointment_time, duration)
    
    # Kiểm tra trùng lịch
    is_conflict, reason = check_appointment_conflict(
        db=db,
        appointment_time=data.appointment_time,
        end_time=end_time,
        staff_id=data.staff_id
    )
    if is_conflict:
        raise HTTPException(status_code=400, detail=f"Không thể đặt lịch: {reason}")
        
    appointment = Appointment(
        pet_id=pet.id,
        owner_id=pet.owner_id,
        service_id=service.id,
        staff_id=data.staff_id,
        appointment_time=data.appointment_time,
        end_time=end_time,
        status=AppointmentStatus.CONFIRMED.value,
        notes=data.notes
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return enrich_appointment_response(appointment)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
        
    target_time = data.appointment_time or appt.appointment_time
    target_service_id = data.service_id or appt.service_id
    target_staff_id = data.staff_id if data.staff_id is not None else appt.staff_id
    
    service = db.query(Service).filter(Service.id == target_service_id).first()
    duration = service.duration_minutes if service else 60
    new_end_time = calculate_end_time(target_time, duration)
    
    # Nếu có thay đổi thời gian hoặc nhân viên, kiểm tra lại trùng lịch
    if data.appointment_time or (data.staff_id is not None and data.staff_id != appt.staff_id):
        is_conflict, reason = check_appointment_conflict(
            db=db,
            appointment_time=target_time,
            end_time=new_end_time,
            staff_id=target_staff_id,
            exclude_appointment_id=appt.id
        )
        if is_conflict:
            raise HTTPException(status_code=400, detail=f"Không thể đổi lịch: {reason}")
            
    appt.appointment_time = target_time
    appt.end_time = new_end_time
    if data.pet_id:
        appt.pet_id = data.pet_id
        pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
        if pet:
            appt.owner_id = pet.owner_id
    if data.service_id:
        appt.service_id = data.service_id
    if data.staff_id is not None:
        appt.staff_id = data.staff_id
    if data.status:
        appt.status = data.status
    if data.notes is not None:
        appt.notes = data.notes
        
    db.commit()
    db.refresh(appt)
    return enrich_appointment_response(appt)

@router.post("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
        
    try:
        appt.status = AppointmentStatus.CANCELLED.value
        db.commit()
        return {"message": "Đã hủy lịch hẹn thành công", "appointment_id": appointment_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi hủy lịch: {str(e)}")

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
        
    try:
        db.delete(appt)
        db.commit()
        return {"message": "Đã xóa lịch hẹn thành công", "appointment_id": appointment_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa lịch hẹn: {str(e)}")

