from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, Base, engine
from backend.core.security import get_password_hash
from backend.models.user import User, UserRole
from backend.models.owner import PetOwner
from backend.models.pet import Pet, PetSpecies, PetGender
from backend.models.service import Service
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.care_record import CareRecord
from backend.models.vaccination import VaccinationSchedule, VaccinationStatus
from backend.models.invoice import Invoice, InvoiceItem, PaymentMethod, PaymentStatus

def seed_database():
    from backend.core.config import settings
    if "mssql" in settings.DATABASE_URL:
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                res = conn.execute(text("SELECT COUNT(*) FROM sys.tables")).scalar()
                if res == 0:
                    Base.metadata.create_all(bind=engine, checkfirst=False)
        except Exception:
            Base.metadata.create_all(bind=engine, checkfirst=False)
    else:
        Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Kiểm tra nếu đã có dữ liệu users thì kiểm tra tiếp kho hàng
    if db.query(User).count() > 0:
        seed_inventory_items(db)
        db.commit()
        db.close()
        return

    print("[*] Dang khoi tao du lieu mau cho he thong PetCare AI Pro...")


    # 1. TẠO TÀI KHOẢN NGƯỜI DÙNG (USERS & RBAC)
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Nguyễn Văn Quản Lý (Admin)",
        role=UserRole.ADMIN.value,
        phone="0988111222",
        email="admin@petcarepro.vn",
        is_active=True
    )
    
    receptionist_user = User(
        username="reception",
        hashed_password=get_password_hash("123456"),
        full_name="Trần Thị Lan Anh (Lễ tân)",
        role=UserRole.RECEPTIONIST.value,
        phone="0977333444",
        email="lananh@petcarepro.vn",
        is_active=True
    )
    
    groomer_user = User(
        username="staff",
        hashed_password=get_password_hash("123456"),
        full_name="Lê Minh Đức (Kỹ thuật viên Groomer)",
        role=UserRole.STAFF.value,
        phone="0966555666",
        email="duc.groomer@petcarepro.vn",
        is_active=True
    )
    
    db.add_all([admin_user, receptionist_user, groomer_user])
    db.flush()

    # 2. TẠO DANH MỤC DỊCH VỤ (SERVICES)
    services = [
        Service(
            name="Tắm Spa & Sấy thơm dưỡng lông",
            category="Tắm spa",
            price=150000.0,
            duration_minutes=45,
            description="Tắm sạch bằng dầu tắm thảo dược thiên nhiên, vắt tuyến hôi, sấy tơi lông và thoa tinh dầu thơm."
        ),
        Service(
            name="Combo Cắt tỉa Grooming tạo kiểu",
            category="Cắt tỉa grooming",
            price=350000.0,
            duration_minutes=90,
            description="Trọn gói: Tắm spa + Cắt móng + Vệ sinh tai + Cạo bàn/bụng/hậu môn + Cắt tỉa tạo kiểu tròn mặt Hàn Quốc."
        ),
        Service(
            name="Vệ sinh toàn diện (Tai, Móng, Tuyến hôi)",
            category="Chăm sóc cơ bản",
            price=100000.0,
            duration_minutes=30,
            description="Cắt mài móng không đau, nhổ lông tai, vệ sinh tai bằng dung dịch y tế và vắt tuyến hôi."
        ),
        Service(
            name="Gói Siêu VIP Spa & Dưỡng ẩm bùn khoáng",
            category="Combo",
            price=550000.0,
            duration_minutes=120,
            description="Ủ bùn khoáng phục hồi lông hư tổn, tắm bồn sục jacuzzi massage, cắt tỉa form chuẩn thẩm mỹ cao cấp."
        ),
        Service(
            name="Tiêm phòng Vaccine 7 bệnh cho Chó",
            category="Khám & Tiêm phòng",
            price=220000.0,
            duration_minutes=20,
            description="Vaccine Vanguard 7/Zoetis ngừa Care, Parvo, Viêm gan truyền nhiễm, Ho cũi chó, v.v. Kèm khám sàng lọc."
        ),
        Service(
            name="Tiêm phòng Vaccine 4 bệnh cho Mèo",
            category="Khám & Tiêm phòng",
            price=250000.0,
            duration_minutes=20,
            description="Vaccine Felocell ngừa Giảm bạch cầu mèo, Viêm mũi khí quản, Calicivirus và Chlamydia."
        ),
        Service(
            name="Khách sạn thú cưng Pet Hotel (Phòng VIP)",
            category="Lưu trú",
            price=200000.0,
            duration_minutes=60,
            description="Phòng điều hòa 24/7, camera theo dõi trực tiếp, chế độ ăn 3 bữa và dắt đi dạo 2 lần/ngày."
        )
    ]
    db.add_all(services)
    db.flush()

    # 3. TẠO CHỦ NUÔI (PET OWNERS)
    owners = [
        PetOwner(
            full_name="Hoàng Thị Mai",
            phone="0912345678",
            email="mai.hoang@gmail.com",
            address="125 Đường Hoàng Văn Thụ, TP. Thái Nguyên",
            notes="Khách hàng VIP, chăm sóc cún rất kỹ."
        ),
        PetOwner(
            full_name="Nguyễn Tuấn Kiệt",
            phone="0987654321",
            email="kiet.nguyen@yahoo.com",
            address="45 Đường Lương Ngọc Quyến, TP. Thái Nguyên",
            notes="Nuôi 2 bé mèo Anh lông ngắn."
        ),
        PetOwner(
            full_name="Phạm Thu Trang",
            phone="0905112233",
            email="trang.pham@gmail.com",
            address="88 Đường Quang Trung, TP. Thái Nguyên",
            notes="Thường đặt lịch cuối tuần."
        ),
        PetOwner(
            full_name="Vũ Đức Long",
            phone="0934567890",
            email="long.vu@hotmail.com",
            address="12 Tổ 5 Phường Tân Thịnh, TP. Thái Nguyên",
            notes="Chủ của bé Golden Retriever năng động."
        )
    ]
    db.add_all(owners)
    db.flush()

    # 4. TẠO THÚ CƯNG (PETS)
    pets = [
        Pet(
            owner_id=owners[0].id,
            name="Miu Miu",
            species="Chó",
            breed="Poodle Tiny",
            age_years=2,
            age_months=3,
            gender="Cái",
            weight_kg=3.2,
            microchip_id="VN-9820-001",
            allergies="Dị ứng với dầu gội chứa hương liệu nhân tạo đậm đặc.",
            medical_notes="Tính cách hiền, hơi nhát nước, thích được xoa đầu.",
            avatar_url="https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80"
        ),
        Pet(
            owner_id=owners[1].id,
            name="Bắp",
            species="Mèo",
            breed="Mèo Anh Lông Ngắn (BSH)",
            age_years=1,
            age_months=6,
            gender="Đực",
            weight_kg=4.8,
            microchip_id="VN-9820-002",
            allergies="Không có dị ứng thức ăn.",
            medical_notes="Đã triệt sản. Hơi dữ khi sấy đuôi.",
            avatar_url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80"
        ),
        Pet(
            owner_id=owners[2].id,
            name="Corgi Bơ",
            species="Chó",
            breed="Pembroke Welsh Corgi",
            age_years=3,
            age_months=0,
            gender="Đực",
            weight_kg=12.5,
            microchip_id="VN-9820-003",
            allergies="Dị ứng thịt gà công nghiệp (dễ ngứa da).",
            medical_notes="Lông rụng nhiều vào mùa thay lông. Rất năng động, thích ăn thưởng xúc xích.",
            avatar_url="https://images.unsplash.com/photo-1612536057832-2ff7ead58194?auto=format&fit=crop&w=400&q=80"
        ),
        Pet(
            owner_id=owners[3].id,
            name="Rocky",
            species="Chó",
            breed="Golden Retriever",
            age_years=2,
            age_months=8,
            gender="Đực",
            weight_kg=28.0,
            microchip_id="VN-9820-004",
            allergies="Không",
            medical_notes="Rất thân thiện, cực kỳ hợp tác khi tắm.",
            avatar_url="https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400&q=80"
        )
    ]
    db.add_all(pets)
    db.flush()

    # 5. TẠO LỊCH HẸN (APPOINTMENTS)
    now = datetime.now()
    today_9am = datetime(now.year, now.month, now.day, 9, 0)
    today_14pm = datetime(now.year, now.month, now.day, 14, 30)
    tomorrow_10am = datetime(now.year, now.month, now.day, 10, 0) + timedelta(days=1)
    past_3days = now - timedelta(days=3)
    past_10days = now - timedelta(days=10)

    appts = [
        Appointment(
            pet_id=pets[0].id,
            owner_id=owners[0].id,
            service_id=services[1].id, # Combo Cắt tỉa
            staff_id=groomer_user.id,
            appointment_time=today_9am,
            end_time=today_9am + timedelta(minutes=90),
            status=AppointmentStatus.CONFIRMED.value,
            notes="Yêu cầu cắt mặt tròn Teddy Bear, tỉa gọn chân."
        ),
        Appointment(
            pet_id=pets[1].id,
            owner_id=owners[1].id,
            service_id=services[0].id, # Tắm spa
            staff_id=groomer_user.id,
            appointment_time=today_14pm,
            end_time=today_14pm + timedelta(minutes=45),
            status=AppointmentStatus.CONFIRMED.value,
            notes="Tắm sấy khô kĩ lông tơ tránh nấm da."
        ),
        Appointment(
            pet_id=pets[2].id,
            owner_id=owners[2].id,
            service_id=services[3].id, # Gói VIP Spa
            staff_id=groomer_user.id,
            appointment_time=tomorrow_10am,
            end_time=tomorrow_10am + timedelta(minutes=120),
            status=AppointmentStatus.PENDING.value,
            notes="Khách đặt hẹn qua website, cần xác nhận lại."
        ),
        Appointment(
            pet_id=pets[0].id,
            owner_id=owners[0].id,
            service_id=services[0].id, # Tắm spa quá khứ
            staff_id=groomer_user.id,
            appointment_time=past_10days,
            end_time=past_10days + timedelta(minutes=45),
            status=AppointmentStatus.COMPLETED.value,
            notes="Đã hoàn thành xuất sắc."
        )
    ]
    db.add_all(appts)
    db.flush()

    # 6. TẠO HỒ SƠ CHĂM SÓC (CARE RECORDS)
    care_records = [
        CareRecord(
            pet_id=pets[0].id,
            appointment_id=appts[3].id,
            staff_id=groomer_user.id,
            record_date=past_10days,
            weight_kg=3.1,
            coat_skin_condition="Da sạch, không có vảy nấm hay bọ chét. Lông xoăn mềm.",
            ears_eyes_teeth="Tai hơi nhiều dịch nhờn nâu nhẹ, đã rửa sạch bằng dung dịch khử mùi. Mắt sáng.",
            behavior_mood="Rất ngoan, hơi rụt rè lúc mới bật máy sấy nhưng nhanh chóng quen.",
            services_performed="Tắm thảo dược tràm trà, cạo bàn chân, vệ sinh tai móng.",
            notes="Dặn chủ vệ sinh tai 2 ngày/lần trong tuần này.",
            before_photo_url="https://images.unsplash.com/photo-1548767797-d8c844163c4c?auto=format&fit=crop&w=400&q=80",
            after_photo_url="https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80"
        ),
        CareRecord(
            pet_id=pets[0].id,
            staff_id=groomer_user.id,
            record_date=past_3days,
            weight_kg=3.2,
            coat_skin_condition="Lông tơ phát triển tốt, da hồng hào khỏe mạnh.",
            ears_eyes_teeth="Tai đã sạch hoàn toàn, không còn mùi hôi. Vôi răng ít.",
            behavior_mood="Hợp tác cực kỳ tốt, vui vẻ nhận bánh thưởng.",
            services_performed="Tắm dưỡng ẩm tơ tằm, sấy phồng và tỉa bo tròn mặt tròn xoe.",
            notes="Form lông duy trì rất đẹp.",
            before_photo_url="https://images.unsplash.com/photo-1517423440428-a5a00ad493e8?auto=format&fit=crop&w=400&q=80",
            after_photo_url="https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=400&q=80"
        ),
        CareRecord(
            pet_id=pets[1].id,
            staff_id=groomer_user.id,
            record_date=now - timedelta(days=20),
            weight_kg=4.7,
            coat_skin_condition="Lông dày ngắn, có ít gàu nhẹ ở sống lưng.",
            ears_eyes_teeth="Tai sạch, răng trắng đẹp.",
            behavior_mood="Cần 2 bạn giữ khi sấy đuôi.",
            services_performed="Tắm sấy khô, chải lông rụng bằng lược Furminator.",
            notes="Khuyên chủ bổ sung thêm dầu cá hồi để giảm gàu sống lưng.",
            before_photo_url="https://images.unsplash.com/photo-1513360309081-38f0762daed1?auto=format&fit=crop&w=400&q=80",
            after_photo_url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80"
        )
    ]
    db.add_all(care_records)
    db.flush()


    # 7. TẠO LỊCH TIÊM PHÒNG (VACCINATIONS)
    vaccinations = [
        VaccinationSchedule(
            pet_id=pets[0].id,
            vaccine_name="Vaccine Vanguard 7 Bệnh cho Chó (Nhắc lại hàng năm)",
            dose_number="Mũi nhắc lại năm thứ 2",
            manufacturer="Zoetis (USA)",
            batch_number="ZTS-2026-VG7",
            administered_date=date.today() - timedelta(days=330),
            next_due_date=date.today() + timedelta(days=15),
            status=VaccinationStatus.SCHEDULED.value,
            notes="Mũi nhắc lại định kỳ hàng năm. Cần kiểm tra sức khỏe trước tiêm."
        ),
        VaccinationSchedule(
            pet_id=pets[1].id,
            vaccine_name="Vaccine Felocell 4 Bệnh cho Mèo",
            dose_number="Mũi 3 (Hoàn thành phác đồ cơ bản)",
            manufacturer="Zoetis (USA)",
            batch_number="ZTS-2026-FC4",
            administered_date=date.today() - timedelta(days=350),
            next_due_date=date.today() + timedelta(days=7),
            status=VaccinationStatus.SCHEDULED.value,
            notes="Đến hẹn tiêm nhắc lại năm 2026."
        ),
        VaccinationSchedule(
            pet_id=pets[2].id,
            vaccine_name="Vaccine Phòng Dại (Rabisin)",
            dose_number="Mũi hàng năm bắt buộc",
            manufacturer="Boehringer Ingelheim (Pháp)",
            batch_number="BI-2025-RAB",
            administered_date=date.today() - timedelta(days=400),
            next_due_date=date.today() - timedelta(days=10),
            status=VaccinationStatus.OVERDUE.value,
            notes="ĐÃ QUÁ HẠN 10 NGÀY - Hệ thống cần gửi thông báo nhắc khẩn cấp cho chủ nuôi."
        )
    ]
    db.add_all(vaccinations)
    db.flush()

    # 8. TẠO HÓA ĐƠN MẪU (INVOICES)
    inv1 = Invoice(
        invoice_code="INV-20260810-001",
        appointment_id=appts[3].id,
        owner_id=owners[0].id,
        subtotal=150000.0,
        discount_amount=15000.0, # Giảm giá 10% khách quen
        tax_amount=0.0,
        total_amount=135000.0,
        payment_method=PaymentMethod.TRANSFER.value,
        payment_status=PaymentStatus.PAID.value,
        payment_time=past_10days,
        notes="Thanh toán chuyển khoản Vietcombank qua mã QR."
    )
    db.add(inv1)
    db.flush()
    
    inv_item1 = InvoiceItem(
        invoice_id=inv1.id,
        item_name="Tắm Spa & Sấy thơm dưỡng lông",
        quantity=1,
        unit_price=150000.0,
        total_price=150000.0
    )
    db.add(inv_item1)

    # 9. TẠO KHO HÀNG & DƯỢC PHẨM MẪU (INVENTORY & SUPPLIES)
    seed_inventory_items(db)

    db.commit()
    db.close()
    print("[+] Da khoi tao thanh cong co so du lieu mau PetCare AI Pro!")

def seed_inventory_items(db: Session):
    from backend.models.inventory import InventoryItem, StockTransaction, InventoryCategory, TransactionType
    
    if db.query(InventoryItem).count() > 0:
        return

    today = date.today()
    sample_items = [
        InventoryItem(
            sku="VAC-VAN-5L",
            name="Vanguard Plus 5/L (Vaccine phòng 5 bệnh Chó)",
            category=InventoryCategory.VACCINE.value,
            unit="Lọ",
            quantity=45.0,
            min_threshold=10.0,
            cost_price=120000.0,
            selling_price=220000.0,
            batch_number="VN2408A",
            expiry_date=today + timedelta(days=280),
            supplier="Zoetis Vietnam Ltd",
            shelf_location="Tủ lạnh vắc-xin ngăn A1",
            notes="Bảo quản 2-8°C, tránh ánh sáng trực tiếp"
        ),
        InventoryItem(
            sku="VAC-FEL-04",
            name="Felocell 4 (Vaccine phòng 4 bệnh Mèo)",
            category=InventoryCategory.VACCINE.value,
            unit="Lọ",
            quantity=28.0,
            min_threshold=8.0,
            cost_price=145000.0,
            selling_price=260000.0,
            batch_number="FC2406B",
            expiry_date=today + timedelta(days=240),
            supplier="Zoetis Vietnam Ltd",
            shelf_location="Tủ lạnh vắc-xin ngăn A2",
            notes="Phòng viêm mũi, khí quản, calicivirus & panleukopenia"
        ),
        InventoryItem(
            sku="VAC-RAB-01",
            name="Rabisin (Vaccine phòng bệnh Dại Thú Cưng)",
            category=InventoryCategory.VACCINE.value,
            unit="Lọ",
            quantity=60.0,
            min_threshold=15.0,
            cost_price=50000.0,
            selling_price=120000.0,
            batch_number="RB2410C",
            expiry_date=today + timedelta(days=360),
            supplier="Boehringer Ingelheim VN",
            shelf_location="Tủ lạnh vắc-xin ngăn A3",
            notes="Tiêm định kỳ hàng năm cho chó mèo từ 3 tháng tuổi"
        ),
        InventoryItem(
            sku="MED-NEX-M",
            name="NexGard Spectra (7.5kg - 15kg) Trị ve rận & giun tim",
            category=InventoryCategory.MEDICINE.value,
            unit="Hộp",
            quantity=3.0, # Sắp hết hàng (dưới min_threshold 5)
            min_threshold=5.0,
            cost_price=210000.0,
            selling_price=310000.0,
            batch_number="NX2401M",
            expiry_date=today + timedelta(days=35), # Cận date cảnh báo!
            supplier="Boehringer Ingelheim VN",
            shelf_location="Kệ thuốc điều trị B1",
            notes="Dạng viên nhai vị thịt bò thơm ngon dễ uống"
        ),
        InventoryItem(
            sku="MED-BRO-CAT",
            name="Broadline trị nội ngoại ký sinh trùng cho Mèo",
            category=InventoryCategory.MEDICINE.value,
            unit="Ống",
            quantity=16.0,
            min_threshold=6.0,
            cost_price=175000.0,
            selling_price=270000.0,
            batch_number="BL2405X",
            expiry_date=today + timedelta(days=310),
            supplier="Boehringer Ingelheim VN",
            shelf_location="Kệ thuốc điều trị B2",
            notes="Nhỏ gáy chống ve, rận, ghẻ tai và sán dây"
        ),
        InventoryItem(
            sku="SPA-SHM-DERM",
            name="Dầu tắm thảo dược trị nấm ngứa Dermasebb 500ml",
            category=InventoryCategory.SPA_COSMETIC.value,
            unit="Chai",
            quantity=22.0,
            min_threshold=6.0,
            cost_price=180000.0,
            selling_price=290000.0,
            batch_number="DS2407K",
            expiry_date=today + timedelta(days=450),
            supplier="PetCare Dermatology Supply",
            shelf_location="Kệ Spa S1",
            notes="Chiết xuất tràm trà & miconazole trị nấm da hiệu quả"
        ),
        InventoryItem(
            sku="SPA-SHM-ART",
            name="Sữa tắm phục hồi & Dưỡng mượt Artero Hidratante 5L",
            category=InventoryCategory.SPA_COSMETIC.value,
            unit="Can 5L",
            quantity=5.0,
            min_threshold=2.0,
            cost_price=1250000.0,
            selling_price=1850000.0,
            batch_number="AR2403Z",
            expiry_date=today + timedelta(days=500),
            supplier="Artero Cosmetics Spain",
            shelf_location="Kệ Spa S2",
            notes="Dành cho các gói Spa VIP tạo kiểu cún Poodle, Pomeranian"
        ),
        InventoryItem(
            sku="NUT-RC-PD15",
            name="Thức ăn hạt Royal Canin Poodle Adult 1.5kg",
            category=InventoryCategory.NUTRITION.value,
            unit="Gói",
            quantity=18.0,
            min_threshold=5.0,
            cost_price=225000.0,
            selling_price=320000.0,
            batch_number="RC2404P",
            expiry_date=today + timedelta(days=200),
            supplier="Royal Canin Vietnam",
            shelf_location="Kệ Thức Ăn C1",
            notes="Công thức dinh dưỡng độc quyền nuôi dưỡng lông xoăn mềm mượt"
        ),
        InventoryItem(
            sku="NUT-RC-KT85",
            name="Pate mềm cho Mèo con Royal Canin Kitten 85g",
            category=InventoryCategory.NUTRITION.value,
            unit="Túi",
            quantity=2.0, # Sắp hết hàng
            min_threshold=12.0,
            cost_price=22000.0,
            selling_price=35000.0,
            batch_number="RC2402K",
            expiry_date=today + timedelta(days=180),
            supplier="Royal Canin Vietnam",
            shelf_location="Kệ Thức Ăn C2",
            notes="Giàu đạm và prebiotic hỗ trợ tiêu hóa mèo con dưới 12 tháng"
        ),
        InventoryItem(
            sku="SUP-FLX-GAC",
            name="Gạc vô trùng & Băng quấn đàn hồi tự dính PetFlex",
            category=InventoryCategory.MEDICAL_SUPPLIES.value,
            unit="Cuộn",
            quantity=50.0,
            min_threshold=15.0,
            cost_price=18000.0,
            selling_price=35000.0,
            batch_number="FX2409M",
            expiry_date=today + timedelta(days=700),
            supplier="Andover Healthcare USA",
            shelf_location="Tủ Vật Tư Y Tế V1",
            notes="Băng cố định vết thương không dính lông da cún mèo"
        )
    ]

    for item in sample_items:
        db.add(item)
        db.flush()
        # Tạo lịch sử nhập ban đầu
        tx = StockTransaction(
            item_id=item.id,
            transaction_type=TransactionType.IMPORT.value,
            quantity=item.quantity,
            unit_price=item.cost_price,
            total_price=item.quantity * item.cost_price,
            performer_name="Hệ thống khởi tạo",
            reference_code=f"INIT-{item.sku}",
            notes=f"Nhập hàng đầu kỳ từ {item.supplier}"
        )
        db.add(tx)

if __name__ == "__main__":
    seed_database()

