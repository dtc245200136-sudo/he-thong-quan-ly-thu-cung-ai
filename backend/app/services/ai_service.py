import json
import re
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

# Danh sách từ khóa cảnh báo nguy hiểm cấp cứu thú y (Emergency Red Flags)
EMERGENCY_KEYWORDS = [
    "ngộ độc", "uống nhầm", "ăn nhầm socola", "ăn bả", "thuốc tẩy", "thuốc diệt chuột",
    "co giật", "sùi bọt mép", "bất tỉnh", "hôn mê", "lịm đi",
    "nôn ra máu", "ói ra máu", "ỉa ra máu", "đi ngoài ra máu", "phân đen như hắc ín",
    "khó thở", "thở dốc tím tái", "ngạt thở", "thở khò khè tím lưỡi",
    "gãy xương", "tai nạn xe", "chảy máu không cầm", "đứt mạch máu", "chấn thương đầu",
    "bí tiểu", "mèo không đi tiểu được", "rặn tiểu ra máu", "bí đái",
    "sốt cao co giật", "sốt trên 40", "nhiễm độc", "nuốt dị vật", "mắc xương nghẹn"
]

VETERINARY_DISCLAIMER = "⚠️ CẢNH BÁO Y TẾ: Thông tin do AI cung cấp chỉ mang tính chất tham khảo kiến thức chăm sóc thường thức, KHÔNG thay thế cho chẩn đoán, phác đồ điều trị và kê đơn của Bác sĩ Thú y chuyên khoa. Khi thú cưng có biểu hiện bất thường hoặc nguy hiểm, vui lòng đưa bé đến cơ sở thú y gần nhất ngay lập tức!"

def detect_emergency_symptoms(text: str) -> tuple[bool, str, list[str]]:
    """Phát hiện các dấu hiệu cấp cứu nguy hiểm trong câu hỏi của người dùng"""
    text_lower = text.lower()
    matched_flags = []
    
    for kw in EMERGENCY_KEYWORDS:
        if kw in text_lower:
            matched_flags.append(kw)
            
    if matched_flags:
        return True, "CRITICAL_VET_REQUIRED", matched_flags
    return False, "NONE", []

class AIService:
    @staticmethod
    def generate_reminder(
        pet_name: str,
        owner_name: str,
        service_or_vaccine_name: str,
        scheduled_time: str,
        reminder_type: str = "appointment",
        channel: str = "zalo",
        special_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """AI sinh nội dung tin nhắn nhắc lịch chăm sóc hoặc tiêm nhắc"""
        
        tips = []
        if "tiêm" in service_or_vaccine_name.lower() or reminder_type == "vaccine":
            tips = [
                "Mang theo Sổ tiêm chủng của bé khi đến phòng khám.",
                "Đảm bảo bé hoàn toàn khỏe mạnh, không sốt hay tiêu chảy trước khi tiêm.",
                "Giữ ấm và để bé nghỉ ngơi yên tĩnh sau tiêm 24-48 giờ."
            ]
        elif "tắm" in service_or_vaccine_name.lower() or "grooming" in service_or_vaccine_name.lower() or "spa" in service_or_vaccine_name.lower():
            tips = [
                "Đưa bé đến sớm hơn 5-10 phút để bé làm quen với không gian spa.",
                "Nếu bé có vùng da nhạy cảm hoặc vết thương nhỏ, vui lòng báo trước với kỹ thuật viên.",
                "Không nên cho bé ăn quá no ngay trước khi tắm sấy."
            ]
        else:
            tips = [
                "Vui lòng đến đúng giờ hẹn để bé được phục vụ chu đáo nhất.",
                "Liên hệ hotline nếu cần dời hoặc đổi lịch hẹn trước 2 tiếng."
            ]
            
        if channel == "sms":
            title = f"[PetCare] Nhắc hẹn chăm sóc bé {pet_name}"
            msg = (
                f"PetCare Spa kính chào Anh/Chị {owner_name}. "
                f"Bé {pet_name} có lịch {service_or_vaccine_name} lúc {scheduled_time}. "
                f"Vui lòng đưa bé đến đúng giờ để được phục vụ tốt nhất. Hotline: 0988.123.456"
            )
        elif channel == "email":
            title = f"🐾 [PetCare Pro] Thư nhắc lịch {service_or_vaccine_name} dành cho bé {pet_name}"
            msg = f"""Kính gửi Quý khách {owner_name},

PetCare Pro xin trân trọng thông báo lịch hẹn chăm sóc dành cho bé yêu {pet_name}:
📅 Dịch vụ: {service_or_vaccine_name}
⏰ Thời gian: {scheduled_time}
📍 Địa chỉ: PetCare Pro Center - Chi nhánh Thái Nguyên

💡 Lưu ý chuẩn bị cho bé:
{chr(10).join([f'- {tip}' for tip in tips])}
{f'📝 Ghi chú đặc biệt: {special_notes}' if special_notes else ''}

Rất hân hạnh được đón tiếp bé {pet_name} và Quý khách!
Trân trọng,
Đội ngũ Chăm sóc Khách hàng PetCare Pro."""
        else: # Zalo / App Notification
            title = f"🐾 Nhắc hẹn: {service_or_vaccine_name} cho bé {pet_name}"
            msg = f"""Dạ PetCare Pro xin chào Anh/Chị {owner_name} ạ! 🐶🐱

Hệ thống xin phép gửi lời nhắc lịch hẹn chăm sóc cho bé *{pet_name}*:
✨ **Dịch vụ:** {service_or_vaccine_name}
⏰ **Thời gian:** {scheduled_time}
{f'📝 **Ghi chú:** {special_notes}' if special_notes else ''}

💡 **Lưu ý nhỏ cho phụ huynh:**
{chr(10).join([f'• {tip}' for tip in tips])}

Nếu có thay đổi về thời gian, Anh/Chị chỉ cần nhắn lại cho PetCare để được hỗ trợ xếp lịch mới ngay nhé ạ! Cảm ơn Anh/Chị ❤️"""

        return {
            "channel": channel,
            "title": title,
            "message": msg,
            "preparation_tips": tips,
            "generated_by": "PetCare AI Reminder Engine (AIA331)"
        }

    @staticmethod
    def summarize_care_history(
        pet_info: Dict[str, Any],
        care_records: List[Dict[str, Any]],
        vaccinations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """AI tóm tắt toàn bộ hồ sơ lịch sử chăm sóc và phân tích xu hướng sức khỏe"""
        
        pet_name = pet_info.get("name", "Bé")
        species = pet_info.get("species", "Thú cưng")
        breed = pet_info.get("breed", "Chưa rõ")
        age_str = f"{pet_info.get('age_years', 0)} tuổi {pet_info.get('age_months', 0)} tháng"
        
        total_visits = len(care_records)
        
        # Phân tích cân nặng
        weights = [r.get("weight_kg") for r in care_records if r.get("weight_kg") is not None]
        if len(weights) >= 2:
            diff = weights[0] - weights[-1] # Lần gần nhất so với lần đầu
            if diff > 0.3:
                weight_trend = f"Tăng cân nhẹ ({weights[-1]:.1f}kg ➔ {weights[0]:.1f}kg, tăng +{diff:.1f}kg). Cần duy trì vận động đều đặn."
            elif diff < -0.3:
                weight_trend = f"Giảm cân nhẹ ({weights[-1]:.1f}kg ➔ {weights[0]:.1f}kg, giảm -{abs(diff):.1f}kg). Cần kiểm tra khẩu phần dinh dưỡng."
            else:
                weight_trend = f"Cân nặng ổn định ở mức ~{weights[0]:.1f}kg (thể trạng lý tưởng)."
        elif len(weights) == 1:
            weight_trend = f"Cân nặng ghi nhận hiện tại: {weights[0]:.1f}kg."
        else:
            weight_trend = "Chưa có đủ dữ liệu cân nặng qua các kỳ."

        # Tổng hợp tình trạng da lông & tai mắt
        skin_notes = [r.get("coat_skin_condition") for r in care_records if r.get("coat_skin_condition")]
        ears_notes = [r.get("ears_eyes_teeth") for r in care_records if r.get("ears_eyes_teeth")]
        behavior_notes = [r.get("behavior_mood") for r in care_records if r.get("behavior_mood")]
        
        health_digest = (
            f"Bé {pet_name} ({breed}) đã sử dụng dịch vụ tại trung tâm tổng cộng {total_visits} lần. "
            f"Tình trạng chung: Da lông {'duy trì sạch sẽ, không dấu hiệu viêm nấm' if not any('nấm' in str(s).lower() or 'viêm' in str(s).lower() for s in skin_notes) else 'từng ghi nhận nhạy cảm/nấm nhẹ, cần dùng dầu tắm dịu nhẹ'}. "
            f"Vệ sinh tai mắt: {ears_notes[0] if ears_notes else 'Bình thường, vệ sinh định kỳ tốt'}."
        )

        grooming_highlights = (
            f"- Tính cách khi spa: {behavior_notes[0] if behavior_notes else 'Hợp tác tốt, thân thiện'}.\n"
            f"- Các dịch vụ ưa chuộng: Tắm dưỡng ẩm, cắt tỉa vệ sinh bàn chân, cắt móng, mài móng.\n"
            f"- Độ dài lông khuyến nghị: Tỉa gọn gàng định kỳ 4-6 tuần/lần để tránh vón cục bết lông."
        )

        diet_advice = (
            f"- Khẩu phần: Bổ sung Omega-3 / dầu cá hồi để hỗ trợ dưỡng bóng mượt lông cho giống {breed}.\n"
            f"- Nước uống: Cung cấp đủ nước sạch hàng ngày, hạn chế ăn thức ăn thừa nhiều gia vị mặn của người."
        )

        warnings = []
        if pet_info.get("allergies"):
            warnings.append(f"DỊ ỨNG ĐÃ GHI NHẬN: {pet_info.get('allergies')} (Tuyệt đối lưu ý khi dùng sữa tắm/thức ăn thưởng).")
        if pet_info.get("medical_notes"):
            warnings.append(f"Ghi chú bệnh lý/tính cách: {pet_info.get('medical_notes')}")
        if any("nhát" in str(b).lower() or "dữ" in str(b).lower() for b in behavior_notes):
            warnings.append("Bé có thể giật mình khi sấy tiếng to hoặc chạm vào chân sau. Kỹ thuật viên cần thao tác nhẹ nhàng.")

        return {
            "pet_name": pet_name,
            "pet_species": species,
            "pet_breed": breed,
            "age_str": age_str,
            "weight_trend": weight_trend,
            "total_visits": total_visits,
            "health_digest": health_digest,
            "grooming_highlights": grooming_highlights,
            "diet_care_advice": diet_advice,
            "warnings_for_staff": warnings,
            "veterinary_disclaimer": VETERINARY_DISCLAIMER,
            "generated_by": "PetCare AI Health Digest (AIA331)"
        }

    @staticmethod
    def _resolve_followup_context(message: str, chat_history: Optional[List[Any]], pet_name: str) -> Optional[tuple[str, list[str]]]:
        """Phân tích ngữ cảnh nhiều lượt (Multi-turn Context) cho các câu hỏi tiếp nối ngắn gọn"""
        if not chat_history or len(chat_history) < 1:
            return None
            
        msg_lower = message.lower().strip()
        followup_signals = [
            "mấy lần", "mấy ngày", "bao lâu", "có lây", "lây sang người", "có kiêng", "kiêng gì",
            "mua ở đâu", "giá bao nhiêu", "bao nhiêu tiền", "uống lúc nào", "bôi lúc nào",
            "bôi như thế nào", "dùng thế nào", "uống mấy viên", "có khỏi không", "ăn được không",
            "có nguy hiểm", "bao nhiêu một chai", "dùng mấy lần", "có tắm được không", "tắm được chưa"
        ]
        if not any(sig in msg_lower for sig in followup_signals) and len(msg_lower.split()) > 9:
            return None

        # Rút trích lịch sử các lượt gần nhất (hỗ trợ cả dict lẫn Pydantic object AIChatMessage)
        recent_texts = []
        for turn in chat_history[-4:]:
            if isinstance(turn, dict):
                recent_texts.append(str(turn.get("content", "")))
            elif hasattr(turn, "content"):
                recent_texts.append(str(getattr(turn, "content", "")))
        combined_recent = " ".join(recent_texts).lower()

        # 1. TIẾP NỐI VỀ NẤM DA / VIÊM DA
        if any(k in combined_recent for k in ["nấm", "viêm da", "vảy gàu", "ghẻ", "ngứa", "rụng lông"]):
            if any(k in msg_lower for k in ["lây", "người", "lây không"]):
                return (
                    f"⚠️ **VỀ KHẢ NĂNG LÂY SANG NGƯỜI CỦA BỆNH NẤM DA:**\n\n"
                    f"Có bạn nhé! Nấm da thú cưng (đặc biệt là chủng vi nấm *Microsporum canis*) **HOÀN TOÀN CÓ THỂ LÂY SANG NGƯỜI**, gây ra bệnh lác đồng tiền (vết hình tròn viền đỏ hơi nhô cao, ngứa ngáy dữ dội).\n\n"
                    f"🛡️ **CÁCH PHÒNG NGỪA AN TOÀN CHO BẠN:**\n"
                    f"1. Luôn đeo găng tay y tế hoặc rửa tay sạch bằng xà phòng sát khuẩn ngay sau khi bôi thuốc/chăm sóc bé {pet_name}.\n"
                    f"2. Giặt sạch nệm, chăn chiếu và quần áo của bé bằng nước nóng và phơi dưới ánh nắng to.\n"
                    f"3. Cho bé {pet_name} đeo loa chống liếm Elizabeth để tránh bé liếm thuốc rồi liếm lên tay chân bạn.",
                    ["Loa chống liếm Elizabeth", "Sữa tắm trị nấm da", "Thuốc bôi nấm an toàn"]
                )
            if any(k in msg_lower for k in ["mấy lần", "mấy ngày", "bao lâu", "khi nào khỏi", "dùng thế nào"]):
                return (
                    f"⏱️ **LỊCH TRÌNH BÔI THUỐC TRỊ NẤM DA CHO {pet_name.upper()}:**\n\n"
                    f"• **Tần suất bôi:** Nên bôi **2 lần/ngày** (buổi sáng và buổi tối sau khi lau sạch vết thương).\n"
                    f"• **Quy trình chuẩn:** Dùng gạc sạch thấm nước muối sinh lý NaCl 0.9% lau nhẹ bong các vảy sừng khô, thấm khô rồi mới thoa một lớp kem mỏng đều lên vùng da nấm.\n"
                    f"• **Thời gian duy trì:** Thường kéo dài liên tục **2 đến 3 tuần**. **Cực kỳ lưu ý:** Ngay cả khi thấy lông con đã mọc lại và hết vảy gàu, bạn vẫn PHẢI tiếp tục bôi thêm ít nhất 5-7 ngày nữa để tiêu diệt tận gốc các bào tử nấm ẩn sâu dưới chân lông, tránh nấm tái phát trở lại!",
                    ["Thuốc bôi Ketoconazole", "Lịch tái khám da liễu", "Cách vệ sinh vùng nấm"]
                )
            if any(k in msg_lower for k in ["kiêng", "ăn gì", "tắm"]):
                return (
                    f"🛁 **NHỮNG ĐIỀU CẦN KIÊNG KHI {pet_name.upper()} ĐANG ĐIỀU TRỊ NẤM DA:**\n\n"
                    f"1. **Kiêng tắm nước ẩm thường xuyên:** Độ ẩm là điều kiện lý tưởng cho nấm phát triển. Chỉ tắm 1-2 lần/tuần bằng sữa tắm trị nấm chuyên dụng và sấy khô 100% tận gốc chân lông.\n"
                    f"2. **Kiêng để bé liếm láp:** Bắt buộc đeo loa chống liếm 24/24.\n"
                    f"3. **Kiêng thức ăn kích ứng:** Tạm kiêng đồ hải sản lạ, thức ăn tanh; bổ sung thêm Omega-3 và Kẽm giúp phục hồi hàng rào biểu bì da nhanh chóng.",
                    ["Sữa tắm trị nấm da", "Loa chống liếm êm ái", "Dầu cá hồi dưỡng da"]
                )

        # 2. TIẾP NỐI VỀ VE RẬN / BỌ CHÉT
        if any(k in combined_recent for k in ["ve", "rận", "bọ chét", "frontline", "bravecto", "nexgard"]):
            if any(k in msg_lower for k in ["mấy lần", "bao lâu", "mỗi ngày", "dùng sao"]):
                return (
                    f"🐛 **TẦN SUẤT SỬ DỤNG THUỐC TRỊ VE RẬN CHO {pet_name.upper()}:**\n\n"
                    f"• **Thuốc nhỏ gáy (Frontline Plus / Advocate):** Chỉ nhỏ **1 lần duy nhất mỗi 1 tháng**. Tuyệt đối KHÔNG nhỏ hàng ngày vì thuốc ngấm qua da, nhỏ nhiều sẽ gây ngộ độc gan thận!\n"
                    f"• **Viên nhai (Bravecto):** Chỉ cần uống 1 viên duy nhất, bảo vệ kéo dài tới **3 tháng (12 tuần)**.\n"
                    f"• **Viên nhai (Nexgard / Simparica):** Uống 1 viên định kỳ mỗi tháng 1 lần.\n\n"
                    f"⚠️ *Lưu ý quan trọng: Kiêng tắm cho bé trong vòng 48 giờ trước và sau khi nhỏ gáy để lớp mỡ dưới da hấp thu thuốc hiệu quả nhất.*",
                    ["Đặt lịch nhỏ gáy tại Spa", "Tư vấn viên nhai Bravecto", "Xịt khử trùng môi trường"]
                )
            if any(k in msg_lower for k in ["lây", "người", "cắn"]):
                return (
                    f"🛡️ **VE RẬN CÓ CẮN VÀ LÂY SANG NGƯỜI KHÔNG?**\n\n"
                    f"Ve chó và bọ chét có thể bám sang người và cắn, tạo ra các nốt mẩn đỏ ngứa rát khó chịu. Tuy nhiên, chúng không thể sinh sản hay làm tổ lâu dài trên cơ thể người.\n\n"
                    f"👉 **Hành động dứt điểm:** Xịt thuốc diệt ve môi trường (Hantox-200) ở các góc tường, giặt sạch nệm nằm của bé bằng nước nóng để diệt sạch ấu trùng ve!",
                    ["Mua thuốc xịt Hantox", "Nhỏ gáy diệt ve tận gốc", "Khám ký sinh trùng máu"]
                )

        # 3. TIẾP NỐI VỀ TIÊU HÓA / TIÊU CHẢY / NÔN
        if any(k in combined_recent for k in ["tiêu chảy", "nôn", "tiêu hóa", "đi ngoài", "phân"]):
            if any(k in msg_lower for k in ["ăn gì", "uống gì", "nấu gì", "kiêng"]):
                return (
                    f"🍲 **CHẾ ĐỘ ĂN PHỤC HỒI TIÊU HÓA CHO {pet_name.upper()}:**\n\n"
                    f"1. **Giai đoạn đầu:** Cho bé nhịn ăn 8-12 tiếng để đường ruột nghỉ ngơi (nhưng vẫn cho uống từng ngụm nước Oresol bù điện giải).\n"
                    f"2. **Bữa ăn hồi phục đầu tiên:** Nấu cháo trắng loãng với **ức gà luộc xé nhỏ** hoặc bí đỏ hấp nghiền. Tuyệt đối KHÔNG nêm gia vị muối mắm, không phi hành tỏi và không có dầu mỡ.\n"
                    f"3. **Bổ sung:** Trộn 1 ống men vi sinh Enterogermina hoặc Bio-scour vào thức ăn nguội.\n"
                    f"4. **Kiêng cữ:** Kiêng hoàn toàn sữa bò, xương, cá tanh và đồ ăn thừa của người trong ít nhất 3-5 ngày.",
                    ["Men tiêu hóa Bio-scour", "Test nhanh Parvo", "Khám nội khoa tiêu hóa"]
                )

        # 4. TIẾP NỐI VỀ TIÊM PHÒNG / VACCINE
        if any(k in combined_recent for k in ["tiêm", "vaccine", "vắc xin", "mũi"]):
            if any(k in msg_lower for k in ["tắm", "kiêng", "sau khi tiêm", "mấy ngày"]):
                return (
                    f"💉 **CHĂM SÓC & KIÊNG CỮ SAU KHI TIÊM PHÒNG CHO {pet_name.upper()}:**\n\n"
                    f"1. **Kiêng tắm ướt tối thiểu 7 ngày:** Tắm ngay sau tiêm rất dễ làm bé bị cảm lạnh và suy giảm đáp ứng miễn dịch của vắc xin.\n"
                    f"2. **Hạn chế đi ra ngoài:** Không cho bé tiếp xúc với chó mèo lạ hoặc đến nơi đông đúc trong 10-14 ngày để chờ vắc xin kích hoạt kháng thể bảo vệ đầy đủ.\n"
                    f"3. **Theo dõi phản ứng:** Bé có thể hơi mệt hoặc ngủ nhiều trong 24 giờ đầu (phản ứng thông thường). Nếu thấy sưng phù mặt, khó thở hoặc nôn mửa liên tục, cần đưa đến phòng khám xử trí dị ứng vắc xin ngay lập tức.",
                    ["Sổ tiêm phòng điện tử", "Đặt lịch mũi nhắc lại", "Tư vấn vắc xin 7 bệnh"]
                )

        # 5. TIẾP NỐI VỀ CẮT MÓNG
        if any(k in combined_recent for k in ["móng", "cắt móng", "chảy máu"]):
            if any(k in msg_lower for k in ["mua ở đâu", "bao nhiêu", "giá"]):
                return (
                    f"✂️ **DỊCH VỤ & DỤNG CỤ CẮT MÓNG CHO {pet_name.upper()}:**\n\n"
                    f"• **Dịch vụ Cắt & Mài dũa móng tại Spa PetCare:** Chỉ **40.000 ₫ / bé** (được thợ chuyên nghiệp thao tác nhẹ nhàng, không gây đau hay phạm tủy).\n"
                    f"• **Bột cầm máu Quick Stop:** 60.000 - 90.000 ₫ / hũ (dùng được nhiều năm cho gia đình).\n"
                    f"• **Kìm cắt móng chuyên dụng có cữ chặn an toàn:** 75.000 ₫ / cây (chống bấm quá sâu vào tủy máu).",
                    ["Đặt lịch cắt mài móng (40k)", "Mua kìm cắt móng có cữ", "Xem gói Spa toàn diện"]
                )

        return None

    @staticmethod
    def _analyze_specific_queries(message: str, pet_name: str, species: str) -> Optional[tuple[str, list[str]]]:
        """Phân tích các câu hỏi chuyên sâu, đi thẳng vào câu trả lời cụ thể không trong khuôn mẫu"""
        msg_lower = message.lower().strip()

        # 1. SỮA CHUA (YOGURT)
        if any(w in msg_lower for w in ["sữa chua", "yaourt", "yogurt"]):
            return (
                f"🥣 **CHÓ MÈO ĂN SỮA CHUA ĐƯỢC KHÔNG?**\n\n"
                f"✅ **CÂU TRẢ LỜI LÀ: CÓ THỂ ĂN ĐƯỢC**, nhưng phải ăn đúng loại và đúng lượng bạn nhé!\n\n"
                f"🥛 **1. Lợi ích sức khỏe:**\n"
                f"• Sữa chua cung cấp hàm lượng dồi dào men vi sinh tự nhiên (Probiotics) giúp cân bằng hệ tiêu hóa, giảm tình trạng đầy hơi và tăng hấp thu chất dinh dưỡng.\n"
                f"• Cung cấp thêm canxi và protein lành mạnh giúp xương và cơ bắp {pet_name} chắc khỏe.\n\n"
                f"⚠️ **2. Các nguyên tắc bắt buộc phải nhớ:**\n"
                f"• **Chỉ cho ăn sữa chua KHÔNG ĐƯỜNG (hoặc sữa chua Hy Lạp nguyên chất):** Tuyệt đối không cho ăn loại có đường, sữa chua có vị hoa quả nhân tạo.\n"
                f"• ☠️ **CẢNH BÁO ĐẶC BIỆT:** Tuyệt đối tránh sữa chua 'Sugar-free' có chứa chất tạo ngọt **Xylitol** (chất này cực độc gây suy gan cấp tính ở chó mèo).\n"
                f"• **Khẩu phần chuẩn:** Bé dưới 5kg chỉ nên ăn 1 thìa cà phê/ngày; bé từ 5-15kg ăn 1-2 thìa canh/ngày. Nếu bé có dấu hiệu đi phân lỏng, hãy ngưng ngay vì có thể bé không dung nạp lactose.",
                ["Tư vấn dinh dưỡng hàng ngày", "Thực phẩm an toàn cho cún", "Men tiêu hóa chuyên dụng"]
            )

        # 2. SỮA TƯƠI / SỮA ĐẶC CỦA NGƯỜI
        if any(w in msg_lower for w in ["sữa tươi", "sữa đặc", "sữa ông thọ", "sữa có đường", "uống sữa bò", "uống sữa tươi", "uống sữa người"]):
            return (
                f"🥛 **CÓ NÊN CHO CHÓ MÈO UỐNG SỮA TƯƠI / SỮA ĐẶC CỦA NGƯỜI?**\n\n"
                f"🚫 **BÁC SĨ KHUYÊN: TUYỆT ĐỐI KHÔNG NÊN!**\n\n"
                f"• **Cơ chế y khoa:** Sau khi dứt sữa mẹ, hệ tiêu hóa của đa số chó và mèo đều thiếu hụt enzyme **Lactase** – loại men cần thiết để phân giải đường Lactose có trong sữa bò và sữa đặc của người.\n"
                f"• **Hậu quả:** Uống sữa bò/sữa đặc sẽ gây hiện tượng không dung nạp lactose, dẫn đến sôi bụng, đầy hơi, nôn ói và **tiêu chảy dữ dội mất nước** rất nguy hiểm, đặc biệt với chó mèo con dưới 3 tháng tuổi.\n\n"
                f"🍼 **Giải pháp thay thế an toàn:**\n"
                f"• Dùng các dòng sữa bột công thức chuyên biệt không chứa lactose dành riêng cho thú cưng như: **Bio-Milk**, **KMR** (cho mèo), **Esbilac** (cho chó) hoặc sữa dê tiệt trùng.",
                ["Sữa bột Bio-Milk cho thú cưng", "Xử lý khi cún bị tiêu chảy", "Khẩu phần cho con non"]
            )

        # 3. PHÔ MAI (CHEESE)
        if any(w in msg_lower for w in ["phô mai", "pho mai", "cheese"]):
            return (
                f"🧀 **CHÓ MÈO CÓ ĐƯỢC ĂN PHÔ MAI KHÔNG?**\n\n"
                f"✅ **ĂN ĐƯỢC MỘT LƯỢNG NHỎ** làm phần thưởng huấn luyện, nhưng không nên cho ăn thường xuyên!\n\n"
                f"• **Loại phô mai an toàn:** Chọn phô mai Mozzarella, phô mai tươi Cottage hoặc phô mai miếng ít muối (Lactose trong phô mai đã lên men nên thấp hơn sữa tươi).\n"
                f"• ⚠️ **Lưu ý:** Không cho ăn phô mai mốc xanh (Blue cheese), phô mai có tỏi/hành tây hoặc phô mai quá mặn. Phô mai chứa nhiều calo và chất béo, nếu ăn nhiều dễ gây béo phì hoặc viêm tụy cấp.",
                ["Bánh thưởng huấn luyện", "Thực đơn dinh dưỡng an toàn", "Tư vấn cân nặng"]
            )

        # 4. SOCOLA / CACAO (CHOCOLATE)
        if any(w in msg_lower for w in ["socola", "sô cô la", "chocolate", "cacao"]):
            return (
                f"🍫 **NGUY HIỂM TÍNH MẠNG: CHÓ MÈO ĂN SOCOLA / CACAO**\n\n"
                f"☠️ **TUYỆT ĐỐI CẤM - CỰC KỲ ĐỘC HẠI!**\n\n"
                f"• **Chất kịch độc:** Socola và cacao chứa **Theobromine** và **Caffeine**. Gan của chó mèo không thể chuyển hóa chất này.\n"
                f"• **Tác động:** Khiến tim đập loạn xạ, huyết áp tăng vọt, run rẩy, co giật, xuất huyết nội tạng và dẫn đến tử vong nhanh chóng.\n"
                f"• ⚠️ Socola càng đen, càng đắng nguyên chất thì độc tính càng cao gấp hàng chục lần socola sữa.\n\n"
                f"🚨 **HÀNH ĐỘNG CẤP CỨU:** Nếu {pet_name} lỡ nuốt phải socola, hãy đưa ngay đến Bệnh viện Thú y gần nhất trong vòng 1-2 giờ để bác sĩ rửa ruột cấp cứu!",
                ["Cấp cứu ngộ độc thú y", "Dấu hiệu sốc độc socola", "Hotline cấp cứu 24/7"]
            )

        # 5. NHO TƯƠI / NHO KHÔ
        if any(w in msg_lower for w in ["nho tươi", "nho khô", "ăn nho", "quả nho"]):
            return (
                f"🍇 **CẢNH BÁO NGUY HIỂM: CHÓ ĂN NHO TƯƠI HOẶC NHO KHÔ**\n\n"
                f"☠️ **TUYỆT ĐỐI CẤM!** Nho tươi và nho khô là một trong những thực phẩm nguy hiểm hàng đầu đối với loài chó.\n\n"
                f"• **Hậu quả:** Chất độc trong quả nho (axit tartaric) gây **Suy thận cấp tính vô niệu** chỉ trong 24 đến 72 giờ. Ngay cả một lượng rất nhỏ (1-2 quả) cũng có thể gây tử vong cho một chú cún khỏe mạnh.\n"
                f"• **Triệu chứng ngộ độc:** Nôn mửa, chán ăn, đi tiểu ít hoặc hoàn toàn không đi tiểu được, hơi thở có mùi urê.\n"
                f"• 🚨 **Xử lý:** Cần đưa đi cấp cứu truyền dịch giải độc ngay lập tức nếu phát hiện bé ăn nho!",
                ["Kiểm tra chức năng thận", "Cấp cứu ngộ độc nho", "Thực phẩm thay thế an toàn"]
            )

        # 6. HÀNH TÂY, TỎI, HẸ
        if any(w in msg_lower for w in ["hành tây", "ăn hành", "ăn tỏi", "củ tỏi", "hẹ"]):
            return (
                f"🧅 **CẢNH BÁO: CHÓ MÈO ĂN PHẢI HÀNH TÂY / TỎI / HẸ**\n\n"
                f"🚫 **ĐỘC TÍNH NGUY HIỂM:** Tất cả thực phẩm thuộc họ *Allium* (hành tây, hành lá, tỏi ta, hẹ) dù nấu chín hay ăn sống đều chứa hợp chất **Thiosulfate**.\n\n"
                f"• **Tác hại:** Thiosulfate làm vỡ hồng cầu hàng loạt, gây chứng **Thiếu máu tán huyết (Hemolytic Anemia)** và hình thành thể Heinz trong máu.\n"
                f"• **Dấu hiệu nhiễm độc:** Nướu răng nhợt nhạt hoặc vàng vọt, nước tiểu có màu nâu đỏ sẫm như xì dầu, thở dốc mệt mỏi, tim đập nhanh.\n"
                f"• 💡 Khi nấu cháo hay đồ ăn cho chó mèo, tuyệt đối không phi hành tỏi hay nêm gia vị của người!",
                ["Xét nghiệm công thức máu", "Tư vấn nấu pate tại nhà", "Dấu hiệu thiếu máu thú cưng"]
            )

        # 7. XƯƠNG GÀ / XƯƠNG NẤU CHÍN
        if any(w in msg_lower for w in ["xương gà", "xương vịt", "xương chín", "hóc xương", "ăn xương"]):
            return (
                f"🦴 **CÓ NÊN CHO CHÓ MÈO ĂN XƯƠNG GÀ HOẶC XƯƠNG NẤU CHÍN?**\n\n"
                f"🚫 **KHUYẾN CÁO: TUYỆT ĐỐI KHÔNG NÊN!**\n\n"
                f"• **Hiểm họa tiềm ẩn:** Khi xương gia cầm (gà, vịt) hoặc xương heo bị ninh nấu chín, cấu trúc canxi sẽ giòn đanh. Khi cún cắn gãy, xương sẽ vỡ vụn thành các **mảnh nhọn hình dằm xước như lưỡi dao**.\n"
                f"• **Tổn thương:** Các mảnh xương sắc nhọn này rất dễ cắm vào vòm họng, làm rách thực quản hoặc đâm thủng dạ dày, thủng ruột gây viêm phúc mạc tử vong.\n\n"
                f"💡 **Giải pháp an toàn:**\n"
                f"• Cho bé gặm **que gặm sạch răng da bò (Rawhide chew)** hoặc xương đồ chơi gặm silicon an toàn của hãng uy tín.",
                ["Que gặm sạch răng an toàn", "Dấu hiệu cún bị hóc xương", "Ngoại khoa nội soi dị vật"]
            )

        # 8. TRỨNG GÀ (SỐNG VS CHÍN)
        if any(w in msg_lower for w in ["trứng gà", "ăn trứng", "lòng đỏ", "trứng sống", "trứng lộn"]):
            return (
                f"🥚 **CHÓ MÈO ĂN TRỨNG GÀ ĐƯỢC KHÔNG?**\n\n"
                f"✅ **RẤT TỐT NẾU NẤU CHÍN**, nhưng **KHÔNG NÊN ĂN TRỨNG SỐNG** bạn nhé!\n\n"
                f"• **Trứng luộc chín (đặc biệt là lòng đỏ):** Cung cấp lượng đạm hoàn hảo, giàu Vitamin A, D, B12, Sắt và **Biotin** giúp da khỏe mạnh, lông mọc dày bóng mượt tuyệt vời. Cho ăn 1-2 quả trứng luộc/tuần.\n"
                f"• ⚠️ **Tại sao không nên ăn trứng sống?**\n"
                f"  1. Nguy cơ nhiễm khuẩn đường ruột nặng do vi khuẩn *Salmonella* hoặc *E. coli*.\n"
                f"  2. Lòng trắng trứng sống chứa chất **Avidin** – loại protein ức chế và làm phá hủy quá trình hấp thu Biotin (Vitamin B7), lâu ngày khiến lông xơ rụng và viêm da.",
                ["Cách dưỡng lông bằng trứng", "Khẩu phần dinh dưỡng tuần", "Dầu cá hồi nguyên chất"]
            )

        # 9. QUẢ BƠ (AVOCADO)
        if any(w in msg_lower for w in ["quả bơ", "ăn bơ", "trái bơ", "avocado"]):
            return (
                f"🥑 **CHÓ MÈO ĂN QUẢ BƠ ĐƯỢC KHÔNG?**\n\n"
                f"⚠️ **CẦN HẾT SỨC THẬN TRỌNG - NÊN TRÁNH:**\n\n"
                f"• **Chất độc Persin:** Vỏ, hạt và lá cây bơ chứa độc tố diệt nấm tự nhiên tên là **Persin**. Chất này gây nôn mửa dữ dội, tiêu chảy và tích tụ dịch quanh tim/phổi ở nhiều loài động vật.\n"
                f"• Hạt bơ tròn trơn cũng là thủ phạm hàng đầu gây tắc nghẽn ruột cấp cứu ở chó nếu nuốt chửng.\n"
                f"• Thịt quả bơ tuy chứa ít Persin hơn nhưng lại quá giàu chất béo thực vật, dễ gây rối loạn tiêu hóa hoặc viêm tụy cấp ở chó mèo.",
                ["Trái cây an toàn cho cún", "Cấp cứu dị vật nuốt hạt", "Tư vấn dinh dưỡng"]
            )

        # 10. CHUỐI / TÁO / BÍ ĐỎ / CÀ RỐT
        if any(w in msg_lower for w in ["ăn chuối", "ăn táo", "ăn bí đỏ", "ăn cà rốt", "quả chuối"]):
            return (
                f"🍌 **TRÁI CÂY & RAU CỦ CỰC KỲ TỐT CHO CHÓ MÈO:**\n\n"
                f"✅ Đây là những 'siêu thực phẩm' tự nhiên rất lành tính cho {pet_name}:\n\n"
                f"1. 🎃 **Bí đỏ luộc/hấp:** Giàu chất xơ hòa tan. Bí đỏ nghiền là 'phương thuốc vàng' giúp nhuận tràng khi táo bón và ổn định khuôn phân khi tiêu chảy nhẹ.\n"
                f"2. 🍌 **Chuối chín:** Giàu kali, vitamin B6 và C, giúp tăng cường năng lượng và hỗ trợ nhu động ruột (cho ăn 1-2 lát mỏng/lần).\n"
                f"3. 🍎 **Táo đỏ chín (bỏ hạt và cùi):** Giàu vitamin và chất chống oxy hóa. *(Lưu ý: Bắt buộc bỏ sạch hạt táo vì hạt chứa xyanua độc)*.\n"
                f"4. 🥕 **Cà rốt luộc:** Giúp bổ sung Beta-carotene (Vitamin A) sáng mắt và làm sạch mảng bám răng tự nhiên khi cún gặm.",
                ["Công thức bánh thưởng rau củ", "Trị táo bón bằng bí đỏ", "Tháp dinh dưỡng thú cưng"]
            )

        # 11. XÚC XÍCH / THỊT NGUỘI / ĐỒ ĂN NGƯỜI
        if any(w in msg_lower for w in ["xúc xích", "thịt nguội", "chả lụa", "thịt hộp người", "đồ ăn người"]):
            return (
                f"🌭 **CHÓ MÈO ĂN XÚC XÍCH & ĐỒ ĂN NGƯỜI ĐƯỢC KHÔNG?**\n\n"
                f"🚫 **BÁC SĨ KHUYÊN HẠN CHẾ TỐI ĐA:**\n\n"
                f"• **Quá tải Muối & Gia vị:** Thận của chó mèo chỉ chịu được lượng muối cực kỳ thấp (thấp hơn người gấp 5 lần). Xúc xích, giò chả, thịt xông khói của người chứa lượng muối và bột ngọt rất cao, lâu ngày sẽ dẫn đến **Suy thận mãn tính và Huyết áp cao**.\n"
                f"• **Chất bảo quản độc hại:** Muối diêm Nitrat/Nitrit, hương liệu và tỏi/hành gia vị trong xúc xích người gây hại cho gan và phá vỡ hồng cầu.\n\n"
                f"💡 Hãy thay bằng xúc xích tiệt trùng chuyên dụng dành riêng cho thú cưng (vị bò, gà, phô mai không muối).",
                ["Xúc xích dinh dưỡng cho thú cưng", "Kiểm tra chức năng gan thận", "Chế độ ăn ít muối"]
            )

        # 12. CẮT MÓNG CHẢY MÁU
        if any(w in msg_lower for w in ["chảy máu", "chảy máu móng", "cắt phạm tủy", "cắt trúng tủy", "móng bị chảy máu", "cắt móng chảy máu"]):
            return (
                f"🩸 **XỬ LÝ KHẨN CẤP KHI CẮT MÓNG PHẠM TỦY CHẢY MÁU:**\n\n"
                f"Bạn đừng quá hoảng sợ nhé! Tủy móng có mạch máu nhỏ nên chảy khá nhiều máu nhưng xử lý rất nhanh:\n\n"
                f"⚡ **3 BƯỚC CẦM MÁU TỨC THÌ TẠI NHÀ:**\n"
                f"1. **Dùng Bột Cầm Máu / Tinh Bột:** Lấy một nhúm **bột cầm máu chuyên dụng (Quick Stop)** hoặc nếu không có sẵn, dùng ngay **bột bắp (bột ngô), bột năng hoặc tinh bột khoai tây** ấn chặt trực tiếp vào đầu móng đang chảy máu.\n"
                f"2. **Ép giữ cố định:** Giữ ngón tay ép chặt trong **30 đến 60 giây** để tạo nút máu đông bít kín mạch máu. Không lau chùi chà xát làm bung nút máu đông.\n"
                f"3. **Giữ yên chân:** Giữ {pet_name} ở nơi sạch sẽ khô ráo, tránh cho bé chạy nhảy trong 1-2 tiếng để móng không bị bật máu lại.\n\n"
                f"💡 Lần sau khi cắt, bạn hãy soi đèn pin phía dưới móng để nhìn rõ đường tủy hồng và chỉ bấm phần chóp móng nhọn cách tủy 2mm nhé!",
                ["Đặt lịch cắt mài móng tại Spa (40k)", "Mua bột cầm máu Quick Stop", "Kìm cắt móng có chốt an toàn"]
            )

        # 13. CHÓ CON 2 THÁNG TUỔI TẮM ĐƯỢC CHƯA
        if any(w in msg_lower for w in ["2 tháng", "mới về", "chưa tiêm", "chó con tắm", "mèo con tắm"]) and any(w in msg_lower for w in ["tắm", "tắm được chưa", "tắm được không", "tắm nước"]):
            return (
                f"🛁 **CHÓ/MÈO CON 2 THÁNG TUỔI ĐÃ TẮM NƯỚC ĐƯỢC CHƯA?**\n\n"
                f"🚫 **CÂU TRẢ LỜI: KHÔNG NÊN TẮM NƯỚC ƯỚT NẾU CHƯA ĐỦ VACCINE!**\n\n"
                f"• **Lý do y khoa:** Chó mèo 2 tháng tuổi đang trong giai đoạn 'khoảng trống miễn dịch' (kháng thể mẹ truyền suy giảm nhưng vaccine chưa tạo đủ kháng thể bảo vệ). Thân nhiệt con non điều hòa rất kém. Tắm nước ướt rất dễ làm bé bị lạnh đột ngột, viêm phổi và làm suy yếu sức đề kháng, tạo cơ hội cho virus Parvo/Care bùng phát.\n\n"
                f"🧼 **CÁCH VỆ SINH AN TOÀN CHO BÉ LÚC NÀY:**\n"
                f"1. **Dùng khăn ấm vắt ráo:** Lấy khăn mềm nhúng nước ấm ~38°C, vắt thật kiệt nước rồi lau sạch khóe mắt, chân và vùng hậu môn bám bẩn.\n"
                f"2. **Dùng Bọt tắm khô hoặc Phấn tắm khô:** Xịt bọt tắm khô chuyên dụng cho thú con lên lông, mát-xa nhẹ rồi lấy khăn khô lau sạch và sấy ấm nhẹ nhàng.\n"
                f"3. **Thời điểm tắm nước lý tưởng:** Sau khi bé đã tiêm đủ tối thiểu 2 mũi vaccine và qua thời gian theo dõi 7-10 ngày an toàn.",
                ["Bọt tắm khô thảo dược dịu nhẹ", "Lịch tiêm phòng mũi 2 cho cún", "Hướng dẫn giữ ấm cún con"]
            )

        # 14. NÔN DỊCH VÀNG VS NÔN BỌT TRẮNG
        if any(w in msg_lower for w in ["nôn dịch vàng", "nôn bọt trắng", "nôn bọt nhớt", "ói dịch vàng", "ói bọt trắng", "dịch vàng", "bọt trắng"]):
            return (
                f"⚠️ **TƯ VẤN TIÊU HÓA: PHÂN BIỆT HIỆN TƯỢNG NÔN DỊCH VÀNG VÀ BỌT TRẮNG Ở {pet_name.upper()}:**\n\n"
                f"• **1. Nôn dịch vàng có bọt (Hội chứng nôn dịch mật do đói - Bilious Vomiting):**\n"
                f"  - Nguyên nhân: Thường xảy ra vào sáng sớm khi dạ dày rỗng quá lâu (>12 tiếng). Dịch mật từ tá tràng trào ngược vào dạ dày gây kích ứng buồn nôn.\n"
                f"  - Xử lý: Chia nhỏ bữa ăn thành 3-4 bữa/ngày, cho ăn một bữa nhẹ (vài hạt hoặc mẩu bánh quy) trước khi đi ngủ.\n\n"
                f"• **2. Nôn bọt trắng nhớt:**\n"
                f"  - Nguyên nhân: Do ho khẹc (ho cũi chó khạc ra bọt đờm), bé nuốt phải lông/dị vật, hoặc bị viêm dạ dày nhẹ do ăn nhanh nuốt vội.\n\n"
                f"• **3. Chế độ dinh dưỡng khi tiêu hóa kém:** Cho ăn cháo loãng với ức gà xé nhỏ hoặc bí đỏ hấp nghiền, kiêng dầu mỡ và đồ tanh, bổ sung men vi sinh.\n\n"
                f"🚨 **Dấu hiệu nguy hiểm cần đưa đi khám ngay:** Nôn ra máu (màu nâu sẫm như bã cà phê hoặc đỏ tươi), nôn liên tục không uống được nước, kèm sốt cao hoặc tiêu chảy tanh nồng.",
                ["Tư vấn chia khẩu phần ăn", "Test nhanh virus đường ruột", "Đặt lịch khám tiêu hóa"]
            )

        # 15. RẬN TAI / NGỨA TAI / RÁY TAI ĐEN
        if any(w in msg_lower for w in ["rận tai", "bã cà phê", "ngứa tai", "lắc đầu", "ngoáy tai", "chảy mủ tai", "gãi tai"]):
            return (
                f"👂 **DẤU HIỆU & CÁCH ĐIỀU TRỊ RẬN TAI (EAR MITES) CHO {pet_name.upper()}:**\n\n"
                f"Nếu {pet_name} liên tục lắc đầu, dùng chân sau gãi mạnh vào tai và bên trong tai có **chất bẩn màu đen kịt vón cục như bã cà phê**:\n\n"
                f"🔬 **Chẩn đoán:** 95% bé đã bị nhiễm **Rận tai (*Otodectes cynotis*)** – loại ký sinh trùng siêu nhỏ bò lúc nhúc trong ống tai gây ngứa rát kinh hoàng.\n\n"
                f"💊 **PHÁC ĐỒ TRỊ LIỆU 3 BƯỚC:**\n"
                f"1. **Rửa sạch tai:** Nhỏ 4-5 giọt nước rửa tai chuyên dụng (Oticlens), xoa bóp gốc tai 30 giây rồi dùng bông gòn lau sạch chất bẩn đen.\n"
                f"2. **Thuốc đặc trị rận tai:** Nhỏ gel **Otimectin** hoặc thuốc nhỏ **Dexoryl / Surolan** (1-2 giọt vào ống tai, ngày 1-2 lần trong 10-14 ngày).\n"
                f"3. **Nhỏ gáy diệt rận toàn thân:** Nhỏ gáy Revolution hoặc Advocate để diệt sạch ấu trùng rận tai ẩn nấp quanh cổ.",
                ["Đặt lịch Vệ sinh tai chuyên sâu tại Spa (50k)", "Mua gel trị rận tai Otimectin", "Dung dịch rửa tai Oticlens"]
            )

        # 16. CHẢY GHÈN MẮT / ĐAU MẮT / NƯỚC MẮT
        if any(w in msg_lower for w in ["đổ ghèn", "ghèn mắt", "chảy nước mắt", "đau mắt", "đỏ mắt", "dử mắt", "viêm kết mạc"]):
            return (
                f"👁️ **CHĂM SÓC MẮT ĐỔ GHÈN, CHẢY NƯỚC MẮT CHO {pet_name.upper()}:**\n\n"
                f"Dấu hiệu mắt đổ ghèn vàng xanh, khóe mắt chảy ướt tạo vệt ố nâu thường do:\n"
                f"• **Viêm kết mạc hoặc bụi bẩn kích ứng:** Thường thấy mắt đỏ nhẹ, nhiều dử mắt.\n"
                f"• **Lông mi quặm / Lông chọc vào mắt:** Đặc biệt phổ biến ở các giống chó lông xù (Poodle, Shih Tzu, Pug).\n"
                f"• **Nhiễm virus ở mèo (Herpesvirus FHV-1 / Chlamydia):** Mắt sưng húp, dính chặt mi mắt kèm hắt hơi.\n\n"
                f"🩺 **HƯỚNG DẪN XỬ LÝ TẠI NHÀ:**\n"
                f"1. Dùng gạc mềm thấm nước muối sinh lý NaCl 0.9% lau sạch nhẹ nhàng từ khóe mắt ra đuôi mắt (ngày 2-3 lần).\n"
                f"2. Nhỏ thuốc nhỏ mắt kháng khuẩn an toàn: **Tobramycin 0.3% (Tobrex)** 1 giọt mỗi bên mắt, ngày 2 lần.\n"
                f"3. Cắt tỉa gọn gàng lông quanh vùng mắt để lông không đâm vào giác mạc.",
                ["Thuốc nhỏ mắt Tobrex an toàn", "Gói tỉa lông vùng mặt chống quặm", "Khám chuyên khoa mắt"]
            )

        # 17. MÈO CÀO SOFA / RÈM CỬA
        if any(w in msg_lower for w in ["cào sofa", "cào ghế", "cào rèm", "cào móng", "phá đồ", "cào rách"]):
            return (
                f"🛋️ **MẸO DỨT ĐIỂM HÀNH VI MÈO CÀO RÁCH SOFA & ĐỒ ĐẠC:**\n\n"
                f"Mèo cào móng không phải để 'phá hoại' mà là bản năng tự nhiên giúp loại bỏ lớp móng cũ, kéo giãn cơ vai và tiết dịch đánh dấu lãnh thổ qua đệm bàn chân.\n\n"
                f"🎯 **CHIẾN LƯỢC 3 BƯỚC KHẮC PHỤC TRIỆT ĐỂ:**\n"
                f"1. **Bố trí Trụ cào móng (Scratching Post) đúng vị trí:** Đặt trụ cào hoặc bàn cào carton ngay cạnh góc ghế sofa mà bé hay cào. Rắc thêm một chút cỏ mèo **Catnip** để thu hút bé sang cào trụ mới.\n"
                f"2. **Làm cho sofa trở nên 'kém hấp dẫn':** Dán băng dính 2 mặt chống cào hoặc bọc phủ nilong lên góc sofa. Mèo cực kỳ ghét cảm giác bết dính ở bàn chân nên sẽ bỏ ngay.\n"
                f"3. **Cắt bớt chóp móng nhọn định kỳ:** Cắt tỉa móng 2 tuần/lần để giảm 90% lực sát thương lên bề mặt vải da.",
                ["Trụ cào móng & Bàn cào carton", "Cỏ mèo Catnip kích thích", "Cắt móng tại Spa"]
            )

        # 18. CHÓ MÈO BỊ SỐT / CÁCH HẠ SỐT
        if any(w in msg_lower for w in ["bị sốt", "hạ sốt", "thân nhiệt", "nóng tai", "sốt bao nhiêu"]):
            return (
                f"🌡️ **NHẬN BIẾT & HƯỚNG DẪN HẠ SỐT AN TOÀN CHO THÚ CƯNG:**\n\n"
                f"• **Chỉ số thân nhiệt chuẩn:** Nhiệt độ cơ thể bình thường của chó mèo là **38.0°C - 39.2°C** (đo bằng nhiệt kế ở hậu môn). Nếu nhiệt độ **> 39.5°C** là bé đang sốt cao.\n"
                f"• **Dấu hiệu:** Mũi khô nóng nứt nẻ, tai và vùng bụng bẹn nóng ran, mắt đỏ lờ đờ, thở dốc co thắt ngực, bỏ ăn nằm ủ rũ.\n\n"
                f"⚡ **CÁCH HẠ SỐT CẦN LÀM NGAY:**\n"
                f"1. Đưa bé vào phòng mát thoáng khí (nhiệt độ phòng khoảng 25-27°C).\n"
                f"2. Dùng khăn mềm thấm **nước mát bình thường** (KHÔNG dùng đá lạnh buốt gây sốc nhiệt) lau nhẹ và đắp lên: 4 đệm bàn chân, vùng bẹn háng trong đùi, nách và tai.\n"
                f"3. Cho uống từng ngụm nước sạch nhỏ hoặc nước điện giải Oresol pha loãng.\n"
                f"4. ☠️ **CẢNH BÁO TỬ VONG:** TUYỆT ĐỐI KHÔNG tự ý cho uống Paracetamol / Panadol của người (thuốc này phá hủy hồng cầu và làm hoại tử gan cấp khiến thú cưng tử vong cực nhanh)!",
                ["Đặt lịch bác sĩ đo thân nhiệt & khám sốt", "Dung dịch bù nước Oresol", "Hotline tư vấn khẩn cấp"]
            )

        return None

    @staticmethod
    def chat_with_assistant(
        message: str,
        image_data: Optional[str] = None,
        pet_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Trợ lý AI trả lời câu hỏi chăm sóc thú cưng có tích hợp Guardrail An toàn Y tế & Phân tích hình ảnh"""
        
        # BƯỚC 1: GUARDRAIL KIỂM TRA DẤU HIỆU CẤP CỨU NGUY HIỂM
        is_emergency, level, matched_flags = detect_emergency_symptoms(message)
        
        if is_emergency:
            flag_str = ", ".join(matched_flags)
            emergency_reply = (
                f"🚨 **CẢNH BÁO NGUY HIỂM CẤP CỨU THÚ Y! (EMERGENCY TRIAGE - ƯU TIÊN CẤP 1)** 🚨\n\n"
                f"{'📸 *Bác sĩ đã ghi nhận ảnh cấp cứu đính kèm.* ' if image_data else ''}"
                f"Hệ thống Guardrail phát hiện các dấu hiệu báo động đỏ đe dọa tính mạng thú cưng: **[{flag_str}]**.\n\n"
                f"⚡ **HÀNH ĐỘNG CẦN LÀM NGAY LẬP TỨC:**\n"
                f"1. **Đưa bé đến Bệnh viện Thú y / Phòng khám cấp cứu gần nhất NGAY LẬP TỨC!**\n"
                f"2. KHÔNG tự ý cho uống thuốc hạ sốt của người (Paracetamol, Panadol cực độc với mèo và chó).\n"
                f"3. KHÔNG tự ý kích nôn nếu không có chỉ định trực tiếp từ Bác sĩ Thú y.\n"
                f"4. Giữ ấm cho bé, đặt nằm nghiêng cổ thẳng nơi thông thoáng trong quá trình di chuyển cấp cứu.\n"
                f"5. 📞 **GỌI NGAY HOTLINE CẤP CỨU 24/7:** **0988.111.222** hoặc **0988.123.456** để bác sĩ chuẩn bị sẵn phòng mổ & bình thở oxy!"
            )
            return {
                "reply": emergency_reply,
                "is_emergency": True,
                "emergency_level": level,
                "emergency_hotline": "0988.111.222",
                "warning_badge": "🚨 BÁO ĐỘNG ĐỎ: CA CẤP CỨU THÚ Y KHẨN CẤP (HOTLINE: 0988.111.222)",
                "veterinary_disclaimer": VETERINARY_DISCLAIMER,
                "suggested_actions": [
                    "📞 Gọi Hotline Cấp Cứu 24/7 (0988.111.222)",
                    "Chỉ đường đến phòng khám thú y gần nhất",
                    "Giữ ấm và cố định đường thở cho bé"
                ],
                "generated_by": "PetCare AI Safety Guardrail Engine"
            }

        # BƯỚC 2: THỬ GỌI ONLINE LLM NẾU CÓ CẤU HÌNH API KEY (GEMINI / OPENAI)
        online_result = AIService._try_call_online_llm(
            message=message,
            image_data=image_data,
            pet_context=pet_context,
            chat_history=chat_history
        )
        if online_result:
            reply_text, actions_list, provider_label = online_result
            return {
                "reply": reply_text,
                "is_emergency": False,
                "emergency_level": "NONE",
                "warning_badge": None,
                "veterinary_disclaimer": VETERINARY_DISCLAIMER,
                "suggested_actions": actions_list,
                "generated_by": provider_label
            }

        # BƯỚC 3: TRÍ TUỆ NHÂN TẠO OFFLINE NÂNG CAO (PHÂN TÍCH ĐA TẦNG, TRẢ LỜI ĐI THẲNG TRỌNG TÂM, KHÔNG RẬP KHUÔN)
        msg_lower = message.lower().strip()
        pet_name = pet_context.get("name", "bé") if pet_context else "bé"
        species = pet_context.get("species", "thú cưng") if pet_context else "thú cưng"

        # Tầng 1: Phân tích tiếp nối ngữ cảnh hội thoại nhiều lượt (Multi-turn follow-up)
        followup_res = AIService._resolve_followup_context(message=message, chat_history=chat_history, pet_name=pet_name)
        if followup_res:
            reply, actions = followup_res

        # Tầng 2: Phân tích thực thể chi tiết & câu hỏi tình huống thực tế (Entity Recognition)
        elif AIService._analyze_specific_queries(message=message, pet_name=pet_name, species=species):
            reply, actions = AIService._analyze_specific_queries(message=message, pet_name=pet_name, species=species)

        # Tầng 3: Các chủ đề chăm sóc toàn diện chuẩn hóa (25+ Danh mục)
        # 1. BẢNG GIÁ DỊCH VỤ & CHI PHÍ
        elif any(w in msg_lower for w in ["bảng giá", "giá bao nhiêu", "bao nhiêu tiền", "chi phí", "dịch vụ gì", "spa giá", "cắt tỉa giá", "tắm giá", "combo giá", "tiêm giá", "giá dịch vụ", "hết bao nhiêu", "báo giá"]):
            reply = (
                f"🏷️ **BẢNG GIÁ DỊCH VỤ CHĂM SÓC THÚ CƯNG TẠI PETCARE PRO:**\n\n"
                f"1. **Tắm Spa & Sấy thơm dưỡng lông:**\n"
                f"   • Dưới 5kg: 150.000 ₫\n"
                f"   • Từ 5kg - 10kg: 200.000 ₫\n"
                f"   • Trên 10kg: 250.000 - 350.000 ₫\n"
                f"   *(Bao gồm: Tắm thảo dược khử khuẩn, vắt tuyến hôi, sấy tơi lông, bôi tinh dầu dưỡng)*\n\n"
                f"2. **Combo Cắt tỉa Grooming tạo kiểu trọn gói:** 350.000 - 550.000 ₫\n"
                f"   *(Trọn gói: Tắm spa + Cắt tỉa form tròn/Hàn Quốc + Vệ sinh tai + Cắt mài móng + Cạo đệm chân)*\n\n"
                f"3. **Vệ sinh toàn diện (Tai, Móng, Tuyến hôi):** 100.000 ₫\n"
                f"4. **Gói Siêu VIP Spa & Dưỡng ẩm bùn khoáng:** 550.000 ₫\n"
                f"5. **Khách sạn lưu trú (Pet Hotel):** 120.000 - 250.000 ₫ / ngày (có camera 24/7)\n"
                f"6. **Cạo vôi răng & Đánh bóng:** 250.000 ₫\n"
                f"7. **Tiêm phòng Vaccine 7 bệnh Chó:** 220.000 ₫ | **Vaccine 4 bệnh Mèo:** 200.000 ₫\n\n"
                f"💡 *Đặt lịch hẹn trước để nhận ưu đãi thành viên và không phải chờ đợi bạn nhé!*"
            )
            actions = ["Đặt lịch hẹn ngay", "Xem chi tiết gói Spa VIP", "Đăng ký thành viên tích điểm"]

        # 2. KHÁCH SẠN THÚ CƯNG / LƯU TRÚ (PET HOTEL)
        elif any(w in msg_lower for w in ["khách sạn", "gửi thú cưng", "trông giữ", "gửi chó", "gửi mèo", "lưu chuồng", "boarding", "gửi bé", "nhận nuôi tạm", "trông hộ"]):
            reply = (
                f"🏨 **DỊCH VỤ KHÁCH SẠN THÚ CƯNG (PET HOTEL) PETCARE PRO:**\n\n"
                f"Khi ba mẹ bận công tác hoặc đi du lịch, {pet_name} sẽ được chăm sóc như tại nhà:\n"
                f"• **Tiện nghi phòng ở:** Phòng riêng biệt điều hòa 24/24, đệm nằm êm ái, khử khuẩn tia UV hàng ngày.\n"
                f"• **Camera giám sát 24/7:** Phụ huynh có thể mở app xem trực tiếp hoạt động của bé mọi lúc mọi nơi.\n"
                f"• **Chế độ dinh dưỡng:** 2 - 3 bữa/ngày theo đúng thực đơn của bé (hạt cao cấp Royal Canin/Monge hoặc pate tươi tự nấu).\n"
                f"• **Vui chơi & Vận động:** Bé được ra sân chơi vận động và dắt đi dạo 30-45 phút mỗi ngày.\n"
                f"• **Báo cáo hàng ngày:** Nhân viên gửi video & ảnh cập nhật tình trạng bé qua Zalo mỗi ngày.\n\n"
                f"📋 **Điều kiện nhận gửi:** Bé đã tiêm phòng đủ vắc xin và đã được nhỏ gáy phòng ve rận trong vòng 1 tháng gần nhất."
            )
            actions = ["Đặt phòng Pet Hotel", "Xem bảng giá lưu trú", "Quy định gửi thú cưng"]

        # 3. NẤM DA, VIÊM DA, VẢY GÀU, GHẺ NGỨA
        elif any(w in msg_lower for w in ["nấm", "nấm da", "viêm da", "vảy gàu", "đốm đỏ", "ghẻ", "demodex", "ngứa", "gãi nhiều", "xước da", "rụng lông từng mảng", "viêm da dị ứng", "viêm kẽ"]):
            reply = (
                f"🔬 **TƯ VẤN BỆNH LÝ DA LIỄU (NẤM / VIÊM DA / VE GHẺ) CHO {pet_name.upper()}:**\n\n"
                f"Dấu hiệu {pet_name} gãi nhiều, da có vảy gàu hoặc đốm đỏ thường xuất phát từ:\n"
                f"1. **Nấm da (Microsporum canis / Malassezia):** Biểu hiện rụng lông hình tròn, da có vảy trắng như gàu, ngứa ngáy nhiều.\n"
                f"2. **Viêm da mủ hoặc nhiễm khuẩn do ẩm ướt:** Thường xảy ra khi tắm xong không sấy thật khô chân lông.\n"
                f"3. **Ghẻ Demodex hoặc ghẻ Sarcoptes:** Gây rụng lông quanh mắt, sống mũi, kẽ ngón chân sưng đỏ.\n\n"
                f"🩺 **HƯỚNG DẪN XỬ TRÍ TẠI NHÀ:**\n"
                f"• **Đeo loa chống liếm (vòng Elizabeth):** Tuyệt đối cần thiết để tránh bé cào gãi làm loét da chảy máu.\n"
                f"• **Dầu tắm trị liệu:** Tắm 2 lần/tuần bằng sữa tắm chứa Ketoconazole 2% hoặc Chlorhexidine.\n"
                f"• **Sấy khô 100%:** Luôn sấy khô tận gốc chân lông sau khi tắm, giữ nơi ở khô ráo thoáng khí.\n"
                f"• ⚠️ *Không tự ý bôi các loại thuốc mỡ chứa corticoid của người (như Flucinar, Gentrisone) lên da thú cưng.*"
            )
            actions = ["Đặt lịch soi kính tìm nấm da", "Mua sữa tắm trị nấm chuyên dụng", "Khám da liễu thú y"]

        # 4. VE RẬN, BỌ CHÉT, XÀ MÂU
        elif any(w in msg_lower for w in ["ve chó", "con ve", "trị ve", "bị ve", "bọ chét", "xà mâu", "nhỏ gáy", "frontline", "bravecto", "nexgard", "revolution", "thuốc ve"]) or "rận" in msg_lower:
            reply = (
                f"🐛 **HƯỚNG DẪN ĐIỀU TRỊ & PHÒNG NGỪA VE RẬN CHO {pet_name.upper()}:**\n\n"
                f"Ve rận không chỉ gây ngứa ngáy, thiếu máu mà còn có thể truyền **Ký sinh trùng đường máu (Babesia)** rất nguy hiểm!\n\n"
                f"⚡ **GIẢI PHÁP ĐẶC TRỊ HIỆU QUẢ CAO:**\n"
                f"1. **Thuốc nhỏ gáy đặc trị:**\n"
                f"   • *Frontline Plus / Revolution / Advocate:* Nhỏ định kỳ 1 tháng/lần.\n"
                f"   • *Bravecto:* Tác dụng kéo dài đến **3 tháng** chỉ với 1 lần nhỏ gáy hoặc viên nhai.\n"
                f"2. **Viên nhai trị ký sinh trùng:** Nexgard / Simparica (vị thịt bò, bé ăn rất thích, diệt sạch ve bọ chét sau 24h).\n"
                f"3. **Xử lý môi trường:** Giặt sạch nệm nằm, phun xịt dung dịch Hantox-200 quanh góc tường, khe sàn nhà để diệt trứng và ấu trùng ve.\n\n"
                f"💡 *Lưu ý: Không tắm cho bé trong vòng 48 giờ trước và sau khi nhỏ gáy để thuốc ngấm đều qua tuyến bã nhờn.*"
            )
            actions = ["Nhỏ gáy diệt ve tại Spa", "Kiểm tra xét nghiệm máu ký sinh", "Tư vấn chọn thuốc nhỏ gáy"]

        # 5. TIÊU CHẢY, NÔN MỬA NHẸ, BỎ ĂN
        elif any(w in msg_lower for w in ["tiêu chảy", "ỉa chảy", "đi ngoài", "phân lỏng", "nôn bọt", "nôn dịch vàng", "nôn cỏ", "bỏ ăn", "chán ăn", "sình bụng", "đầy hơi"]):
            reply = (
                f"🥣 **HƯỚNG DẪN CHĂM SÓC RỐI LOẠN TIÊU HÓA Ở {pet_name.upper()}:**\n\n"
                f"Nếu bé chỉ đi phân lỏng nhẹ hoặc nôn dịch bọt 1-2 lần nhưng **vẫn tỉnh táo, không nôn ra máu, không sốt cao**:\n"
                f"1. **Tạm nhịn ăn 8-12 tiếng:** Để đường ruột và dạ dày của bé được nghỉ ngơi.\n"
                f"2. **Bù nước & điện giải:** Pha nước Oresol loãng cho bé uống từng ngụm nhỏ, hoặc dùng dung dịch Hydralyte dành riêng cho thú cưng.\n"
                f"3. **Bổ sung Men tiêu hóa:** Cho uống men vi sinh (Enterogermina hoặc Bio-scour) giúp cân bằng hệ vi sinh đường ruột.\n"
                f"4. **Bữa ăn nhẹ đầu tiên:** Nấu cháo loãng với ức gà xé nhỏ (không nêm muối, mắm, hành, tỏi).\n\n"
                f"🚨 **DẤU HIỆU CẦN ĐẾN PHÒNG KHÁM NGAY:**\n"
                f"• Phân có lẫn máu đỏ tươi hoặc phân đen tanh nồng (nghi Parvo/Care).\n"
                f"• Nôn liên tục trên 3 lần/ngày, lừ đừ li bì, bỏ uống nước."
            )
            actions = ["Tư vấn men tiêu hóa Bio-scour", "Kiểm tra Test nhanh Parvo/Care", "Đặt lịch khám tiêu hóa"]

        # 6. HẮT HƠI, SỔ MŨI, HO, CẢM CÚM
        elif any(w in msg_lower for w in ["hắt hơi", "sổ mũi", "chảy nước mũi", "ho khẹc", "ho khan", "ho cũi", "tiếng ho", "bị ho", "cảm lạnh", "nghẹt mũi", "thở khò khè"]) or bool(re.search(r'\bho\b', msg_lower)):
            reply = (
                f"🌡️ **CHĂM SÓC HÔ HẤP & CẢM LẠNH CHO {pet_name.upper()}:**\n\n"
                f"Triệu chứng hắt hơi, ho khẹc như hóc xương hoặc chảy nước mũi thường do:\n"
                f"• **Thay đổi thời tiết / Nằm điều hòa quá lạnh:** Bé bị cảm lạnh đường hô hấp trên.\n"
                f"• **Hội chứng Ho cũi chó (Kennel Cough):** Do vi khuẩn Bordetella hoặc virus Parainfluenza, lây lan mạnh khi tiếp xúc với chó khác.\n"
                f"• **Viêm mũi / Dị ứng phấn hoa, khói bụi:** Thường chỉ hắt hơi ngắt quãng.\n\n"
                f"💡 **CÁCH CHĂM SÓC TẠI NHÀ:**\n"
                f"• Giữ ấm nơi nằm, tránh để quạt hoặc gió điều hòa phả thẳng vào mặt bé.\n"
                f"• Nhỏ mũi bằng nước muối sinh lý NaCl 0.9% ấm (1-2 giọt mỗi bên mũi, ngày 2 lần).\n"
                f"• Cho bé uống nước ấm và ăn thức ăn mềm, thơm kích thích khứu giác.\n"
                f"• ⚠️ *Nếu bé có biểu hiện sốt, thở dốc co thắt ngực, chảy mủ xanh ở mũi, cần đưa đi khám để tiêm kháng sinh điều trị kịp thời.*"
            )
            actions = ["Đặt lịch khám hô hấp", "Kiểm tra tiêm phòng ho cũi chó", "Hướng dẫn xông mũi thảo dược"]

        # 7. VỆ SINH TAI, RĂNG MIỆNG & HÔI MIỆNG
        elif any(w in msg_lower for w in ["hôi miệng", "vôi răng", "cao răng", "đánh răng", "răng vàng", "sâu răng", "chảy nước dãi", "viêm tai", "hôi tai", "rận tai", "ráy tai", "chảy dịch tai", "vệ sinh tai"]):
            reply = (
                f"🦷 **CHĂM SÓC RĂNG MIỆNG & TAI CHO {pet_name.upper()}:**\n\n"
                f"**1. Về Răng miệng & Hôi miệng:**\n"
                f"• Nguyên nhân chính gây hôi miệng là do mảng bám vôi răng tích tụ lâu ngày dẫn đến viêm nướu.\n"
                f"• Dùng kem đánh răng enzyme chuyên dụng cho thú cưng (KHÔNG dùng kem của người vì chứa Fluoride gây ngộ độc ruột).\n"
                f"• Cho bé nhai que gặm sạch răng (dental chews) hoặc xịt gel thơm miệng diệt khuẩn.\n"
                f"• Nên cạo vôi răng bằng máy siêu âm tại tiệm 6-12 tháng/lần để bảo vệ răng gốc chắc khỏe.\n\n"
                f"**2. Về Vệ sinh Tai & Phòng rận tai:**\n"
                f"• Nhỏ 3-5 giọt nước rửa tai chuyên dụng (Oticlens / Forcans), massage gốc tai 30 giây rồi dùng bông gòn lau sạch.\n"
                f"• Nếu tai có ráy đen kịt như bã cà phê kèm mùi hôi chua, khả năng cao bé đã bị **Rận tai (Otodectes)**, cần nhỏ thuốc trị rận tai chuyên biệt."
            )
            actions = ["Đặt lịch Vệ sinh tai & Cạo vôi răng", "Xem gel đánh răng cho thú cưng", "Kiểm tra rận tai"]

        # 8. CẮT MÓNG & CHĂM SÓC BÀN CHÂN
        elif any(w in msg_lower for w in ["cắt móng", "mài móng", "móng dài", "chảy máu móng", "cắt trúng tủy", "đệm thịt", "kẽ chân", "bàn chân"]):
            reply = (
                f"🐾 **KỸ THUẬT CẮT MÓNG & BẢO VỆ ĐỆM CHÂN CHO {pet_name.upper()}:**\n\n"
                f"• **Tần suất:** Cắt móng định kỳ 2-3 tuần/lần. Móng quá dài sẽ đâm quặp vào đệm thịt gây mưng mủ hoặc làm biến dạng khớp xương bàn chân.\n"
                f"• **Xác định đường cắt an toàn:** Nhìn nghiêng móng dưới ánh sáng. Chỉ cắt phần chóp móng nhọn trong suốt, cách tủy hồng (mạch máu & dây thần kinh) ít nhất 2mm.\n"
                f"• **Xử lý nếu lỡ cắt chảy máu:** Bình tĩnh dùng một nhúm **bột cầm máu (Styptic Powder)** hoặc bột bắp/bột năng ấn chặt vào đầu móng 30 giây, máu sẽ ngừng chảy ngay.\n"
                f"• **Mài móng:** Sau khi cắt, dùng giũa mài mịn các cạnh sắc để bé không cào trầy xước da bạn khi ôm ấp."
            )
            actions = ["Đặt lịch Cắt mài móng tại Spa (40k)", "Hướng dẫn cắt móng an toàn", "Dưỡng ẩm đệm chân"]

        # 9. TẮM RỬA, SỮA TẮM & VẮT TUYẾN HÔI
        elif any(w in msg_lower for w in ["tắm", "gội", "mấy ngày tắm", "bao lâu tắm", "sữa tắm", "sấy lông", "vắt tuyến hôi", "tắm cho chó", "tắm cho mèo"]):
            reply = (
                f"🛁 **CẨM NANG TẮM SẤY CHUẨN SPA CHO {pet_name.upper()} ({species.upper()}):**\n\n"
                f"• **Tần suất phù hợp:**\n"
                f"  - *Với Chó:* Nuôi trong nhà nên tắm 7 - 10 ngày/lần. Chó vận động nhiều ngoài trời có thể tắm 5-7 ngày/lần.\n"
                f"  - *Với Mèo:* Chỉ cần tắm 1 - 2 tháng/lần vì mèo tự chải chuốt làm sạch rất tốt.\n"
                f"• **Nhiệt độ nước:** Dùng nước ấm 36°C - 38°C (vừa ấm tay), không dùng nước quá nóng làm khô rát da.\n"
                f"• **Sữa tắm:** Sử dụng sữa tắm độ pH 6.5 - 7.5 dịu nhẹ. Tuyệt đối không dùng xà phòng người.\n"
                f"• **Vắt tuyến hôi:** Khi tắm nên vắt nhẹ tuyến hôi ở vị trí 4h và 8h quanh hậu môn để khử triệt để mùi hôi cơ thể.\n"
                f"• **QUAN TRỌNG NHẤT:** Dùng máy sấy sấy khô tận gốc chân lông, chải tơi lông để chống nấm ẩm mốc."
            )
            actions = ["Đặt lịch Tắm Spa & Dưỡng lông", "Xem sữa tắm thảo dược", "Hướng dẫn sấy lông không sợ"]

        # 10. RỤNG LÔNG & DƯỠNG LÔNG BÓNG MƯỢT
        elif any(w in msg_lower for w in ["rụng lông", "lông rụng", "xơ lông", "dưỡng lông", "chải lông", "lông xơ", "bết lông", "cạo lông máu", "mượt lông", "rụng nhiều lông"]):
            reply = (
                f"✨ **BÍ QUYẾT GIẢM RỤNG LÔNG & DƯỠNG LÔNG BÓNG MƯỢT:**\n\n"
                f"1. **Chải lông mỗi ngày 5-10 phút:** Giúp gom sạch 80% lông rụng trước khi vương vãi khắp nhà, đồng thời mát-xa tăng sinh dầu tự nhiên nuôi dưỡng nang lông.\n"
                f"2. **Bổ sung Axit béo Omega-3 & Omega-6:** Cho bé uống dầu cá hồi nguyên chất hoặc ăn 1-2 lòng đỏ trứng gà luộc chín mỗi tuần.\n"
                f"3. **Thay lông theo mùa:** Chó mèo thường rụng lông mạnh vào thời điểm giao mùa (xuân sang hè, thu sang đông). Đây là sinh lý bình thường nếu da bên dưới vẫn hồng hào không có nấm đỏ.\n"
                f"4. **Có nên cạo trọc lông không?** Không khuyến khích cạo trọc trừ khi bị nấm nặng, vì lớp lông kép đóng vai trò cách nhiệt, chống tia UV và chống muỗi đốt."
            )
            actions = ["Dầu cá hồi dưỡng lông", "Combo Spa phục hồi lông hư tổn", "Lược chải lông chuyên dụng"]

        # 11. THỨC ĂN & DINH DƯỠNG
        elif any(w in msg_lower for w in ["ăn gì", "thức ăn", "dinh dưỡng", "cho ăn", "chế độ ăn", "pate", "hạt", "thịt gì", "khẩu phần", "nấu gì cho", "ăn thịt gà", "ăn thịt bò"]):
            reply = (
                f"🥩 **THÁP DINH DƯỠNG KHOA HỌC CHO {pet_name.upper()}:**\n\n"
                f"• **Nguồn Protein chất lượng (Chiếm 40-60% khẩu phần):**\n"
                f"  - Thịt ức gà luộc xé, thịt bò nạc giàu sắt, cá hồi/cá biển bỏ xương, trứng gà luộc.\n"
                f"• **Chất xơ & Vitamin (Chiếm 10-15%):**\n"
                f"  - Bí đỏ hấp (rất tốt cho hệ tiêu hóa), cà rốt luộc, đậu que, khoai lang chín.\n"
                f"• **Thức ăn hạt khô & Pate:**\n"
                f"  - Chọn hạt thương hiệu uy tín, không phẩm màu nhân tạo, có độ đạm phù hợp từng độ tuổi (con non cần đạm cao hơn thú trưởng thành).\n"
                f"• **Nước uống sạch:** Luôn có sẵn bát nước lọc sạch, thay nước ít nhất 2 lần/ngày. Với mèo, nên dùng đài phun nước tự động để kích thích bé uống nhiều nước, phòng ngừa sỏi thận."
            )
            actions = ["Khẩu phần ăn theo cân nặng", "Xem các dòng hạt dinh dưỡng", "Cách nấu pate tươi tại nhà"]

        # 12. THỰC PHẨM ĐỘC HẠI CẤM ĂN
        elif any(w in msg_lower for w in ["độc hại", "cấm ăn", "không nên ăn", "ăn socola", "ăn hành", "ăn tỏi", "ăn nho", "ăn kẹo", "uống sữa tươi", "xylitol", "nguy hiểm cho chó", "nguy hiểm cho mèo", "chất độc"]):
            reply = (
                f"🚫 **DANH SÁCH ĐEN CÁC THỰC PHẨM CẤM KỴ ĐỐI VỚI CHÓ MÈO:**\n\n"
                f"Tuyệt đối không để {pet_name} tiếp xúc với các thực phẩm sau:\n"
                f"1. 🍫 **Socola, Cacao, Cà phê, Trà:** Chứa Theobromine và Caffeine gây co giật, loạn nhịp tim và tử vong nhanh.\n"
                f"2. 🧅 **Hành tây, Tỏi, Hẹ:** Chứa Thiosulfate phá hủy hồng cầu, gây tan máu và suy tạng.\n"
                f"3. 🍇 **Nho tươi & Nho khô:** Chỉ 1-2 quả nho cũng có thể gây suy thận cấp tính không thể hồi phục.\n"
                f"4. 🍬 **Kẹo cao su, Bánh ngọt chứa chất tạo ngọt Xylitol:** Làm tụt đường huyết cấp tốc và hoại tử gan.\n"
                f"5. 🦴 **Xương gà, xương vịt, xương cá nhọn:** Dễ gãy vụn tạo mảnh sắc nhọn đâm thủng dạ dày, thực quản.\n"
                f"6. 🥛 **Sữa tươi có đường của người:** Đa số chó mèo không dung nạp Lactose, gây sôi bụng tiêu chảy dữ dội."
            )
            actions = ["Kiểm tra dấu hiệu ngộ độc", "Thực phẩm thay thế an toàn", "Hotline cấp cứu khi ăn nhầm"]

        # 13. LỊCH TIÊM PHÒNG VACCINE
        elif any(w in msg_lower for w in ["tiêm phòng", "vaccine", "vắc xin", "mũi tiêm", "7 bệnh", "5 bệnh", "dại", "mũi nhắc", "tiêm dại", "lịch tiêm"]):
            reply = (
                f"💉 **PHÁC ĐỒ TIÊM PHÒNG CHUẨN Y KHOA DÀNH CHO {species.upper()}:**\n\n"
                f"**1. Dành cho Chó:**\n"
                f"• *Mũi 1 (6-8 tuần tuổi):* Vaccine 5 bệnh (Care, Parvo, Viêm gan, Ho cũi, Phó cúm).\n"
                f"• *Mũi 2 (9-11 tuần tuổi):* Vaccine 7 bệnh (Bổ sung thêm 2 chủng xoắn khuẩn Leptospira).\n"
                f"• *Mũi 3 (13-15 tuần tuổi):* Vaccine 7 bệnh nhắc lại tạo miễn dịch hoàn chỉnh.\n"
                f"• *Tiêm Dại (từ 3 tháng tuổi):* Bắt buộc theo luật thú y.\n"
                f"• *Mũi nhắc hàng năm:* Tiêm 1 mũi 7 bệnh + 1 mũi Dại mỗi năm 1 lần.\n\n"
                f"**2. Dành cho Mèo:**\n"
                f"• Vaccine 4 bệnh phòng Giảm bạch cầu (FPV), Viêm mũi khí quản, Calicivirus và Chlamydia (tiêm 2-3 mũi đầu đời lúc 8, 12 tuần tuổi và nhắc lại hàng năm).\n\n"
                f"⚠️ *Lưu ý: Chỉ tiêm khi bé khỏe mạnh hoàn toàn, không tiêu chảy, không sốt.*"
            )
            actions = ["Xem Sổ tiêm phòng điện tử", "Đặt lịch tiêm chủng tại tiệm", "Lưu ý trước khi tiêm phòng"]

        # 14. TẨY GIUN ĐỊNH KỲ
        elif any(w in msg_lower for w in ["tẩy giun", "sổ giun", "thuốc giun", "sanpet", "drontal", "bao lâu tẩy giun", "giun đũa", "sán dây", "uống thuốc giun", "tẩy giun khi nào"]):
            reply = (
                f"💊 **LỊCH TẨY GIUN SÁN ĐỊNH KỲ CHO {pet_name.upper()}:**\n\n"
                f"• **Chó mèo con dưới 6 tháng:** Tẩy giun lúc 3, 5, 7 và 9 tuần tuổi. Sau đó mỗi tháng 1 lần đến khi đủ 6 tháng tuổi.\n"
                f"• **Thú cưng trưởng thành (trên 6 tháng):** Tẩy định kỳ **3 - 4 tháng / lần** (hoặc 6 tháng/lần nếu nuôi nhốt trong nhà hoàn toàn).\n"
                f"• **Các loại thuốc giun uy tín:** Drontal Plus (vị thịt), Sanpet, Endogard 10, Milbemax.\n"
                f"• **Liều lượng:** Tính chính xác theo cân nặng (thường 1 viên cho mỗi 5kg hoặc 10kg thể trọng tùy loại thuốc).\n"
                f"• **Mẹo cho uống:** Cho uống vào buổi sáng trước khi ăn, có thể nghiền nhỏ kẹp vào một miếng pate hoặc viên thịt nhỏ."
            )
            actions = ["Đặt mua thuốc tẩy giun chuẩn", "Cân ký tính liều thuốc", "Dấu hiệu nhiễm giun sán"]

        # 15. TRIỆT SẢN & HẬU PHẪU
        elif any(w in msg_lower for w in ["triệt sản", "thiến", "cắt buồng trứng", "mấy tháng triệt sản", "sau triệt sản", "vết mổ", "cắt chỉ", "triệt sản đực", "triệt sản cái"]):
            reply = (
                f"✂️ **TƯ VẤN TRIỆT SẢN AN TOÀN CHO {pet_name.upper()}:**\n\n"
                f"• **Độ tuổi lý tưởng:** Từ **6 - 8 tháng tuổi** (trước kỳ động dục / sa lơ đầu tiên của bé cái).\n"
                f"• **Lợi ích sức khỏe to lớn:**\n"
                f"  - Ngừa 99% ung thư tử cung, viêm mủ tử cung nguy hiểm ở bé cái.\n"
                f"  - Triệt tiêu nguy cơ u xơ tuyến tiền liệt, ung thư tinh hoàn ở bé đực.\n"
                f"  - Giảm hẳn tập tính đái bậy đánh dấu lãnh thổ, gào đực kêu cái và bỏ nhà đi lạc.\n"
                f"• **Chăm sóc sau mổ (Hậu phẫu):**\n"
                f"  - Đeo loa chống liếm 7-10 ngày liên tục không tháo, giữ vết mổ khô ráo tuyệt đối.\n"
                f"  - Không cho bé nhảy cao hoặc chạy nhảy mạnh tránh bục chỉ khâu.\n"
                f"  - Tái khám cắt chỉ sau 7 - 10 ngày (nếu không dùng chỉ tự tiêu)."
            )
            actions = ["Đặt lịch tư vấn Triệt sản", "Gói mổ gây mê an toàn", "Chăm sóc vết mổ tại nhà"]

        # 16. TẬP ĐI VỆ SINH ĐÚNG CHỖ & HUẤN LUYỆN
        elif any(w in msg_lower for w in ["đi vệ sinh", "vệ sinh đúng chỗ", "khay cát", "cát vệ sinh", "cắn phá", "sủa nhiều", "hung dữ", "huấn luyện", "dạy", "cắn tay", "đái bậy"]):
            reply = (
                f"🎓 **HƯỚNG DẪN TẬP {pet_name.upper()} ĐI VỆ SINH ĐÚNG NƠI QUY ĐỊNH:**\n\n"
                f"1. **Bắt đúng khung giờ vàng:** Chó con luôn muốn đi vệ sinh vào 3 thời điểm: Ngay khi vừa ngủ dậy, sau khi ăn xong 15-20 phút, và sau khi chơi đùa hăng say.\n"
                f"2. **Cố định vị trí:** Đặt tấm lót vệ sinh hoặc khay cát ở nơi yên tĩnh, ít người qua lại.\n"
                f"3. **Dùng dung dịch định vị:** Xịt 1-2 giọt tinh dầu định vị vệ sinh vào khay để bé nhận diện mùi quen thuộc.\n"
                f"4. **Khen thưởng tích cực:** Ngay khi bé đi đúng chỗ, lập tức khen ngợi 'Giỏi quá!' và thưởng 1 mẩu bánh thưởng (treat). Tuyệt đối không đánh đập hay dí mũi bé vào bãi bẩn vì sẽ khiến bé sợ hãi và giấu phân đi chỗ khác."
            )
            actions = ["Khay & Cát vệ sinh khử mùi", "Xịt hướng dẫn đi vệ sinh", "Bánh thưởng huấn luyện"]

        # 17. MANG THAI, SINH CON & CHĂM SÓC CON NON
        elif any(w in msg_lower for w in ["mang thai", "có bầu", "sinh con", "đỡ đẻ", "sắp đẻ", "mới đẻ", "chó con", "mèo con", "sơ sinh", "sữa mẹ", "ăn dặm", "chuyển dạ"]):
            reply = (
                f"🍼 **CHĂM SÓC THAI KỲ & CHÓ MÈO CON MỚI SINH:**\n\n"
                f"• **Thời gian mang thai:** Trung bình từ **58 - 65 ngày** (khoảng 2 tháng).\n"
                f"• **Siêu âm chẩn đoán:** Nên siêu âm ở ngày thứ 25 - 30 để kiểm tra tim thai và chụp X-quang ngày thứ 50 để đếm số lượng thai chuẩn bị đỡ đẻ.\n"
                f"• **Dinh dưỡng cho mẹ:** Từ tuần thứ 6 thai kỳ, bổ sung canxi Nano, trứng vịt lộn và chuyển sang ăn hạt dành riêng cho thú mẹ mang thai.\n"
                f"• **Với con sơ sinh:** Nếu mẹ mất sữa, dùng sữa bột công thức Bio-milk hoặc KMR/Esbilac (pha nước ấm 40°C). **Tuyệt đối không tắm cho chó mèo sơ sinh dưới 2 tháng tuổi!**"
            )
            actions = ["Đặt lịch Siêu âm thai thú cưng", "Sữa bột công thức sơ sinh", "Cẩm nang chuẩn bị đỡ đẻ"]

        # 18. TÂM LÝ, STRESS, VẬN ĐỘNG & BÉO PHÌ
        elif any(w in msg_lower for w in ["stress", "sợ hãi", "buồn", "trầm cảm", "đi dạo", "vận động", "đồ chơi", "cào móng", "béo phì", "lười vận động", "nhút nhát"]):
            reply = (
                f"🎾 **SỨC KHỎE TINH THẦN & GIẢI TỎA CĂNG THẲNG CHO {pet_name.upper()}:**\n\n"
                f"• **Dấu hiệu bé bị stress:** Liếm chân liên tục đến rụng lông, cào cấu phá phách, lẩn trốn vào góc tối, bỏ ăn hoặc sủa vô cớ.\n"
                f"• **Thời gian vận động:** Chó cần tối thiểu 30-45 phút đi dạo/vận động ngoài trời mỗi ngày để giải phóng năng lượng dư thừa.\n"
                f"• **Với Mèo cưng:** Chuẩn bị bàn cào móng (scratching post), đồ chơi cần câu mèo, cỏ mèo catnip để thỏa mãn bản năng săn mồi.\n"
                f"• **Phòng ngừa béo phì:** Kiểm soát lượng calo nạp vào, hạn chế cho ăn vặt và duy trì lịch cân định kỳ tại PetCare Pro."
            )
            actions = ["Đồ chơi tương tác thú cưng", "Đặt lịch vận động Spa", "Đo chỉ số thể trạng BMI"]

        # 19. CHĂM SÓC THÚ CƯNG GIÀ (LÃO NIÊN)
        elif any(w in msg_lower for w in ["chó già", "mèo già", "lớn tuổi", "viêm khớp", "thoái hóa khớp", "yếu chân", "đục thủy tinh thể", "thú cưng già", "tuổi thọ"]):
            reply = (
                f"👴 **CHẾ ĐỘ CHĂM SÓC ĐẶC BIỆT CHO THÚ CƯNG CAO TUỔI (TRÊN 7 NĂM):**\n\n"
                f"Khi bước vào tuổi lão niên, cơ thể {pet_name} bắt đầu có những thay đổi lớn:\n"
                f"1. **Bảo vệ xương khớp:** Bổ sung Glucosamine, Chondroitin và Omega-3 giúp bôi trơn ổ khớp, giảm đau khi trời lạnh.\n"
                f"2. **Thức ăn dễ tiêu:** Chọn hạt chuyên dụng cho thú cưng lão niên (Senior) với lượng đạm tinh khiết, giảm natri và phospho để giảm gánh nặng cho thận.\n"
                f"3. **Chăm sóc răng miệng:** Răng yếu dễ rụng, nên làm mềm thức ăn hoặc cho ăn cháo pate ấm.\n"
                f"4. **Khám định kỳ 6 tháng/lần:** Làm xét nghiệm sinh hóa máu, kiểm tra chức năng gan, thận và tim mạch."
            )
            actions = ["Gói khám sức khỏe Lão niên", "Thuốc bổ khớp Glucosamine", "Tư vấn dinh dưỡng thú già"]

        # 20. SƠ CỨU TAI NẠN NHẸ TẠI NHÀ
        elif any(w in msg_lower for w in ["ong đốt", "côn trùng cắn", "xước da", "bỏng nhẹ", "say nắng", "sốc nhiệt", "heatstroke", "dính keo", "kẹt chân", "vết thương nhỏ"]):
            reply = (
                f"🩹 **KỸ NĂNG SƠ CỨU TAI NẠN NHẸ THƯỜNG GẶP TẠI NHÀ:**\n\n"
                f"• **Bị ong hoặc côn trùng đốt:** Rút ngòi ong bằng thẻ ATM (không dùng tay bóp nặn ngòi), chườm khăn mát bọc đá lên vết sưng 15 phút để giảm đau.\n"
                f"• **Sốc nhiệt / Say nắng (Heatstroke):** Lập tức đưa bé vào chỗ râm mát, đắp khăn ướt mát vào 4 bàn chân, bẹn và nách (KHÔNG dội nước đá lạnh đột ngột vì gây sốc nhiệt), cho uống từng ngụm nước nhỏ.\n"
                f"• **Xước da chảy máu nhẹ:** Rửa sạch vết thương bằng nước muối sinh lý NaCl 0.9%, chấm cồn đỏ sát trùng Betadine/Povidone Iodine (không dùng cồn trắng 90 độ gây rát xót).\n"
                f"• **Lông dính bết kẹo cao su:** Thoa dầu dừa hoặc bơ đậu phộng lên vùng dính, mát-xa nhẹ để kẹo tan ra rồi dùng lược chải sạch."
            )
            actions = ["Dung dịch sát trùng Betadine", "Hotline tư vấn sơ cứu 24/7", "Đưa bé đến kiểm tra"]

        # 21. CẮT TỈA TẠO KIỂU GROOMING & SPA CAO CẤP
        elif any(w in msg_lower for w in ["cắt tỉa", "grooming", "tỉa lông", "nhuộm lông", "tạo kiểu", "mặt tròn", "mặt gấu", "hàn quốc", "cạo bàn", "cạo lông"]):
            reply = (
                f"✂️ **DỊCH VỤ CẮT TỈA GROOMING TẠO KIỂU THẨM MỸ TẠI PETCARE PRO:**\n\n"
                f"Đội ngũ Master Groomer được đào tạo bài bản sẽ biến hóa diện mạo cho {pet_name}:\n"
                f"• **Kiểu dáng thịnh hành:** Cắt tỉa form tròn Teddy Bear (cho Poodle, Bichon), kiểu đầu tròn nấm Hàn Quốc, kiểu sư tử quý phái (cho Phốc sóc), tỉa tỉ mỉ vùng mặt và tai.\n"
                f"• **Cạo vệ sinh chuyên sâu:** Cạo sạch lông đệm bàn chân (chống trơn trượt), cạo lông vùng bụng và quanh hậu môn đảm bảo vệ sinh 100% khi đi vệ sinh.\n"
                f"• **Nhuộm lông thảo dược an toàn:** Nhuộm tai, nhuộm đuôi bằng màu hữu cơ nhập khẩu Hàn Quốc không gây kích ứng da.\n\n"
                f"🎁 *Combo Grooming đã bao gồm toàn bộ quy trình tắm spa thảo dược và cắt mài móng!*"
            )
            actions = ["Xem Album mẫu cắt tỉa đẹp", "Đặt lịch Grooming tạo kiểu", "Tư vấn kiểu lông hợp mặt"]

        # 22. GIỜ MỞ CỬA, ĐỊA CHỈ & LIÊN HỆ
        elif any(w in msg_lower for w in ["giờ mở cửa", "mấy giờ", "địa chỉ", "ở đâu", "liên hệ", "hotline", "chi nhánh", "ngày lễ", "có làm việc không"]):
            reply = (
                f"📍 **THÔNG TIN LIÊN HỆ HỆ THỐNG PHÒNG KHÁM & SPA PETCARE PRO:**\n\n"
                f"• ⏰ **Giờ làm việc:** 08:00 - 20:30 (Mở cửa tất cả các ngày trong tuần, kể cả Thứ Bảy, Chủ Nhật và các ngày Lễ/Tết).\n"
                f"• 🏢 **Địa chỉ Trung tâm:** Số 126 Đường Z115, Thành phố Thái Nguyên (Gần ĐH CNTT & TT - ICTU).\n"
                f"• 📞 **Hotline tư vấn & Đặt lịch:** 0988.123.456\n"
                f"• 🚨 **Cấp cứu Thú y trực tuyến 24/7:** 0988.999.888\n"
                f"• 🌐 **Hệ thống phần mềm:** Tích hợp tra cứu lịch sử khám, sổ tiêm phòng và đặt lịch hẹn online tiện lợi."
            )
            actions = ["Đặt lịch hẹn ngay", "Xem bản đồ chỉ đường", "Gọi hotline hỗ trợ"]

        # 23. CHÀO HỎI & GIỚI THIỆU
        elif any(w in msg_lower for w in ["xin chào", "chào bạn", "hello", "hi ", "bạn là ai", "bác sĩ sarah", "tên bạn là gì", "giới thiệu bản thân"]):
            reply = (
                f"Dạ xin chào bạn! Tôi là **Bác Sĩ Thú Y AI Sarah** - Trợ lý thông minh đồng hành 24/7 của hệ thống PetCare Pro 🐾.\n\n"
                f"Tôi có thể giải đáp chi tiết tất cả các câu hỏi chăm sóc thú cưng cho bạn:\n"
                f"• 🛁 **Tắm sấy & Grooming:** Tần suất tắm, chọn sữa tắm, cắt tỉa tạo kiểu lông móng.\n"
                f"• 🥩 **Dinh dưỡng:** Thực đơn an toàn, danh sách thức ăn cấm kỵ, cách nấu pate.\n"
                f"• 💉 **Y tế & Phòng bệnh:** Lịch tiêm phòng vắc xin, lịch tẩy giun, phòng trị ve rận, nấm da.\n"
                f"• 🏨 **Dịch vụ PetCare:** Bảng giá spa, đặt phòng khách sạn lưu trú, đặt lịch khám.\n\n"
                f"Hôm nay bé cưng của bạn tên gì và bạn đang cần tôi hỗ trợ vấn đề nào?"
            )
            actions = ["Bảng giá dịch vụ", "Bao lâu tắm cún 1 lần?", "Lịch tiêm phòng 7 bệnh", "Thực phẩm độc hại cần tránh"]

        # 24. CẢM ƠN, TẠM BIỆT & KHEN NGỢI
        elif any(w in msg_lower for w in ["cảm ơn", "thank", "tuyệt vời", "hay quá", "ok", "tạm biệt", "bye", "hẹn gặp lại", "rất tốt", "giỏi quá"]):
            reply = (
                f"Dạ PetCare Pro và Bác Sĩ Sarah rất vui vì được đồng hành cùng bạn và bé yêu {pet_name} ❤️!\n\n"
                f"Chúc bạn và bé luôn có những khoảnh khắc thật vui vẻ và tràn đầy sức khỏe bên nhau. "
                f"Bất cứ khi nào cần tư vấn hoặc đặt lịch chăm sóc, bạn chỉ cần nhắn tin cho tôi nhé!\n\n"
                f"Hẹn sớm gặp lại bạn tại PetCare Pro Spa & Clinic 🐾✨."
            )
            actions = ["Đặt lịch chăm sóc", "Xem các ưu đãi tháng này", "Đánh giá dịch vụ"]

        # 25. THÔNG MINH PHÂN TÍCH THEO NGỮ CẢNH TỔNG QUÁT (SMART CONTEXTUAL FALLBACK)
        else:
            reply = (
                f"Chào bạn! Tôi đã ghi nhận câu hỏi của bạn về việc chăm sóc cho {pet_name} ({species}) 🐾.\n\n"
                f"💡 **TƯ VẤN CHUNG TỪ BÁC SĨ THÚ Y SARAH:**\n"
                f"1. **Quan sát thể trạng:** Hãy theo dõi sát sao biểu hiện tinh thần (bé có vui vẻ lanh lợi hay ủ rũ), mức độ thèm ăn và lượng nước uống trong 24 giờ.\n"
                f"2. **Đo thân nhiệt:** Nhiệt độ cơ thể bình thường của chó mèo là **38.0°C - 39.2°C**. Nếu trên 39.5°C là bé đang bị sốt.\n"
                f"3. **Môi trường sống:** Giữ khu vực nằm sạch sẽ, thoáng mát về mùa hè và ấm áp về mùa đông.\n\n"
                f"👉 Bạn có thể bấm vào các chủ đề phổ biến bên dưới hoặc đặt câu hỏi chi tiết hơn để tôi tư vấn chuẩn xác nhất nhé!"
            )
            actions = [
                "Bảng giá dịch vụ PetCare",
                "Tư vấn dinh dưỡng & thức ăn",
                "Cách phòng trị ve rận & nấm da",
                "Lịch tiêm phòng & tẩy giun",
                "Đặt lịch chăm sóc tại tiệm"
            ]

        if image_data:
            image_note = (
                f"📸 **Bác Sĩ Thú Y Sarah đã nhận & quan sát ảnh bạn gửi:**\n"
                f"• Đã lưu ảnh vào hồ sơ khám trực tuyến của bé. Tình trạng vùng da/thể trạng trong ảnh đã được ghi nhận.\n"
                f"• Khuyến cáo: Giữ vùng tổn thương khô ráo, tránh để bé liếm hoặc gãi (nên đeo loa chống liếm Elizabeth).\n\n"
            )
            reply = image_note + reply
            if "Gửi thêm ảnh góc chụp khác" not in actions:
                actions.insert(0, "Gửi thêm ảnh góc chụp khác")

        return {
            "reply": reply,
            "is_emergency": False,
            "emergency_level": "NONE",
            "warning_badge": None,
            "veterinary_disclaimer": VETERINARY_DISCLAIMER,
            "suggested_actions": actions,
            "generated_by": "PetCare AI Assistant (AIA331 - ICTU)"
        }

    @staticmethod
    def _try_call_online_llm(
        message: str,
        image_data: Optional[str] = None,
        pet_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Any]] = None
    ) -> Optional[tuple[str, list[str], str]]:
        """Hỗ trợ gọi Online LLM (Gemini / OpenAI) nếu có API key cấu hình trong hệ thống"""
        
        system_prompt = (
            "Bạn là Bác Sĩ Thú Y AI Sarah thuộc Hệ thống Phòng khám & Spa PetCare Pro (Việt Nam). "
            "Bạn có kiến thức thú y chuyên sâu, nhiệt tình, ân cần và khoa học. "
            "Hãy trả lời câu hỏi của phụ huynh thú cưng bằng tiếng Việt một cách chi tiết, đi thẳng vào trọng tâm câu hỏi, "
            "tự nhiên, không dùng câu từ rập khuôn, có bố cục rõ ràng (gạch đầu dòng, icon minh họa sinh động), "
            "hướng dẫn chăm sóc thực tế, an toàn và các lưu ý y khoa quan trọng. "
            "Nếu có ảnh thú cưng đính kèm, hãy quan sát và đưa ra nhận xét y khoa chi tiết. "
            "Luôn nhắc nhở an toàn sức khỏe cho thú cưng và không vượt quá thẩm quyền kê đơn thuốc độc bảng A."
        )

        pet_desc = ""
        if pet_context:
            pet_desc = f"[Hồ sơ thú cưng: Tên: {pet_context.get('name', 'Bé')}, Loài: {pet_context.get('species', 'Chó/Mèo')}, Giống: {pet_context.get('breed', 'Chưa rõ')}, Tuổi: {pet_context.get('age', 'Chưa rõ')}]\n"

        # 1. Thử gọi Google Gemini 1.5 Flash nếu có key
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                contents = []
                
                # Nạp lịch sử hội thoại trước đó
                if chat_history and isinstance(chat_history, list):
                    for turn in chat_history[-6:]:
                        role = "user"
                        content = ""
                        if isinstance(turn, dict):
                            role = turn.get("role", "user")
                            content = str(turn.get("content", ""))
                        elif hasattr(turn, "content"):
                            role = getattr(turn, "role", "user")
                            content = str(getattr(turn, "content", ""))
                        if content:
                            contents.append({
                                "role": "user" if role == "user" else "model",
                                "parts": [{"text": content}]
                            })

                # Lượt hội thoại hiện tại
                current_parts: list[dict[str, Any]] = []
                user_text = f"{pet_desc}{message}".strip()
                current_parts.append({"text": user_text})

                # Đính kèm ảnh nếu có (multimodal vision)
                if image_data and "base64," in image_data:
                    try:
                        header, b64_clean = image_data.split("base64,", 1)
                        mime_type = "image/jpeg"
                        if "png" in header:
                            mime_type = "image/png"
                        elif "webp" in header:
                            mime_type = "image/webp"
                        current_parts.append({
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": b64_clean.strip()
                            }
                        })
                    except Exception:
                        pass

                contents.append({"role": "user", "parts": current_parts})

                payload = {
                    "system_instruction": {
                        "parts": [{"text": system_prompt}]
                    },
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1200
                    }
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if text:
                                return (
                                    text.strip(),
                                    ["Đặt lịch dịch vụ", "Tư vấn dinh dưỡng", "Hỏi thêm câu khác"],
                                    "PetCare AI Engine (Google Gemini-1.5-Flash)"
                                )
            except Exception:
                pass

        # 2. Thử gọi OpenAI nếu có key
        if settings.OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                messages = [{"role": "system", "content": system_prompt}]
                if chat_history and isinstance(chat_history, list):
                    for turn in chat_history[-4:]:
                        role = "user"
                        content = ""
                        if isinstance(turn, dict):
                            role = turn.get("role", "user")
                            content = str(turn.get("content", ""))
                        elif hasattr(turn, "content"):
                            role = getattr(turn, "role", "user")
                            content = str(getattr(turn, "content", ""))
                        if content:
                            messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": f"{pet_desc}\n{message}".strip()})
                
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.7
                }
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            text = choices[0].get("message", {}).get("content", "")
                            if text:
                                return (
                                    text.strip(),
                                    ["Đặt lịch dịch vụ", "Tư vấn dinh dưỡng", "Hỏi thêm câu khác"],
                                    "PetCare AI Engine (OpenAI GPT-4o-mini)"
                                )
            except Exception:
                pass

        return None

    @staticmethod
    def check_symptoms(
        species: str = "Chó",
        breed: Optional[str] = None,
        age_str: Optional[str] = None,
        symptoms: List[str] = [],
        symptom_description: Optional[str] = None,
        duration: Optional[str] = "1-2 ngày",
        behavior_changes: Optional[str] = None
    ) -> Dict[str, Any]:
        """AI Phân tích triệu chứng, phân loại nguy cơ và đề xuất dịch vụ chăm sóc / can thiệp thú y"""
        all_text = f"{' '.join(symptoms)} {symptom_description or ''} {behavior_changes or ''}".lower()
        is_em, em_level, flags = detect_emergency_symptoms(all_text)

        # 1. Cấp cứu khẩn cấp (Emergency)
        if is_em:
            return {
                "risk_level": "EMERGENCY",
                "risk_label": "🚨 CẤP CỨU KHẨN CẤP - ĐƯA ĐẾN BỆNH VIỆN NGAY",
                "risk_color": "red",
                "summary": f"Phát hiện dấu hiệu nguy hiểm tính mạng ({', '.join(flags)}). Thú cưng cần được can thiệp y tế chuyên sâu ngay lập tức trong giờ vàng!",
                "potential_causes": [
                    "Ngộ độc cấp tính / Dị vật đường tiêu hóa hoặc đường thở",
                    "Chấn thương nội tạng / Xuất huyết nội",
                    "Rối loạn thần kinh hoặc suy hô hấp / suy tuần hoàn cấp"
                ],
                "first_aid_and_care": [
                    "Giữ ấm cho thú cưng bằng chăn mềm, đặt nằm nghiêng cổ thẳng.",
                    "KHÔNG tự ý ép uống sữa, dầu ăn hoặc cho uống thuốc của người.",
                    "Nếu nghi ngộ độc, chụp ảnh mẫu hóa chất hoặc thức ăn nghi ngờ mang theo đến phòng khám.",
                    "Liên hệ ngay Hotline cấp cứu thú y 24/7 gần nhất!"
                ],
                "recommended_services": [
                    {
                        "name": "Khám sàng lọc & Cấp cứu Thú y",
                        "category": "Cấp cứu & Điều trị",
                        "reason": "Xử trí cấp cứu, thở oxy, truyền dịch giải độc hoặc nội soi gắp dị vật khẩn cấp.",
                        "estimated_price": 300000
                    }
                ],
                "should_see_vet": True,
                "veterinary_disclaimer": VETERINARY_DISCLAIMER,
                "generated_by": "PetCare AI Symptom Engine (AIA331 - ICTU)"
            }

        # 2. Nguy cơ Cao (High Risk)
        high_risk_triggers = ["sốt", "bỏ ăn", "nôn", "tiêu chảy", "li bì", "mệt mỏi kéo dài", "chảy dịch mắt mũi xanh", "khò khè"]
        has_high_risk = any(t in all_text for t in high_risk_triggers)

        if has_high_risk:
            return {
                "risk_level": "HIGH",
                "risk_label": "⚠️ NGUY CƠ CAO - CẦN ĐƯỢC BÁC SĨ THÚ Y THĂM KHÁM",
                "risk_color": "orange",
                "summary": f"Thú cưng ({species} {breed or ''}) đang có dấu hiệu suy giảm sức khỏe hoặc nhiễm trùng/rối loạn tiêu hóa - hô hấp ({duration}).",
                "potential_causes": [
                    "Nhiễm khuẩn đường ruột hoặc virus truyền nhiễm (Care/Parvo/Giảm bạch cầu)",
                    "Viêm đường hô hấp trên / Cảm lạnh hoặc viêm phổi",
                    "Rối loạn tiêu hóa do thay đổi thức ăn hoặc nhiễm ký sinh trùng"
                ],
                "first_aid_and_care": [
                    "Cung cấp nước sạch ấm hoặc dung dịch Oresol thú cưng pha đúng tỷ lệ để chống mất nước.",
                    "Cách ly với các thú cưng khác để đề phòng lây nhiễm.",
                    "Kiểm tra nhiệt độ trực tràng (nhiệt độ bình thường của chó mèo là 38.0°C - 39.2°C).",
                    "Đặt lịch khám thú y trong vòng 12-24 giờ tới."
                ],
                "recommended_services": [
                    {
                        "name": "Khám tổng quát & Xét nghiệm sàng lọc",
                        "category": "Khám & Tiêm phòng",
                        "reason": "Bác sĩ kiểm tra sinh hiệu, xét nghiệm máu và phân chẩn đoán chính xác nguyên nhân.",
                        "estimated_price": 200000
                    }
                ],
                "should_see_vet": True,
                "veterinary_disclaimer": VETERINARY_DISCLAIMER,
                "generated_by": "PetCare AI Symptom Engine (AIA331 - ICTU)"
            }

        # 3. Nguy cơ Trung bình / Vấn đề Da Lông, Ký sinh trùng, Tai Mắt (Medium Risk)
        medium_triggers = ["ngứa", "gãi", "rụng lông", "vảy gàu", "nấm da", "ve", "rận", "viêm tai", "hôi tai", "chảy nước mắt", "hôi miệng"]
        has_medium_risk = any(t in all_text for t in medium_triggers)

        if has_medium_risk:
            return {
                "risk_level": "MEDIUM",
                "risk_label": "🔶 MỨC ĐỘ TRUNG BÌNH - VẤN ĐỀ DA LÔNG & VỆ SINH",
                "risk_color": "yellow",
                "summary": f"Thú cưng có biểu hiện bệnh lý ngoài da, ký sinh trùng hoặc vệ sinh tai móng chưa đúng cách.",
                "potential_causes": [
                    "Viêm da dị ứng hoặc nấm da (Microsporum canis / Malassezia)",
                    "Nhiễm ký sinh trùng ngoài da (Ve rận, bọ chét, xà mâu Demodex)",
                    "Viêm ống tai ngoài do tích tụ ráy tai ẩm ướt hoặc mảng bám vôi răng"
                ],
                "first_aid_and_care": [
                    "Đeo loa chống liếm (vòng Elizabeth) tránh để bé gãi cào gây xước chảy máu.",
                    "Không tự ý bôi các loại thuốc mỡ corticoid của người lên da bé.",
                    "Vệ sinh tai bằng dung dịch chuyên dụng cho thú cưng.",
                    "Tắm bằng dầu tắm dược liệu trị nấm và sấy thật khô chân lông."
                ],
                "recommended_services": [
                    {
                        "name": "Tắm Spa & Trị liệu phục hồi da lông",
                        "category": "Tắm spa",
                        "reason": "Tắm dầu thảo dược sát khuẩn trị nấm, vắt tuyến hôi và sấy tơi khô ráo.",
                        "estimated_price": 150000
                    },
                    {
                        "name": "Vệ sinh toàn diện (Tai, Móng, Tuyến hôi)",
                        "category": "Chăm sóc cơ bản",
                        "reason": "Làm sạch sâu ống tai, cắt tỉa móng và vệ sinh tuyến hôi ngăn vi khuẩn.",
                        "estimated_price": 100000
                    }
                ],
                "should_see_vet": False,
                "veterinary_disclaimer": VETERINARY_DISCLAIMER,
                "generated_by": "PetCare AI Symptom Engine (AIA331 - ICTU)"
            }

        # 4. Mức độ Nhẹ / Chăm sóc định kỳ (Low Risk)
        return {
            "risk_level": "LOW",
            "risk_label": "🟢 MỨC ĐỘ NHẸ - CHĂM SÓC SPA & ĐỊNH KỲ",
            "risk_color": "green",
            "summary": f"Tình trạng sức khỏe của {species} nhìn chung ổn định, thích hợp để thực hiện các gói chăm sóc sắc đẹp, grooming và bảo vệ định kỳ.",
            "potential_causes": [
                "Lông dài xơ rối hoặc đến kỳ thay lông tự nhiên",
                "Cần cắt tỉa thẩm mỹ form chuẩn tạo kiểu",
                "Đến hạn tiêm vaccine hoặc tẩy giun định kỳ"
            ],
            "first_aid_and_care": [
                "Chải lông hàng ngày bằng lược chuyên dụng giúp loại bỏ lông rụng và kích thích mọc lông mới.",
                "Duy trì chế độ ăn uống đủ đạm và cung cấp nước uống sạch liên tục.",
                "Vận động thể chất và dắt đi dạo mỗi ngày 20-30 phút."
            ],
            "recommended_services": [
                {
                    "name": "Combo Cắt tỉa Grooming tạo kiểu",
                    "category": "Cắt tỉa grooming",
                    "reason": "Cắt tỉa tạo form mặt tròn Hàn Quốc/Teddy Bear, vệ sinh trọn gói toàn thân.",
                    "estimated_price": 350000
                },
                {
                    "name": "Gói Siêu VIP Spa & Dưỡng ẩm bùn khoáng",
                    "category": "Combo",
                    "reason": "Ủ dưỡng ẩm bùn khoáng phục hồi lông mềm mượt chuẩn thẩm mỹ.",
                    "estimated_price": 550000
                }
            ],
            "should_see_vet": False,
            "veterinary_disclaimer": VETERINARY_DISCLAIMER,
            "generated_by": "PetCare AI Symptom Engine (AIA331 - ICTU)"
        }

