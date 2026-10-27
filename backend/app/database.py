import sys
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
from .models import Base, User, Owner, Pet, Service, Appointment, CareRecord, VaccineReminder, Invoice, AISessionLog

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

engine_kwargs = {}
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
if "mssql" in settings.DATABASE_URL:
    engine_kwargs["use_setinputsizes"] = False

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_sqlserver_database():
    """Tự động kiểm tra và tạo database trên SQL Server nếu chưa tồn tại"""
    if "mssql" in settings.DATABASE_URL:
        try:
            import pyodbc
            auth_str = (
                f"UID={settings.SQLSERVER_USER};PWD={settings.SQLSERVER_PASSWORD};"
                if settings.SQLSERVER_USER and settings.SQLSERVER_PASSWORD
                else f"Trusted_Connection={settings.SQLSERVER_TRUSTED};"
            )
            master_conn_str = f"DRIVER={{{settings.SQLSERVER_DRIVER}}};SERVER={settings.SQLSERVER_SERVER};DATABASE=master;{auth_str}"
            conn = pyodbc.connect(master_conn_str, autocommit=True, timeout=5)
            cur = conn.cursor()
            cur.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{settings.SQLSERVER_DATABASE}') CREATE DATABASE [{settings.SQLSERVER_DATABASE}] COLLATE Vietnamese_CI_AS;")
            conn.close()
            print(f"[SQL Server] Đã xác nhận cơ sở dữ liệu '{settings.SQLSERVER_DATABASE}' sẵn sàng.")
        except Exception as e:
            print(f"[SQL Server] Lưu ý kiểm tra máy chủ SQL Server: {e}")

def migrate_from_sqlite(db: Session) -> bool:
    """Tự động đồng bộ dữ liệu từ file petcare.db sang SQL Server nếu có"""
    if not settings.DB_PATH.exists():
        return False
    try:
        import sqlite3
        sq_conn = sqlite3.connect(settings.DB_PATH)
        sq_conn.row_factory = sqlite3.Row
        sq_cur = sq_conn.cursor()

        user_rows = sq_cur.execute("SELECT * FROM users ORDER BY id").fetchall()
        if not user_rows:
            sq_conn.close()
            return False

        print(f"[SQL Server] Đang sao chép {len(user_rows)} người dùng từ SQLite sang SQL Server...")
        for row in user_rows:
            db.add(User(
                id=row['id'],
                username=row['username'],
                full_name=row['full_name'],
                email=row['email'],
                role=row['role'],
                password_hash=row['password_hash'],
                is_active=bool(row['is_active'])
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM owners ORDER BY id").fetchall():
            db.add(Owner(
                id=row['id'],
                name=row['name'],
                phone=row['phone'],
                email=row['email'],
                address=row['address'],
                notes=row['notes']
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM pets ORDER BY id").fetchall():
            db.add(Pet(
                id=row['id'],
                owner_id=row['owner_id'],
                name=row['name'],
                species=row['species'],
                breed=row['breed'],
                age_months=row['age_months'],
                gender=row['gender'],
                weight_kg=row['weight_kg'],
                allergies=row['allergies'],
                medical_history=row['medical_history'],
                avatar_url=row['avatar_url'],
                notes=row['notes']
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM services ORDER BY id").fetchall():
            db.add(Service(
                id=row['id'],
                name=row['name'],
                category=row['category'],
                duration_minutes=row['duration_minutes'],
                price=row['price'],
                description=row['description'],
                is_active=bool(row['is_active'])
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM appointments ORDER BY id").fetchall():
            db.add(Appointment(
                id=row['id'],
                pet_id=row['pet_id'],
                owner_id=row['owner_id'],
                service_id=row['service_id'],
                staff_id=row['staff_id'],
                appointment_date=row['appointment_date'],
                appointment_time=row['appointment_time'],
                status=row['status'],
                cancel_reason=row['cancel_reason'],
                notes=row['notes']
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM care_records ORDER BY id").fetchall():
            db.add(CareRecord(
                id=row['id'],
                pet_id=row['pet_id'],
                appointment_id=row['appointment_id'],
                staff_id=row['staff_id'],
                record_date=row['record_date'],
                fur_skin_condition=row['fur_skin_condition'],
                weight_recorded_kg=row['weight_recorded_kg'],
                behavior_notes=row['behavior_notes'],
                products_used=row['products_used'],
                staff_notes=row['staff_notes'],
                home_care_instructions=row['home_care_instructions']
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM vaccine_reminders ORDER BY id").fetchall():
            db.add(VaccineReminder(
                id=row['id'],
                pet_id=row['pet_id'],
                vaccine_name=row['vaccine_name'],
                dose_number=row['dose_number'],
                administered_date=row['administered_date'],
                next_due_date=row['next_due_date'],
                status=row['status'],
                notes=row['notes']
            ))
        db.commit()

        for row in sq_cur.execute("SELECT * FROM invoices ORDER BY id").fetchall():
            db.add(Invoice(
                id=row['id'],
                invoice_code=row['invoice_code'],
                owner_id=row['owner_id'],
                appointment_id=row['appointment_id'],
                total_amount=row['total_amount'],
                discount_amount=row['discount_amount'],
                final_amount=row['final_amount'],
                payment_method=row['payment_method'],
                payment_status=row['payment_status'],
                notes=row['notes']
            ))
        db.commit()

        try:
            for row in sq_cur.execute("SELECT * FROM ai_session_logs ORDER BY id").fetchall():
                db.add(AISessionLog(
                    id=row['id'],
                    feature_type=row['feature_type'],
                    pet_id=row['pet_id'],
                    user_prompt=row['user_prompt'],
                    ai_response=row['ai_response'],
                    has_disclaimer=bool(row['has_disclaimer']),
                    model_name=row['model_name']
                ))
            db.commit()
        except Exception:
            pass

        sq_conn.close()
        print("[SQL Server] Hoàn tất đồng bộ toàn bộ dữ liệu từ SQLite sang SQL Server!")
        return True
    except Exception as e:
        print(f"[SQL Server] Lỗi đồng bộ từ SQLite: {e}")
        db.rollback()
        return False

def init_db():
    ensure_sqlserver_database()
    
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
    
    # Check if DB has data already
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            if "mssql" in settings.DATABASE_URL and settings.DB_PATH.exists():
                migrated = migrate_from_sqlite(db)
                if not migrated:
                    seed_initial_data(db)
            else:
                seed_initial_data(db)
    finally:
        db.close()

def seed_initial_data(db: Session):
    # 1. USERS (Roles: admin, receptionist, staff)
    users = [
        User(
            username="admin",
            full_name="Nguyễn Văn Quản Lý",
            email="admin@petcare.vn",
            role="admin",
            password_hash="admin123", # For demo/school grading simplicity
            is_active=True
        ),
        User(
            username="le_tan",
            full_name="Trần Thu Lễ Tân",
            email="letan@petcare.vn",
            role="receptionist",
            password_hash="rec123",
            is_active=True
        ),
        User(
            username="groomer_duc",
            full_name="Hoàng Minh Đức (Groomer)",
            email="duc.groomer@petcare.vn",
            role="staff",
            password_hash="staff123",
            is_active=True
        )
    ]
    db.add_all(users)
    db.commit()

    # 2. OWNERS
    owners = [
        Owner(
            name="Nguyễn Thị Bích Trâm",
            phone="0987654321",
            email="tram.bich@gmail.com",
            address="12 Đường Hoàng Văn Thụ, TP. Thái Nguyên",
            notes="Khách hàng VIP, rất yêu chiều cún cưng"
        ),
        Owner(
            name="Trần Minh Quân",
            phone="0912345678",
            email="quan.tm@outlook.com",
            address="88 Đường Lương Ngọc Quyến, TP. Thái Nguyên",
            notes="Nuôi mèo Anh lông ngắn, thường thích dịch vụ tắm sấy thơm dịu"
        ),
        Owner(
            name="Lê Thuỳ Trang",
            phone="0978112233",
            email="trang.le@gmail.com",
            address="Khu Đô thị Crown Villas, TP. Thái Nguyên",
            notes="Nuôi 2 bé cún Golden và Poodle"
        ),
        Owner(
            name="Phạm Quốc Huy",
            phone="0934567890",
            email="huy.pq@gmail.com",
            address="45 Đường Bến Oánh, TP. Thái Nguyên",
            notes="Thường đặt lịch cuối tuần"
        )
    ]
    db.add_all(owners)
    db.commit()

    # 3. PETS
    pets = [
        Pet(
            owner_id=1,
            name="Bim Bim",
            species="Chó",
            breed="Poodle Toy lông xoăn",
            age_months=18,
            gender="Đực",
            weight_kg=3.5,
            allergies="Dị ứng với xà phòng có cồn và mùi nồng",
            medical_history="Đã tiêm 2 mũi dại và 7 bệnh năm trước, da hơi khô vào mùa đông",
            avatar_url="https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=150&auto=format&fit=crop&q=80",
            notes="Rất hiền, thích được gãi tai"
        ),
        Pet(
            owner_id=2,
            name="Miu Miu",
            species="Mèo",
            breed="Mèo Anh lông ngắn (British Shorthair)",
            age_months=14,
            gender="Cái",
            weight_kg=4.2,
            allergies="Không có",
            medical_history="Tẩy giun định kỳ 3 tháng trước, mắt hay chảy ghèn nhẹ",
            avatar_url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=150&auto=format&fit=crop&q=80",
            notes="Hơi nhát người lạ, cần nhân viên vuốt ve làm quen trước khi tắm"
        ),
        Pet(
            owner_id=3,
            name="Lạc Lạc",
            species="Chó",
            breed="Golden Retriever",
            age_months=24,
            gender="Đực",
            weight_kg=28.5,
            allergies="Không có",
            medical_history="Đang khỏe mạnh toàn diện, thích vận động nhiều",
            avatar_url="https://images.unsplash.com/photo-1552053831-71594a27632d?w=150&auto=format&fit=crop&q=80",
            notes="Năng động, cần buộc dây cẩn thận khi di chuyển"
        ),
        Pet(
            owner_id=3,
            name="Bắp",
            species="Chó",
            breed="Corgi chân ngắn",
            age_months=10,
            gender="Cái",
            weight_kg=9.8,
            allergies="Không",
            medical_history="Lông rụng nhiều khi thay mùa",
            avatar_url="https://images.unsplash.com/photo-1612536057832-2ff7ead7f363?w=150&auto=format&fit=crop&q=80",
            notes="Rất thích ăn thưởng bánh thưởng gà"
        ),
        Pet(
            owner_id=4,
            name="Bông Gòn",
            species="Mèo",
            breed="Mèo Ba Tư trắng",
            age_months=20,
            gender="Đực",
            weight_kg=4.0,
            allergies="Nhạy cảm với sữa tắm có hương liệu nhân tạo",
            medical_history="Lông dày dễ bị rối nút",
            avatar_url="https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=150&auto=format&fit=crop&q=80",
            notes="Cần chải tơ kỹ càng"
        )
    ]
    db.add_all(pets)
    db.commit()

    # 4. SERVICES
    services = [
        Service(
            name="Tắm Spa Thảo Mộc & Vệ Sinh Toàn Diện",
            category="Spa & Tắm",
            duration_minutes=60,
            price=150000.0,
            description="Tắm sấy tạo phồng, vắt tuyến hôi, vệ sinh mắt tai, cắt mài móng, xịt dưỡng lông hương hoa tự nhiên.",
            is_active=True
        ),
        Service(
            name="Cắt Tỉa Tạo Kiểu Lông Nghệ Thuật (Grooming VIP)",
            category="Cắt tỉa tạo kiểu",
            duration_minutes=90,
            price=280000.0,
            description="Tắm dưỡng làm mềm mượt, sấy phồng, cắt tỉa tạo kiểu theo phong cách Hàn/Nhật (Gấu Teddy, Boo, Tròn đầu).",
            is_active=True
        ),
        Service(
            name="Vệ Sinh Tai & Cắt Mài Móng Cơ Bản",
            category="Vệ sinh",
            duration_minutes=30,
            price=60000.0,
            description="Nhổ lông tai, nhỏ dung dịch làm sạch tai, cắt và dũa tròn móng tránh trầy xước.",
            is_active=True
        ),
        Service(
            name="Tiêm Phòng Vaccine Nhắc Lại 7 Bệnh / Dại",
            category="Tiêm phòng & Khám",
            duration_minutes=25,
            price=220000.0,
            description="Khám lâm sàng tổng quan, đo nhiệt độ, tiêm phòng vaccine nhập khẩu chính hãng kèm sổ theo dõi.",
            is_active=True
        ),
        Service(
            name="Tẩy Giun & Nhỏ Gáy Phòng Ve Rận Trọn Gói",
            category="Tiêm phòng & Khám",
            duration_minutes=20,
            price=90000.0,
            description="Uống thuốc tẩy giun phổ rộng và nhỏ gáy thảo dược phòng ve, rận, bọ chét hiệu quả 3 tháng.",
            is_active=True
        ),
        Service(
            name="Khách Sạn Thú Cưng Pet Hotel Theo Ngày",
            category="Khách sạn",
            duration_minutes=1440,
            price=200000.0,
            description="Phòng máy lạnh riêng biệt, camera theo dõi 24/7, chế độ ăn hạt dinh dưỡng và dạo chơi 2 lần/ngày.",
            is_active=True
        )
    ]
    db.add_all(services)
    db.commit()

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    next_week_str = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    # 5. APPOINTMENTS
    appointments = [
        Appointment(
            pet_id=1,
            owner_id=1,
            service_id=2, # Cắt tỉa VIP
            staff_id=3, # Hoàng Minh Đức
            appointment_date=today_str,
            appointment_time="09:00",
            status="confirmed",
            notes="Cắt tỉa phom gấu Teddy dễ thương cho bé Bim Bim"
        ),
        Appointment(
            pet_id=2,
            owner_id=2,
            service_id=1, # Tắm spa thảo mộc
            staff_id=3,
            appointment_date=today_str,
            appointment_time="14:30",
            status="in_progress",
            notes="Dùng sữa tắm dịu nhẹ cho mèo lông ngắn"
        ),
        Appointment(
            pet_id=3,
            owner_id=3,
            service_id=1, # Tắm spa
            staff_id=3,
            appointment_date=tomorrow_str,
            appointment_time="10:00",
            status="confirmed",
            notes="Golden Retriever tắm sấy phồng và chải lông rụng"
        ),
        Appointment(
            pet_id=4,
            owner_id=3,
            service_id=3, # Vệ sinh tai móng
            staff_id=3,
            appointment_date=yesterday_str,
            appointment_time="16:00",
            status="completed",
            notes="Đã vệ sinh sạch tai và dũa móng 4 chân"
        )
    ]
    db.add_all(appointments)
    db.commit()

    # 6. CARE RECORD (for completed appointment)
    care_records = [
        CareRecord(
            pet_id=4,
            appointment_id=4,
            staff_id=3,
            record_date=yesterday_str,
            fur_skin_condition="Da khỏe, không phát hiện ve rận, lông rụng vừa phải",
            weight_recorded_kg=9.8,
            behavior_notes="Bé Bắp hơi ngọ nguậy lúc cắt móng chân sau nhưng sau khi cho bánh thưởng thì rất ngoan",
            products_used="Dung dịch vệ sinh tai sinh học Bio-Ear, bột cầm máu móng an toàn",
            staff_notes="Đã kiểm tra tuyến hôi sạch sẽ, tai không viêm",
            home_care_instructions="Nhỏ nước muối sinh lý rửa mắt 1 lần/ngày, chải lông mỗi sáng để giảm lông rụng trên sàn."
        ),
        CareRecord(
            pet_id=1,
            appointment_id=None,
            staff_id=3,
            record_date=(datetime.date.today() - datetime.timedelta(days=15)).strftime("%Y-%m-%d"),
            fur_skin_condition="Lông xoăn tơ mượt, da cổ có nốt đỏ nhỏ do gãi nhẹ",
            weight_recorded_kg=3.4,
            behavior_notes="Rất quấn nhân viên, ngoan",
            products_used="Sữa tắm dịu da ngứa thảo dược hoa cúc",
            staff_notes="Khuyên chủ nuôi hạn chế cho bé gãi vùng cổ",
            home_care_instructions="Tránh đeo vòng cổ quá chật, giữ khô lông sau khi đi dạo."
        )
    ]
    db.add_all(care_records)
    db.commit()

    # 7. VACCINE REMINDERS
    vaccine_reminders = [
        VaccineReminder(
            pet_id=1,
            vaccine_name="Vaccine phòng 7 bệnh chó (Nobivac DHPPI+L)",
            dose_number=3,
            administered_date=(datetime.date.today() - datetime.timedelta(days=350)).strftime("%Y-%m-%d"),
            next_due_date=(datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
            status="pending",
            notes="Mũi nhắc lại hàng năm sắp đến hạn"
        ),
        VaccineReminder(
            pet_id=2,
            vaccine_name="Vaccine phòng dại Rabisin",
            dose_number=1,
            administered_date=(datetime.date.today() - datetime.timedelta(days=330)).strftime("%Y-%m-%d"),
            next_due_date=(datetime.date.today() + datetime.timedelta(days=12)).strftime("%Y-%m-%d"),
            status="pending",
            notes="Tiêm phòng định kỳ dại cho mèo"
        ),
        VaccineReminder(
            pet_id=3,
            vaccine_name="Tẩy giun định kỳ 3 tháng",
            dose_number=4,
            administered_date=(datetime.date.today() - datetime.timedelta(days=95)).strftime("%Y-%m-%d"),
            next_due_date=(datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
            status="overdue",
            notes="Đã quá hạn 2 ngày, cần liên hệ chủ nuôi đưa bé đến uống thuốc giun"
        )
    ]
    db.add_all(vaccine_reminders)
    db.commit()

    # 8. INVOICES
    invoices = [
        Invoice(
            invoice_code="INV-20261025-001",
            owner_id=3,
            appointment_id=4,
            total_amount=60000.0,
            discount_amount=0.0,
            final_amount=60000.0,
            payment_method="Chuyển khoản QR",
            payment_status="paid",
            paid_at=datetime.datetime.utcnow(),
            notes="Thanh toán dịch vụ vệ sinh tai móng cho bé Bắp"
        )
    ]
    db.add_all(invoices)
    db.commit()
