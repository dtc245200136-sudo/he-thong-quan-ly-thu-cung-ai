from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict

# Owner Schemas
class PetOwnerBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class PetOwnerCreate(PetOwnerBase):
    pass

class PetOwnerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

# Pet Schemas
class PetBase(BaseModel):
    owner_id: int
    name: str
    species: str = "Chó"
    breed: Optional[str] = None
    age_years: int = 1
    age_months: int = 0
    gender: str = "Đực"
    weight_kg: float = 3.5
    microchip_id: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    avatar_url: Optional[str] = None

class PetCreate(PetBase):
    pass

class PetUpdate(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age_years: Optional[int] = None
    age_months: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    microchip_id: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    avatar_url: Optional[str] = None

class PetResponse(PetBase):
    id: int
    created_at: Optional[datetime] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PetOwnerResponse(PetOwnerBase):
    id: int
    created_at: Optional[datetime] = None
    pets: List[PetResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    category: str
    price: float
    duration_minutes: int = 60
    description: Optional[str] = None
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
