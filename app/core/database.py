from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

connect_args = {}
engine_kwargs = {}

def ensure_database_exists():
    """Tự động kiểm tra và tạo database trên MySQL hoặc SQL Server nếu chưa tồn tại"""
    if "mysql" in settings.DATABASE_URL:
        try:
            import pymysql
            conn = pymysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                connect_timeout=5
            )
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"[MySQL] Đã xác nhận cơ sở dữ liệu '{settings.MYSQL_DATABASE}' sẵn sàng.")
        except Exception as e:
            print(f"[MySQL] Lưu ý kiểm tra database: {e}")
    elif "mssql" in settings.DATABASE_URL:
        try:
            import pyodbc
            auth_part = (
                f"UID={settings.SQLSERVER_USER};PWD={settings.SQLSERVER_PASSWORD};"
                if settings.SQLSERVER_USER and settings.SQLSERVER_PASSWORD
                else f"Trusted_Connection={settings.SQLSERVER_TRUSTED};"
            )
            master_conn_str = f"DRIVER={{{settings.SQLSERVER_DRIVER}}};SERVER={settings.SQLSERVER_SERVER};DATABASE=master;{auth_part}"
            conn = pyodbc.connect(master_conn_str, autocommit=True, timeout=5)
            cur = conn.cursor()
            cur.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{settings.SQLSERVER_DATABASE}') CREATE DATABASE [{settings.SQLSERVER_DATABASE}] COLLATE Vietnamese_CI_AS;")
            conn.close()
        except Exception as e:
            print(f"[SQL Server] Lưu ý kiểm tra database: {e}")

ensure_database_exists()

if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
elif "mysql" in settings.DATABASE_URL:
    engine_kwargs["pool_recycle"] = 3600
    engine_kwargs["pool_pre_ping"] = True
elif "mssql" in settings.DATABASE_URL:
    engine_kwargs["use_setinputsizes"] = False
    if "ODBC Driver" in settings.DATABASE_URL:
        engine_kwargs["fast_executemany"] = True
    
    # Cấu hình pyodbc & MSSQL để luôn dùng kiểu NVARCHAR và SQL_WVARCHAR cho String/Text,
    # bảo toàn 100% tiếng Việt có dấu Unicode không bị biến thành dấu hỏi (?)
    import re
    from datetime import datetime
    from sqlalchemy.types import String as SAString, Text as SAText, DateTime as SADateTime, TypeDecorator
    import sqlalchemy.dialects.mssql.pyodbc as mssql_pyodbc
    import sqlalchemy.dialects.mssql.base as mssql_base
    
    class SafeDateTime(TypeDecorator):
        impl = SADateTime
        cache_ok = True

        def process_result_value(self, value, dialect):
            if value is None:
                return None
            if isinstance(value, str):
                s = re.sub(r'(\.\d{6})\d+', r'\1', value)
                try:
                    return datetime.fromisoformat(s)
                except Exception:
                    return value
            return value

    mssql_pyodbc.MSDialect_pyodbc.colspecs[SADateTime] = SafeDateTime
    mssql_pyodbc.MSDialect_pyodbc.colspecs[SAString] = mssql_pyodbc._Unicode_pyodbc
    mssql_pyodbc.MSDialect_pyodbc.colspecs[SAText] = mssql_pyodbc._UnicodeText_pyodbc
    mssql_base.MSTypeCompiler.visit_VARCHAR = lambda self, type_, **kw: self._extend("NVARCHAR", type_, length=type_.length or "max")
    mssql_base.MSTypeCompiler.visit_TEXT = lambda self, type_, **kw: "NVARCHAR(max)"

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Kiểm tra kết nối cơ sở dữ liệu và tự động dự phòng nếu máy chủ chưa bật
if "sqlite" not in settings.DATABASE_URL:
    try:
        with engine.connect() as test_conn:
            pass
        if "mysql" in settings.DATABASE_URL:
            print(f"[MySQL] Kết nối thành công tới máy chủ MySQL ({settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE})")
        elif "mssql" in settings.DATABASE_URL:
            print(f"[SQL Server] Kết nối thành công tới SQL Server ({settings.SQLSERVER_SERVER}/{settings.SQLSERVER_DATABASE})")
    except Exception as e:
        if "mysql" in settings.DATABASE_URL:
            print(f"[CẢNH BÁO DATABASE] Không thể kết nối tới MySQL tại {settings.MYSQL_HOST}:{settings.MYSQL_PORT} ({e}).")
            print("[CẢNH BÁO DATABASE] Gợi ý: Hãy bật dịch vụ MySQL (qua XAMPP hoặc Windows Services), hoặc kiểm tra mật khẩu trong .env.")
            print("[CẢNH BÁO DATABASE] Đang tự động chuyển sang chế độ dự phòng SQLite (petcare.db) để hệ thống hoạt động ổn định!")
        else:
            print(f"[CẢNH BÁO DATABASE] Không thể kết nối SQL Server ({e}). Chuyển sang SQLite.")
        fallback_url = "sqlite:///petcare_app.db"
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
