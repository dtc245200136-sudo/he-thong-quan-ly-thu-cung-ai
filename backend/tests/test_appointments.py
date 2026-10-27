import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from backend.app.models import Base, Owner, Pet, Service, Appointment, User
from backend.app.routes.appointments import check_appointment_conflict

# In-memory SQLite for testing
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Seed minimal test data
    staff = User(username="staff1", full_name="Kỹ thuật viên 1", email="s1@pet.vn", role="staff", password_hash="pass")
    owner = Owner(name="Nguyễn Văn A", phone="0988000111")
    session.add_all([staff, owner])
    session.commit()

    pet = Pet(owner_id=owner.id, name="Milu", species="Chó", breed="Corgi")
    service = Service(name="Tắm spa", price=120000.0)
    session.add_all([pet, service])
    session.commit()

    yield session
    session.close()

def test_no_conflict_on_empty_slot(db_session):
    # Slot is free -> Should not raise exception
    check_appointment_conflict(
        db=db_session,
        appointment_date="2026-11-01",
        appointment_time="10:00",
        pet_id=1,
        staff_id=1
    )

def test_pet_slot_conflict_detected(db_session):
    # Book an appointment
    apt = Appointment(
        pet_id=1,
        owner_id=1,
        service_id=1,
        staff_id=1,
        appointment_date="2026-11-01",
        appointment_time="10:00",
        status="confirmed"
    )
    db_session.add(apt)
    db_session.commit()

    # Attempting to book the same pet at the exact same slot must raise HTTPException 400
    with pytest.raises(HTTPException) as exc_info:
        check_appointment_conflict(
            db=db_session,
            appointment_date="2026-11-01",
            appointment_time="10:00",
            pet_id=1
        )
    assert exc_info.value.status_code == 400
    assert "Trùng lịch" in exc_info.value.detail

def test_staff_slot_conflict_detected(db_session):
    # Create second pet
    pet2 = Pet(owner_id=1, name="Kiki", species="Chó", breed="Poodle")
    db_session.add(pet2)
    db_session.commit()

    # Staff 1 already booked for pet 1 at 10:00
    apt = Appointment(
        pet_id=1,
        owner_id=1,
        service_id=1,
        staff_id=1,
        appointment_date="2026-11-01",
        appointment_time="10:00",
        status="confirmed"
    )
    db_session.add(apt)
    db_session.commit()

    # Pet 2 attempts to book Staff 1 at the exact same slot -> Must raise conflict
    with pytest.raises(HTTPException) as exc_info:
        check_appointment_conflict(
            db=db_session,
            appointment_date="2026-11-01",
            appointment_time="10:00",
            pet_id=pet2.id,
            staff_id=1
        )
    assert exc_info.value.status_code == 400
    assert "Trùng lịch" in exc_info.value.detail
