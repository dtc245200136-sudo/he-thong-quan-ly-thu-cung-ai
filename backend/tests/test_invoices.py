import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, Owner, Invoice
from backend.app.routes.invoices import generate_invoice_code

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    owner = Owner(name="Trần Thị B", phone="0977111222")
    session.add(owner)
    session.commit()

    yield session
    session.close()

def test_generate_invoice_code_format(db_session):
    code1 = generate_invoice_code(db_session)
    assert code1.startswith("INV-")
    assert code1.endswith("-001")

def test_invoice_calculation(db_session):
    total = 200000.0
    discount = 30000.0
    final = max(0.0, total - discount)
    assert final == 170000.0

    inv = Invoice(
        invoice_code="INV-20261101-001",
        owner_id=1,
        total_amount=total,
        discount_amount=discount,
        final_amount=final,
        payment_method="Tiền mặt",
        payment_status="paid"
    )
    db_session.add(inv)
    db_session.commit()

    saved_inv = db_session.query(Invoice).filter(Invoice.id == inv.id).first()
    assert saved_inv is not None
    assert saved_inv.final_amount == 170000.0
    assert saved_inv.payment_status == "paid"
