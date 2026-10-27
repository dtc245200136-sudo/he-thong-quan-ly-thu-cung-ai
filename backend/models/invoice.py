import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base

class PaymentMethod(str, enum.Enum):
    CASH = "Tiền mặt"
    TRANSFER = "Chuyển khoản / QR"
    CARD = "Thẻ POS"

class PaymentStatus(str, enum.Enum):
    UNPAID = "Chưa thanh toán"
    PAID = "Đã thanh toán"
    REFUNDED = "Đã hoàn tiền"
    CANCELLED = "Đã hủy"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_code = Column(String(50), unique=True, index=True, nullable=False) # Vd: INV-20260819-001
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    owner_id = Column(Integer, ForeignKey("pet_owners.id"), nullable=False)
    
    subtotal = Column(Float, default=0.0, nullable=False)     # Tổng tiền dịch vụ gốc
    discount_amount = Column(Float, default=0.0)             # Giảm giá / Khuyến mãi
    tax_amount = Column(Float, default=0.0)                  # Thuế VAT (nếu có)
    total_amount = Column(Float, default=0.0, nullable=False)# Tổng thanh toán cuối cùng
    
    payment_method = Column(String(50), default=PaymentMethod.CASH.value)
    payment_status = Column(String(50), default=PaymentStatus.PAID.value)
    payment_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("PetOwner", back_populates="invoices")
    appointment = relationship("Appointment", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String(150), nullable=False) # Tên dịch vụ hoặc phụ kiện/spa
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
