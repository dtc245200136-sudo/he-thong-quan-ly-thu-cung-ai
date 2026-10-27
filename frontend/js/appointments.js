// PetCare AI Pro - Appointments Module

async function loadAppointments() {
    const tbody = document.getElementById('all-appointments-tbody');
    if (!tbody) return;

    const dateFilter = document.getElementById('filter-appt-date')?.value;
    const statusFilter = document.getElementById('filter-appt-status')?.value;

    let url = '/appointments?';
    if (dateFilter) url += `date_str=${dateFilter}&`;
    if (statusFilter) url += `status_filter=${statusFilter}&`;

    try {
        const appts = await apiCall(url);
        
        if (appts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 2.5rem;">Không tìm thấy lịch hẹn nào phù hợp bộ lọc.</td></tr>`;
            return;
        }

        tbody.innerHTML = appts.map(a => `
            <tr>
                <td>
                    <strong>#${a.id}</strong><br>
                    <small style="color: var(--text-muted);">${formatDateTime(a.appointment_time)}</small>
                </td>
                <td>
                    <strong>${a.pet_name || 'Bé'}</strong> <span class="badge" style="font-size: 0.65rem;">${a.pet_species || ''}</span>
                </td>
                <td>
                    ${a.owner_name || 'Khách'}<br>
                    <small style="color: var(--text-muted);"><i class="fa-solid fa-phone"></i> ${a.owner_phone || ''}</small>
                </td>
                <td>
                    <span style="color: #818cf8; font-weight: 600;">${a.service_name}</span><br>
                    <small>${formatCurrency(a.service_price)}</small>
                </td>
                <td>
                    <span class="badge" style="background: rgba(255,255,255,0.06);">${a.staff_name || 'Chưa xếp'}</span>
                </td>
                <td>
                    ${getStatusBadge(a.status)}
                </td>
                <td>
                    <small style="color: var(--text-muted); font-style: italic;">${a.notes || 'Không có ghi chú'}</small>
                </td>
                <td style="min-width: 220px;">
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
                        ${renderAppointmentActions(a)}
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger);">Lỗi tải danh sách lịch hẹn: ${e.message}</td></tr>`;
    }
}

function renderAppointmentActions(a) {
    const jsonA = JSON.stringify(a).replace(/"/g, '&quot;');
    let html = '';

    // 1. Nút nghiệp vụ chính theo luồng
    if (a.status === 'PENDING') {
        html += `
            <button class="btn btn-primary btn-sm" onclick="updateApptStatus(${a.id}, 'CONFIRMED')" title="Duyệt lịch hẹn này">
                <i class="fa-solid fa-check"></i> Duyệt
            </button>
        `;
    } else if (a.status === 'CONFIRMED') {
        html += `
            <button class="btn btn-success btn-sm" onclick="updateApptStatus(${a.id}, 'IN_PROGRESS')" title="Bắt đầu thực hiện dịch vụ">
                <i class="fa-solid fa-play"></i> Bắt đầu
            </button>
        `;
    } else if (a.status === 'IN_PROGRESS') {
        html += `
            <button class="btn btn-success btn-sm" onclick="quickCompleteAppt(${a.id})" title="Hoàn thành & Lập hóa đơn tính tiền">
                <i class="fa-solid fa-check-double"></i> Hoàn thành
            </button>
        `;
    } else if (a.status === 'COMPLETED') {
        html += `
            <button class="btn btn-secondary btn-sm" onclick="switchTab('invoices')" title="Xem hóa đơn thanh toán">
                <i class="fa-solid fa-receipt"></i> Hóa đơn
            </button>
        `;
    }

    // 2. Nút Icon Dấu X (Hủy nhanh lịch hẹn)
    if (a.status !== 'COMPLETED' && a.status !== 'CANCELLED') {
        html += `
            <button class="btn-icon btn-danger-icon" onclick="cancelAppt(${a.id})" title="Hủy lịch hẹn">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;
    }

    // 3. Nút Icon Dấu ... (Menu tùy chọn mở rộng)
    html += `
        <div class="dropdown-action-wrapper" style="position: relative; display: inline-block;">
            <button class="btn-icon btn-more-icon" onclick="toggleApptMenu(event, ${a.id})" title="Thao tác khác (...)">
                <i class="fa-solid fa-ellipsis"></i>
            </button>
            <div id="appt-menu-${a.id}" class="appt-dropdown-menu" style="display: none;">
                ${a.status !== 'CANCELLED' ? `
                    <button class="appt-dropdown-item" onclick="triggerAIReminderForAppt(${jsonA})">
                        <i class="fa-solid fa-paper-plane" style="color: #6366f1;"></i> Gửi tin nhắc hẹn
                    </button>
                ` : ''}
                ${a.status === 'CANCELLED' ? `
                    <button class="appt-dropdown-item" onclick="updateApptStatus(${a.id}, 'CONFIRMED')">
                        <i class="fa-solid fa-rotate-left" style="color: #6366f1;"></i> Khôi phục lịch
                    </button>
                ` : ''}
                <button class="appt-dropdown-item" onclick="switchTab('care')">
                    <i class="fa-solid fa-notes-medical" style="color: #06b6d4;"></i> Hồ sơ chăm sóc
                </button>
                <button class="appt-dropdown-item" onclick="switchTab('invoices')">
                    <i class="fa-solid fa-receipt" style="color: #f59e0b;"></i> Hóa đơn thanh toán
                </button>
                <button class="appt-dropdown-item text-danger" onclick="deleteAppt(${a.id})">
                    <i class="fa-solid fa-trash"></i> Xóa lịch hẹn
                </button>
            </div>
        </div>
    `;

    return html;
}

function toggleApptMenu(e, id) {
    if (e) e.stopPropagation();
    const menu = document.getElementById(`appt-menu-${id}`);
    if (!menu) return;
    const isHidden = menu.style.display === 'none' || !menu.style.display;
    document.querySelectorAll('.appt-dropdown-menu').forEach(m => m.style.display = 'none');
    if (isHidden) {
        menu.style.display = 'flex';
    }
}

// Bấm ra ngoài đóng tất cả menu ...
document.addEventListener('click', () => {
    document.querySelectorAll('.appt-dropdown-menu').forEach(m => m.style.display = 'none');
});

function openBookingModal() {
    const timeInput = document.getElementById('modal-book-time');
    if (timeInput) {
        // Default to next hour
        const nextHour = new Date();
        nextHour.setHours(nextHour.getHours() + 1, 0, 0, 0);
        timeInput.value = new Date(nextHour.getTime() - nextHour.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    const alertBox = document.getElementById('booking-conflict-alert');
    if (alertBox) alertBox.style.display = 'none';

    openModal('modal-booking');
}

async function submitBooking() {
    const petId = document.getElementById('modal-book-pet')?.value;
    const serviceId = document.getElementById('modal-book-service')?.value;
    const timeVal = document.getElementById('modal-book-time')?.value;
    const staffId = document.getElementById('modal-book-staff')?.value;
    const notes = document.getElementById('modal-book-notes')?.value;

    const alertBox = document.getElementById('booking-conflict-alert');

    if (!petId || !serviceId || !timeVal) {
        showToast('Vui lòng chọn thú cưng, dịch vụ và thời gian hẹn!', 'error');
        return;
    }

    try {
        const payload = {
            pet_id: parseInt(petId),
            service_id: parseInt(serviceId),
            staff_id: staffId ? parseInt(staffId) : null,
            appointment_time: new Date(timeVal).toISOString(),
            notes: notes || null
        };

        const newAppt = await apiCall('/appointments', 'POST', payload);
        closeModal('modal-booking');
        showToast(`Đặt lịch hẹn thành công cho bé ${newAppt.pet_name}!`, 'success');
        
        loadAppointments();
        loadDashboard();
    } catch (err) {
        if (alertBox) {
            alertBox.style.display = 'block';
            alertBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <strong>CẢNH BÁO TRÙNG LỊCH:</strong><br>${err.message}`;
        }
        showToast(err.message, 'error');
    }
}

async function updateApptStatus(apptId, newStatus) {
    try {
        await apiCall(`/appointments/${apptId}`, 'PUT', { status: newStatus });
        showToast(`Đã chuyển trạng thái lịch hẹn #${apptId} sang ${newStatus}!`, 'success');
        loadAppointments();
        loadDashboard();
    } catch (e) {
        showToast('Lỗi cập nhật: ' + e.message, 'error');
    }
}

async function cancelAppt(apptId) {
    if (!confirm('Bạn có chắc chắn muốn hủy lịch hẹn này?')) return;
    try {
        await apiCall(`/appointments/${apptId}/cancel`, 'POST');
        showToast(`Đã hủy lịch hẹn #${apptId}`, 'info');
        loadAppointments();
        loadDashboard();
    } catch (e) {
        showToast('Lỗi hủy lịch: ' + e.message, 'error');
    }
}

async function deleteAppt(apptId) {
    if (!confirm(`Bạn có chắc chắn muốn xóa vĩnh viễn lịch hẹn #${apptId} không?\nThao tác này không thể hoàn tác!`)) return;
    try {
        await apiCall(`/appointments/${apptId}`, 'DELETE');
        showToast(`Đã xóa vĩnh viễn lịch hẹn #${apptId}`, 'success');
        loadAppointments();
        loadDashboard();
    } catch (e) {
        showToast('Lỗi xóa lịch hẹn: ' + e.message, 'error');
    }
}

async function quickCompleteAppt(apptId) {
    try {
        // Tự động tạo hóa đơn và đánh dấu hoàn thành
        const inv = await apiCall(`/invoices/from-appointment/${apptId}`, 'POST');
        showToast(`Đã tạo hóa đơn ${inv.invoice_code} và hoàn thành lịch hẹn!`, 'success');
        
        loadAppointments();
        loadDashboard();
        loadInvoices();
    } catch (e) {
        showToast('Lỗi thu tiền: ' + e.message, 'error');
    }
}

function triggerAIReminderForAppt(appt) {
    switchTab('ai_studio');
    
    // Auto-fill into AI Studio
    setTimeout(() => {
        const petInput = document.getElementById('ai-rem-pet');
        const ownerInput = document.getElementById('ai-rem-owner');
        const serviceInput = document.getElementById('ai-rem-service');
        const timeInput = document.getElementById('ai-rem-time');

        if (petInput) petInput.value = appt.pet_name || '';
        if (ownerInput) ownerInput.value = appt.owner_name || '';
        if (serviceInput) serviceInput.value = appt.service_name || '';
        if (timeInput) timeInput.value = formatDateTime(appt.appointment_time);

        generateAIReminder();
    }, 150);
}
