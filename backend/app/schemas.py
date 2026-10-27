from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- AUTH & USER ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None
    password: str
    role: Optional[str] = "receptionist"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    role: str # admin, receptionist, staff
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- OWNER ---
class OwnerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class OwnerCreate(OwnerBase):
    pass

class OwnerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class OwnerResponse(OwnerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    pet_count: Optional[int] = 0

# --- PET ---
class PetBase(BaseModel):
    name: str
    species: str = "Chó" # Chó, Mèo, Khác
    breed: Optional[str] = None
    age_months: int = 12
    gender: str = "Đực"
    weight_kg: float = 3.0
    allergies: Optional[str] = "Không có"
    medical_history: Optional[str] = None
    avatar_url: Optional[str] = None
    notes: Optional[str] = None

class PetCreate(PetBase):
    owner_id: int

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age_months: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    avatar_url: Optional[str] = None
    notes: Optional[str] = None

class PetResponse(PetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    created_at: datetime

# --- SERVICE ---
class ServiceBase(BaseModel):
    name: str
    category: str = "Spa & Tắm"
    duration_minutes: int = 60
    price: float = 100000.0
    description: Optional[str] = None
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# --- APPOINTMENT ---
class AppointmentCreate(BaseModel):
    pet_id: int
    owner_id: int
    service_id: int
    staff_id: Optional[int] = None
    appointment_date: str # YYYY-MM-DD
    appointment_time: str # HH:MM
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    staff_id: Optional[int] = None
    service_id: Optional[int] = None
    status: Optional[str] = None
    cancel_reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pet_id: int
    pet_name: Optional[str] = None
    pet_species: Optional[str] = None
    pet_breed: Optional[str] = None
    owner_id: int
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    service_id: int
    service_name: Optional[str] = None
    service_price: Optional[float] = None
    staff_id: Optional[int] = None
    staff_name: Optional[str] = None
    appointment_date: str
    appointment_time: str
    status: str
    cancel_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    has_care_record: Optional[bool] = False
    has_invoice: Optional[bool] = False

# --- CARE RECORD ---
class CareRecordCreate(BaseModel):
    pet_id: int
    appointment_id: Optional[int] = None
    staff_id: Optional[int] = None
    record_date: str # YYYY-MM-DD
    fur_skin_condition: str = "Bình thường, sạch sẽ"
    weight_recorded_kg: Optional[float] = None
    behavior_notes: Optional[str] = "Ngoan ngoãn, hợp tác"
    products_used: Optional[str] = "Sữa tắm dịu nhẹ dưỡng ẩm"
    staff_notes: Optional[str] = None
    home_care_instructions: Optional[str] = None

class CareRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pet_id: int
    pet_name: Optional[str] = None
    appointment_id: Optional[int] = None
    staff_id: Optional[int] = None
    staff_name: Optional[str] = None
    record_date: str
    fur_skin_condition: str
    weight_recorded_kg: Optional[float] = None
    behavior_notes: Optional[str] = None
    products_used: Optional[str] = None
    staff_notes: Optional[str] = None
    home_care_instructions: Optional[str] = None
    created_at: datetime

# --- VACCINE REMINDER ---
class VaccineReminderCreate(BaseModel):
    pet_id: int
    vaccine_name: str
    dose_number: int = 1
    administered_date: Optional[str] = None
    next_due_date: str
    notes: Optional[str] = None

class VaccineReminderUpdate(BaseModel):
    status: Optional[str] = None
    administered_date: Optional[str] = None
    next_due_date: Optional[str] = None
    notes: Optional[str] = None

class VaccineReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pet_id: int
    pet_name: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    vaccine_name: str
    dose_number: int
    administered_date: Optional[str] = None
    next_due_date: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

# --- INVOICE ---
class InvoiceCreate(BaseModel):
    appointment_id: Optional[int] = None
    owner_id: int
    total_amount: float
    discount_amount: float = 0.0
    payment_method: str = "Tiền mặt"
    payment_status: str = "paid"
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invoice_code: str
    owner_id: int
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    appointment_id: Optional[int] = None
    service_name: Optional[str] = None
    pet_name: Optional[str] = None
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    payment_status: str
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime

# --- AI REQUEST & RESPONSE ---
class AIReminderRequest(BaseModel):
    reminder_type: str = "appointment" # "appointment" or "vaccine"
    appointment_id: Optional[int] = None
    vaccine_reminder_id: Optional[int] = None
    tone: str = "friendly" # "friendly", "formal", "cute_fun", "sms_short"
    custom_note: Optional[str] = None

class AIReminderResponse(BaseModel):
    title: str
    recipient_name: str
    recipient_phone: str
    message: str
    channel_recommendation: str
    model_used: str

class AISummaryRequest(BaseModel):
    pet_id: int

class AISummaryResponse(BaseModel):
    pet_id: int
    pet_name: str
    summary_markdown: str
    health_alerts: List[str]
    suggested_actions: List[str]
    model_used: str

class AIConsultationRequest(BaseModel):
    pet_id: Optional[int] = None
    question: str
    chat_history: Optional[List[dict]] = None

class AIConsultationResponse(BaseModel):
    answer: str
    medical_disclaimer: str
    is_urgent_medical_alert: bool
    emergency_hotline: Optional[str] = "0988.111.222"
    recommended_topics: List[str]
    model_used: str

class AISettings(BaseModel):
    provider: str
    has_gemini_key: bool
    has_openai_key: bool
