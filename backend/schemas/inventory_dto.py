from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class InventoryItemBase(BaseModel):
    sku: str
    name: str
    category: str = "Thuốc điều trị"
    unit: str = "Lọ"
    quantity: float = 0.0
    min_threshold: float = 5.0
    cost_price: float = 0.0
    selling_price: float = 0.0
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None
    shelf_location: Optional[str] = None
    notes: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    min_threshold: Optional[float] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None
    shelf_location: Optional[str] = None
    notes: Optional[str] = None

class InventoryItemResponse(InventoryItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stock_status: Optional[str] = "IN_STOCK"
    is_expiring_soon: Optional[bool] = False
    days_to_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class StockInRequest(BaseModel):
    item_id: int
    quantity: float
    unit_cost: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None
    performer_name: Optional[str] = "Thủ kho"
    reference_code: Optional[str] = None
    notes: Optional[str] = None

class StockOutRequest(BaseModel):
    item_id: int
    quantity: float
    reason: Optional[str] = "Dùng cho dịch vụ Spa / Khám bệnh"
    performer_name: Optional[str] = "Kỹ thuật viên"
    reference_code: Optional[str] = None
    notes: Optional[str] = None

class StockTransactionResponse(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str] = None
    item_sku: Optional[str] = None
    transaction_type: str
    quantity: float
    unit_price: float
    total_price: float
    performer_name: str
    reference_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class InventoryStatsResponse(BaseModel):
    total_items_count: int
    total_stock_quantity: float
    total_inventory_value_vnd: float
    low_stock_count: int
    expiring_soon_count: int
    expired_count: int
    category_breakdown: List[dict]
