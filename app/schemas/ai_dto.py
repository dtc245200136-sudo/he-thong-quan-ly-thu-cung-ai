from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AIReminderRequest(BaseModel):
    pet_name: str
    owner_name: str
    service_or_vaccine_name: str
    scheduled_time: str
    reminder_type: str = "appointment" # "appointment" or "vaccine"
    channel: str = "zalo" # "sms", "zalo", "email"
    special_notes: Optional[str] = None

class AIReminderResponse(BaseModel):
    channel: str
    title: str
    message: str
    preparation_tips: List[str] = []
    generated_by: str

class AICareSummaryRequest(BaseModel):
    pet_id: int

class AICareSummaryResponse(BaseModel):
    pet_name: str
    pet_species: str
    pet_breed: Optional[str] = None
    age_str: str
    weight_trend: str
    total_visits: int
    health_digest: str
    grooming_highlights: str
    diet_care_advice: str
    warnings_for_staff: List[str] = []
    veterinary_disclaimer: str
    generated_by: str

class AIChatMessage(BaseModel):
    role: str # "user", "assistant", "system"
    content: str

class AIChatRequest(BaseModel):
    message: str
    image_data: Optional[str] = None # Base64 or image URL
    pet_context: Optional[Dict[str, Any]] = None # {name, species, breed, age, weight}
    chat_history: Optional[List[AIChatMessage]] = []

class AIChatResponse(BaseModel):
    reply: str
    is_emergency: bool = False
    emergency_level: str = "NONE" # "NONE", "MILD_ATTENTION", "CRITICAL_VET_REQUIRED"
    warning_badge: Optional[str] = None
    veterinary_disclaimer: str
    suggested_actions: List[str] = []
    generated_by: str

class AIConfigUpdateRequest(BaseModel):
    provider: str # "offline", "gemini", "openai"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

class AISymptomCheckRequest(BaseModel):
    species: str = "Chó" # "Chó" hoặc "Mèo"
    breed: Optional[str] = None
    age_str: Optional[str] = None
    symptoms: List[str] = [] # Danh sách triệu chứng chọn sẵn hoặc gõ
    symptom_description: Optional[str] = None # Mô tả chi tiết
    duration: Optional[str] = "1-2 ngày" # Thời gian xuất hiện triệu chứng
    behavior_changes: Optional[str] = None # Thay đổi hành vi

class AISymptomCheckResponse(BaseModel):
    risk_level: str # "LOW", "MEDIUM", "HIGH", "EMERGENCY"
    risk_label: str # "Mức độ nhẹ / Theo dõi", "Mức độ trung bình / Cần chăm sóc", "Nguy cơ cao / Khám thú y ngay"
    risk_color: str # "green", "yellow", "orange", "red"
    summary: str
    potential_causes: List[str] = []
    first_aid_and_care: List[str] = []
    recommended_services: List[Dict[str, Any]] = [] # [{name, category, reason, estimated_price}]
    should_see_vet: bool = False
    veterinary_disclaimer: str
    generated_by: str

