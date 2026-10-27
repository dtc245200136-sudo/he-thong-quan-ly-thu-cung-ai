import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.owner import PetOwner
from app.models.pet import Pet
from app.models.care_record import CareRecord

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    owner = PetOwner(full_name="Chủ Miu", phone="0911222333")
    session.add(owner)
    session.flush()
    
    pet = Pet(owner_id=owner.id, name="Miu", species="Mèo", weight_kg=4.0)
    session.add(pet)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_care_record_and_update_pet_weight(db):
    pet = db.query(Pet).first()
    assert pet.weight_kg == 4.0
    
    new_weight = 4.5
    care = CareRecord(
        pet_id=pet.id,
        record_date=datetime.now(),
        weight_kg=new_weight,
        coat_skin_condition="Da sạch, lông mềm",
        behavior_mood="Hợp tác tốt"
    )
    db.add(care)
    pet.weight_kg = new_weight
    db.commit()
    
    # Kiểm tra
    saved_care = db.query(CareRecord).filter(CareRecord.pet_id == pet.id).first()
    assert saved_care is not None
    assert saved_care.weight_kg == 4.5
    assert pet.weight_kg == 4.5
