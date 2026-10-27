import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.core.database import Base
from backend.models.owner import PetOwner
from backend.models.pet import Pet
from backend.models.vaccination import VaccinationSchedule, VaccinationStatus
from main import app

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    owner = PetOwner(full_name="Nguyễn Văn An", phone="0987654321")
    session.add(owner)
    session.flush()

    pet = Pet(owner_id=owner.id, name="Cún Vàng", species="Chó", breed="Golden Retriever")
    session.add(pet)
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_vaccination_schedule_properties_and_overdue(db):
    pet = db.query(Pet).first()

    # 1. Lịch tiêm trong tương lai (SCHEDULED, không overdue)
    future_date = date.today() + timedelta(days=14)
    vac_future = VaccinationSchedule(
        pet_id=pet.id,
        vaccine_name="Vaccine 7 bệnh",
        dose_number="Mũi 2",
        next_due_date=future_date,
        status=VaccinationStatus.SCHEDULED.value
    )
    db.add(vac_future)
    db.commit()
    db.refresh(vac_future)

    assert vac_future.is_overdue is False
    assert vac_future.effective_status == "SCHEDULED"
    assert vac_future.status_display == "Đã lên lịch"
    assert vac_future.days_until_due == 14

    # 2. Lịch tiêm trong quá khứ chưa tiêm -> Tự động nhận diện OVERDUE
    past_date = date.today() - timedelta(days=5)
    vac_past = VaccinationSchedule(
        pet_id=pet.id,
        vaccine_name="Vaccine Dại",
        dose_number="Mũi nhắc lại",
        next_due_date=past_date,
        status=VaccinationStatus.SCHEDULED.value
    )
    db.add(vac_past)
    db.commit()
    db.refresh(vac_past)

    assert vac_past.is_overdue is True
    assert vac_past.effective_status == "OVERDUE"
    assert vac_past.status_display == "Quá hạn tiêm"
    assert vac_past.days_until_due == -5


def test_vaccination_mark_administered_method(db):
    pet = db.query(Pet).first()
    due_date = date.today()
    vac = VaccinationSchedule(
        pet_id=pet.id,
        vaccine_name="Tẩy giun định kỳ",
        next_due_date=due_date,
        status=VaccinationStatus.SCHEDULED.value
    )
    db.add(vac)
    db.commit()

    # Thực hiện tiêm
    next_cycle = date.today() + timedelta(days=90)
    vac.mark_administered(
        administered_date=date.today(),
        next_due_date=next_cycle,
        dose_number="Mũi 1",
        batch_number="ZOETIS-2026-X9",
        manufacturer="Zoetis",
        reaction_notes="Bình thường, không sốt",
        notes="Tiêm 1ml dưới da gáy"
    )
    db.commit()
    db.refresh(vac)

    assert vac.status == VaccinationStatus.COMPLETED.value
    assert vac.effective_status == "COMPLETED"
    assert vac.is_overdue is False
    assert vac.batch_number == "ZOETIS-2026-X9"
    assert vac.manufacturer == "Zoetis"
    assert vac.next_due_date == next_cycle


def test_vaccination_to_dict_and_repr(db):
    pet = db.query(Pet).first()
    vac = VaccinationSchedule(
        pet_id=pet.id,
        vaccine_name="Vaccine 4 bệnh cho Mèo",
        dose_number="Mũi 1",
        next_due_date=date.today() + timedelta(days=21),
        status=VaccinationStatus.SCHEDULED.value
    )
    db.add(vac)
    db.commit()
    db.refresh(vac)

    d = vac.to_dict()
    assert d["vaccine_name"] == "Vaccine 4 bệnh cho Mèo"
    assert d["status"] == "SCHEDULED"
    assert d["days_until_due"] == 21
    assert "VaccinationSchedule" in repr(vac)


def test_core_protocols_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/vaccinations/core-protocols")
    assert res.status_code == 200
    data = res.json()
    assert "dog_core" in data
    assert "cat_core" in data
    assert len(data["dog_core"]) >= 3
    assert len(data["cat_core"]) >= 3
