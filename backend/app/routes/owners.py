from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Owner, Pet
from ..schemas import OwnerCreate, OwnerUpdate, OwnerResponse

router = APIRouter(prefix="/api/owners", tags=["Owners"])

@router.get("", response_model=List[OwnerResponse])
def get_owners(
    q: Optional[str] = Query(None, description="Search by name or phone"),
    db: Session = Depends(get_db)
):
    query = db.query(Owner)
    if q:
        query = query.filter(
            (Owner.name.ilike(f"%{q}%")) | (Owner.phone.ilike(f"%{q}%"))
        )
    owners = query.order_by(Owner.id.desc()).all()
    results = []
    for o in owners:
        resp = OwnerResponse.model_validate(o)
        resp.pet_count = len(o.pets)
        results.append(resp)
    return results

@router.get("/{owner_id}", response_model=OwnerResponse)
def get_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy chủ nuôi!")
    resp = OwnerResponse.model_validate(owner)
    resp.pet_count = len(owner.pets)
    return resp

@router.post("", response_model=OwnerResponse)
def create_owner(data: OwnerCreate, db: Session = Depends(get_db)):
    # Check phone duplicate
    existing = db.query(Owner).filter(Owner.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được đăng ký bởi chủ nuôi khác!")
    owner = Owner(**data.model_dump())
    db.add(owner)
    db.commit()
    db.refresh(owner)
    resp = OwnerResponse.model_validate(owner)
    resp.pet_count = 0
    return resp

@router.put("/{owner_id}", response_model=OwnerResponse)
def update_owner(owner_id: int, data: OwnerUpdate, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy chủ nuôi!")
    
    update_data = data.model_dump(exclude_unset=True)
    if "phone" in update_data and update_data["phone"] != owner.phone:
        existing = db.query(Owner).filter(Owner.phone == update_data["phone"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng!")

    for key, value in update_data.items():
        setattr(owner, key, value)
    db.commit()
    db.refresh(owner)
    resp = OwnerResponse.model_validate(owner)
    resp.pet_count = len(owner.pets)
    return resp

@router.delete("/{owner_id}")
def delete_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy chủ nuôi!")
    db.delete(owner)
    db.commit()
    return {"message": f"Đã xóa thành công chủ nuôi '{owner.name}' và các thú cưng liên quan."}
