from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Invoice, Appointment, Owner
from ..schemas import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

def serialize_invoice(inv: Invoice) -> InvoiceResponse:
    resp = InvoiceResponse.model_validate(inv)
    if inv.owner:
        resp.owner_name = inv.owner.name
        resp.owner_phone = inv.owner.phone
    if inv.appointment:
        if inv.appointment.service:
            resp.service_name = inv.appointment.service.name
        if inv.appointment.pet:
            resp.pet_name = inv.appointment.pet.name
    return resp

def generate_invoice_code(db: Session) -> str:
    today_str = datetime.date.today().strftime("%Y%m%d")
    count_today = db.query(Invoice).filter(Invoice.invoice_code.like(f"INV-{today_str}-%")).count()
    return f"INV-{today_str}-{(count_today + 1):03d}"

@router.get("", response_model=List[InvoiceResponse])
def get_invoices(
    status: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.payment_status == status)
    if owner_id:
        query = query.filter(Invoice.owner_id == owner_id)
    invoices = query.order_by(Invoice.id.desc()).all()
    return [serialize_invoice(inv) for inv in invoices]

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn!")
    return serialize_invoice(inv)

@router.post("", response_model=InvoiceResponse)
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.id == data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Chủ nuôi không tồn tại!")

    # Check if appointment already has an invoice
    if data.appointment_id:
        existing = db.query(Invoice).filter(Invoice.appointment_id == data.appointment_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Lịch hẹn này đã có hóa đơn thanh toán!")

    code = generate_invoice_code(db)
    final_amt = max(0.0, data.total_amount - data.discount_amount)

    invoice = Invoice(
        invoice_code=code,
        owner_id=data.owner_id,
        appointment_id=data.appointment_id,
        total_amount=data.total_amount,
        discount_amount=data.discount_amount,
        final_amount=final_amt,
        payment_method=data.payment_method,
        payment_status=data.payment_status,
        paid_at=datetime.datetime.utcnow() if data.payment_status == "paid" else None,
        notes=data.notes
    )
    db.add(invoice)

    # Mark appointment completed if linked
    if data.appointment_id:
        apt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
        if apt and apt.status != "completed":
            apt.status = "completed"

    db.commit()
    db.refresh(invoice)
    return serialize_invoice(invoice)

@router.patch("/{invoice_id}/pay", response_model=InvoiceResponse)
def mark_invoice_as_paid(invoice_id: int, payment_method: str = "Tiền mặt", db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn!")
    inv.payment_status = "paid"
    inv.payment_method = payment_method
    inv.paid_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(inv)
    return serialize_invoice(inv)

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn!")
    db.delete(inv)
    db.commit()
    return {"message": "Đã xóa hóa đơn thành công."}
