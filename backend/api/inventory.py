from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from backend.core.database import get_db
from backend.models.inventory import InventoryItem, StockTransaction, InventoryCategory, StockStatus, TransactionType
from backend.schemas.inventory_dto import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    StockInRequest,
    StockOutRequest,
    StockTransactionResponse,
    InventoryStatsResponse
)

router = APIRouter(prefix="/inventory", tags=["Quản Lý Kho Hàng & Dược Phẩm (Inventory & Supplies)"])

def enrich_item_status(item: InventoryItem) -> dict:
    """Bổ sung trạng thái tồn kho & cảnh báo hạn sử dụng cho từng sản phẩm"""
    today = date.today()
    stock_status = StockStatus.IN_STOCK.value
    is_expiring_soon = False
    days_to_expiry = None

    # 1. Kiểm tra tồn kho
    if item.quantity <= 0:
        stock_status = StockStatus.OUT_OF_STOCK.value
    elif item.quantity <= item.min_threshold:
        stock_status = StockStatus.LOW_STOCK.value

    # 2. Kiểm tra hạn sử dụng
    if item.expiry_date:
        days_to_expiry = (item.expiry_date - today).days
        if days_to_expiry < 0:
            stock_status = StockStatus.EXPIRED.value
        elif days_to_expiry <= 60: # Cận date trong vòng 60 ngày
            is_expiring_soon = True

    return {
        "id": item.id,
        "sku": item.sku,
        "name": item.name,
        "category": item.category,
        "unit": item.unit,
        "quantity": item.quantity,
        "min_threshold": item.min_threshold,
        "cost_price": item.cost_price,
        "selling_price": item.selling_price,
        "batch_number": item.batch_number,
        "expiry_date": item.expiry_date,
        "supplier": item.supplier,
        "shelf_location": item.shelf_location,
        "notes": item.notes,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "stock_status": stock_status,
        "is_expiring_soon": is_expiring_soon,
        "days_to_expiry": days_to_expiry
    }

@router.get("/items", response_model=List[InventoryItemResponse])
def get_inventory_items(
    category: Optional[str] = Query(None, description="Lọc theo danh mục"),
    status_filter: Optional[str] = Query(None, description="Lọc theo trạng thái: ALL, LOW_STOCK, EXPIRING_SOON, OUT_OF_STOCK"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo Tên, SKU hoặc Vị trí"),
    db: Session = Depends(get_db)
):
    query = db.query(InventoryItem)

    if category and category != "ALL":
        query = query.filter(InventoryItem.category == category)

    if search:
        search_kw = f"%{search.strip()}%"
        query = query.filter(
            or_(
                InventoryItem.name.ilike(search_kw),
                InventoryItem.sku.ilike(search_kw),
                InventoryItem.supplier.ilike(search_kw),
                InventoryItem.shelf_location.ilike(search_kw)
            )
        )

    items = query.order_by(InventoryItem.id.desc()).all()
    enriched = [enrich_item_status(item) for item in items]

    if status_filter:
        if status_filter == "LOW_STOCK":
            enriched = [x for x in enriched if x["stock_status"] == StockStatus.LOW_STOCK.value]
        elif status_filter == "EXPIRING_SOON":
            enriched = [x for x in enriched if x["is_expiring_soon"] or x["stock_status"] == StockStatus.EXPIRED.value]
        elif status_filter == "OUT_OF_STOCK":
            enriched = [x for x in enriched if x["stock_status"] == StockStatus.OUT_OF_STOCK.value]

    return enriched

@router.get("/stats", response_model=InventoryStatsResponse)
def get_inventory_stats(db: Session = Depends(get_db)):
    items = db.query(InventoryItem).all()
    enriched = [enrich_item_status(item) for item in items]

    total_items = len(items)
    total_qty = sum(item.quantity for item in items)
    total_value = sum(item.quantity * item.cost_price for item in items)

    low_stock = sum(1 for x in enriched if x["stock_status"] == StockStatus.LOW_STOCK.value)
    expiring_soon = sum(1 for x in enriched if x["is_expiring_soon"])
    expired = sum(1 for x in enriched if x["stock_status"] == StockStatus.EXPIRED.value)

    # Thống kê theo danh mục
    cat_counts = {}
    for item in items:
        cat = item.category or "Khác"
        if cat not in cat_counts:
            cat_counts[cat] = {"category": cat, "count": 0, "value_vnd": 0.0}
        cat_counts[cat]["count"] += 1
        cat_counts[cat]["value_vnd"] += item.quantity * item.cost_price

    return {
        "total_items_count": total_items,
        "total_stock_quantity": total_qty,
        "total_inventory_value_vnd": total_value,
        "low_stock_count": low_stock,
        "expiring_soon_count": expiring_soon,
        "expired_count": expired,
        "category_breakdown": list(cat_counts.values())
    }

@router.post("/items", response_model=InventoryItemResponse)
def create_inventory_item(item_data: InventoryItemCreate, db: Session = Depends(get_db)):
    sku_clean = item_data.sku.strip().upper()
    existing = db.query(InventoryItem).filter(InventoryItem.sku == sku_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã sản phẩm / SKU '{sku_clean}' đã tồn tại.")

    new_item = InventoryItem(
        sku=sku_clean,
        name=item_data.name.strip(),
        category=item_data.category,
        unit=item_data.unit.strip(),
        quantity=item_data.quantity,
        min_threshold=item_data.min_threshold,
        cost_price=item_data.cost_price,
        selling_price=item_data.selling_price,
        batch_number=item_data.batch_number.strip() if item_data.batch_number else None,
        expiry_date=item_data.expiry_date,
        supplier=item_data.supplier.strip() if item_data.supplier else None,
        shelf_location=item_data.shelf_location.strip() if item_data.shelf_location else None,
        notes=item_data.notes
    )
    db.add(new_item)
    db.flush()

    # Nếu có số lượng ban đầu, ghi nhận giao dịch nhập đầu kỳ
    if item_data.quantity > 0:
        tx = StockTransaction(
            item_id=new_item.id,
            transaction_type=TransactionType.IMPORT.value,
            quantity=item_data.quantity,
            unit_price=item_data.cost_price,
            total_price=item_data.quantity * item_data.cost_price,
            performer_name="Khởi tạo kho ban đầu",
            reference_code=f"INIT-{new_item.sku}",
            notes="Tồn kho đầu kỳ khởi tạo"
        )
        db.add(tx)

    db.commit()
    db.refresh(new_item)
    return enrich_item_status(new_item)

@router.put("/items/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(item_id: int, update_data: InventoryItemUpdate, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng trong kho.")

    if update_data.sku:
        sku_clean = update_data.sku.strip().upper()
        if sku_clean != item.sku:
            existing = db.query(InventoryItem).filter(InventoryItem.sku == sku_clean).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Mã SKU '{sku_clean}' đã được sử dụng.")
            item.sku = sku_clean

    for field, value in update_data.model_dump(exclude_unset=True).items():
        if field != "sku":
            setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return enrich_item_status(item)

@router.delete("/items/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng trong kho.")

    db.delete(item)
    db.commit()
    return {"success": True, "message": f"Đã xóa mặt hàng '{item.name}' khỏi hệ thống kho."}

@router.post("/stock-in")
def stock_in_item(data: StockInRequest, db: Session = Depends(get_db)):
    """Phiếu Nhập kho hàng mới từ Nhà Cung Cấp"""
    item = db.query(InventoryItem).filter(InventoryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng để nhập kho.")

    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Số lượng nhập phải lớn hơn 0.")

    unit_cost = data.unit_cost if (data.unit_cost is not None and data.unit_cost >= 0) else item.cost_price
    
    # Cập nhật số lượng và thông tin lô mới
    item.quantity += data.quantity
    if data.unit_cost is not None and data.unit_cost > 0:
        item.cost_price = data.unit_cost
    if data.batch_number:
        item.batch_number = data.batch_number.strip()
    if data.expiry_date:
        item.expiry_date = data.expiry_date
    if data.supplier:
        item.supplier = data.supplier.strip()

    # Tạo bản ghi lịch sử nhập
    tx = StockTransaction(
        item_id=item.id,
        transaction_type=TransactionType.IMPORT.value,
        quantity=data.quantity,
        unit_price=unit_cost,
        total_price=data.quantity * unit_cost,
        performer_name=data.performer_name or "Thủ kho PetCare",
        reference_code=data.reference_code or f"NK-{datetime.now().strftime('%y%m%d%H%M')}",
        notes=data.notes or f"Nhập hàng từ {item.supplier or 'NCC'}"
    )
    db.add(tx)
    db.commit()
    db.refresh(item)

    return {
        "success": True,
        "message": f"✅ Đã nhập thành công {data.quantity} {item.unit} '{item.name}'. Tồn kho hiện tại: {item.quantity} {item.unit}.",
        "item": enrich_item_status(item),
        "transaction_id": tx.id
    }

@router.post("/stock-out")
def stock_out_item(data: StockOutRequest, db: Session = Depends(get_db)):
    """Phiếu Xuất kho sử dụng dịch vụ Spa / Bác sĩ khám hoặc bán lẻ"""
    item = db.query(InventoryItem).filter(InventoryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng để xuất kho.")

    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Số lượng xuất phải lớn hơn 0.")

    if item.quantity < data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Số lượng tồn kho không đủ để xuất! Tồn hiện tại: {item.quantity} {item.unit}, yêu cầu xuất: {data.quantity} {item.unit}."
        )

    # Giảm tồn kho
    item.quantity -= data.quantity

    # Ghi nhận giao dịch xuất
    tx = StockTransaction(
        item_id=item.id,
        transaction_type=TransactionType.EXPORT.value,
        quantity=data.quantity,
        unit_price=item.cost_price,
        total_price=data.quantity * item.cost_price,
        performer_name=data.performer_name or "Kỹ thuật viên",
        reference_code=data.reference_code or f"XK-{datetime.now().strftime('%y%m%d%H%M')}",
        notes=f"[{data.reason}] {data.notes or ''}"
    )
    db.add(tx)
    db.commit()
    db.refresh(item)

    return {
        "success": True,
        "message": f"📤 Đã xuất thành công {data.quantity} {item.unit} '{item.name}'. Tồn kho còn lại: {item.quantity} {item.unit}.",
        "item": enrich_item_status(item),
        "transaction_id": tx.id
    }

@router.get("/transactions", response_model=List[StockTransactionResponse])
def get_stock_transactions(
    item_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(StockTransaction)
    if item_id:
        query = query.filter(StockTransaction.item_id == item_id)
    if transaction_type and transaction_type != "ALL":
        query = query.filter(StockTransaction.transaction_type == transaction_type)

    txs = query.order_by(StockTransaction.created_at.desc()).limit(limit).all()
    results = []
    for t in txs:
        results.append({
            "id": t.id,
            "item_id": t.item_id,
            "item_name": t.item.name if t.item else "N/A",
            "item_sku": t.item.sku if t.item else "N/A",
            "transaction_type": t.transaction_type,
            "quantity": t.quantity,
            "unit_price": t.unit_price,
            "total_price": t.total_price,
            "performer_name": t.performer_name,
            "reference_code": t.reference_code,
            "notes": t.notes,
            "created_at": t.created_at
        })
    return results
