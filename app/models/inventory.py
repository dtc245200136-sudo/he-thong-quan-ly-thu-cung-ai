import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class InventoryCategory(str, enum.Enum):
    MEDICINE = "Thuốc điều trị"
    VACCINE = "Vắc xin thú y"
    SPA_COSMETIC = "Mỹ phẩm Spa & Grooming"
    NUTRITION = "Thức ăn & Dinh dưỡng"
    MEDICAL_SUPPLIES = "Vật tư & Thiết bị y tế"
    ACCESSORIES = "Phụ kiện & Đồ dùng"

class StockStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"        # Còn hàng (Đủ định mức)
    LOW_STOCK = "LOW_STOCK"      # Cảnh báo sắp hết hàng
    OUT_OF_STOCK = "OUT_OF_STOCK"# Hết hàng
    EXPIRED = "EXPIRED"          # Hết hạn sử dụng

class TransactionType(str, enum.Enum):
    IMPORT = "IMPORT"  # Nhập kho (Mua hàng từ NCC)
    EXPORT = "EXPORT"  # Xuất kho (Sử dụng dịch vụ Spa/Khám hoặc Bán lẻ)
    ADJUST = "ADJUST"  # Điều chỉnh kiểm kê

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False) # Mã sản phẩm / Barcode
    name = Column(String(200), index=True, nullable=False)
    category = Column(String(100), default=InventoryCategory.MEDICINE.value, nullable=False)
    unit = Column(String(50), default="Lọ", nullable=False) # Chai, Lọ, Hộp, Gói, Cái, Túi
    quantity = Column(Float, default=0.0, nullable=False)
    min_threshold = Column(Float, default=5.0, nullable=False) # Định mức tồn tối thiểu
    cost_price = Column(Float, default=0.0, nullable=False) # Giá nhập vốn
    selling_price = Column(Float, default=0.0, nullable=False) # Giá bán/tính phí
    batch_number = Column(String(100), nullable=True) # Số lô sản xuất
    expiry_date = Column(Date, nullable=True) # Hạn sử dụng
    supplier = Column(String(200), nullable=True) # Nhà cung cấp
    shelf_location = Column(String(100), nullable=True) # Vị trí ngăn kệ
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Quan hệ với lịch sử xuất nhập
    transactions = relationship("StockTransaction", back_populates="item", cascade="all, delete-orphan")

class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(String(20), default=TransactionType.IMPORT.value, nullable=False) # IMPORT, EXPORT, ADJUST
    quantity = Column(Float, nullable=False) # Số lượng thay đổi (dương)
    unit_price = Column(Float, default=0.0, nullable=False)
    total_price = Column(Float, default=0.0, nullable=False)
    performer_name = Column(String(100), default="Thủ kho PetCare", nullable=False) # Người thực hiện
    reference_code = Column(String(100), nullable=True) # Mã phiếu nhập/hóa đơn/phiếu khám
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("InventoryItem", back_populates="transactions")
