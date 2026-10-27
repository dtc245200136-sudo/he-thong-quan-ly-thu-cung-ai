import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, Unicode, UnicodeText, Index, text
from sqlalchemy.orm import declarative_base, relationship

String = Unicode
Text = UnicodeText

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(String(20), default="receptionist") # admin, receptionist, staff
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_users_email", "email", unique=True, mssql_where=text("email IS NOT NULL")),
    )

    # Relationships
    assigned_appointments = relationship("Appointment", back_populates="staff", foreign_keys="Appointment.staff_id")
    care_records = relationship("CareRecord", back_populates="staff", foreign_keys="CareRecord.staff_id")


class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="owner")
    invoices = relationship("Invoice", back_populates="owner")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    species = Column(String(50), default="Chó") # Chó, Mèo, Khác
    breed = Column(String(100), nullable=True) # Poodle, Mèo Anh lông ngắn, v.v.
    age_months = Column(Integer, default=12)
    gender = Column(String(10), default="Đực") # Đực, Cái
    weight_kg = Column(Float, default=3.0)
    allergies = Column(String(255), default="Không có")
    medical_history = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("Owner", back_populates="pets")
    appointments = relationship("Appointment", back_populates="pet", cascade="all, delete-orphan")
    care_records = relationship("CareRecord", back_populates="pet", cascade="all, delete-orphan")
    vaccine_reminders = relationship("VaccineReminder", back_populates="pet", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(50), default="Spa & Tắm") # Spa & Tắm, Cắt tỉa tạo kiểu, Vệ sinh, Tiêm phòng & Khám, Khách sạn
    duration_minutes = Column(Integer, default=60)
    price = Column(Float, nullable=False, default=100000.0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    appointments = relationship("Appointment", back_populates="service")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    appointment_date = Column(String(20), nullable=False) # YYYY-MM-DD
    appointment_time = Column(String(10), nullable=False) # HH:MM (e.g. 09:00, 14:30)
    status = Column(String(20), default="confirmed") # pending, confirmed, in_progress, completed, cancelled
    cancel_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    pet = relationship("Pet", back_populates="appointments")
    owner = relationship("Owner", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    staff = relationship("User", back_populates="assigned_appointments", foreign_keys=[staff_id])
    care_record = relationship("CareRecord", back_populates="appointment", uselist=False)
    invoice = relationship("Invoice", back_populates="appointment", uselist=False)


class CareRecord(Base):
    __tablename__ = "care_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    record_date = Column(String(20), nullable=False) # YYYY-MM-DD
    fur_skin_condition = Column(String(255), default="Bình thường, sạch sẽ") # Tình trạng da lông
    weight_recorded_kg = Column(Float, nullable=True)
    behavior_notes = Column(String(255), default="Ngoan ngoãn, hợp tác") # Hành vi
    products_used = Column(String(255), default="Sữa tắm dịu nhẹ dưỡng ẩm") # Sản phẩm đã dùng
    staff_notes = Column(Text, nullable=True) # Ghi chú của nhân viên chăm sóc
    home_care_instructions = Column(Text, nullable=True) # Hướng dẫn cho chủ nuôi
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    pet = relationship("Pet", back_populates="care_records")
    appointment = relationship("Appointment", back_populates="care_record")
    staff = relationship("User", back_populates="care_records", foreign_keys=[staff_id])


class VaccineReminder(Base):
    __tablename__ = "vaccine_reminders"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    vaccine_name = Column(String(120), nullable=False) # e.g., "Vaccine phòng 7 bệnh chó", "Vaccine dại", "Tẩy giun định kỳ"
    dose_number = Column(Integer, default=1)
    administered_date = Column(String(20), nullable=True) # YYYY-MM-DD
    next_due_date = Column(String(20), nullable=False) # YYYY-MM-DD
    status = Column(String(20), default="pending") # pending, completed, overdue
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    pet = relationship("Pet", back_populates="vaccine_reminders")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_code = Column(String(50), unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    total_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(30), default="Tiền mặt") # Tiền mặt, Chuyển khoản QR, Thẻ
    payment_status = Column(String(20), default="paid") # pending, paid, cancelled
    paid_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("Owner", back_populates="invoices")
    appointment = relationship("Appointment", back_populates="invoice")


class AISessionLog(Base):
    __tablename__ = "ai_session_logs"

    id = Column(Integer, primary_key=True, index=True)
    feature_type = Column(String(50), nullable=False) # reminder, summary, consultation
    pet_id = Column(Integer, nullable=True)
    user_prompt = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    has_disclaimer = Column(Boolean, default=True)
    model_name = Column(String(50), default="PetCare-RuleHeuristic-v1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
