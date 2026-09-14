from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

connect_args = {}
engine_kwargs = {}

if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False
elif "mssql" in settings.DATABASE_URL:
    engine_kwargs["fast_executemany"] = True
    
    # Cấu hình pyodbc & MSSQL để luôn dùng kiểu NVARCHAR và SQL_WVARCHAR cho String/Text,
    # bảo toàn 100% tiếng Việt có dấu Unicode không bị biến thành dấu hỏi (?)
    from sqlalchemy.types import String as SAString, Text as SAText
    import sqlalchemy.dialects.mssql.pyodbc as mssql_pyodbc
    import sqlalchemy.dialects.mssql.base as mssql_base
    
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
