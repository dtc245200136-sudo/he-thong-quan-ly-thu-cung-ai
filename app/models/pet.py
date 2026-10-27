import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class PetSpecies(str, enum.Enum):
    DOG = "Chó"
    CAT = "Mèo"
    RABBIT = "Thỏ"
    HAMSTER = "Hamster / Chuột kiểng"
    BIRD = "Chim cảnh"
    REPTILE = "Bò sát / Rùa"
    HEDGEHOG = "Nhím kiểng"
    OTHER = "Khác"

class PetGender(str, enum.Enum):
    MALE = "Đực"
    FEMALE = "Cái"
    UNKNOWN = "Không xác định"

class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("pet_owners.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    species = Column(String(50), default="Chó", nullable=False) # Chó, Mèo, Khác
    breed = Column(String(100), nullable=True) # Poodle, Corgi, Mèo Ba Tư, Golden...
    age_years = Column(Integer, default=1)
    age_months = Column(Integer, default=0)
    gender = Column(String(20), default="Đực")
    weight_kg = Column(Float, default=3.5)
    microchip_id = Column(String(50), nullable=True)
    allergies = Column(Text, nullable=True) # Tiền sử dị ứng thức ăn/thuốc
    medical_notes = Column(Text, nullable=True) # Bệnh lý nền, ghi chú tính cách (hung dữ, nhát,...)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("PetOwner", back_populates="pets")
    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")
    care_records = relationship("CareRecord", back_populates="pet", cascade="all, delete-orphan")
    vaccinations = relationship("VaccinationSchedule", back_populates="pet", cascade="all, delete-orphan")
