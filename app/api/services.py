from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.service import Service
from app.schemas.pet_dto import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["Quản lý Dịch vụ & Bảng giá (Services)"])

@router.get("", response_model=List[ServiceResponse])
def list_services(
    category: Optional[str] = Query(None, description="Lọc theo danh mục"),
    is_active: Optional[bool] = Query(None, description="Lọc dịch vụ đang hoạt động"),
    db: Session = Depends(get_db)
):
    query = db.query(Service)
    if category:
        query = query.filter(Service.category == category)
    if is_active is not None:
        query = query.filter(Service.is_active == is_active)
    return query.all()

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
    return service

@router.post("", response_model=ServiceResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    service = Service(**service_data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
        
    for key, value in service_data.model_dump(exclude_unset=True).items():
        setattr(service, key, value)
        
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
        
    db.delete(service)
    db.commit()
    return {"message": "Đã xóa dịch vụ thành công"}
