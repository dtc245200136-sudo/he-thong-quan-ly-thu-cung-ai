from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.owner import PetOwner
from backend.models.pet import Pet
from backend.models.service import Service
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.vaccination import VaccinationSchedule
from backend.models.care_record import CareRecord
from backend.models.invoice import Invoice, PaymentStatus
from backend.models.user import User, UserRole

router = APIRouter(prefix="/customer", tags=["Cổng Khách Hàng (Customer Portal & Online Booking)"])

class CustomerBookingRequest(BaseModel):
    owner_name: str
    phone: str
    email: Optional[str] = None
    pet_id: Optional[int] = None
    pet_name: Optional[str] = None
    species: Optional[str] = "Chó"
    breed: Optional[str] = None
    avatar_url: Optional[str] = None
    service_id: int
    appointment_time: datetime
    notes: Optional[str] = None

@router.get("/lookup")
def customer_lookup(phone: str = Query(..., description="Số điện thoại chủ nuôi"), db: Session = Depends(get_db)):
    """Tra cứu hồ sơ khách hàng, danh sách thú cưng, lịch tiêm phòng, lịch hẹn & điểm tích lũy thành viên"""
    phone_clean = phone.strip()
    owner = db.query(PetOwner).filter(PetOwner.phone == phone_clean).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng với số điện thoại này.")

    # 1. Tính toán điểm tích lũy & Hạng thành viên (Loyalty Program)
    paid_invoices = db.query(Invoice).filter(
        Invoice.owner_id == owner.id,
        Invoice.payment_status == PaymentStatus.PAID.value
    ).all()
    total_spent = sum(inv.total_amount for inv in paid_invoices)
    loyalty_points = int(total_spent // 10000) # 1 điểm cho mỗi 10k VNĐ

    tier_name = "Thành viên Tiêu chuẩn (Standard)"
    tier_badge = "standard"
    tier_discount = 0
    if loyalty_points >= 500:
        tier_name = "Thành viên Kim Cương (Diamond VIP)"
        tier_badge = "diamond"
        tier_discount = 15
    elif loyalty_points >= 200:
        tier_name = "Thành viên Vàng (Gold VIP)"
        tier_badge = "gold"
        tier_discount = 10
    elif loyalty_points >= 50:
        tier_name = "Thành viên Bạc (Silver)"
        tier_badge = "silver"
        tier_discount = 5

    # 2. Danh sách thú cưng
    pets = db.query(Pet).filter(Pet.owner_id == owner.id).all()
    pet_ids = [p.id for p in pets]

    # 3. Lịch hẹn
    appointments = db.query(Appointment).filter(Appointment.owner_id == owner.id).order_by(Appointment.appointment_time.desc()).all()
    appt_list = []
    for appt in appointments:
        service_name = appt.service.name if appt.service else "Dịch vụ tùy chỉnh"
        pet_name = appt.pet.name if appt.pet else "N/A"
        staff_name = appt.staff.full_name if appt.staff else "Chuyên viên PetCare"
        appt_list.append({
            "id": appt.id,
            "pet_name": pet_name,
            "service_name": service_name,
            "staff_name": staff_name,
            "appointment_time": appt.appointment_time.isoformat() if appt.appointment_time else "",
            "status": appt.status,
            "notes": appt.notes
        })

    # 4. Lịch tiêm phòng
    vaccinations = db.query(VaccinationSchedule).filter(VaccinationSchedule.pet_id.in_(pet_ids)).order_by(VaccinationSchedule.next_due_date.asc()).all() if pet_ids else []
    vac_list = []
    for v in vaccinations:
        pet_obj = next((p for p in pets if p.id == v.pet_id), None)
        vac_list.append({
            "id": v.id,
            "pet_name": pet_obj.name if pet_obj else "N/A",
            "vaccine_name": v.vaccine_name,
            "administered_date": v.administered_date.isoformat() if v.administered_date else None,
            "next_due_date": v.next_due_date.isoformat() if v.next_due_date else "",
            "status": v.status,
            "notes": v.notes
        })

    # 5. Nhật ký chăm sóc gần nhất
    care_records = db.query(CareRecord).filter(CareRecord.pet_id.in_(pet_ids)).order_by(CareRecord.record_date.desc()).limit(10).all() if pet_ids else []
    care_list = []
    for c in care_records:
        pet_obj = next((p for p in pets if p.id == c.pet_id), None)
        care_list.append({
            "id": c.id,
            "pet_name": pet_obj.name if pet_obj else "N/A",
            "record_date": c.record_date.isoformat() if c.record_date else "",
            "weight_kg": c.weight_kg,
            "services_performed": c.services_performed,
            "coat_skin_condition": c.coat_skin_condition,
            "notes": c.notes
        })

    return {
        "owner": {
            "id": owner.id,
            "full_name": owner.full_name,
            "phone": owner.phone,
            "email": owner.email,
            "address": owner.address,
            "loyalty": {
                "tier_name": tier_name,
                "tier_badge": tier_badge,
                "discount_percent": tier_discount,
                "points": loyalty_points,
                "total_spent": total_spent
            }
        },
        "pets": [
            {
                "id": p.id,
                "name": p.name,
                "species": p.species,
                "breed": p.breed,
                "age_years": p.age_years,
                "age_months": p.age_months,
                "gender": p.gender,
                "weight_kg": p.weight_kg,
                "microchip_id": p.microchip_id,
                "allergies": p.allergies,
                "medical_notes": p.medical_notes,
                "avatar_url": p.avatar_url or "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80"
            }
            for p in pets
        ],
        "appointments": appt_list,
        "vaccinations": vac_list,
        "care_records": care_list
    }

@router.post("/book-appointment")
@router.post("/book")
def customer_book_appointment(
    data: CustomerBookingRequest,
    db: Session = Depends(get_db)
):
    """Khách hàng tự đặt lịch hẹn dịch vụ Spa / Khám trực tuyến"""
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại.")

    # 1. Tìm hoặc tạo chủ nuôi
    owner = db.query(PetOwner).filter(PetOwner.phone == data.phone.strip()).first()
    if not owner:
        owner = PetOwner(
            full_name=data.owner_name.strip(),
            phone=data.phone.strip(),
            email=data.email.strip() if data.email else None,
            address="Đăng ký trực tuyến qua Cổng Khách Hàng",
            notes="Khách hàng đặt hẹn online"
        )
        db.add(owner)
        db.flush()

    # 2. Tìm hoặc tạo thú cưng
    pet = None
    if data.pet_id:
        pet = db.query(Pet).filter(Pet.id == data.pet_id, Pet.owner_id == owner.id).first()

    if not pet:
        pet_name = data.pet_name.strip() if data.pet_name else "Bé cưng"
        pet = Pet(
            owner_id=owner.id,
            name=pet_name,
            species=data.species or "Chó",
            breed=data.breed or "Chưa rõ giống",
            age_years=1,
            age_months=0,
            gender="Đực",
            avatar_url=data.avatar_url or "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80"
        )
        db.add(pet)
        db.flush()

    # 3. Gán nhân viên kỹ thuật mặc định (Groomer hoặc Staff)
    staff = db.query(User).filter(User.role == UserRole.STAFF.value, User.is_active == True).first()
    if not staff:
        staff = db.query(User).filter(User.is_active == True).first()

    end_time = data.appointment_time + timedelta(minutes=service.duration_minutes or 60)

    # 4. Tạo lịch hẹn mới
    new_appt = Appointment(
        pet_id=pet.id,
        owner_id=owner.id,
        service_id=service.id,
        staff_id=staff.id if staff else None,
        appointment_time=data.appointment_time,
        end_time=end_time,
        status=AppointmentStatus.PENDING.value,
        notes=f"[Đặt Online] {data.notes or 'Khách đặt hẹn trực tuyến qua Cổng Khách Hàng'}"
    )
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)

    return {
        "success": True,
        "message": "🎉 Đặt lịch hẹn thành công! Lễ tân PetCare AI Pro sẽ liên hệ xác nhận trong ít phút.",
        "appointment_id": new_appt.id,
        "appointment_time": new_appt.appointment_time.isoformat(),
        "pet_name": pet.name,
        "service_name": service.name,
        "status": new_appt.status,
        "appointment": {
            "id": new_appt.id,
            "pet_name": pet.name,
            "service_name": service.name,
            "appointment_time": new_appt.appointment_time.isoformat(),
            "status": new_appt.status
        }
    }

class PetWeightUpdateRequest(BaseModel):
    weight_kg: float
    notes: Optional[str] = None
    record_date: Optional[datetime] = None

@router.post("/pets/{pet_id}/weight")
def update_pet_weight(
    pet_id: int,
    data: PetWeightUpdateRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật cân nặng mới cho thú cưng và tự động lưu lịch sử vào CareRecord để AI theo dõi xu hướng"""
    if data.weight_kg <= 0 or data.weight_kg > 200:
        raise HTTPException(status_code=400, detail="Cân nặng không hợp lệ (phải từ 0.1 kg đến 200 kg).")

    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thú cưng.")

    old_weight = pet.weight_kg
    pet.weight_kg = round(data.weight_kg, 2)

    # Tự động lưu bản ghi vào Sổ Chăm Sóc (CareRecord) để theo dõi lịch sử và biểu đồ cân nặng
    care = CareRecord(
        pet_id=pet.id,
        record_date=data.record_date or datetime.now(),
        weight_kg=pet.weight_kg,
        services_performed="Cập nhật cân nặng định kỳ",
        notes=data.notes or f"Ghi nhận cân nặng mới {pet.weight_kg} kg (trước đó {old_weight or 'chưa cân'} kg)"
    )
    db.add(care)
    db.commit()
    db.refresh(pet)

    return {
        "success": True,
        "message": f"🎉 Đã cập nhật cân nặng cho bé {pet.name}: {pet.weight_kg} kg!",
        "pet_id": pet.id,
        "pet_name": pet.name,
        "new_weight_kg": pet.weight_kg,
        "old_weight_kg": old_weight
    }
