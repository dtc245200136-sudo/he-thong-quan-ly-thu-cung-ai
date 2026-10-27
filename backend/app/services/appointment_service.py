from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.appointment import Appointment, AppointmentStatus
from app.models.service import Service

def calculate_end_time(start_time: datetime, duration_minutes: int) -> datetime:
    return start_time + timedelta(minutes=duration_minutes)

def check_appointment_conflict(
    db: Session,
    appointment_time: datetime,
    end_time: datetime,
    staff_id: Optional[int] = None,
    exclude_appointment_id: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra xem lịch hẹn mới có bị trùng khung giờ với lịch hẹn đã có của nhân viên không.
    Điều kiện trùng thời gian: (StartA < EndB) và (EndA > StartB)
    """
    if appointment_time >= end_time:
        return True, "Thời gian bắt đầu phải trước thời gian kết thúc."

    if appointment_time < datetime.now() - timedelta(minutes=15):
        return True, "Không thể đặt lịch hẹn trong quá khứ."

    # Nếu có gán nhân viên cụ thể, kiểm tra trùng lịch nhân viên đó
    if staff_id:
        query = db.query(Appointment).filter(
            Appointment.staff_id == staff_id,
            Appointment.status.in_([AppointmentStatus.PENDING.value, AppointmentStatus.CONFIRMED.value, AppointmentStatus.IN_PROGRESS.value]),
            and_(
                Appointment.appointment_time < end_time,
                Appointment.end_time > appointment_time
            )
        )
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        conflicting = query.first()
        if conflicting:
            time_str = conflicting.appointment_time.strftime("%H:%M %d/%m/%Y")
            return True, f"Nhân viên chăm sóc đã có lịch hẹn bận trong khung giờ này (bắt đầu lúc {time_str})."

    # Kiểm tra giới hạn công suất tiếp nhận của tiệm cùng một thời điểm (tối đa 4 thú cưng cùng lúc)
    MAX_CONCURRENT_PETS = 4
    concurrent_query = db.query(Appointment).filter(
        Appointment.status.in_([AppointmentStatus.PENDING.value, AppointmentStatus.CONFIRMED.value, AppointmentStatus.IN_PROGRESS.value]),
        and_(
            Appointment.appointment_time < end_time,
            Appointment.end_time > appointment_time
        )
    )
    if exclude_appointment_id:
        concurrent_query = concurrent_query.filter(Appointment.id != exclude_appointment_id)
        
    if concurrent_query.count() >= MAX_CONCURRENT_PETS:
        return True, f"Cửa hàng đã đạt công suất tối đa ({MAX_CONCURRENT_PETS} bé) trong khung giờ này. Vui lòng chọn giờ khác."

    return False, None
