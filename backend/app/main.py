import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import init_db
from .routes import (
    auth, owners, pets, services, appointments,
    care_records, vaccines, invoices, analytics, ai
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

import sys

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed demo data
    init_db()
    print(f"[PetCare AI] Database initialized successfully at {settings.DATABASE_URL}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"Học phần: {settings.COURSE} - Đề tài: {settings.PROJECT_CODE}\n{settings.UNIVERSITY}",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable caching for instant hot-reload of CSS & JS
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Include all API routes
app.include_router(auth.router)
app.include_router(owners.router)
app.include_router(pets.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(care_records.router)
app.include_router(vaccines.router)
app.include_router(invoices.router)
app.include_router(analytics.router)
app.include_router(ai.router)

# Mount frontend static directories
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "PetCare AI API is running! Frontend index.html not yet found."}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "course": settings.COURSE,
        "code": settings.PROJECT_CODE
    }
