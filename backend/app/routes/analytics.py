from typing import Dict, Any, List
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Appointment, Invoice, Pet, Owner, Service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    # Counts
    total_pets = db.query(Pet).count()
    total_owners = db.query(Owner).count()
    today_appointments = db.query(Appointment).filter(Appointment.appointment_date == today_str).count()
    total_appointments = db.query(Appointment).count()

    # Revenue
    paid_invoices = db.query(Invoice).filter(Invoice.payment_status == "paid").all()
    total_revenue = sum(inv.final_amount for inv in paid_invoices)
    pending_revenue = sum(inv.final_amount for inv in db.query(Invoice).filter(Invoice.payment_status == "pending").all())

    # Customer Return Rate calculation:
    # Owners who booked >= 2 appointments
    owner_apt_counts = db.query(
        Appointment.owner_id, func.count(Appointment.id)
    ).group_by(Appointment.owner_id).all()
    
    repeat_customers = sum(1 for _, count in owner_apt_counts if count >= 2)
    return_rate = (repeat_customers / total_owners * 100) if total_owners > 0 else 0.0

    # Service Popularity
    service_stats = db.query(
        Service.name, func.count(Appointment.id).label("count")
    ).join(Appointment, Appointment.service_id == Service.id)\
     .group_by(Service.id)\
     .order_by(func.count(Appointment.id).desc())\
     .limit(5).all()

    popular_services = [{"name": s[0], "count": s[1]} for s in service_stats]

    # Appointments by status
    status_counts = db.query(
        Appointment.status, func.count(Appointment.id)
    ).group_by(Appointment.status).all()
    status_breakdown = {s[0]: s[1] for s in status_counts}

    return {
        "total_pets": total_pets,
        "total_owners": total_owners,
        "today_appointments": today_appointments,
        "total_appointments": total_appointments,
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "repeat_customers_count": repeat_customers,
        "repeat_customer_rate": round(return_rate, 1),
        "popular_services": popular_services,
        "status_breakdown": status_breakdown
    }
