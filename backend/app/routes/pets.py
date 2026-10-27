from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Pet, Owner
from ..schemas import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/api/pets", tags=["Pets"])

@router.get("", response_model=List[PetResponse])
def get_pets(
    owner_id: Optional[int] = Query(None),
    species: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Pet)
    if owner_id:
        query = query.filter(Pet.owner_id == owner_id)
    if species:
        query = query.filter(Pet.species == species)
    if q:
        query = query.filter((Pet.name.ilike(f"%{q}%")) | (Pet.breed.ilike(f"%{q}%")))
        
    pets = query.order_by(Pet.id.desc()).all()
    results = []
    for p in pets:
        resp = PetResponse.model_validate(p)
        if p.owner:
            resp.owner_name = p.owner.name
            resp.owner_phone = p.owner.phone
        results.append(resp)
    return results

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng!")
    resp = PetResponse.model_validate(pet)
    if pet.owner:
        resp.owner_name = pet.owner.name
        resp.owner_phone = pet.owner.phone
    return resp

@router.post("", response_model=PetResponse)
def create_pet(data: PetCreate, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.id == data.owner_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Chủ nuôi không tồn tại!")
    
    pet = Pet(**data.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    resp = PetResponse.model_validate(pet)
    resp.owner_name = owner.name
    resp.owner_phone = owner.phone
    return resp

@router.put("/{pet_id}", response_model=PetResponse)
def update_pet(pet_id: int, data: PetUpdate, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng!")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    resp = PetResponse.model_validate(pet)
    if pet.owner:
        resp.owner_name = pet.owner.name
        resp.owner_phone = pet.owner.phone
    return resp

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Không tìm thấy thú cưng!")
    db.delete(pet)
    db.commit()
    return {"message": f"Đã xóa thành công hồ sơ thú cưng '{pet.name}'."}
