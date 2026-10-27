import os
import json
import re
import requests
from typing import Dict, Any, List, Optional
from .config import settings

# --- SYSTEM PROMPT & DISCLAIMERS ---
PETCARE_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Chuyên viên Chăm sóc Thú cưng của hệ thống PetCare AI. "
    "Nhiệm vụ: Cung cấp thông tin hướng dẫn chăm sóc cơ bản (vệ sinh, dinh dưỡng, chải chuốt lông, lịch tiêm phòng). "
    "QUY TẮC BẮT BUỘC: Bạn KHÔNG được chẩn đoán bệnh tật hoặc kê đơn thuốc thú y. "
    "Mọi câu trả lời PHẢI kèm theo cảnh báo rõ ràng rằng thông tin chỉ mang tính tham khảo và khuyên liên hệ bác sĩ thú y khi có dấu hiệu bất thường."
)

PETCARE_MEDICAL_DISCLAIMER = (
    "⚠️ LƯU Ý Y TẾ THÚ Y: Thông tin do Trợ lý AI cung cấp chỉ mang tính chất tham khảo cơ bản, "
    "KHÔNG thay thế cho việc khám, chẩn đoán và điều trị của Bác sĩ Thú y có chứng chỉ hành nghề. "
    "Nếu thú cưng có triệu chứng bệnh lý hoặc dấu hiệu bất thường, vui lòng đưa bé đến Phòng khám Thú y gần nhất ngay lập tức!"
)

# Urgent keywords that indicate dangerous medical emergencies (both accented and unaccented)
EMERGENCY_KEYWORDS = [
    # Accented
    "co giật", "sốt cao", "nôn ra máu", "tiêu chảy ra máu", "hôn mê", "bất tỉnh",
    "khó thở", "thở dốc", "thở khò khè", "nuốt dị vật", "ngộ độc", "liếm bả", "sưng phù mặt",
    "bỏ ăn 3 ngày", "bỏ ăn nhiều ngày", "gãy chân", "chảy máu không ngừng", "tai nạn",
    # Unaccented & variants
    "co giat", "sot cao", "non ra mau", "tieu chay ra mau", "hon me", "bat tinh",
    "kho tho", "tho doc", "tho kho khe", "nuot di vat", "ngo doc", "liem ba", "sung phu mat",
    "bo an 3 ngay", "bo an nhieu ngay", "gay chan", "chay mau", "tai nan", "cap cuu"
]


class AIService:
    @staticmethod
    def detect_emergency(text: str) -> bool:
        lower_text = text.lower()
        for kw in EMERGENCY_KEYWORDS:
            if kw in lower_text:
                return True
        return False

    @staticmethod
    def call_gemini_api(prompt: str, system_instruction: str = PETCARE_SYSTEM_PROMPT) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_instruction}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
            }
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[AI Service] Gemini API call error: {e}")
        return None

    @staticmethod
    def call_openai_api(prompt: str, system_instruction: str = PETCARE_SYSTEM_PROMPT) -> Optional[str]:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return None
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.4,
                "max_tokens": 1000
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[AI Service] OpenAI API call error: {e}")
        return None

    @classmethod
    def generate_reminder_message(
        cls,
        reminder_type: str,
        owner_name: str,
        owner_phone: str,
        pet_name: str,
        pet_species: str,
        service_or_vaccine: str,
        date_str: str,
        time_str: Optional[str] = None,
        tone: str = "friendly",
        custom_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates tailored reminders for appointment or vaccination.
        Supports tones: 'friendly', 'formal', 'cute_fun', 'sms_short'
        """
        # Try LLM first if API key configured
        llm_prompt = (
            f"Hãy viết một tin nhắn nhắc lịch {reminder_type} cho khách hàng:\n"
            f"- Tên chủ nuôi: {owner_name}\n"
            f"- Tên thú cưng: {pet_name} ({pet_species})\n"
            f"- Dịch vụ / Mũi tiêm: {service_or_vaccine}\n"
            f"- Thời gian hẹn/Đến hạn: {date_str} {time_str or ''}\n"
            f"- Phong cách tin nhắn: {tone} (thân thiện, tôn trọng, chuyên nghiệp)\n"
            f"- Ghi chú bổ sung: {custom_note or 'Không'}\n"
            "Hãy viết ngắn gọn, lịch sự, có lời chào và dặn dò khách hàng chuẩn bị trước khi đưa bé đến."
        )

        llm_result = None
        model_used = "PetCare-RuleHeuristic-Engine"
        if settings.GEMINI_API_KEY:
            llm_result = cls.call_gemini_api(llm_prompt)
            if llm_result:
                model_used = "Google-Gemini-1.5-Flash"
        elif settings.OPENAI_API_KEY:
            llm_result = cls.call_openai_api(llm_prompt)
            if llm_result:
                model_used = "OpenAI-GPT-3.5-Turbo"

        if llm_result:
            return {
                "title": f"Nhắc lịch {service_or_vaccine} cho bé {pet_name}",
                "recipient_name": owner_name,
                "recipient_phone": owner_phone,
                "message": llm_result,
                "channel_recommendation": "Zalo OA / SMS / Cuộc gọi nhắc",
                "model_used": model_used
            }

        # High-quality Rule-based Heuristic Generator (Offline & Deterministic)
        greeting = f"Dạ kính chào Anh/Chị {owner_name},"
        time_desc = f"vào lúc {time_str} ngày {date_str}" if time_str else f"vào ngày {date_str}"
        note_text = f"\n📌 Lưu ý thêm từ tiệm: {custom_note}" if custom_note else ""

        if reminder_type == "vaccine":
            if tone == "formal":
                message = (
                    f"{greeting}\n\n"
                    f"Hệ thống PetCare xin trân trọng thông báo: Bé {pet_name} ({pet_species}) của Quý khách "
                    f"đã đến lịch tiêm phòng nhắc lại gói: 【{service_or_vaccine}】 vào ngày {date_str}.\n"
                    f"Việc tiêm phòng đúng hạn giúp bé duy trì kháng thể miễn dịch tốt nhất trước các bệnh truyền nhiễm nguy hiểm.{note_text}\n\n"
                    f"Quý khách vui lòng liên hệ hotline hoặc phản hồi tin nhắn này để xếp lịch đón bé nhé.\n"
                    f"Trân trọng cảm ơn Quý khách!"
                )
            elif tone == "cute_fun":
                message = (
                    f"Gâu gâu meo meo! 🐾 Chào Ba/Mẹ {owner_name} thân yêu ạ!\n\n"
                    f"Em là bé {pet_name} đây nè! Sắp đến hạn {date_str} để em đi tiêm 'áo giáp hộ mệnh' 【{service_or_vaccine}】 rồi ạ. "
                    f"Ba/Mẹ đừng quên đặt lịch đưa em qua PetCare để em luôn khỏe mạnh, tung tăng chơi cùng Ba/Mẹ nha! ❤️🐾{note_text}\n\n"
                    f"PetCare đang đợi 2 Ba/Mẹ và em bé ghé chơi nè!"
                )
            elif tone == "sms_short":
                message = (
                    f"[PETCARE] Nhac lich: Be {pet_name} den han tiem {service_or_vaccine} ngay {date_str}. "
                    f"Kinh moi Anh/Chi {owner_name} lien he 0987654321 de dat hen. Tran trong!"
                )
            else: # friendly (default)
                message = (
                    f"{greeting} PetCare chúc Anh/Chị một ngày tốt lành! ✨\n\n"
                    f"PetCare xin phép gửi lời nhắc: Bé {pet_name} nhà mình sắp đến lịch tiêm phòng/uống ngừa: "
                    f"【{service_or_vaccine}】 vào ngày {date_str} tới đây ạ.\n\n"
                    f"💡 Dặn dò nhỏ: Trước khi đưa bé đi tiêm, Anh/Chị kiểm tra xem bé có đang ăn ngủ khỏe mạnh không và tránh tắm cho bé sát giờ tiêm nhé.{note_text}\n\n"
                    f"Anh/Chị có thể bấm xác nhận lịch hẹn để PetCare chuẩn bị đón bé chu đáo nhất ạ!"
                )
        else:
            # Appointment reminder
            if tone == "formal":
                message = (
                    f"{greeting}\n\n"
                    f"PetCare xin trân trọng xác nhận lịch hẹn dịch vụ của bé {pet_name} ({pet_species}):\n"
                    f"• Dịch vụ: {service_or_vaccine}\n"
                    f"• Thời gian: {time_desc}\n"
                    f"• Địa điểm: PetCare Spa & Clinic, Thái Nguyên\n"
                    f"Kính mong Quý khách đưa bé đến đúng giờ để dịch vụ đạt kết quả hoàn hảo nhất.{note_text}\n\n"
                    f"PetCare trân trọng đón tiếp Quý khách!"
                )
            elif tone == "cute_fun":
                message = (
                    f"Woohoo! 🐶🐱 Chào Ba/Mẹ {owner_name} ơi!\n\n"
                    f"Ngày mai {time_desc}, bé {pet_name} có hẹn đi 'tút lại nhan sắc' với gói: 【{service_or_vaccine}】 tại PetCare nè! "
                    f"Các cô chú kỹ thuật viên đã chuẩn bị sẵn sữa tắm thơm phức và đồ chơi đợi bé rồi ạ! ✨🛁{note_text}\n\n"
                    f"Ba/Mẹ nhớ chở bé đến đúng giờ để bé được thư giãn trọn vẹn nhất nhé! Yêu thương nhiều ạ!"
                )
            elif tone == "sms_short":
                message = (
                    f"[PETCARE] Nhac hen: Be {pet_name} co lich {service_or_vaccine} vao {time_desc}. "
                    f"LH 0987654321 neu can doi gio. Xin cam on!"
                )
            else: # friendly (default)
                message = (
                    f"{greeting} PetCare xin gửi lời chào ấm áp tới Anh/Chị! 🌿\n\n"
                    f"Hệ thống xin nhắc Anh/Chị về lịch hẹn chăm sóc cho bé {pet_name} ({pet_species}):\n"
                    f"📅 Thời gian: {time_desc}\n"
                    f"✂️ Dịch vụ: {service_or_vaccine}\n"
                    f"📍 Trạng thái: Đã sẵn sàng nhân sự và phòng phục vụ bé.{note_text}\n\n"
                    f"Anh/Chị lưu ý cho bé đi vệ sinh trước khi đến tiệm để bé cảm thấy thoải mái nhất nhé! Hẹn gặp lại bé {pet_name} ạ! ❤️"
                )

        return {
            "title": f"Nhắc lịch {service_or_vaccine} cho bé {pet_name}",
            "recipient_name": owner_name,
            "recipient_phone": owner_phone,
            "message": message,
            "channel_recommendation": "Zalo OA / Tin nhắn SMS / Gọi điện thoại",
            "model_used": model_used
        }

    @classmethod
    def generate_pet_care_summary(
        cls,
        pet_info: Dict[str, Any],
        care_records: List[Dict[str, Any]],
        vaccine_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Summarizes care history, skin/fur condition, weights, and health reminders.
        """
        prompt = (
            f"Dưới đây là hồ sơ chăm sóc của thú cưng:\n"
            f"- Tên: {pet_info.get('name')}, Giống: {pet_info.get('breed')}, Loài: {pet_info.get('species')}\n"
            f"- Tuổi: {pet_info.get('age_months')} tháng, Cân nặng: {pet_info.get('weight_kg')} kg\n"
            f"- Dị ứng: {pet_info.get('allergies', 'Không')}\n"
            f"- Lịch sử chăm sóc gần đây ({len(care_records)} lần):\n"
            f"{json.dumps(care_records, ensure_ascii=False, indent=2)}\n"
            f"- Lịch tiêm phòng / phòng bệnh:\n"
            f"{json.dumps(vaccine_history, ensure_ascii=False, indent=2)}\n\n"
            "Hãy phân tích và viết báo cáo tóm tắt hồ sơ chăm sóc theo định dạng Markdown:\n"
            "1. Tóm tắt tình trạng thể chất và lông da qua các lần chăm sóc.\n"
            "2. Biến động cân nặng và hành vi khi làm dịch vụ.\n"
            "3. Các lưu ý quan trọng cần chủ nuôi theo dõi tại nhà.\n"
            "4. Đề xuất dịch vụ hoặc lịch nhắc tiếp theo."
        )

        model_used = "PetCare-RuleHeuristic-Engine"
        llm_result = None
        if settings.GEMINI_API_KEY:
            llm_result = cls.call_gemini_api(prompt)
            if llm_result:
                model_used = "Google-Gemini-1.5-Flash"
        elif settings.OPENAI_API_KEY:
            llm_result = cls.call_openai_api(prompt)
            if llm_result:
                model_used = "OpenAI-GPT-3.5-Turbo"

        health_alerts = []
        suggested_actions = []

        # Analyze warnings
        allergies = pet_info.get("allergies", "")
        if allergies and allergies.lower() not in ["không", "không có", "none"]:
            health_alerts.append(f"Tiền sử dị ứng: {allergies}. Tránh các hoạt chất tẩy rửa mạnh.")

        for v in vaccine_history:
            if v.get("status") == "overdue":
                health_alerts.append(f"Mũi tiêm '{v.get('vaccine_name')}' ĐÃ QUÁ HẠN ({v.get('next_due_date')}). Cần bổ sung ngay!")
            elif v.get("status") == "pending":
                suggested_actions.append(f"Nhắc lịch tiêm '{v.get('vaccine_name')}' dự kiến ngày {v.get('next_due_date')}.")

        if not care_records:
            suggested_actions.append("Bé chưa có hồ sơ spa/chăm sóc gần đây. Nên đặt lịch Tắm spa dưỡng ẩm để làm sạch lông da.")

        if llm_result:
            return {
                "pet_id": pet_info.get("id"),
                "pet_name": pet_info.get("name"),
                "summary_markdown": llm_result,
                "health_alerts": health_alerts,
                "suggested_actions": suggested_actions,
                "model_used": model_used
            }

        # Rule-based structured analysis
        recent_records_summary = ""
        if care_records:
            recent = care_records[0]
            recent_records_summary = (
                f"- **Lần chăm sóc gần nhất ({recent.get('record_date')}):**\n"
                f"  • *Tình trạng da lông:* {recent.get('fur_skin_condition')}\n"
                f"  • *Cân nặng đo được:* {recent.get('weight_recorded_kg', pet_info.get('weight_kg'))} kg\n"
                f"  • *Hành vi phản ứng:* {recent.get('behavior_notes')}\n"
                f"  • *Sản phẩm sử dụng:* {recent.get('products_used')}\n"
                f"  • *Ghi chú nhân viên:* {recent.get('staff_notes') or 'Bé hợp tác tốt'}\n"
                f"  • *Lời khuyên dặn dò:* {recent.get('home_care_instructions') or 'Chải lông và giữ khô thoáng da'}\n"
            )
        else:
            recent_records_summary = "- Chưa có dữ liệu ghi nhận lần làm dịch vụ chi tiết nào trước đây."

        markdown_body = (
            f"### 📋 Tóm Tắt Hồ Sơ Chăm Sóc Bé {pet_info.get('name')} ({pet_info.get('breed', 'Chưa rõ')})\n\n"
            f"**1. Thông tin thể trạng cơ bản:**\n"
            f"- **Loài & Giống:** {pet_info.get('species')} - {pet_info.get('breed')}\n"
            f"- **Tuổi:** {pet_info.get('age_months')} tháng tuổi | **Giới tính:** {pet_info.get('gender')}\n"
            f"- **Cân nặng hiện tại:** {pet_info.get('weight_kg')} kg\n"
            f"- **Tiền sử dị ứng & bệnh:** {pet_info.get('allergies', 'Không có')} | {pet_info.get('medical_history', 'Bình thường')}\n\n"
            f"**2. Đánh giá tình trạng lông da & thể chất:**\n"
            f"{recent_records_summary}\n"
            f"**3. Tình trạng phòng bệnh & tiêm chủng:**\n"
            f"- Tổng số mũi tiêm/phòng dịch đã quản lý: {len(vaccine_history)} mũi.\n"
            f"- Trạng thái chung: " + ("Cần bổ sung mũi tiêm quá hạn!" if any(v.get('status') == 'overdue' for v in vaccine_history) else "Đang theo dõi đều đặn.") + "\n\n"
            f"**4. Lời khuyên chăm sóc tại nhà từ AI:**\n"
            f"- Chải lông định kỳ 1-2 lần/ngày để giảm lông vón cục và kích thích lưu thông máu dưới da.\n"
            f"- Vệ sinh tai và khóe mắt bằng nước muối sinh lý ấm chuyên dụng cho thú cưng.\n"
            f"- Đảm bảo chế độ ăn giàu protein, bổ sung omega-3 hoặc dầu cá hồi để lông bóng mượt."
        )

        suggested_actions.append("Đặt lịch Spa tắm dưỡng định kỳ 2 tuần/lần để bảo vệ da lông.")

        return {
            "pet_id": pet_info.get("id"),
            "pet_name": pet_info.get("name"),
            "summary_markdown": markdown_body,
            "health_alerts": health_alerts,
            "suggested_actions": suggested_actions,
            "model_used": model_used
        }

    @classmethod
    def answer_consultation(
        cls,
        question: str,
        pet_info: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[dict]] = None
    ) -> Dict[str, Any]:
        """
        Answers routine pet care questions with mandatory veterinary disclaimers and emergency detection.
        """
        is_emergency = cls.detect_emergency(question)

        # If emergency detected, return immediate high-priority warning
        if is_emergency:
            emergency_answer = (
                f"🚨 **CẢNH BÁO NGUY HIỂM KHẨN CẤP! (EMERGENCY TRIAGE - ƯU TIÊN CẤP 1)**\n\n"
                f"Dựa trên các dấu hiệu bạn vừa mô tả trong câu hỏi (*'{question}'*), "
                f"thú cưng có khả năng đang gặp tình trạng sức khỏe nguy kịch, đe dọa trực tiếp đến tính mạng!\n\n"
                f"⚡ **HÀNH ĐỘNG CẦN THỰC HIỆN NGAY LẬP TỨC:**\n"
                f"1. **ĐƯA BÉ ĐẾN PHÒNG KHÁM HOẶC BỆNH VIỆN THÚ Y GẦN NHẤT NGAY** để được bác sĩ cấp cứu chuyên khoa.\n"
                f"2. KHÔNG tự ý cho bé uống thuốc hạ sốt của người (như Paracetamol/Panadol cực kỳ độc cho chó mèo).\n"
                f"3. Giữ ấm và để bé nằm nghiêng nơi thoáng đãng, yên tĩnh, giữ thẳng đường thở trong lúc di chuyển.\n"
                f"4. 📞 **GỌI NGAY HOTLINE CẤP CỨU 24/7:** **0988.111.222** hoặc **0988.123.456** để bác sĩ chuẩn bị sẵn lồng ấp và thiết bị hồi sức trước khi bạn đưa bé đến!"
            )
            return {
                "answer": emergency_answer,
                "medical_disclaimer": PETCARE_MEDICAL_DISCLAIMER,
                "is_urgent_medical_alert": True,
                "emergency_hotline": "0988.111.222",
                "recommended_topics": ["Hotline Cấp cứu 24/7", "Chỉ đường phòng khám gần nhất", "Kỹ năng sơ cứu trên xe"],
                "model_used": "PetCare-Safety-Guardrail"
            }

        # Contextual prompt for normal questions
        pet_context = ""
        if pet_info:
            pet_context = (
                f"Thông tin thú cưng tham khảo: Bé tên {pet_info.get('name')}, "
                f"loài {pet_info.get('species')}, giống {pet_info.get('breed')}, "
                f"{pet_info.get('age_months')} tháng tuổi, nặng {pet_info.get('weight_kg')} kg.\n"
            )

        prompt = (
            f"{pet_context}"
            f"Khách hàng hỏi: {question}\n\n"
            "Hãy trả lời chi tiết, tận tình, dễ hiểu về kiến thức chăm sóc thú cưng thông thường (vệ sinh, dinh dưỡng, chải chuốt, thói quen). "
            "Nhắc nhở nhẹ nhàng khách hàng đưa bé đi khám nếu triệu chứng kéo dài."
        )

        model_used = "PetCare-RuleHeuristic-Engine"
        llm_result = None
        if settings.GEMINI_API_KEY:
            llm_result = cls.call_gemini_api(prompt)
            if llm_result:
                model_used = "Google-Gemini-1.5-Flash"
        elif settings.OPENAI_API_KEY:
            llm_result = cls.call_openai_api(prompt)
            if llm_result:
                model_used = "OpenAI-GPT-3.5-Turbo"

        if llm_result:
            return {
                "answer": llm_result,
                "medical_disclaimer": PETCARE_MEDICAL_DISCLAIMER,
                "is_urgent_medical_alert": False,
                "recommended_topics": ["Lịch tiêm phòng định kỳ", "Dịch vụ Tắm Spa & Vệ sinh", "Chế độ dinh dưỡng khoa học"],
                "model_used": model_used
            }

        # Knowledge-base heuristic responses for common questions
        q_lower = question.lower()
        if "tắm" in q_lower or "spa" in q_lower:
            answer = (
                "🛁 **Hướng dẫn chăm sóc & tắm cho thú cưng an toàn:**\n\n"
                "1. **Tần suất tắm:**\n"
                "   - Chó: Khoảng 7 - 10 ngày/lần (nếu cún vận động ngoài trời nhiều) hoặc 2 tuần/lần.\n"
                "   - Mèo: Khoảng 3 - 4 tuần/lần vì mèo có tập tính tự liếm láp làm sạch cơ thể.\n"
                "2. **Nước tắm:** Sử dụng nước ấm vừa phải (khoảng 37°C - 38°C), không dùng nước quá lạnh hoặc quá nóng.\n"
                "3. **Sữa tắm:** Bắt buộc dùng sữa tắm chuyên dụng cho thú cưng có độ pH 6.5 - 7.5 cân bằng. Tuyệt đối không dùng dầu gội người vì làm hỏng lớp dầu tự nhiên bảo vệ da.\n"
                "4. **Sấy khô:** Sau khi tắm xong, cần lau ráo bằng khăn vi sợi và sấy thật khô tận chân lông, đặc biệt là vùng nách, kẽ chân và tai để tránh nấm da."
            )
            topics = ["Dịch vụ Spa Thảo Mộc", "Cắt tỉa tạo kiểu lông", "Vệ sinh tai móng"]
        elif "ăn" in q_lower or "dinh dưỡng" in q_lower or "thức ăn" in q_lower:
            answer = (
                "🍖 **Lời khuyên về dinh dưỡng khoa học cho thú cưng:**\n\n"
                "1. **Thức ăn khuyên dùng:**\n"
                "   - Hạt chất lượng cao có nguồn gốc rõ ràng (hàm lượng đạm > 26% cho chó, > 30% cho mèo).\n"
                "   - Bổ sung pate, ức gà luộc xé nhỏ, thịt bò nạc, bí đỏ nghiền và một ít rau củ.\n"
                "2. **CÁC THỰC PHẨM ĐỘC HẠI CẦN TUYỆT ĐỐI TRÁNH:**\n"
                "   - ❌ Socola, cà phê, trà (chứa Theobromine gây ngộ độc tim mạch).\n"
                "   - ❌ Hành, tỏi, hẹ (phá hủy hồng cầu gây thiếu máu tán huyết).\n"
                "   - ❌ Nho tươi, nho khô (gây suy thận cấp tính).\n"
                "   - ❌ Xương gà hoặc xương cá nhỏ nhọn (dễ găm thủng thực quản, dạ dày).\n"
                "3. **Nước uống:** Luôn cung cấp sẵn bát nước lọc sạch và thay nước 2 lần/ngày."
            )
            topics = ["Thức ăn hạt dinh dưỡng", "Thực phẩm cấm kỵ", "Bổ sung canxi và vitamin"]
        elif "tiêm" in q_lower or "vaccine" in q_lower or "chích" in q_lower:
            answer = (
                "💉 **Lịch tiêm phòng khuyến nghị chuẩn thú y:**\n\n"
                "1. **Đối với Chó:**\n"
                "   - Mũi 1 (6-8 tuần tuổi): Vaccine 5 hoặc 7 bệnh (Parvo, Carre, Viêm gan...).\n"
                "   - Mũi 2 & 3 (cách nhau 3-4 tuần): Vaccine 7 bệnh tăng cường kháng thể.\n"
                "   - Từ 12 tuần tuổi: Tiêm vaccine phòng dại (Rabies).\n"
                "   - **Nhắc lại:** Tiêm nhắc lại 1 mũi 7 bệnh và 1 mũi Dại MỖI NĂM MỘT LẦN.\n"
                "2. **Đối với Mèo:**\n"
                "   - Mũi 1 (8 tuần tuổi): Vaccine phòng 3 hoặc 4 bệnh cho mèo (giảm bạch cầu, viêm mũi khí quản, Calici...).\n"
                "   - Mũi 2 (cách 3-4 tuần): Mũi nhắc lại lần 1.\n"
                "   - Sau đó tiêm vaccine phòng dại và tiêm nhắc lại hàng năm."
            )
            topics = ["Đăng ký lịch tiêm", "Tẩy giun định kỳ", "Theo dõi sau tiêm"]
        elif "rụng lông" in q_lower or "lông" in q_lower:
            answer = (
                "✨ **Giải pháp giảm rụng lông và chăm sóc lông bóng mượt:**\n\n"
                "1. **Chải lông mỗi ngày:** Dùng lược chải tơ hoặc găng tay chải lông để loại bỏ lông chết trước khi rụng khắp nhà.\n"
                "2. **Bổ sung Omega-3 & Omega-6:** Thêm dầu cá hồi tinh khiết hoặc viên dầu cá vào bữa ăn giúp nang lông chắc khỏe, da mềm mại.\n"
                "3. **Tránh môi trường quá khô:** Nếu bé nằm điều hòa thường xuyên, da dễ bị khô bong vảy, hãy xịt dưỡng khoáng ẩm thảo mộc.\n"
                "4. **Kiểm tra da:** Nếu thấy bé gãi liên tục, xuất hiện mảng đỏ, vảy gàu hoặc rụng lông từng mảng tròn, đó có thể là dấu hiệu nấm hoặc viêm da - cần khám thú y."
            )
            topics = ["Dưỡng ẩm lông da", "Cắt tỉa gọn gàng", "Kiểm tra ký sinh trùng"]
        else:
            answer = (
                f"Chào bạn! Cảm ơn bạn đã quan tâm đến việc chăm sóc thú cưng yêu quý. 🐾\n\n"
                f"Về câu hỏi: *'{question}'*:\n\n"
                f"- Để thú cưng luôn khỏe mạnh và năng động, điều quan trọng nhất là duy trì lối sống lành mạnh: "
                f"ăn uống cân đối, vận động ít nhất 20-30 phút mỗi ngày, và giữ môi trường sống sạch sẽ thoáng mát.\n"
                f"- Định kỳ đưa bé đến PetCare để tắm spa dưỡng lông, vệ sinh tai móng và kiểm tra cân nặng.\n"
                f"- Theo dõi sát các thói quen hàng ngày (lượng nước uống, màu phân, độ thèm ăn, ánh mắt lanh lợi)."
            )
            topics = ["Đặt lịch chăm sóc", "Tư vấn dinh dưỡng", "Tiêm phòng & Tẩy giun"]

        return {
            "answer": answer,
            "medical_disclaimer": PETCARE_MEDICAL_DISCLAIMER,
            "is_urgent_medical_alert": False,
            "recommended_topics": topics,
            "model_used": model_used
        }
