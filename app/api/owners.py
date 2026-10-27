from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.owner import PetOwner
from app.schemas.pet_dto import PetOwnerCreate, PetOwnerUpdate, PetOwnerResponse

router = APIRouter(prefix="/owners", tags=["Quản lý Chủ nuôi (Pet Owners)"])

@router.get("", response_model=List[PetOwnerResponse])
def list_owners(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc số điện thoại"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(PetOwner)
    if search:
        query = query.filter(
            (PetOwner.full_name.ilike(f"%{search}%")) |
            (PetOwner.phone.ilike(f"%{search}%"))
        )
    return query.order_by(PetOwner.id.desc()).offset(skip).limit(limit).all()

@router.get("/{owner_id}", response_model=PetOwnerResponse)
def get_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    owner = db.query(PetOwner).filter(PetOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin chủ nuôi")
    return owner

@router.post("", response_model=PetOwnerResponse)
def create_owner(
    owner_data: PetOwnerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing = db.query(PetOwner).filter(PetOwner.phone == owner_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã được đăng ký bởi chủ nuôi khác")
        
    owner = PetOwner(**owner_data.model_dump())
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner

@router.put("/{owner_id}", response_model=PetOwnerResponse)
def update_owner(
    owner_id: int,
    owner_data: PetOwnerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    owner = db.query(PetOwner).filter(PetOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin chủ nuôi")
        
    for key, value in owner_data.model_dump(exclude_unset=True).items():
        setattr(owner, key, value)
        
    db.commit()
    db.refresh(owner)
    return owner

@router.delete("/{owner_id}")
def delete_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    owner = db.query(PetOwner).filter(PetOwner.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin chủ nuôi")
        
    db.delete(owner)
    db.commit()
    return {"message": "Đã xóa chủ nuôi và các thú cưng liên quan thành công"}
