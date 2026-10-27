import os
import urllib.parse
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "petcare.db"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "Hệ thống Quản lý Thú cưng và Lịch chăm sóc có Tích hợp AI"
    PROJECT_CODE: str = "80286"
    COURSE: str = "AIA331 - Ứng dụng trí tuệ nhân tạo"
    UNIVERSITY: str = "Đại học Thái Nguyên - Trường ĐH CNTT & TT (ICTU)"
    
    # Database Settings: mysql, mssql (SQL Server) hoặc sqlite
    DB_TYPE: str = os.getenv("DB_TYPE", "mysql")

    # MySQL Settings
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "petcare_db")

    # SQL Server Settings
    SQLSERVER_SERVER: str = os.getenv("SQLSERVER_SERVER", r".\SQL2022")
    SQLSERVER_DATABASE: str = os.getenv("SQLSERVER_DATABASE", "petcare_db")
    SQLSERVER_DRIVER: str = os.getenv("SQLSERVER_DRIVER", "SQL Server")
    SQLSERVER_USER: str = os.getenv("SQLSERVER_USER", "")
    SQLSERVER_PASSWORD: str = os.getenv("SQLSERVER_PASSWORD", "")
    SQLSERVER_TRUSTED: str = os.getenv("SQLSERVER_TRUSTED", "yes")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_PATH: Path = DB_PATH

    SECRET_KEY: str = "petcare-secret-key-aia331-ictu-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # AI Engine Settings
    DEFAULT_AI_PROVIDER: str = "auto" # "auto", "gemini", "openai", "heuristic"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            db_type = self.DB_TYPE.lower()
            if db_type == "sqlite":
                self.DATABASE_URL = f"sqlite:///{DB_PATH}"
            elif db_type == "mysql":
                quoted_pwd = urllib.parse.quote_plus(self.MYSQL_PASSWORD) if self.MYSQL_PASSWORD else ""
                auth_part = f"{self.MYSQL_USER}:{quoted_pwd}@" if self.MYSQL_USER else ""
                self.DATABASE_URL = f"mysql+pymysql://{auth_part}{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
            else:
                if self.SQLSERVER_USER and self.SQLSERVER_PASSWORD:
                    auth_part = f"UID={self.SQLSERVER_USER};PWD={self.SQLSERVER_PASSWORD};"
                else:
                    auth_part = f"Trusted_Connection={self.SQLSERVER_TRUSTED};"
                
                odbc_str = f"DRIVER={{{self.SQLSERVER_DRIVER}}};SERVER={self.SQLSERVER_SERVER};DATABASE={self.SQLSERVER_DATABASE};{auth_part}"
                encoded = urllib.parse.quote_plus(odbc_str)
                self.DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={encoded}"

settings = Settings()


