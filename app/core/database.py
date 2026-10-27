from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

connect_args = {}
engine_kwargs = {}

def ensure_database_exists():
    """Tự động kiểm tra và tạo database trên SQL Server nếu chưa tồn tại"""
    if "mssql" in settings.DATABASE_URL:
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
