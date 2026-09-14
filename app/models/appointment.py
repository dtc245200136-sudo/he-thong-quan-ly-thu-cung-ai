import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AppointmentStatus(str, enum.Enum):
    PENDING = "PENDING"         # Chờ xác nhận
    CONFIRMED = "CONFIRMED"     # Đã xác nhận
    IN_PROGRESS = "IN_PROGRESS" # Đang thực hiện
    COMPLETED = "COMPLETED"     # Đã hoàn thành
    CANCELLED = "CANCELLED"     # Đã hủy

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("pet_owners.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nhân viên phụ trách
    
    appointment_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(30), default=AppointmentStatus.CONFIRMED.value, nullable=False)
    notes = Column(Text, nullable=True)
    
    reminder_sent = Column(DateTime, nullable=True) # Thời điểm gửi tin nhắn AI nhắc lịch
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pet = relationship("Pet", back_populates="appointments")
    owner = relationship("PetOwner")
    service = relationship("Service", back_populates="appointments")
    staff = relationship("User")
    care_record = relationship("CareRecord", back_populates="appointment", uselist=False)
    invoice = relationship("Invoice", back_populates="appointment", uselist=False)
