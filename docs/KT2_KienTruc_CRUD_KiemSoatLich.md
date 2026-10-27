# BÁO CÁO KIỂM TRA 2 (KT2): THIẾT KẾ KIẾN TRÚC CRUD & THUẬT TOÁN CHỐNG TRÙNG LỊCH

**Trường Đại học Công Nghệ Thông Tin và Truyền Thông (ICTU) - Đại học Thái Nguyên**  
**Học phần:** Ứng dụng trí tuệ nhân tạo (AIA331)  
**Mã số đề tài:** 80286  

---

## 1. Kiến Trúc Hệ Thống (Architecture)

Hệ thống được thiết kế theo mô hình 3 lớp phân tách rõ ràng (Clean 3-Tier Architecture):
- **Presentation Layer (Frontend):** Single Page Application xây dựng bằng HTML5, CSS3 hiện đại (Glassmorphism, CSS Custom Properties, Responsive UI), và Vanilla JS Module kết nối RESTful API.
- **Application & Business Logic Layer (Backend):** FastAPI (Python 3.14), Pydantic V2 Schema Validation, SQLAlchemy ORM, và Module AI Service tích hợp (Gemini API / OpenAI / Rule-based NLP Engine).
- **Persistence Layer (Database):** CSDL SQLite với ACID transaction, foreign keys cascade và indexing trên các trường truy vấn cao (`phone`, `appointment_date`, `status`).

---

## 2. Thuật Toán Kiểm Soát & Xử Lý Trùng Lịch (Conflict Resolution Algorithm)

### 2.1. Bài toán đặt ra
Trong nghiệp vụ Spa thú cưng, các lỗi trùng lịch phổ biến gây tắc nghẽn tiệm gồm:
1. **Trùng thú cưng (Pet Overlap):** Một bé thú cưng không thể vừa được tắm vừa được khám ở hai slot giờ trùng nhau.
2. **Trùng nhân viên kỹ thuật (Staff Overlap):** Một kỹ thuật viên (Groomer) chỉ có thể chăm sóc tối đa 1 bé tại cùng một khung giờ phục vụ.

### 2.2. Thuật toán kiểm tra xung đột trong `backend/app/routes/appointments.py`

```python
def check_appointment_conflict(
    db: Session,
    appointment_date: str,
    appointment_time: str,
    pet_id: int,
    staff_id: Optional[int] = None,
    exclude_id: Optional[int] = None
):
    active_statuses = ["pending", "confirmed", "in_progress"]

    # 1. Kiểm tra thú cưng đã có lịch hẹn trùng giờ chưa
    pet_conflict = db.query(Appointment).filter(
        Appointment.pet_id == pet_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(active_statuses)
    )
    if exclude_id:
        pet_conflict = pet_conflict.filter(Appointment.id != exclude_id)
    if pet_conflict.first():
        raise HTTPException(
            status_code=400,
            detail=f"Trùng lịch: Thú cưng này đã có lịch hẹn vào lúc {appointment_time} ngày {appointment_date}!"
        )

    # 2. Kiểm tra kỹ thuật viên phụ trách đã kín lịch slot này chưa
    if staff_id:
        staff_conflict = db.query(Appointment).filter(
            Appointment.staff_id == staff_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_(active_statuses)
        )
        if exclude_id:
            staff_conflict = staff_conflict.filter(Appointment.id != exclude_id)
        if staff_conflict.first():
            raise HTTPException(
                status_code=400,
                detail=f"Trùng lịch: Kỹ thuật viên đã kín lịch vào {appointment_time} ngày {appointment_date}!"
            )
```

---

## 3. Danh Mục API Endpoints

| Phương thức | Đường dẫn API | Chức năng nghiệp vụ |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Xác thực đăng nhập và cấp token phân quyền |
| `GET` / `POST` | `/api/owners` | Xem danh sách chủ nuôi / Thêm chủ nuôi mới |
| `GET` / `POST` | `/api/pets` | Xem danh sách thú cưng / Đăng ký thú cưng |
| `GET` / `POST` | `/api/services` | Tra cứu bảng giá & gói dịch vụ spa/tiêm |
| `POST` | `/api/appointments` | Đặt lịch mới (tự động chạy thuật toán chống trùng lịch) |
| `PUT` | `/api/appointments/{id}` | Đổi lịch (Reschedule - kiểm tra trùng slot mới) |
| `PATCH` | `/api/appointments/{id}/cancel` | Hủy lịch kèm lý do khách bận |
| `POST` | `/api/care-records` | Ghi nhận hồ sơ chăm sóc & tự động cập nhật cân nặng mới cho pet |
| `GET` / `POST` | `/api/vaccines` | Theo dõi lịch tiêm phòng & cảnh báo mũi tiêm quá hạn |
| `POST` | `/api/invoices` | Lập hóa đơn tính tiền và chiết khấu |
| `GET` | `/api/analytics/dashboard` | Thống kê KPI, doanh thu, lượt dịch vụ và tỷ lệ khách quay lại |
