from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base

class CareRecord(Base):
    __tablename__ = "care_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    record_date = Column(DateTime, default=func.now(), nullable=False)
    weight_kg = Column(Float, nullable=True)
    
    # Tình trạng sức khỏe & da lông chi tiết
    coat_skin_condition = Column(String(255), nullable=True) # Vd: Lông mượt, da sạch / Da có nấm nhẹ / Rụng lông mùa
    ears_eyes_teeth = Column(String(255), nullable=True)     # Vd: Tai sạch, mắt sáng, nhiều vôi răng
    behavior_mood = Column(String(255), nullable=True)       # Vd: Hợp tác tốt, hơi nhát nước, hiền lành
    services_performed = Column(Text, nullable=True)         # Vd: Tắm sấy thảo dược, cắt móng, tỉa lông tạo kiểu tròn
    
    notes = Column(Text, nullable=True)                      # Lời dặn dò của nhân viên cho chủ
    before_photo_url = Column(String(255), nullable=True)
    after_photo_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pet = relationship("Pet", back_populates="care_records")
    appointment = relationship("Appointment", back_populates="care_record")
    staff = relationship("User")
