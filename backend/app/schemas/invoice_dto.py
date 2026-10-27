from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class InvoiceItemBase(BaseModel):
    item_name: str
    quantity: int = 1
    unit_price: float
    total_price: float

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    owner_id: int
    appointment_id: Optional[int] = None
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    payment_method: str = "Tiền mặt"
    payment_status: str = "Đã thanh toán"
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    discount_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: int
    invoice_code: str
    appointment_id: Optional[int] = None
    owner_id: int
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: str
    payment_status: str
    payment_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_address: Optional[str] = None
    items: List[InvoiceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
