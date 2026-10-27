import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, Owner, Pet, CareRecord

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    owner = Owner(name="Lê Văn C", phone="0966333444")
    session.add(owner)
    session.commit()

    pet = Pet(owner_id=owner.id, name="Miu", species="Mèo", weight_kg=3.5)
    session.add(pet)
    session.commit()

    yield session
    session.close()

def test_care_record_creation(db_session):
    record = CareRecord(
        pet_id=1,
        record_date="2026-11-01",
        fur_skin_condition="Lông sạch, da không nấm",
        weight_recorded_kg=3.8,
        behavior_notes="Hiền lành, hợp tác",
        products_used="Sữa tắm dưỡng lông mượt",
        staff_notes="Bé tăng 0.3kg so với tháng trước"
    )
    db_session.add(record)
    
    # Auto update pet weight
    pet = db_session.query(Pet).filter(Pet.id == 1).first()
    pet.weight_kg = record.weight_recorded_kg
    db_session.commit()

    saved_pet = db_session.query(Pet).filter(Pet.id == 1).first()
    assert saved_pet.weight_kg == 3.8

    saved_cr = db_session.query(CareRecord).filter(CareRecord.id == record.id).first()
    assert saved_cr.fur_skin_condition == "Lông sạch, da không nấm"
