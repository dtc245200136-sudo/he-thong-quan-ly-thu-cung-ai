from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.invoice import Invoice, InvoiceItem, PaymentMethod, PaymentStatus
from app.models.owner import PetOwner
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.invoice_dto import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.services.invoice_service import generate_invoice_code, create_invoice_from_appointment

router = APIRouter(prefix="/invoices", tags=["Quản lý Hóa đơn & Thanh toán (Invoices)"])

def enrich_invoice_response(inv: Invoice) -> dict:
    owner = inv.owner
    return {
        "id": inv.id,
        "invoice_code": inv.invoice_code,
        "appointment_id": inv.appointment_id,
        "owner_id": inv.owner_id,
        "subtotal": inv.subtotal,
        "discount_amount": inv.discount_amount,
        "tax_amount": inv.tax_amount,
        "total_amount": inv.total_amount,
        "payment_method": inv.payment_method,
        "payment_status": inv.payment_status,
        "payment_time": inv.payment_time,
        "notes": inv.notes,
        "created_at": inv.created_at,
        "owner_name": owner.full_name if owner else None,
        "owner_phone": owner.phone if owner else None,
        "owner_address": owner.address if owner else None,
        "items": [
            {
                "id": item.id,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }
            for item in inv.items
        ]
    }

@router.get("/pending-appointments")
def get_pending_invoicing_appointments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy danh sách các lịch hẹn đang chờ thu tiền (chưa có hóa đơn hoặc chưa hoàn thành)"""
    invoiced_appt_ids = [inv.appointment_id for inv in db.query(Invoice.appointment_id).filter(Invoice.appointment_id.isnot(None)).all()]
    
    query = db.query(Appointment).filter(
        Appointment.status.in_([AppointmentStatus.IN_PROGRESS.value, AppointmentStatus.CONFIRMED.value])
    )
    if invoiced_appt_ids:
        query = query.filter(~Appointment.id.in_(invoiced_appt_ids))
        
    appts = query.order_by(Appointment.appointment_time.desc()).limit(30).all()
    
    return [
        {
            "id": a.id,
            "pet_name": a.pet.name if a.pet else "Bé",
            "owner_id": a.owner_id,
            "owner_name": a.owner.full_name if a.owner else "Khách",
            "owner_phone": a.owner.phone if a.owner else "",
            "service_name": a.service.name if a.service else "Dịch vụ Spa",
            "service_price": a.service.price if a.service else 0,
            "appointment_time": a.appointment_time.strftime("%d/%m/%Y %H:%M") if a.appointment_time else ""
        }
        for a in appts
    ]

@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    owner_id: Optional[int] = Query(None, description="Lọc theo khách hàng"),
    payment_status: Optional[str] = Query(None, description="Lọc theo trạng thái thanh toán"),
    search: Optional[str] = Query(None, description="Tìm theo mã HĐ, tên khách hoặc số điện thoại"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Invoice).join(PetOwner, Invoice.owner_id == PetOwner.id, isouter=True)
    
    if owner_id:
        query = query.filter(Invoice.owner_id == owner_id)
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Invoice.invoice_code.ilike(search_term),
                PetOwner.full_name.ilike(search_term),
                PetOwner.phone.ilike(search_term)
            )
        )
        
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return [enrich_invoice_response(i) for i in invoices]

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
    return enrich_invoice_response(inv)

@router.post("/from-appointment/{appointment_id}", response_model=InvoiceResponse)
def create_from_appointment(
    appointment_id: int,
    payment_method: str = "Tiền mặt",
    discount_amount: float = 0.0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        inv = create_invoice_from_appointment(
            db=db,
            appointment_id=appointment_id,
            payment_method=payment_method,
            discount_amount=max(0.0, float(discount_amount or 0.0))
        )
        return enrich_invoice_response(inv)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi tạo hóa đơn từ lịch hẹn: {str(e)}")

@router.post("", response_model=InvoiceResponse)
def create_custom_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    owner = db.query(PetOwner).filter(PetOwner.id == data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin chủ nuôi")
        
    if not data.items or len(data.items) == 0:
        raise HTTPException(status_code=400, detail="Hóa đơn phải có ít nhất một mặt hàng hoặc dịch vụ")
        
    for item in data.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Số lượng của mặt hàng '{item.item_name}' phải lớn hơn 0")
        if item.unit_price < 0:
            raise HTTPException(status_code=400, detail=f"Đơn giá của mặt hàng '{item.item_name}' không được âm")
            
    subtotal = sum(item.unit_price * item.quantity for item in data.items)
    discount = max(0.0, float(data.discount_amount or 0.0))
    tax = max(0.0, float(data.tax_amount or 0.0))
    total_amount = max(0.0, subtotal - discount + tax)
    
    try:
        invoice = Invoice(
            invoice_code=generate_invoice_code(),
            appointment_id=data.appointment_id,
            owner_id=data.owner_id,
            subtotal=subtotal,
            discount_amount=discount,
            tax_amount=tax,
            total_amount=total_amount,
            payment_method=data.payment_method or PaymentMethod.CASH.value,
            payment_status=data.payment_status or PaymentStatus.PAID.value,
            payment_time=datetime.now() if data.payment_status == PaymentStatus.PAID.value else None,
            notes=data.notes
        )
        db.add(invoice)
        db.flush()
        
        for item_data in data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                item_name=item_data.item_name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.unit_price * item_data.quantity
            )
            db.add(item)
            
        # Nếu có liên kết lịch hẹn và đã thanh toán, chuyển trạng thái lịch hẹn sang COMPLETED
        if data.appointment_id:
            appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
            if appt and data.payment_status == PaymentStatus.PAID.value:
                appt.status = AppointmentStatus.COMPLETED.value
                
        db.commit()
        db.refresh(invoice)
        return enrich_invoice_response(invoice)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu hóa đơn: {str(e)}")

@router.put("/{invoice_id}/pay")
def pay_invoice(
    invoice_id: int,
    payment_method: str = "Tiền mặt",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
        
    try:
        inv.payment_status = PaymentStatus.PAID.value
        inv.payment_method = payment_method
        inv.payment_time = datetime.now()
        
        if inv.appointment:
            inv.appointment.status = AppointmentStatus.COMPLETED.value
            
        db.commit()
        return {"message": "Thanh toán hóa đơn thành công", "invoice_code": inv.invoice_code}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi thanh toán: {str(e)}")

@router.put("/{invoice_id}/cancel")
def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
        
    try:
        inv.payment_status = PaymentStatus.CANCELLED.value
        db.commit()
        return {"message": "Đã hủy hóa đơn thành công", "invoice_code": inv.invoice_code}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi hủy hóa đơn: {str(e)}")

@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
        
    try:
        db.delete(inv)
        db.commit()
        return {"message": "Đã xóa hóa đơn thành công", "id": invoice_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa hóa đơn: {str(e)}")

