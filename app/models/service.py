from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False) # Tắm spa, Cắt tỉa grooming, Khám & Tiêm phòng, Lưu trú Pet Hotel, Combo
    price = Column(Float, nullable=False) # VNĐ
    duration_minutes = Column(Integer, default=60) # Thời lượng ước tính (phút)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="service")
