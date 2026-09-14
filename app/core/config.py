import os
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
    
    # Database (Microsoft SQL Server - Windows Authentication via pyodbc)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://@localhost/DEMO AI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )
    
    # AI Engine Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "offline") # "offline", "gemini", "openai"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

