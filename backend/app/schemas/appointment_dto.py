from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

class AppointmentBase(BaseModel):
    pet_id: int
    service_id: int
    staff_id: Optional[int] = None
    appointment_time: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    pet_id: Optional[int] = None
    service_id: Optional[int] = None
    staff_id: Optional[int] = None
    appointment_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    pet_id: int
    owner_id: int
    service_id: int
    staff_id: Optional[int] = None
    appointment_time: datetime
    end_time: datetime
    status: str
    notes: Optional[str] = None
    reminder_sent: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    pet_name: Optional[str] = None
    pet_species: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    service_name: Optional[str] = None
    service_price: Optional[float] = None
    staff_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Vaccination Schemas
class VaccinationBase(BaseModel):
    pet_id: int
    vaccine_name: str
    dose_number: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    administered_date: Optional[date] = None
    next_due_date: date
    status: str = "SCHEDULED"
    administered_by_id: Optional[int] = None
    reaction_notes: Optional[str] = None
    notes: Optional[str] = None

class VaccinationCreate(VaccinationBase):
    pass

class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    dose_number: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    administered_date: Optional[date] = None
    next_due_date: Optional[date] = None
    status: Optional[str] = None
    administered_by_id: Optional[int] = None
    reaction_notes: Optional[str] = None
    notes: Optional[str] = None

class VaccinationResponse(VaccinationBase):
    id: int
    reminder_sent: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pet_name: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    status_display: Optional[str] = None
    is_overdue: Optional[bool] = None
    days_until_due: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

