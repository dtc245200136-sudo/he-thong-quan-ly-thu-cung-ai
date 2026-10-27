import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).resolve().parent
backend_dir = str(BASE_DIR / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.seed import seed_database

# Routers
from app.api.auth import router as auth_router
from app.api.owners import router as owners_router
from app.api.pets import router as pets_router
from app.api.services import router as services_router
from app.api.appointments import router as appointments_router
from app.api.care_records import router as care_records_router
from app.api.vaccinations import router as vaccinations_router
from app.api.invoices import router as invoices_router
from app.api.stats import router as stats_router
from app.api.ai_features import router as ai_router
from app.api.customer_portal import router as customer_router
from app.api.inventory import router as inventory_router

try:
    seed_database()
except Exception:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        seed_database()
    except Exception as e:
        print(f"Lỗi khởi tạo seed data: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=f"Hệ thống Quản lý Dịch vụ Thú cưng & Lịch Chăm sóc Tích hợp AI - Học phần {settings.COURSE_NAME} - {settings.UNIVERSITY}",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(owners_router, prefix=settings.API_V1_STR)
app.include_router(pets_router, prefix=settings.API_V1_STR)
app.include_router(services_router, prefix=settings.API_V1_STR)
app.include_router(appointments_router, prefix=settings.API_V1_STR)
app.include_router(care_records_router, prefix=settings.API_V1_STR)
app.include_router(vaccinations_router, prefix=settings.API_V1_STR)
app.include_router(invoices_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(customer_router, prefix=settings.API_V1_STR)



# Mount Frontend Files (serving frontend directory)
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_spa():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": f"{settings.PROJECT_NAME} API is running. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    import sys
    import uvicorn
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
        
    print(f"[*] Dang khoi dong {settings.PROJECT_NAME}...")
    print(f"[*] Truoc mat truy cap he thong tai: http://localhost:3000 (hoac http://127.0.0.1:3000)")
    print(f"[*] Tai lieu API Swagger: http://localhost:3000/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)

