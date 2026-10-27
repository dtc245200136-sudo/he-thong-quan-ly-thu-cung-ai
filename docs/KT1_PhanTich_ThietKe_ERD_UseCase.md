# BÁO CÁO KIỂM TRA 1 (KT1): PHÂN TÍCH NGHIỆP VỤ & THIẾT KẾ HỆ THỐNG

**Trường Đại học Công Nghệ Thông Tin và Truyền Thông (ICTU) - Đại học Thái Nguyên**  
**Học phần:** Ứng dụng trí tuệ nhân tạo (AIA331)  
**Mã số đề tài:** 80286  
**Tên đề tài:** Hệ thống quản lý thú cưng và lịch chăm sóc có tích hợp AI (PetCare AI)  

---

## 1. Phân Tích Nghiệp Vụ Hệ Thống

Cửa hàng dịch vụ thú cưng phục vụ 3 nhóm đối tượng chính:
1. **Chủ nuôi (Pet Owners):** Có nhu cầu đặt lịch spa, tắm sấy, cắt tỉa lông, tiêm phòng và nhận tin nhắn nhắc lịch định kỳ, hướng dẫn chăm sóc cơ bản.
2. **Lễ tân (Receptionist):** Tiếp nhận thông tin chủ nuôi, xếp lịch hẹn, điều phối kỹ thuật viên, lập hóa đơn và theo dõi thanh toán.
3. **Kỹ thuật viên / Chuyên viên chăm sóc (Staff/Groomer):** Thực hiện quy trình spa, ghi nhận thể trạng lông da, cân nặng và dặn dò sau dịch vụ.
4. **Quản lý (Admin):** Toàn quyền kiểm soát danh mục dịch vụ, bảng giá, cấu hình AI, thống kê doanh thu và tỷ lệ khách hàng quay lại.

---

## 2. Biểu Đồ Ca Sử Dụng (Use Case Diagram)

```mermaid
graph TD
    User([Người dùng])
    Admin([Quản lý - Admin])
    Receptionist([Lễ tân - Receptionist])
    Staff([Nhân viên - Staff])

    User --> Admin
    User --> Receptionist
    User --> Staff

    subgraph "Hệ Thống PetCare AI"
        UC_Auth(Đăng nhập & Phân quyền RBAC)
        UC_PetOwner(Quản lý Chủ nuôi & Thú cưng)
        UC_Appointment(Đặt lịch & Chống trùng lịch)
        UC_CareRecord(Ghi nhận Hồ sơ Chăm sóc)
        UC_Vaccine(Theo dõi Lịch tiêm nhắc & Phòng bệnh)
        UC_Invoice(Lập hóa đơn & Thanh toán)
        UC_Analytics(Thống kê Doanh thu & Khách quay lại)
        
        subgraph "Chức Năng AI"
            UC_AIReminder(AI Sinh tin nhắn nhắc lịch hẹn / tiêm phòng)
            UC_AISummary(AI Tóm tắt hồ sơ sức khỏe & da lông)
            UC_AIChat(AI Tư vấn chăm sóc có Disclaimer y tế)
        end
    end

    Admin --> UC_Auth
    Admin --> UC_Analytics
    Admin --> UC_Invoice

    Receptionist --> UC_PetOwner
    Receptionist --> UC_Appointment
    Receptionist --> UC_Vaccine
    Receptionist --> UC_Invoice
    Receptionist --> UC_AIReminder

    Staff --> UC_CareRecord
    Staff --> UC_Appointment

    User --> UC_AIChat
    User --> UC_AISummary
```

---

## 3. Biểu Đồ Thực Thể Quan Hệ (ERD - Entity Relationship Diagram)

```mermaid
erDiagram
    USERS ||--o{ APPOINTMENTS : "thực hiện"
    USERS ||--o{ CARE_RECORDS : "ghi nhận"
    OWNERS ||--o{ PETS : "sở hữu"
    OWNERS ||--o{ APPOINTMENTS : "đặt lịch"
    OWNERS ||--o{ INVOICES : "thanh toán"
    PETS ||--o{ APPOINTMENTS : "làm dịch vụ"
    PETS ||--o{ CARE_RECORDS : "có lịch sử"
    PETS ||--o{ VACCINE_REMINDERS : "có lịch tiêm"
    SERVICES ||--o{ APPOINTMENTS : "thuộc về"
    APPOINTMENTS ||--o| CARE_RECORDS : "sinh ra"
    APPOINTMENTS ||--o| INVOICES : "lập hóa đơn"

    USERS {
        int id PK
        string username
        string full_name
        string role "admin / receptionist / staff"
        string password_hash
        boolean is_active
    }

    OWNERS {
        int id PK
        string name
        string phone
        string email
        string address
        text notes
    }

    PETS {
        int id PK
        int owner_id FK
        string name
        string species "Chó / Mèo"
        string breed
        int age_months
        string gender
        float weight_kg
        string allergies
        text medical_history
    }

    SERVICES {
        int id PK
        string name
        string category
        int duration_minutes
        float price
        text description
        boolean is_active
    }

    APPOINTMENTS {
        int id PK
        int pet_id FK
        int owner_id FK
        int service_id FK
        int staff_id FK
        string appointment_date
        string appointment_time
        string status "pending / confirmed / in_progress / completed / cancelled"
        string cancel_reason
    }

    CARE_RECORDS {
        int id PK
        int pet_id FK
        int appointment_id FK
        int staff_id FK
        string record_date
        string fur_skin_condition
        float weight_recorded_kg
        string behavior_notes
        string products_used
        text staff_notes
        text home_care_instructions
    }

    VACCINE_REMINDERS {
        int id PK
        int pet_id FK
        string vaccine_name
        int dose_number
        string administered_date
        string next_due_date
        string status "pending / completed / overdue"
        string notes
    }

    INVOICES {
        int id PK
        string invoice_code
        int owner_id FK
        int appointment_id FK
        float total_amount
        float discount_amount
        float final_amount
        string payment_method
        string payment_status "pending / paid"
        datetime paid_at
    }

    AI_SESSION_LOGS {
        int id PK
        string feature_type
        int pet_id
        text user_prompt
        text ai_response
        boolean has_disclaimer
        string model_name
    }
```
