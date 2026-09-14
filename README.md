# 🐾 PetCare AI Pro - Hệ thống Quản lý Dịch vụ Thú cưng & Lịch Chăm sóc Tích hợp AI

**ĐẠI HỌC THÁI NGUYÊN - TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG (ICTU)**  
**Học phần:** Ứng dụng trí tuệ nhân tạo (AIA331)  
**Mã số đề tài:** 80286  

---

## 🌟 Giới thiệu Dự án
**PetCare AI Pro** là hệ thống quản trị chuyên nghiệp dành cho các trung tâm dịch vụ thú cưng, kết hợp Trí tuệ Nhân tạo xuyên suốt vòng đời phát triển phần mềm (SDLC):
- **Quản lý nghiệp vụ:** Chủ nuôi, thú cưng, dịch vụ bảng giá, đặt lịch thông minh chống trùng lịch, hồ sơ chăm sóc chi tiết, sổ tiêm phòng điện tử, lập hóa đơn và thống kê doanh thu.
- **Phân quyền RBAC:** Quản lý (`ADMIN`), Lễ tân (`RECEPTIONIST`), Kỹ thuật viên Groomer (`STAFF`).
- **3 Phân hệ AI:**
  1. 📱 **AI Sinh tin nhắn nhắc lịch hẹn & tiêm nhắc:** Đa kênh (SMS, Zalo, Email).
  2. 📋 **AI Tóm tắt hồ sơ chăm sóc & phân tích sức khỏe:** Xu hướng cân nặng, da lông, cảnh báo dị ứng.
  3. 🤖 **Trợ lý AI Tư vấn Chăm sóc:** Có hệ thống **Safety Guardrail** phát hiện triệu chứng cấp cứu nguy hiểm và luôn kèm cảnh báo y tế thú y.

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy (1-Click)

### 1. Cài đặt các thư viện cần thiết
Mở Terminal hoặc PowerShell tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Cơ sở dữ liệu (Microsoft SQL Server)
Hệ thống sử dụng **Microsoft SQL Server** với database `DEMO AI` trên `localhost`, kết nối qua **Windows Authentication** và driver **pyodbc**:
- **Database:** `DEMO AI`
- **Authentication:** Windows Authentication (Trusted Connection)
- **Chuỗi kết nối mặc định:** `mssql+pyodbc://@localhost/DEMO AI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes`
- Hệ thống tự động tạo bảng (`create_all`) và nạp sẵn dữ liệu mẫu (`seed_database`) khi khởi chạy.

### 3. Khởi chạy ứng dụng
Chạy lệnh:
```bash
python main.py
```
*Hoặc nhấp đúp vào file `run.bat` trên Windows.*

Sau khi khởi chạy:
- 🌐 **Giao diện Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Tài liệu API Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Tài khoản Thử nghiệm (Sẵn dữ liệu mẫu phong phú)

Hệ thống đã tự động nạp dữ liệu mẫu (Seed data). Bạn có thể bấm thanh chuyển tài khoản nhanh (1-Click) trên đầu trang Web:

| Vai trò | Tên đăng nhập | Mật khẩu | Quyền hạn chính |
| :--- | :--- | :--- | :--- |
| **Admin / Quản lý** | `admin` | `admin123` | Toàn quyền cấu hình, thống kê KPI, quản lý tài khoản |
| **Lễ tân** | `reception` | `123456` | Tiếp đón khách, đặt lịch, tạo hóa đơn, gửi AI nhắc lịch |
| **Kỹ thuật viên** | `staff` | `123456` | Xem lịch làm việc, cập nhật hồ sơ chăm sóc, gọi AI tóm tắt |

---

## 🧪 Chạy Kiểm thử Tự động (Automated Test Suite)
Chạy lệnh pytest để kiểm tra lịch hẹn, hóa đơn, hồ sơ chăm sóc và guardrails AI:
```bash
python -m pytest tests/ -v
```

---

## 📁 Cấu trúc Thư mục Dự án

```
e:\demo Môn AI\
├── app/
│   ├── api/             # REST API Routers (Auth, Owners, Pets, Services, Appointments, Invoices, AI)
│   ├── core/            # Config, Database engine, JWT Security & RBAC
│   ├── models/          # SQLAlchemy Database Models (User, Pet, Owner, Appointment, Invoice, CareRecord,...)
│   ├── schemas/         # Pydantic DTO Schemas validation
│   ├── services/        # Business Logic & AI Engine (Gemini/OpenAI/Offline Smart Engine)
│   └── seed.py          # Dữ liệu khởi tạo mẫu thực tế
├── static/              # Giao diện Web SPA Hiện đại
│   ├── index.html       # Master Layout & Dashboard
│   ├── css/style.css    # Glassmorphism Styling & Responsive
│   └── js/              # Modular Javascript (app, auth, dashboard, appointments, pets, care, invoices, ai)
├── tests/               # Unit Test & Integration Test Suite (pytest)
├── docs/                # Báo cáo SDLC AIA331 (KT1, KT2, KT3, Cuối kỳ) & Sơ đồ ERD
├── requirements.txt     # Danh sách thư viện Python
├── run.bat              # Script chạy nhanh cho Windows
└── main.py              # Điểm khởi chạy FastAPI Backend
```
