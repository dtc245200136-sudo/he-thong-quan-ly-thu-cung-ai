from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Service
from ..schemas import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/api/services", tags=["Services"])

@router.get("", response_model=List[ServiceResponse])
def get_services(
    category: Optional[str] = Query(None),
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.is_active == True)
    if category:
        query = query.filter(Service.category == category)
    return query.order_by(Service.id.asc()).all()

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    srv = db.query(Service).filter(Service.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ!")
    return srv

@router.post("", response_model=ServiceResponse)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    srv = Service(**data.model_dump())
    db.add(srv)
    db.commit()
    db.refresh(srv)
    return srv

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    srv = db.query(Service).filter(Service.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ!")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(srv, key, value)
    db.commit()
    db.refresh(srv)
    return srv

@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    srv = db.query(Service).filter(Service.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ!")
    srv.is_active = False # Soft delete
    db.commit()
    return {"message": f"Dịch vụ '{srv.name}' đã được chuyển sang trạng thái ngưng hoạt động."}
