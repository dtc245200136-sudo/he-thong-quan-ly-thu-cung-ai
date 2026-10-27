from datetime import datetime
import random
from sqlalchemy.orm import Session
from backend.models.invoice import Invoice, InvoiceItem, PaymentMethod, PaymentStatus
from backend.models.appointment import Appointment, AppointmentStatus

def generate_invoice_code() -> str:
    now = datetime.now()
    random_digits = random.randint(100, 999)
    return f"INV-{now.strftime('%Y%m%d%H%M')}-{random_digits}"

def calculate_invoice_totals(items_data: list, discount_amount: float = 0.0, tax_amount: float = 0.0) -> tuple:
    subtotal = sum(item["unit_price"] * item.get("quantity", 1) for item in items_data)
    total_amount = max(0.0, subtotal - discount_amount + tax_amount)
    return subtotal, total_amount

def create_invoice_from_appointment(
    db: Session,
    appointment_id: int,
    payment_method: str = PaymentMethod.CASH.value,
    discount_amount: float = 0.0,
    tax_amount: float = 0.0,
    notes: str = None
) -> Invoice:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise ValueError("Không tìm thấy lịch hẹn")
        
    service = appointment.service
    if not service:
        raise ValueError("Không tìm thấy thông tin dịch vụ của lịch hẹn")

    # Kiểm tra xem lịch hẹn đã có hóa đơn chưa
    existing_invoice = db.query(Invoice).filter(Invoice.appointment_id == appointment_id).first()
    if existing_invoice:
        return existing_invoice

    unit_price = service.price
    subtotal = unit_price
    total_amount = max(0.0, subtotal - discount_amount + tax_amount)

    invoice = Invoice(
        invoice_code=generate_invoice_code(),
        appointment_id=appointment.id,
        owner_id=appointment.owner_id,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=PaymentStatus.PAID.value,
        payment_time=datetime.now(),
        notes=notes or f"Thanh toán dịch vụ {service.name} cho bé {appointment.pet.name if appointment.pet else ''}"
    )
    db.add(invoice)
    db.flush()

    # Thêm item dịch vụ chính
    item = InvoiceItem(
        invoice_id=invoice.id,
        item_name=service.name,
        quantity=1,
        unit_price=unit_price,
        total_price=unit_price
    )
    db.add(item)
    
    # Cập nhật trạng thái lịch hẹn sang COMPLETED
    appointment.status = AppointmentStatus.COMPLETED.value
    
    db.commit()
    db.refresh(invoice)
    return invoice
