import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User, UserRole
from app.models.owner import PetOwner
from app.models.pet import Pet
from app.models.service import Service
from app.models.appointment import Appointment, AppointmentStatus
from app.services.appointment_service import check_appointment_conflict, calculate_end_time

# Dùng SQLite In-Memory cho Testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Tạo dữ liệu test cơ bản
    staff = User(username="test_groomer", hashed_password="pw", full_name="Groomer Test", role="STAFF")
    owner = PetOwner(full_name="Chủ test", phone="0999888777")
    session.add_all([staff, owner])
    session.flush()
    
    pet = Pet(owner_id=owner.id, name="Test Dog", species="Chó", breed="Poodle")
    service = Service(name="Tắm spa", category="Tắm", price=100000.0, duration_minutes=60)
    session.add_all([pet, service])
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_calculate_end_time():
    start = datetime(2026, 8, 20, 10, 0)
    end = calculate_end_time(start, 60)
    assert end == datetime(2026, 8, 20, 11, 0)

def test_no_conflict_on_empty_schedule(db):
    start = datetime.now() + timedelta(days=1, hours=2)
    end = start + timedelta(minutes=60)
    staff = db.query(User).first()
    
    is_conflict, reason = check_appointment_conflict(db, start, end, staff_id=staff.id)
    assert is_conflict is False
    assert reason is None

def test_detect_same_staff_slot_conflict(db):
    staff = db.query(User).first()
    owner = db.query(PetOwner).first()
    pet = db.query(Pet).first()
    service = db.query(Service).first()
    
    start1 = datetime.now() + timedelta(days=2, hours=3)
    end1 = start1 + timedelta(minutes=60)
    
    # Tạo lịch hẹn 1
    appt1 = Appointment(
        pet_id=pet.id,
        owner_id=owner.id,
        service_id=service.id,
        staff_id=staff.id,
        appointment_time=start1,
        end_time=end1,
        status=AppointmentStatus.CONFIRMED.value
    )
    db.add(appt1)
    db.commit()
    
    # Cố tình đặt lịch hẹn 2 bị giao thoa thời gian (chồng 30 phút) cùng nhân viên
    start2 = start1 + timedelta(minutes=30)
    end2 = start2 + timedelta(minutes=60)
    
    is_conflict, reason = check_appointment_conflict(db, start2, end2, staff_id=staff.id)
    assert is_conflict is True
    assert "bận trong khung giờ" in reason
