// PetCare AI Pro - AI Features & Chatbot Module

let chatHistory = [];

function toggleAIChat() {
    const chatWin = document.getElementById('ai-chat-window');
    if (!chatWin) return;
    chatWin.classList.toggle('active');
    if (chatWin.classList.contains('active')) {
        const input = document.getElementById('chat-input-field');
        if (input) {
            setTimeout(() => input.focus(), 150);
        }
        const container = document.getElementById('chat-messages-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
}

function clearAIChatHistory() {
    chatHistory = [];
    const container = document.getElementById('chat-messages-container');
    if (container) {
        container.innerHTML = `
            <div class="chat-bubble ai">
                Xin chào bạn! Tôi là <strong>Bác Sĩ Thú Y AI Sarah (PetCare Pro)</strong> 🐾.
                <br><br>
                Tôi có thể giải đáp chi tiết và chuyên sâu:
                <ul style="margin: 0.4rem 0 0.4rem 1.2rem; padding: 0; list-style-type: disc;">
                    <li>Bảng giá dịch vụ Spa, cắt tỉa, lưu trú khách sạn thú cưng.</li>
                    <li>Chế độ dinh dưỡng, cách nấu pate &amp; các thực phẩm cấm kỵ.</li>
                    <li>Phòng trị ve rận, bọ chét, nấm da, viêm tai &amp; hôi miệng.</li>
                    <li>Lịch tiêm phòng vắc xin 5/7 bệnh, tẩy giun &amp; triệt sản an toàn.</li>
                    <li>Cảnh báo dấu hiệu nguy hiểm và hướng dẫn sơ cứu khẩn cấp 24/7.</li>
                </ul>
                <em>Bạn muốn tìm hiểu hoặc cần tư vấn về vấn đề nào cho bé cưng?</em>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.25rem;">
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Bảng giá dịch vụ spa và cắt tỉa bao nhiêu?')">
                    🏷️ Bảng giá dịch vụ
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Dịch vụ khách sạn gửi thú cưng như thế nào?')">
                    🏨 Khách sạn Pet Hotel
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Bao lâu nên tắm cho cún 1 lần và chọn sữa tắm gì?')">
                    🐶 Bao lâu tắm cún 1 lần?
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Dấu hiệu nhận biết và cách trị nấm da, viêm da')">
                    🔬 Trị nấm &amp; ngứa da
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Cách nhỏ gáy trị ve rận và bọ chét cho chó mèo')">
                    🐛 Trị ve rận &amp; bọ chét
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Thực phẩm nào gây độc hại cho cún mèo?')">
                    🍗 Thực phẩm độc hại cần tránh
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Lịch tiêm phòng vắc xin 7 bệnh cho chó')">
                    💉 Lịch tiêm phòng 7 bệnh
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Bao lâu thì nên tẩy giun cho thú cưng 1 lần?')">
                    💊 Lịch tẩy giun định kỳ
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Cách vệ sinh răng miệng và trị hôi miệng cho cún mèo')">
                    🦷 Trị hôi miệng &amp; vôi răng
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #1e293b; font-weight: 600; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('Cách dạy chó mèo đi vệ sinh đúng chỗ')">
                    🚽 Dạy đi vệ sinh đúng chỗ
                </button>
                <button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.74rem; border-radius: 9999px; background: #fef2f2; border: 1.5px solid #fecaca; color: #dc2626; font-weight: 700; padding: 5px 12px; cursor: pointer;" onclick="sendChatMessage('thú cưng co giật, nôn ra máu')">
                    🚨 Demo Cấp Cứu: thú cưng co giật, nôn ra máu
                </button>
            </div>
        `;
    }
    showToast('Đã làm mới cuộc trò chuyện với Bác Sĩ AI Sarah', 'info');
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendChatMessage();
    }
}

let isAIChatBusy = false;

async function sendChatMessage(customMsg = null) {
    if (isAIChatBusy) return;

    const input = document.getElementById('chat-input-field');
    const sendBtn = document.getElementById('chat-send-btn');
    const msg = customMsg || input?.value.trim();
    if (!msg) return;

    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    // Check for attached photo
    const attachedImg = (typeof currentChatAttachedImage !== 'undefined') ? currentChatAttachedImage : null;
    if (typeof removeChatPhotoAttachment === 'function') {
        removeChatPhotoAttachment();
    }

    // Append User message
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    
    if (attachedImg) {
        userBubble.innerHTML = `
            <div style="margin-bottom: 6px;">
                <img src="${attachedImg}" alt="Ảnh thú cưng gửi bác sĩ" style="max-width: 100%; max-height: 200px; border-radius: 10px; object-fit: cover; border: 2px solid rgba(255,255,255,0.6); box-shadow: 0 4px 10px rgba(0,0,0,0.18);">
            </div>
            <div>${msg.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        `;
    } else {
        userBubble.textContent = msg;
    }
    container.appendChild(userBubble);
    container.scrollTop = container.scrollHeight;

    if (!customMsg && input) input.value = '';

    // Lock UI during response
    isAIChatBusy = true;
    if (sendBtn) sendBtn.disabled = true;

    // Typing indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble ai';
    typingBubble.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #4f46e5; font-weight: 600;">
            <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
            <em>Bác sĩ AI đang xem xét ${attachedImg ? 'hình ảnh & ' : ''}tổng hợp thông tin...</em>
        </div>
    `;
    container.appendChild(typingBubble);
    container.scrollTop = container.scrollHeight;

    try {
        const response = await apiCall('/ai/chat', 'POST', {
            message: msg,
            image_data: attachedImg,
            chat_history: chatHistory
        });

        typingBubble.remove();

        const aiBubble = document.createElement('div');
        aiBubble.className = `chat-bubble ${response.is_emergency ? 'emergency' : 'ai'}`;
        
        let html = '';
        if (response.is_emergency) {
            const hotline = response.emergency_hotline || '0988.111.222';
            html += `
            <div class="emergency-triage-banner">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid rgba(239, 68, 68, 0.35); padding-bottom: 6px;">
                    <div style="font-weight: 800; color: #ef4444; display: flex; align-items: center; gap: 0.4rem; font-size: 0.95rem;">
                        <span style="font-size: 1.3rem;">🚨</span>
                        <span>${response.warning_badge || 'BÁO ĐỘNG ĐỎ: CA CẤP CỨU THÚ Y KHẨN CẤP (EMERGENCY TRIAGE)'}</span>
                    </div>
                    <span style="background: #ef4444; color: #fff; padding: 3px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">Ưu Tiên Cấp 1</span>
                </div>
                <div style="font-size: 0.82rem; color: #991b1b; font-weight: 600; margin-bottom: 8px;">
                    ⚡ Phát hiện dấu hiệu cấp cứu đe dọa tính mạng! Không tự điều trị tại nhà - Hãy đưa bé đến viện thú y ngay.
                </div>
                <div class="emergency-hotline-box">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.5rem;">📞</span>
                        <div>
                            <div style="font-size: 0.7rem; color: #fca5a5; font-weight: 700; text-transform: uppercase;">Hotline Cấp Cứu Thú Y 24/7 Trực Tiếp:</div>
                            <div class="emergency-hotline-num">${hotline}</div>
                        </div>
                    </div>
                    <a href="tel:${hotline.replace(/\./g, '')}" class="emergency-call-btn">
                        <span>GỌI BÁC SĨ CẤP CỨU NGAY</span>
                    </a>
                </div>
            </div>`;
        }
        
        html += `<div style="white-space: pre-line; line-height: 1.6;">${response.reply}</div>`;
        
        if (response.suggested_actions && response.suggested_actions.length > 0) {
            html += `<div style="margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap;">`;
            response.suggested_actions.forEach(action => {
                const safeAction = action.replace(/'/g, "\\'");
                html += `<button type="button" class="btn btn-secondary btn-sm" style="font-size: 0.73rem; padding: 4px 10px; border-radius: 9999px; background: #ffffff; border: 1px solid #cbd5e1; font-weight: 600; cursor: pointer;" onclick="sendChatMessage('${safeAction}')">${action}</button>`;
            });
            html += `</div>`;
        }
        html += `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 0.68rem; color: #64748b; border-top: 1px dashed #e2e8f0; padding-top: 5px; flex-wrap: wrap; gap: 4px;">
                <span>${response.veterinary_disclaimer}</span>
                <span style="font-weight: 700; color: #4f46e5; flex-shrink: 0;">${response.generated_by || 'PetCare AI'}</span>
            </div>
        `;

        aiBubble.innerHTML = html;
        container.appendChild(aiBubble);
        container.scrollTop = container.scrollHeight;

        // Cập nhật huy hiệu Engine thời gian thực trên Header
        if (response.generated_by) {
            const badge = document.getElementById('ai-chat-engine-badge');
            if (badge) {
                if (response.generated_by.includes('Gemini')) {
                    badge.innerHTML = '✨ Gemini 1.5 Flash';
                    badge.style.background = 'linear-gradient(135deg, #4f46e5, #ec4899)';
                } else if (response.generated_by.includes('OpenAI')) {
                    badge.innerHTML = '🤖 GPT-4o-mini';
                    badge.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                } else {
                    badge.innerHTML = '⚡ Smart AI';
                    badge.style.background = 'rgba(255,255,255,0.25)';
                }
            }
        }

        chatHistory.push({ role: 'user', content: msg });
        chatHistory.push({ role: 'assistant', content: response.reply });
    } catch (e) {
        typingBubble.remove();
        const errBubble = document.createElement('div');
        errBubble.className = 'chat-bubble ai';
        errBubble.style.color = '#dc2626';
        errBubble.style.background = '#fef2f2';
        errBubble.style.borderColor = '#fecaca';
        errBubble.innerHTML = `<strong>Lỗi kết nối AI:</strong> ${e.message}`;
        container.appendChild(errBubble);
        container.scrollTop = container.scrollHeight;
    } finally {
        isAIChatBusy = false;
        if (sendBtn) sendBtn.disabled = false;
        if (input) input.focus();
    }
}

// ========== AI STUDIO TAB FUNCTIONS ==========
async function initAIStudio() {
    populateAIStudioAppts();
    populateModalDropdowns();
}

async function populateAIStudioAppts() {
    const select = document.getElementById('ai-reminder-select-appt');
    if (!select) return;

    try {
        const appts = await apiCall('/appointments');
        select.innerHTML = `<option value="">-- Chọn lịch hẹn có sẵn để tự động điền --</option>` + appts.map(a => 
            `<option value="${a.id}" data-pet="${a.pet_name || ''}" data-owner="${a.owner_name || ''}" data-service="${a.service_name || ''}" data-time="${formatDateTime(a.appointment_time)}">
                #${a.id} - ${a.pet_name || 'Bé'} (${a.service_name}) - ${formatDateTime(a.appointment_time)}
            </option>`
        ).join('');
    } catch (e) {
        console.error('Lỗi nạp danh sách lịch hẹn vào AI Studio:', e);
    }
}

function autoFillReminderForm() {
    const select = document.getElementById('ai-reminder-select-appt');
    const selectedOption = select.options[select.selectedIndex];
    if (!selectedOption || !selectedOption.value) return;

    document.getElementById('ai-rem-pet').value = selectedOption.getAttribute('data-pet') || '';
    document.getElementById('ai-rem-owner').value = selectedOption.getAttribute('data-owner') || '';
    document.getElementById('ai-rem-service').value = selectedOption.getAttribute('data-service') || '';
    document.getElementById('ai-rem-time').value = selectedOption.getAttribute('data-time') || '';
}

async function generateAIReminder(remType = 'appointment') {
    let petName = document.getElementById('ai-rem-pet')?.value?.trim();
    let ownerName = document.getElementById('ai-rem-owner')?.value?.trim();
    let serviceName = document.getElementById('ai-rem-service')?.value?.trim();
    let timeVal = document.getElementById('ai-rem-time')?.value?.trim();

    // Tự động điền mẫu demo nếu để trống
    if (!petName) { petName = 'Miu Miu'; const el = document.getElementById('ai-rem-pet'); if (el) el.value = petName; }
    if (!ownerName) { ownerName = 'Nguyễn Thị Thảo'; const el = document.getElementById('ai-rem-owner'); if (el) el.value = ownerName; }
    if (!serviceName) { serviceName = 'Tắm Spa thảo dược & Tỉa lông'; const el = document.getElementById('ai-rem-service'); if (el) el.value = serviceName; }
    if (!timeVal) { timeVal = '09:00 ngày mai'; const el = document.getElementById('ai-rem-time'); if (el) el.value = timeVal; }

    const channelRadios = document.getElementsByName('rem-channel');
    let channel = 'zalo';
    for (const r of channelRadios) {
        if (r.checked) channel = r.value;
    }

    const btn = document.querySelector('button[onclick*="generateAIReminder"]');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AI đang sinh nội dung tin nhắn...';
    }

    try {
        const data = await apiCall('/ai/generate-reminder', 'POST', {
            pet_name: petName,
            owner_name: ownerName,
            service_or_vaccine_name: serviceName,
            scheduled_time: timeVal,
            reminder_type: remType,
            channel: channel
        });

        const resultBox = document.getElementById('ai-reminder-result-box');
        const resultText = document.getElementById('ai-reminder-result-text');

        if (resultBox && resultText) {
            resultBox.style.display = 'block';
            resultText.textContent = data.message;
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        showToast('AI đã tạo tin nhắn nhắc hẹn thành công!', 'success');
    } catch (e) {
        showToast('Lỗi tạo tin nhắn AI: ' + e.message, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
}

function copyReminderText() {
    const text = document.getElementById('ai-reminder-result-text')?.textContent;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Đã sao chép nội dung tin nhắn vào clipboard!', 'success');
    });
}

async function generateAICareSummary() {
    const petSelect = document.getElementById('ai-summary-pet-select');
    let petId = petSelect?.value;
    if (!petId && petSelect && petSelect.options.length > 0) {
        petId = petSelect.options[0].value;
        petSelect.value = petId;
    }
    if (!petId) {
        petId = 1;
    }

    const btn = document.querySelector('button[onclick*="generateAICareSummary"]');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AI đang phân tích toàn bộ hồ sơ...';
    }

    try {
        const summary = await apiCall('/ai/care-summary', 'POST', { pet_id: parseInt(petId) });
        
        const box = document.getElementById('ai-summary-result-box');
        if (!box) return;
        box.style.display = 'block';

        document.getElementById('sum-pet-header').innerHTML = `<i class="fa-solid fa-paw"></i> Báo cáo Hồ sơ Sức khỏe: <strong>${summary.pet_name}</strong> (${summary.pet_species} - ${summary.pet_breed || ''}, ${summary.age_str})`;
        document.getElementById('sum-weight-trend').textContent = summary.weight_trend;
        document.getElementById('sum-health-digest').textContent = summary.health_digest;
        document.getElementById('sum-grooming-highlights').textContent = summary.grooming_highlights;
        document.getElementById('sum-diet-advice').textContent = summary.diet_care_advice;
        document.getElementById('sum-disclaimer').textContent = summary.veterinary_disclaimer;

        const warnBox = document.getElementById('sum-warnings-box');
        const warnText = document.getElementById('sum-warnings-text');
        if (summary.warnings_for_staff && summary.warnings_for_staff.length > 0) {
            warnBox.style.display = 'block';
            warnText.textContent = summary.warnings_for_staff.join(' | ');
        } else {
            warnBox.style.display = 'none';
        }

        box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        showToast(`Đã tổng hợp hồ sơ sức khỏe bé ${summary.pet_name}!`, 'success');
    } catch (e) {
        showToast('Lỗi tóm tắt hồ sơ: ' + e.message, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
}

// Safety Guardrail Test Simulator
function testSafetyPrompt(promptText) {
    const input = document.getElementById('safety-prompt-input');
    if (input) {
        input.value = promptText;
        runSafetyTest();
    }
}

async function runSafetyTest() {
    const input = document.getElementById('safety-prompt-input');
    const msg = input?.value.trim();
    if (!msg) {
        showToast('Vui lòng nhập câu hỏi kiểm thử!', 'error');
        return;
    }

    const resultBox = document.getElementById('safety-test-result');
    if (!resultBox) return;

    resultBox.style.display = 'block';
    resultBox.innerHTML = '<div class="glass-panel" style="padding: 1rem;"><i class="fa-solid fa-spinner fa-spin"></i> Đang chạy phân tích Guardrails AI...</div>';

    try {
        const resp = await apiCall('/ai/chat', 'POST', { message: msg });
        
        let badgeHtml = resp.is_emergency 
            ? `<span class="badge badge-overdue" style="font-size: 0.85rem;"><i class="fa-solid fa-triangle-exclamation"></i> KẾT QUẢ GUARDRAIL: PHÁT HIỆN CẤP CỨU THÚ Y</span>`
            : `<span class="badge badge-confirmed" style="font-size: 0.85rem;"><i class="fa-solid fa-shield-check"></i> KẾT QUẢ GUARDRAIL: AN TOÀN - CÂU HỎI THƯỜNG THỨC</span>`;

        resultBox.innerHTML = `
            <div class="glass-panel" style="padding: 1.25rem; border-color: ${resp.is_emergency ? '#ef4444' : '#10b981'};">
                <div style="margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    ${badgeHtml}
                    <small style="color: var(--text-muted); font-size: 0.78rem; font-weight: 600;"><i class="fa-solid fa-microchip"></i> ${resp.generated_by}</small>
                </div>
                <div class="ai-guardrail-box">
                    ${resp.reply}
                </div>
                <div class="ai-disclaimer-box" style="margin-top: 0.75rem;">
                    <strong>🩺 Veterinary Disclaimer:</strong> ${resp.veterinary_disclaimer}
                </div>
            </div>
        `;
    } catch (e) {
        resultBox.innerHTML = `<div class="glass-panel" style="padding: 1rem; color: var(--danger);">Lỗi: ${e.message}</div>`;
    }
}

// ========== AI SYMPTOM CHECKER FUNCTIONS ==========
let selectedSymptomsList = [];

function toggleSymptomTag(element, tag) {
    element.classList.toggle('active');
    if (element.classList.contains('active')) {
        if (!selectedSymptomsList.includes(tag)) selectedSymptomsList.push(tag);
    } else {
        selectedSymptomsList = selectedSymptomsList.filter(t => t !== tag);
    }
}

async function runSymptomAnalysis() {
    const species = document.getElementById('symptom-species')?.value || 'Chó';
    const breed = document.getElementById('symptom-breed')?.value?.trim();
    const duration = document.getElementById('symptom-duration')?.value || '1-2 ngày';
    const customDesc = document.getElementById('symptom-custom-desc')?.value?.trim();
    const resultBox = document.getElementById('symptom-analysis-result');

    if (selectedSymptomsList.length === 0 && !customDesc) {
        showToast('Vui lòng chọn ít nhất một triệu chứng hoặc nhập mô tả!', 'error');
        return;
    }

    if (!resultBox) return;
    resultBox.style.display = 'block';
    resultBox.innerHTML = `
        <div class="glass-panel" style="padding: 2rem; text-align: center; color: var(--text-muted);">
            <i class="fa-solid fa-spinner fa-spin fa-2x" style="color: #6366f1;"></i>
            <p style="margin-top: 10px; font-weight: 600;">AI đang đối soát cơ sở tri thức thú y và phân tích triệu chứng...</p>
        </div>
    `;

    try {
        const payload = {
            species,
            breed: breed || null,
            symptoms: selectedSymptomsList,
            symptom_description: customDesc,
            duration
        };

        const res = await apiCall('/ai/symptom-checker', 'POST', payload);
        renderSymptomAnalysisResult(res);
        showToast('Đã hoàn tất phân tích triệu chứng!', 'success');
    } catch (e) {
        resultBox.innerHTML = `<div class="glass-panel" style="padding: 1.5rem; color: var(--danger);">Lỗi phân tích: ${e.message}</div>`;
    }
}

function renderSymptomAnalysisResult(data) {
    const resultBox = document.getElementById('symptom-analysis-result');
    if (!resultBox) return;

    let borderCol = '#10b981';
    let badgeClass = 'badge-risk-green';

    if (data.risk_color === 'red') {
        borderCol = '#ef4444';
        badgeClass = 'badge-risk-red';
    } else if (data.risk_color === 'orange') {
        borderCol = '#f97316';
        badgeClass = 'badge-risk-orange';
    } else if (data.risk_color === 'yellow') {
        borderCol = '#eab308';
        badgeClass = 'badge-risk-yellow';
    }

    resultBox.innerHTML = `
        <div class="glass-panel" style="padding: 1.75rem; border: 2px solid ${borderCol}; border-radius: var(--radius-lg);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.1rem; flex-wrap: wrap; gap: 8px;">
                <span class="badge ${badgeClass}" style="font-size: 0.9rem; padding: 6px 14px;">
                    ${data.risk_label}
                </span>
                <small style="color: var(--text-muted); font-size: 0.78rem; font-weight: 600;"><i class="fa-solid fa-microchip"></i> ${data.generated_by}</small>
            </div>

            <div class="ai-result-summary">
                ${data.summary}
            </div>

            <!-- Potential Causes & First Aid Grid -->
            <div class="charts-grid" style="margin-bottom: 1.25rem;">
                <div class="ai-causes-card">
                    <h5 class="ai-causes-title"><i class="fa-solid fa-magnifying-glass"></i> Nguyên nhân tiềm ẩn:</h5>
                    <ul class="ai-causes-list">
                        ${data.potential_causes.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                </div>

                <div class="ai-firstaid-card">
                    <h5 class="ai-firstaid-title"><i class="fa-solid fa-hand-holding-medical"></i> Hướng dẫn sơ cứu &amp; Chăm sóc:</h5>
                    <ul class="ai-firstaid-list">
                        ${data.first_aid_and_care.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                </div>
            </div>

            <!-- Recommended Services -->
            ${data.recommended_services.length > 0 ? `
            <div style="margin-bottom: 1.25rem;">
                <h5 class="ai-section-subtitle"><i class="fa-solid fa-sparkles"></i> Dịch vụ &amp; Liệu trình đề xuất:</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 0.75rem;">
                    ${data.recommended_services.map(s => `
                        <div class="ai-service-item">
                            <div>
                                <div class="ai-service-name">${s.name}</div>
                                <div class="ai-service-reason">${s.reason}</div>
                                <div class="ai-service-price">${(s.estimated_price || 0).toLocaleString()} ₫</div>
                            </div>
                            <button class="btn btn-primary btn-sm" style="margin-top: 10px; justify-content: center; width: 100%;" onclick="bookRecommendedService('${s.name}')">
                                <i class="fa-solid fa-calendar-check"></i> Đặt Lịch Dịch Vụ Này
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}

            <!-- Disclaimer -->
            <div class="ai-disclaimer-box">
                ${data.veterinary_disclaimer}
            </div>
        </div>
    `;
}

function bookRecommendedService(serviceName) {
    const role = State.currentUser ? State.currentUser.role : 'CUSTOMER';
    if (role === 'CUSTOMER') {
        selectServiceToBook(serviceName);
    } else {
        switchTab('appointments');
        openBookingModal();
        // Pre-select service in admin/staff booking modal
        setTimeout(() => {
            const serviceSelect = document.getElementById('modal-book-service');
            if (serviceSelect) {
                for (let i = 0; i < serviceSelect.options.length; i++) {
                    if (serviceSelect.options[i].text.toLowerCase().includes(serviceName.toLowerCase()) || serviceName.toLowerCase().includes(serviceSelect.options[i].text.toLowerCase())) {
                        serviceSelect.selectedIndex = i;
                        break;
                    }
                }
            }
        }, 200);
    }
}

// ========== AI ENGINE CONFIG MODAL ==========
async function openAIConfigModal() {
    openModal('modal-ai-config');
    await loadAIConfig();
}

async function loadAIConfig() {
    try {
        const cfg = await apiCall('/ai/config', 'GET');
        const providerSel = document.getElementById('ai-cfg-provider');
        const geminiInput = document.getElementById('ai-cfg-gemini-key');
        if (providerSel && cfg.current_provider) {
            providerSel.value = cfg.current_provider;
        }
        if (geminiInput) {
            if (cfg.has_gemini_key) {
                geminiInput.placeholder = `Đã lưu key (${cfg.gemini_api_key_masked || '***'}). Nhập key mới nếu muốn đổi.`;
            } else {
                geminiInput.placeholder = 'Dán Gemini API Key (bắt đầu bằng AIzaSy...)';
            }
        }
        
        // Sync badge
        const badge = document.getElementById('ai-chat-engine-badge');
        if (badge && cfg.current_provider) {
            if (cfg.current_provider === 'gemini') {
                badge.innerHTML = '✨ Gemini 1.5 Flash';
                badge.style.background = 'linear-gradient(135deg, #4f46e5, #ec4899)';
            } else if (cfg.current_provider === 'openai') {
                badge.innerHTML = '🤖 GPT-4o-mini';
                badge.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            } else {
                badge.innerHTML = '⚡ Smart AI';
                badge.style.background = 'rgba(255,255,255,0.25)';
            }
        }
        handleAIProviderChange();
    } catch (e) {
        console.warn('Không thể nạp cấu hình AI:', e);
    }
}

function handleAIProviderChange() {
    const sel = document.getElementById('ai-cfg-provider');
    const geminiGroup = document.getElementById('ai-gemini-key-group');
    if (!sel || !geminiGroup) return;
    // Always keep visible so user can see and configure
    geminiGroup.style.display = 'block';
}

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const eye = document.getElementById(`${inputId}-eye`);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (eye) eye.className = 'fa-regular fa-eye-slash';
    } else {
        input.type = 'password';
        if (eye) eye.className = 'fa-regular fa-eye';
    }
}

async function saveAIConfig() {
    const provider = document.getElementById('ai-cfg-provider')?.value || 'offline';
    const geminiKey = document.getElementById('ai-cfg-gemini-key')?.value.trim();
    
    try {
        const payload = { provider: provider };
        if (geminiKey) {
            payload.gemini_api_key = geminiKey;
        }
        const res = await apiCall('/ai/config', 'POST', payload);
        showToast(res.message || 'Cập nhật cấu hình AI Engine thành công!', 'success');
        closeModal('modal-ai-config');
        
        // Update chat window engine badge
        const badge = document.getElementById('ai-chat-engine-badge');
        if (badge) {
            if (provider === 'gemini') {
                badge.innerHTML = '✨ Gemini 1.5 Flash';
                badge.style.background = 'linear-gradient(135deg, #4f46e5, #ec4899)';
            } else if (provider === 'openai') {
                badge.innerHTML = '🤖 GPT-4o-mini';
                badge.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            } else {
                badge.innerHTML = '⚡ Smart AI';
                badge.style.background = 'rgba(255,255,255,0.25)';
            }
        }
    } catch (e) {
        showToast('Lỗi lưu cấu hình: ' + e.message, 'error');
    }
}

// Tự động kiểm tra cấu hình AI khi trang tải
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(loadAIConfig, 1000);
});

