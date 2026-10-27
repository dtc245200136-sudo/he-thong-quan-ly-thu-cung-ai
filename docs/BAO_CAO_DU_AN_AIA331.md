# BÁO CÁO TỔNG KẾT ĐỒ ÁN HỌC PHẦN
## ỨNG DỤNG TRÍ TUỆ NHÂN TẠO - MÃ HỌC PHẦN: AIA331
**Mã số đề tài:** 80286  
**Tên đề tài:** Hệ thống quản lý thú cưng và lịch chăm sóc có tích hợp AI (PetCare AI)  
**Đơn vị:** Đại học Thái Nguyên - Trường Đại học Công Nghệ Thông Tin và Truyền Thông (ICTU)  

---

## MỤC LỤC
1. Giới thiệu bài toán và Mục tiêu đề tài
2. Khảo sát nghiệp vụ & Phân tích yêu cầu chức năng
3. Thiết kế hệ thống & Mô hình dữ liệu (ERD, Use Case)
4. Thiết kế các chức năng Trí tuệ nhân tạo (AI Integration)
5. Thuật toán kiểm soát xung đột lịch hẹn (Conflict Resolution)
6. Kế hoạch kiểm thử & Kết quả Unit Tests (Pytest)
7. Hướng dẫn cài đặt và Vận hành hệ thống
8. Đánh giá kết quả đạt được và Hướng phát triển

---

## 1. GIỚI THIỆU BÀI TOÁN & MỤC TIÊU ĐỀ TÀI

### 1.1. Bối cảnh
Tại các cửa hàng dịch vụ thú cưng (Pet Care & Spa), quy trình tiếp đón khách hàng, theo dõi lịch tắm cắt tỉa, nhắc tiêm phòng và thanh toán thường gặp nhiều khó khăn nếu ghi chép thủ công. Khách hàng thường xuyên quên lịch tiêm nhắc lại hoặc cần tư vấn nhanh về cách chăm sóc thú cưng tại nhà.

### 1.2. Mục tiêu dự án
- Xây dựng phần mềm quản lý toàn diện: Chủ nuôi, thú cưng, dịch vụ, lịch hẹn, hồ sơ chăm sóc, tiêm phòng và hóa đơn.
- Tích hợp công nghệ AI sinh tin nhắn nhắc lịch tự động, tóm tắt diễn biến thể trạng thú cưng và giải đáp câu hỏi chăm sóc có rào chắn bảo vệ y tế (Medical Disclaimer).
- Ứng dụng AI xuyên suốt các giai đoạn của quy trình phát triển phần mềm (SDLC: KT1, KT2, KT3 và Báo cáo tổng kết).

---

## 2. YÊU CẦU CHỨC NĂNG HỆ THỐNG

### 2.1. Phân quyền người dùng (RBAC)
- **Quản lý (Admin):** Toàn quyền xem thống kê, doanh thu, quản trị người dùng và cài đặt AI Engine.
- **Lễ tân (Receptionist):** Quản lý chủ nuôi, thú cưng, đặt lịch, đổi lịch, tạo hóa đơn và phát tin nhắn nhắc AI.
- **Kỹ thuật viên (Staff/Groomer):** Theo dõi lịch được giao, ghi nhận hồ sơ chăm sóc da lông, cân nặng và hướng dẫn chủ nuôi.

### 2.2. Nghiệp vụ cốt lõi
1. **Quản lý chủ nuôi & thú cưng:** Lưu trữ giống loài, tuổi, cân nặng, tiền sử dị ứng.
2. **Đặt lịch & Chống trùng lịch:** Tự động phát hiện xung đột thời gian của thú cưng hoặc kỹ thuật viên.
3. **Hồ sơ chăm sóc:** Ghi nhận sản phẩm sử dụng, tình trạng da lông, cân nặng qua các lần đến tiệm.
4. **Nhắc tiêm & Phòng bệnh:** Theo dõi mũi tiêm quá hạn hoặc sắp đến hạn.
5. **Hóa đơn & Thanh toán:** Tính tiền, áp dụng giảm giá, hỗ trợ thanh toán tiền mặt/chuyển khoản QR.
6. **Thống kê Dashboard:** Lượt phục vụ, tổng doanh thu, tỷ lệ khách hàng quay lại.

### 2.3. Chức năng AI
1. **AI Soạn tin nhắn nhắc lịch:** Tự động điền ngữ cảnh, tùy biến phong cách (Thân thiện, Lịch sự, Dễ thương, SMS).
2. **AI Tóm tắt hồ sơ chăm sóc:** Đọc toàn bộ lịch sử spa, phân tích xu hướng thể trạng và cảnh báo sức khỏe.
3. **AI Trợ lý tư vấn chăm sóc:** Trả lời câu hỏi dinh dưỡng, vệ sinh; tự động nhận diện triệu chứng khẩn cấp và kích hoạt cảnh báo đỏ y tế thú y.

---

## 3. CÔNG NGHỆ SỬ DỤNG
- **Backend:** FastAPI, Python 3.14, SQLAlchemy ORM, Pydantic V2, Pytest.
- **Frontend:** HTML5 Semantic, CSS3 Custom Properties (Modern Glassmorphism UI), Vanilla JavaScript ES6+.
- **Database:** SQLite (Hỗ trợ ACID, không phụ thuộc cài đặt máy chủ ngoài).
- **AI Engine:** Tích hợp linh hoạt Google Gemini API, OpenAI GPT-3.5 API và Động cơ Heuristic Rule-based NLP chạy nội bộ 100% an toàn.

---

## 4. KẾT QUẢ ĐẠT ĐƯỢC
- Hệ thống hoạt động mượt mà, đầy đủ 100% các yêu cầu bài toán đặt ra.
- 10/10 Unit tests tự động kiểm thử nghiệp vụ và an toàn AI đều đạt kết quả PASS.
- Giao diện người dùng sang trọng, trực quan, hỗ trợ chuyển đổi vai trò (Role switch) ngay trên thanh bên.
