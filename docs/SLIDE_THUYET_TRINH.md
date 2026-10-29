# KỊCH BẢN THUYẾT TRÌNH & DÀN Ý SLIDE BẢO VỆ ĐỒ ÁN
## HỌC PHẦN: ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AIA331)
**Mã đề tài:** 80286  
**Đề tài:** Hệ thống quản lý thú cưng và lịch chăm sóc có tích hợp AI  
**Sinh viên thực hiện:** [Họ và tên sinh viên]  
**Giảng viên hướng dẫn:** [Tên Giảng viên]  
**Trường:** Đại học Công Nghệ Thông Tin và Truyền Thông (ICTU) - ĐH Thái Nguyên  

---

### SLIDE 1: TRANG TIÊU ĐỀ
- Tên trường & Khoa CNTT
- Tên đề tài: "Hệ Thống Quản Lý Thú Cưng Và Lịch Chăm Sóc Có Tích Hợp AI (PetCare AI)"
- Mã học phần: AIA331 | Mã dự án: 80286

### SLIDE 2: ĐẶT VẤN ĐỀ & BÀI TOÁN THỰC TIỄN
- Nhu cầu chăm sóc thú cưng tại các đô thị tăng trưởng mạnh.
- Khó khăn của tiệm chăm sóc: Quản lý lịch thủ công dễ bị trùng giờ, khách hay quên lịch tiêm phòng nhắc lại, khách cần tư vấn cơ bản nhưng nhân viên quá tải.
- Giải pháp: Xây dựng hệ thống PetCare AI quản lý toàn diện và ứng dụng AI thông minh hỗ trợ vận hành.

### SLIDE 3: MỤC TIÊU & CÁC CHỨC NĂNG CHÍNH
- **Nghiệp vụ cốt lõi:**
  - Phân quyền RBAC 3 vai trò nội bộ (Admin, Lễ tân, Kỹ thuật viên Groomer).
  - Quản lý thú cưng, chủ nuôi, hóa đơn, kho hàng và thuật toán chống trùng lịch.
  - **Cổng Khách Hàng Nhanh (Quick Portal / Kiosk Mode):** Khách hàng hoặc quầy tự phục vụ tại cửa hàng chỉ cần nhập SĐT là tra cứu tức thì hạng thẻ VIP, điểm thưởng, số tiêm chủng điện tử và đặt lịch nhanh mà không cần đăng nhập tài khoản phức tạp.
- **Tính năng AI tích hợp:**
  1. AI Soạn tin nhắn nhắc lịch (Tự động điền ngữ cảnh, tùy biến phong cách SMS/Zalo/Email).
  2. AI Tóm tắt hồ sơ chăm sóc thú cưng (Phân tích diễn biến cân nặng, cảnh báo lông da/dị ứng).
  3. AI Trợ lý tư vấn chăm sóc với Veterinary Disclaimer và cơ chế nhận diện dấu hiệu cấp cứu đỏ (Emergency Red Flags).

### SLIDE 4: ỨNG DỤNG AI TRONG SDLC (QUY TRÌNH PHÁT TRIỂN)
- **KT1:** AI hỗ trợ phân tích ca sử dụng (Use Case) và thiết kế sơ đồ quan hệ thực thể (ERD).
- **KT2:** Thiết kế CRUD chuẩn hóa và thuật toán kiểm tra xung đột thời gian (Conflict Resolution).
- **KT3:** Thiết kế bộ Prompt Template an toàn, xây dựng ma trận Unit Test và kiểm thử câu hỏi nguy cấp.
- **Cuối kỳ:** Tài liệu hóa mã nguồn, báo cáo đồ án và kiểm thử tự động với Pytest.

### SLIDE 5: KIẾN TRÚC KỸ THUẬT (TECH STACK)
- Backend: FastAPI (Python 3.14), SQLAlchemy ORM, SQLite.
- Frontend: HTML5, CSS3 Glassmorphism Modern UI, Vanilla JS.
- AI Engine: Google Gemini API / OpenAI / Heuristic Engine chạy nội bộ không lỗi mạng.
- Testing: Pytest tự động 10/10 test cases PASS.

### SLIDE 6: DEMO TÍNH NĂNG NỔI BẬT (LIVE DEMO)
- 1. **Cổng Khách Hàng Nhanh (Kiosk Mode):** Nhập SĐT tra cứu tức thì thẻ VIP, số điểm thưởng, lịch tiêm phòng sắp tới và đặt lịch dịch vụ nhanh.
- 2. **Chuyển đổi phân quyền RBAC 1-click:** Trải nghiệm góc nhìn Admin, Lễ tân và Kỹ thuật viên Groomer.
- 3. **Thuật toán kiểm soát lịch:** Thử nghiệm đặt lịch và kiểm tra cơ chế chặn xung đột thời gian (Slot Conflict Detection).
- 4. **Trải nghiệm AI Studio:** Soạn tin nhắn Zalo/SMS cá nhân hóa, tóm tắt diễn biến sức khỏe thú cưng, và kiểm thử Chatbot nhận diện tình huống khẩn cấp y tế.

### SLIDE 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN
- Hệ thống hoàn thành 100% mục tiêu học phần đề ra.
- Hướng phát triển: Tích hợp nhận diện hình ảnh da lông thú cưng qua Computer Vision để tự động phát hiện nấm da, ve rận.
- Lời cảm ơn Hội đồng chấm thi!
