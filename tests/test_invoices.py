import pytest
from fastapi.testclient import TestClient
from main import app
from backend.services.invoice_service import calculate_invoice_totals, generate_invoice_code

client = TestClient(app)

def get_auth_token():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_generate_invoice_code_format():
    code = generate_invoice_code()
    assert code.startswith("INV-")
    assert len(code) >= 15

def test_calculate_invoice_totals_standard():
    items = [
        {"unit_price": 150000.0, "quantity": 1},
        {"unit_price": 50000.0, "quantity": 2}
    ]
    subtotal, total = calculate_invoice_totals(items, discount_amount=25000.0, tax_amount=0.0)
    assert subtotal == 250000.0
    assert total == 225000.0

def test_calculate_invoice_totals_with_discount_exceeding_subtotal():
    items = [{"unit_price": 100000.0, "quantity": 1}]
    subtotal, total = calculate_invoice_totals(items, discount_amount=150000.0, tax_amount=0.0)
    assert subtotal == 100000.0
    assert total == 0.0 # Không âm

def test_api_invoices_empty_items_validation():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/v1/invoices", json={
        "owner_id": 1,
        "items": []
    }, headers=headers)
    assert res.status_code == 400
    assert "ít nhất" in res.json()["detail"].lower()

def test_api_invoices_crud_flow():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List pending appointments
    res_pending = client.get("/api/v1/invoices/pending-appointments", headers=headers)
    assert res_pending.status_code == 200

    # 2. Create custom invoice
    res_create = client.post("/api/v1/invoices", json={
        "owner_id": 1,
        "discount_amount": 10000,
        "tax_amount": 0,
        "payment_method": "Tiền mặt",
        "payment_status": "Chưa thanh toán",
        "notes": "Hóa đơn test tự động",
        "items": [
            {"item_name": "Thuốc xịt ve rận Hantox", "quantity": 1, "unit_price": 75000, "total_price": 75000}
        ]
    }, headers=headers)
    assert res_create.status_code == 200
    inv_data = res_create.json()
    assert inv_data["total_amount"] == 65000.0
    inv_id = inv_data["id"]

    # 3. Pay invoice
    res_pay = client.put(f"/api/v1/invoices/{inv_id}/pay", json={"payment_method": "Chuyển khoản / QR"}, headers=headers)
    assert res_pay.status_code == 200

    # 4. Delete invoice
    res_del = client.delete(f"/api/v1/invoices/{inv_id}", headers=headers)
    assert res_del.status_code == 200

