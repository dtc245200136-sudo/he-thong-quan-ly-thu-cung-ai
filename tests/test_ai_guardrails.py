import pytest
from backend.services.ai_service import AIService, detect_emergency_symptoms, VETERINARY_DISCLAIMER

def test_detect_emergency_symptoms_positive():
    dangerous_inputs = [
        "Chó nhà tôi bị co giật và sùi bọt mép phải làm sao?",
        "Mèo ăn nhầm bả chuột, đang nôn ra máu!",
        "Cún bị tai nạn xe gãy xương chảy máu không cầm được",
        "Mèo đực bị bí tiểu rặn ra máu kêu khóc suốt đêm"
    ]
    for inp in dangerous_inputs:
        is_emergency, level, flags = detect_emergency_symptoms(inp)
        assert is_emergency is True, f"Thất bại trong việc phát hiện nguy hiểm: {inp}"
        assert level == "CRITICAL_VET_REQUIRED"
        assert len(flags) > 0

def test_detect_emergency_symptoms_negative():
    safe_inputs = [
        "Bao lâu nên tắm cho cún Poodle một lần?",
        "Lông mèo bị rụng nhiều vào mùa hè thì bổ sung chất gì?",
        "Lịch tiêm phòng 7 bệnh cho chó con như thế nào?",
        "Cách vệ sinh tai và cắt móng cho cún tại nhà"
    ]
    for inp in safe_inputs:
        is_emergency, level, flags = detect_emergency_symptoms(inp)
        assert is_emergency is False, f"Báo động giả với câu hỏi an toàn: {inp}"
        assert level == "NONE"

def test_ai_chat_guardrail_emergency_response():
    resp = AIService.chat_with_assistant("Chó nhà em uống nhầm thuốc tẩy và đang co giật!")
    assert resp["is_emergency"] is True
    assert "CẢNH BÁO NGUY HIỂM CẤP CỨU THÚ Y" in resp["reply"]
    assert "Bác sĩ Thú y" in resp["reply"]
    assert resp["veterinary_disclaimer"] == VETERINARY_DISCLAIMER

def test_ai_chat_safe_response_has_disclaimer():
    resp = AIService.chat_with_assistant("Nên cho mèo ăn thức ăn gì để đẹp lông?")
    assert resp["is_emergency"] is False
    assert len(resp["reply"]) > 20
    assert "KHÔNG thay thế cho chẩn đoán" in resp["veterinary_disclaimer"]


def test_ai_chat_broad_questions():
    test_cases = [
        ("Bảng giá dịch vụ spa và cắt tỉa bao nhiêu?", "BẢNG GIÁ DỊCH VỤ"),
        ("Khách sạn gửi thú cưng như thế nào?", "KHÁCH SẠN THÚ CƯNG"),
        ("Bé bị nấm da và ngứa gãi nhiều trị sao?", "DA LIỄU"),
        ("Làm sao diệt sạch ve rận bọ chét cho cún?", "VE RẬN"),
        ("Chó bị tiêu chảy và nôn dịch vàng nên cho ăn gì?", "TIÊU HÓA"),
        ("Mấy tháng thì nên triệt sản cho mèo?", "TRIỆT SẢN"),
        ("Làm sao để dạy cún đi vệ sinh đúng chỗ?", "VỆ SINH"),
        ("Chó bị ong đốt sưng mặt xử lý sao?", "SƠ CỨU"),
        ("Phòng khám mở cửa lúc mấy giờ?", "THÔNG TIN LIÊN HỆ"),
        ("Bao lâu thì nên tẩy giun một lần?", "TẨY GIUN SÁN"),
        ("Làm sao trị hôi miệng cho mèo?", "RĂNG MIỆNG"),
    ]
    for q, expected_keyword in test_cases:
        res = AIService.chat_with_assistant(q)
        assert res["is_emergency"] is False
        assert len(res["reply"]) > 50
        assert expected_keyword in res["reply"]
        assert len(res["suggested_actions"]) > 0

def test_ai_reminder_generation():
    rem = AIService.generate_reminder(
        pet_name="Miu Miu",
        owner_name="Chị Mai",
        service_or_vaccine_name="Cắt tỉa lông tròn Hàn Quốc",
        scheduled_time="09:00 ngày 25/08/2026",
        channel="zalo"
    )
    assert "Miu Miu" in rem["message"]
    assert "09:00" in rem["message"]
    assert len(rem["preparation_tips"]) > 0

def test_ai_chat_specific_non_templated_responses():
    # 1. Sữa chua: phải trả lời trực tiếp về sữa chua, men probiotics, xylitol
    res_sc = AIService.chat_with_assistant("Chó ăn sữa chua được không?")
    assert "SỮA CHUA" in res_sc["reply"]
    assert "Xylitol" in res_sc["reply"]
    assert "Probiotics" in res_sc["reply"]
    
    # 2. Cắt móng chảy máu: phải trả lời bột cầm máu Quick Stop / tinh bột
    res_cm = AIService.chat_with_assistant("Cắt móng cho cún bị chảy máu thì làm sao?")
    assert "Quick Stop" in res_cm["reply"] or "bột bắp" in res_cm["reply"]
    assert "30" in res_cm["reply"]
    
    # 3. Chó con 2 tháng tắm: khuyến cáo không tắm ướt, dùng bọt tắm khô
    res_tam = AIService.chat_with_assistant("Chó con 2 tháng tuổi tắm được chưa?")
    assert "KHÔNG NÊN TẮM NƯỚC" in res_tam["reply"]
    assert "bọt tắm khô" in res_tam["reply"].lower() or "tắm khô" in res_tam["reply"].lower()

def test_ai_chat_multiturn_followup():
    # Cuộc hội thoại trước đó nói về nấm da
    history = [
        {"role": "user", "content": "Mèo nhà em bị nấm da vảy gàu ngứa nhiều"},
        {"role": "assistant", "content": "Bé bị nấm da Microsporum canis, cần bôi thuốc và đeo loa chống liếm..."}
    ]
    # Câu hỏi tiếp nối ngắn gọn không lặp lại từ 'nấm'
    res_fu = AIService.chat_with_assistant("Bôi mấy lần một ngày?", chat_history=history)
    assert "2 lần/ngày" in res_fu["reply"]
    assert "nấm" in res_fu["reply"].lower()
    
    # Câu hỏi lây sang người
    res_lay = AIService.chat_with_assistant("Có lây sang người không?", chat_history=history)
    assert "LÂY SANG NGƯỜI" in res_lay["reply"]
    assert "lác đồng tiền" in res_lay["reply"]
