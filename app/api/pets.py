from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pet import Pet
from app.models.owner import PetOwner
from app.schemas.pet_dto import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/pets", tags=["Quản lý Thú cưng (Pets)"])

def enrich_pet_response(pet: Pet) -> dict:
    return {
        "id": pet.id,
        "owner_id": pet.owner_id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "age_years": pet.age_years,
        "age_months": pet.age_months,
        "gender": pet.gender,
        "weight_kg": pet.weight_kg,
        "microchip_id": pet.microchip_id,
        "allergies": pet.allergies,
        "medical_notes": pet.medical_notes,
        "avatar_url": pet.avatar_url,
        "created_at": pet.created_at,
        "owner_name": pet.owner.full_name if pet.owner else None,
        "owner_phone": pet.owner.phone if pet.owner else None
    }

@router.get("", response_model=List[PetResponse])
def list_pets(
    owner_id: Optional[int] = Query(None, description="Lọc theo ID chủ nuôi"),
    species: Optional[str] = Query(None, description="Lọc theo loài (Chó, Mèo,...)"),
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc giống"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Pet)
    if owner_id:
        query = query.filter(Pet.owner_id == owner_id)
    if species:
        query = query.filter(Pet.species == species)
    if search:
        query = query.filter(
            (Pet.name.ilike(f"%{search}%")) |
            (Pet.breed.ilike(f"%{search}%"))
        )
    pets = query.order_by(Pet.id.desc()).offset(skip).limit(limit).all()
    return [enrich_pet_response(p) for p in pets]

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thú cưng")
    return enrich_pet_response(pet)

@router.post("", response_model=PetResponse)
def create_pet(
    pet_data: PetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    owner = db.query(PetOwner).filter(PetOwner.id == pet_data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy chủ nuôi tương ứng")
        
    pet = Pet(**pet_data.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return enrich_pet_response(pet)

@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: int,
    pet_data: PetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thú cưng")
        
    for key, value in pet_data.model_dump(exclude_unset=True).items():
        setattr(pet, key, value)
        
    db.commit()
    db.refresh(pet)
    return enrich_pet_response(pet)

@router.delete("/{pet_id}")
def delete_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thú cưng")
        
    db.delete(pet)
    db.commit()
    return {"message": "Đã xóa thú cưng thành công"}
