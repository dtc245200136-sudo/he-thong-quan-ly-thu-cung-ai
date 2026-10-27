from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.invoice import Invoice, PaymentStatus
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.pet import Pet
from backend.models.owner import PetOwner
from backend.models.service import Service

router = APIRouter(prefix="/stats", tags=["Báo cáo & Thống kê (Dashboard Stats)"])

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    today = date.today()
    start_today = datetime.combine(today, datetime.min.time())
    end_today = datetime.combine(today, datetime.max.time())
    
    # 1. Tổng số khách & thú cưng
    total_owners = db.query(PetOwner).count()
    total_pets = db.query(Pet).count()
    
    # 2. Lịch hẹn hôm nay
    today_appointments = db.query(Appointment).filter(
        Appointment.appointment_time >= start_today,
        Appointment.appointment_time <= end_today
    ).count()
    
    # 3. Tổng doanh thu đã thanh toán
    total_revenue_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.payment_status == PaymentStatus.PAID.value
    ).scalar()
    total_revenue = total_revenue_query or 0.0
    
    # 4. Doanh thu hôm nay
    today_revenue_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.payment_status == PaymentStatus.PAID.value,
        func.coalesce(Invoice.payment_time, Invoice.created_at) >= start_today,
        func.coalesce(Invoice.payment_time, Invoice.created_at) <= end_today
    ).scalar()
    today_revenue = today_revenue_query or 0.0
    
    # 5. Tỷ lệ khách quay lại (Khách có >= 2 lịch hẹn)
    owners_with_appointments = db.query(
        Appointment.owner_id,
        func.count(Appointment.id).label("count")
    ).group_by(Appointment.owner_id).all()
    
    total_active_owners = len(owners_with_appointments)
    returning_owners = sum(1 for o in owners_with_appointments if o.count >= 2)
    retention_rate = round((returning_owners / total_active_owners * 100), 1) if total_active_owners > 0 else 0.0
    
    # 6. Doanh thu 7 ngày gần nhất (để vẽ Chart)
    daily_revenue = []
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        rev = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.payment_status == PaymentStatus.PAID.value,
            func.coalesce(Invoice.payment_time, Invoice.created_at) >= day_start,
            func.coalesce(Invoice.payment_time, Invoice.created_at) <= day_end
        ).scalar() or 0.0
        
        daily_revenue.append({
            "date": day_date.strftime("%d/%m"),
            "revenue": rev
        })
        
    # 7. Thống kê tỷ lệ theo danh mục dịch vụ
    service_stats = db.query(
        Service.category,
        func.count(Appointment.id).label("count")
    ).join(Appointment, Service.id == Appointment.service_id).group_by(Service.category).all()
    
    categories_data = [
        {"category": cat, "count": cnt} for cat, cnt in service_stats
    ]

    return {
        "total_owners": total_owners,
        "total_pets": total_pets,
        "today_appointments": today_appointments,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "retention_rate": retention_rate,
        "returning_customers_count": returning_owners,
        "daily_revenue": daily_revenue,
        "service_distribution": categories_data
    }
