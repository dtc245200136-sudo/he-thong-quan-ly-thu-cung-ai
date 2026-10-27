import os
import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PetCare AI Pro - Hệ thống Quản lý Dịch vụ Thú cưng tích hợp AI"
    PROJECT_VERSION: str = "1.0.0"
    COURSE_NAME: str = "Ứng dụng trí tuệ nhân tạo - AIA331 (Mã số: 80286)"
    UNIVERSITY: str = "Đại học Thái Nguyên - Trường ĐH CNTT & TT (ICTU)"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "petcare-secret-key-super-secure-aia331-ictu-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database Settings: mysql, mssql, sqlite
    DB_TYPE: str = os.getenv("DB_TYPE", "mysql")

    # MySQL Settings
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "petcare_ai_db")

    # SQL Server Settings
    SQLSERVER_SERVER: str = os.getenv("SQLSERVER_SERVER", r".\SQL2022")
    SQLSERVER_DATABASE: str = os.getenv("SQLSERVER_DATABASE", "petcare_ai_db")
    SQLSERVER_DRIVER: str = os.getenv("SQLSERVER_DRIVER", "SQL Server")
    SQLSERVER_TRUSTED: str = os.getenv("SQLSERVER_TRUSTED", "yes")
    SQLSERVER_USER: str = os.getenv("SQLSERVER_USER", "")
    SQLSERVER_PASSWORD: str = os.getenv("SQLSERVER_PASSWORD", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # AI Engine Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "offline") # "offline", "gemini", "openai"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow", case_sensitive=True)

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            db_type = self.DB_TYPE.lower()
            if db_type == "sqlite":
                self.DATABASE_URL = "sqlite:///petcare_app.db"
            elif db_type == "mysql":
                quoted_pwd = urllib.parse.quote_plus(self.MYSQL_PASSWORD) if self.MYSQL_PASSWORD else ""
                auth_part = f"{self.MYSQL_USER}:{quoted_pwd}@" if self.MYSQL_USER else ""
                self.DATABASE_URL = f"mysql+pymysql://{auth_part}{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
            else:
                if self.SQLSERVER_USER and self.SQLSERVER_PASSWORD:
                    auth_part = f"UID={self.SQLSERVER_USER};PWD={self.SQLSERVER_PASSWORD};"
                else:
                    auth_part = f"Trusted_Connection={self.SQLSERVER_TRUSTED};"
                odbc_conn = f"DRIVER={{{self.SQLSERVER_DRIVER}}};SERVER={self.SQLSERVER_SERVER};DATABASE={self.SQLSERVER_DATABASE};{auth_part}"
                encoded = urllib.parse.quote_plus(odbc_conn)
                self.DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={encoded}"

settings = Settings()


