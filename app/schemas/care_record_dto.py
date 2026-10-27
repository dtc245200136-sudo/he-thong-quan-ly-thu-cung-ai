from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CareRecordBase(BaseModel):
    pet_id: int
    appointment_id: Optional[int] = None
    staff_id: Optional[int] = None
    record_date: Optional[datetime] = None
    weight_kg: Optional[float] = None
    coat_skin_condition: Optional[str] = None
    ears_eyes_teeth: Optional[str] = None
    behavior_mood: Optional[str] = None
    services_performed: Optional[str] = None
    notes: Optional[str] = None
    before_photo_url: Optional[str] = None
    after_photo_url: Optional[str] = None

class CareRecordCreate(CareRecordBase):
    pass

class CareRecordUpdate(BaseModel):
    weight_kg: Optional[float] = None
    coat_skin_condition: Optional[str] = None
    ears_eyes_teeth: Optional[str] = None
    behavior_mood: Optional[str] = None
    services_performed: Optional[str] = None
    notes: Optional[str] = None
    before_photo_url: Optional[str] = None
    after_photo_url: Optional[str] = None

class CareRecordResponse(CareRecordBase):
    id: int
    created_at: Optional[datetime] = None
    pet_name: Optional[str] = None
    pet_species: Optional[str] = None
    pet_breed: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    staff_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
