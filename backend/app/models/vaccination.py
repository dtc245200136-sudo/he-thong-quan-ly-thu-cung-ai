import enum
from datetime import date
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class VaccinationStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"  # Đã lên lịch hẹn tiêm
    COMPLETED = "COMPLETED"  # Đã tiêm thành công
    OVERDUE = "OVERDUE"      # Quá hạn chưa tiêm
    CANCELLED = "CANCELLED"  # Hủy / Tạm hoãn (thú cưng ốm, sốt, đổi lịch)

    @classmethod
    def get_display_name(cls, status_val: str) -> str:
        names = {
            cls.SCHEDULED.value: "Đã lên lịch",
            cls.COMPLETED.value: "Đã tiêm chủng",
            cls.OVERDUE.value: "Quá hạn tiêm",
            cls.CANCELLED.value: "Tạm hoãn / Đã hủy"
        }
        return names.get(status_val, status_val)


class VaccinationSchedule(Base):
    __tablename__ = "vaccination_schedules"

    # Hiệu năng: Index tổng hợp tối ưu cho các truy vấn lọc lịch tiêm thường xuyên
    __table_args__ = (
        Index("ix_vac_pet_id_status", "pet_id", "status"),
        Index("ix_vac_status_due_date", "status", "next_due_date"),
    )

    # Khóa chính & Khóa ngoại
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chi tiết Vaccine lâm sàng
    vaccine_name = Column(String(150), nullable=False, index=True)   # Vd: Vaccine 7 bệnh cho Chó, Vaccine 4 bệnh cho Mèo, Dại (Rabies)
    dose_number = Column(String(50), nullable=True)                   # Vd: Mũi 1, Mũi 2, Mũi 3, Mũi nhắc định kỳ hàng năm
    manufacturer = Column(String(100), nullable=True)                 # Vd: Zoetis, Boehringer Ingelheim, Virbac, Nobivac...
    batch_number = Column(String(60), nullable=True)                  # Số lô vaccine để truy xuất nguồn gốc & kiểm định an toàn
    
    # Thời gian & Trạng thái
    administered_date = Column(Date, nullable=True)                   # Ngày thực tế đã tiêm
    next_due_date = Column(Date, nullable=False, index=True)          # Ngày hẹn tiêm nhắc lại
    status = Column(String(30), default=VaccinationStatus.SCHEDULED.value, nullable=False, index=True)
    
    # Bác sĩ thực hiện & Theo dõi phản ứng lâm sàng
    administered_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # Bác sĩ / Kỹ thuật viên phụ trách
    reaction_notes = Column(String(255), nullable=True)               # Phản ứng sau tiêm: Bình thường, sốt nhẹ, sưng vết tiêm...
    notes = Column(Text, nullable=True)                               # Lời dặn dò bác sĩ, vị trí tiêm (dưới da gáy/bắp đùi)
    
    # Nhắc lịch tự động & Thời gian hệ thống
    reminder_sent = Column(DateTime, nullable=True)                   # Thời điểm AI gửi thông báo nhắc lịch qua Zalo/SMS
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Quan hệ thực thể (Relationships)
    pet = relationship("Pet", back_populates="vaccinations")
    administered_by = relationship("User", foreign_keys=[administered_by_id])

    # Danh mục phác đồ vaccine tiêu chuẩn hỗ trợ AI & gợi ý lịch
    CORE_VACCINES_DOG: List[Dict[str, Any]] = [
        {"name": "Vaccine 7 bệnh (Care, Parvo, Viêm gan, Ho cũi, Lepto, Corona...)", "months_interval": 12},
        {"name": "Vaccine Dại (Rabies)", "months_interval": 12},
        {"name": "Tẩy giun & Ký sinh trùng định kỳ", "months_interval": 3},
    ]

    CORE_VACCINES_CAT: List[Dict[str, Any]] = [
        {"name": "Vaccine 4 bệnh (FPV Giảm bạch cầu, FHV-1, FCV, Chlamydia)", "months_interval": 12},
        {"name": "Vaccine Dại (Rabies)", "months_interval": 12},
        {"name": "Tẩy giun & Phòng ve rận định kỳ", "months_interval": 3},
    ]

    # ===== Smart Model Properties & Nghiệp vụ tự động =====
    @property
    def is_overdue(self) -> bool:
        """Kiểm tra xem lịch tiêm có bị quá hạn so với ngày hiện tại hay không."""
        return (
            self.status == VaccinationStatus.SCHEDULED.value
            and self.next_due_date is not None
            and self.next_due_date < date.today()
        )

    @property
    def days_until_due(self) -> Optional[int]:
        """Số ngày còn lại đến ngày hẹn tiêm (giá trị âm biểu thị số ngày đã quá hạn)."""
        if not self.next_due_date:
            return None
        return (self.next_due_date - date.today()).days

    @property
    def effective_status(self) -> str:
        """Trạng thái thực tế: Tự động chuyển đổi thành OVERDUE nếu đã quá ngày hẹn mà chưa tiêm."""
        if self.is_overdue:
            return VaccinationStatus.OVERDUE.value
        return self.status

    @property
    def status_display(self) -> str:
        """Tên hiển thị tiếng Việt thân thiện của trạng thái tiêm phòng."""
        return VaccinationStatus.get_display_name(self.effective_status)

    def mark_administered(
        self,
        administered_date: Optional[date] = None,
        next_due_date: Optional[date] = None,
        dose_number: Optional[str] = None,
        batch_number: Optional[str] = None,
        manufacturer: Optional[str] = None,
        administered_by_id: Optional[int] = None,
        reaction_notes: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """Đánh dấu hoàn thành mũi tiêm và tự động thiết lập ngày hẹn tiếp theo."""
        self.administered_date = administered_date or date.today()
        self.status = VaccinationStatus.COMPLETED.value
        if next_due_date:
            self.next_due_date = next_due_date
        if dose_number:
            self.dose_number = dose_number
        if batch_number:
            self.batch_number = batch_number
        if manufacturer:
            self.manufacturer = manufacturer
        if administered_by_id:
            self.administered_by_id = administered_by_id
        if reaction_notes:
            self.reaction_notes = reaction_notes
        if notes:
            self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thực thể thành Dictionary phục vụ API, AI Engine và hiển thị."""
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "vaccine_name": self.vaccine_name,
            "dose_number": self.dose_number,
            "manufacturer": self.manufacturer,
            "batch_number": self.batch_number,
            "administered_date": str(self.administered_date) if self.administered_date else None,
            "next_due_date": str(self.next_due_date) if self.next_due_date else None,
            "status": self.effective_status,
            "status_display": self.status_display,
            "is_overdue": self.is_overdue,
            "days_until_due": self.days_until_due,
            "administered_by_id": self.administered_by_id,
            "reaction_notes": self.reaction_notes,
            "notes": self.notes,
            "reminder_sent": self.reminder_sent.isoformat() if self.reminder_sent else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<VaccinationSchedule id={self.id} pet_id={self.pet_id} "
            f"vaccine='{self.vaccine_name}' due={self.next_due_date} status='{self.effective_status}'>"
        )
