# HỆ THỐNG QUẢN LÝ THÚ CƯNG VÀ LỊCH CHĂM SÓC CÓ TÍCH HỢP AI (PETCARE AI)

**ĐẠI HỌC THÁI NGUYÊN - TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG (ICTU)**  
**Học phần:** Ứng dụng trí tuệ nhân tạo (AIA331)  
**Hình thức:** Dự án / Đồ án môn học  
**Mã số đề tài:** 80286  

---

## 🌟 TỔNG QUAN HỆ THỐNG

**PetCare AI** là hệ thống quản lý cửa hàng chăm sóc thú cưng toàn diện kết hợp trí tuệ nhân tạo, giải quyết bài toán:
1. **Quản lý phân quyền (RBAC):** Quản lý (Admin), Lễ tân (Receptionist), Nhân viên chăm sóc (Staff/Groomer) với thanh chuyển quyền Demo 1-click.
2. **Quản lý chủ nuôi & Thú cưng:** Lưu trữ giống loài, độ tuổi, cân nặng, tiền sử dị ứng/bệnh lý.
3. **Quản lý dịch vụ & Bảng giá:** Tắm spa thảo mộc, cắt tỉa tạo kiểu, vệ sinh tai móng, tiêm phòng vaccine, khách sạn thú cưng.
4. **Đặt lịch thông minh:** Thuật toán tự động phát hiện và chặn trùng lịch (Slot conflict detection) cho thú cưng và nhân viên.
5. **Ghi nhận hồ sơ chăm sóc (Pet Care Records):** Lưu trữ tình trạng lông da, cân nặng đo lại, hành vi và hướng dẫn gia đình.
6. **Nhắc lịch tiêm & Tẩy giun:** Tự động phát hiện các mũi tiêm quá hạn hoặc sắp đến hạn.
7. **Lập hóa đơn & Thanh toán:** Tích hợp tính chiết khấu, hình thức tiền mặt, chuyển khoản QR, in hóa đơn chuyên nghiệp.
8. **Thống kê Dashboard:** Trực quan hóa lượt phục vụ, doanh thu và tỷ lệ khách hàng quay lại.
9. **Chức năng AI tích hợp:**
   - **AI Soạn tin nhắn nhắc lịch & tiêm phòng:** Tùy biến phong cách (Thân thiện, Trang trọng, Dễ thương, SMS ngắn gọn), sao chép và mô phỏng gửi Zalo OA / SMS.
   - **AI Tóm tắt hồ sơ chăm sóc:** Phân tích diễn biến thể trạng, biến động cân nặng và cảnh báo lông da.
   - **AI Trợ lý tư vấn chăm sóc:** Giải đáp thắc mắc dinh dưỡng, vệ sinh; tự động nhận diện triệu chứng nguy hiểm và **kích hoạt cảnh báo đỏ y tế thú y kèm Disclaimer bắt buộc**.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```text
Ứng dụng AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint & router mounting
│   │   ├── config.py            # Cấu hình dự án & API keys
│   │   ├── database.py          # Kết nối CSDL SQLite & seed dữ liệu mẫu phong phú
│   │   ├── models.py            # Mô hình dữ liệu ORM (SQLAlchemy)
│   │   ├── schemas.py           # Pydantic Schemas V2
│   │   ├── auth.py              # Xử lý phiên và phân quyền RBAC
│   │   ├── ai_service.py        # Module AI (Gemini, OpenAI, Heuristic fallback & Guardrails)
│   │   └── routes/              # Các API endpoints RESTful
│   │       ├── auth.py
│   │       ├── owners.py
│   │       ├── pets.py
│   │       ├── services.py
│   │       ├── appointments.py
│   │       ├── care_records.py
│   │       ├── vaccines.py
│   │       ├── invoices.py
│   │       ├── analytics.py
│   │       └── ai.py
│   └── tests/                   # Bộ kiểm thử tự động (Unit Tests)
│       ├── test_appointments.py # Test logic đặt lịch & chống trùng lịch (KT2)
│       ├── test_invoices.py     # Test tính tiền hóa đơn & mã số
│       ├── test_care_records.py # Test ghi nhận hồ sơ & cập nhật cân nặng
│       └── test_ai_guardrails.py# Test kiểm thử prompt an toàn & disclaimer y tế (KT3)
├── frontend/
│   ├── index.html               # Giao diện Single Page Application hiện đại
│   ├── css/
│   │   └── style.css            # Thiết kế Glassmorphism, Responsive, Vibrant UI
│   └── js/
│       ├── api.js               # Client gọi API có xử lý lỗi
│       ├── state.js             # Quản lý trạng thái và thông báo Toast
│       ├── components.js        # Render giao diện bảng, thẻ thú cưng, hóa đơn
│       └── app.js               # Điều hướng tab, phân quyền và chức năng AI
├── docs/                        # Tài liệu theo quy trình phát triển SDLC
│   ├── KT1_PhanTich_ThietKe_ERD_UseCase.md
│   ├── KT2_KienTruc_CRUD_KiemSoatLich.md
│   ├── KT3_ThietKePrompt_AnToanAI_Tests.md
│   ├── BAO_CAO_DU_AN_AIA331.md
│   └── SLIDE_THUYET_TRINH.md
├── run.py                       # File khởi động 1-click tự động mở trình duyệt
├── requirements.txt             # Danh mục thư viện phụ thuộc
└── README.md                    # Hướng dẫn sử dụng chi tiết
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### Cách 1: Khởi động 1-Click (Khuyên dùng)
Mở cửa sổ dòng lệnh tại thư mục dự án và chạy:
```bash
python run.py
```
> Trình duyệt web sẽ tự động mở trang chủ tại địa chỉ: `http://127.0.0.1:8000`

### Cách 2: Khởi động thủ công qua Uvicorn
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Giao diện ứng dụng: `http://127.0.0.1:8000`
- Tài liệu API tương tác (Swagger UI): `http://127.0.0.1:8000/docs`

---

## 🧪 CHẠY KIỂM THỬ TỰ ĐỘNG (UNIT TESTS)

Để chạy bộ 10 test cases kiểm thử logic nghiệp vụ và an toàn AI:
```bash
python -m pytest backend/tests
```
Kết quả kiểm thử: **10/10 PASS**.

---

## 🔑 TÀI KHOẢN TRẢI NGHIỆM MẪU (RBAC)

Hệ thống có sẵn bộ chuyển vai trò nhanh (Role Switcher) ở góc dưới thanh bên trái để thầy cô và sinh viên kiểm tra ngay lập tức:
- **Quản lý (Admin):** Toàn quyền kiểm soát và cấu hình AI.
- **Lễ tân (Receptionist):** Quản lý khách, đặt lịch hẹn và nhắc lịch.
- **Kỹ thuật viên (Staff - Groomer):** Ghi chép tình trạng lông da và thực hiện dịch vụ.
