// PetCare AI Pro - Care Records & Vaccinations Module

async function loadCareRecords() {
    const tbody = document.getElementById('care-records-tbody');
    if (!tbody) return;

    const petId = document.getElementById('care-filter-pet')?.value;
    let url = '/care-records?';
    if (petId) url += `pet_id=${petId}&`;

    try {
        const records = await apiCall(url);
        
        if (records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 2.5rem;">Chưa có nhật ký chăm sóc nào.</td></tr>`;
            return;
        }

        tbody.innerHTML = records.map(r => `
            <tr>
                <td><strong>${formatDateTime(r.record_date)}</strong></td>
                <td>
                    <strong>${r.pet_name || 'Bé'}</strong> (${r.pet_species || ''})<br>
                    <small style="color: var(--text-muted);">${r.pet_breed || ''}</small>
                </td>
                <td><strong style="color: #38bdf8;">${r.weight_kg ? r.weight_kg + ' kg' : '-'}</strong></td>
                <td><span style="font-size: 0.85rem;">${r.coat_skin_condition || 'Bình thường'}</span></td>
                <td><span style="font-size: 0.85rem;">${r.ears_eyes_teeth || 'Sạch sẽ'}</span></td>
                <td><span class="badge" style="background: rgba(16,185,129,0.15); color: #34d399;">${r.behavior_mood || 'Ngoan'}</span></td>
                <td>
                    <span style="color: #818cf8; font-weight: 500;">${r.services_performed || ''}</span><br>
                    <small style="color: var(--text-muted); font-style: italic;">${r.notes || ''}</small>
                </td>
                <td><small style="color: var(--text-muted);">${r.staff_name || 'KTV'}</small></td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger);">Lỗi tải hồ sơ chăm sóc: ${e.message}</td></tr>`;
    }
}

function openAddCareRecordModal() {
    populateModalDropdowns();
    openModal('modal-add-care');
}

async function submitAddCareRecord() {
    const petId = document.getElementById('modal-care-pet')?.value;
    const weight = document.getElementById('modal-care-weight')?.value;
    const skin = document.getElementById('modal-care-skin')?.value;
    const ears = document.getElementById('modal-care-ears')?.value;
    const mood = document.getElementById('modal-care-mood')?.value;
    const notes = document.getElementById('modal-care-notes')?.value;

    if (!petId) {
        showToast('Vui lòng chọn thú cưng!', 'error');
        return;
    }

    try {
        const payload = {
            pet_id: parseInt(petId),
            weight_kg: weight ? parseFloat(weight) : null,
            coat_skin_condition: skin || null,
            ears_eyes_teeth: ears || null,
            behavior_mood: mood || null,
            services_performed: notes || null,
            notes: notes || null
        };

        await apiCall('/care-records', 'POST', payload);
        closeModal('modal-add-care');
        showToast('Đã lưu nhật ký buổi chăm sóc thành công!', 'success');
        
        loadCareRecords();
    } catch (e) {
        showToast('Lỗi lưu hồ sơ: ' + e.message, 'error');
    }
}

// ========== VACCINATIONS SECTION ==========
async function loadVaccinations() {
    const tbody = document.getElementById('vaccinations-tbody');
    if (!tbody) return;

    const statusFilter = document.getElementById('vaccine-filter-status')?.value;
    let url = '/vaccinations?';
    if (statusFilter) url += `status=${statusFilter}&`;

    try {
        const vaccs = await apiCall(url);

        if (vaccs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 2.5rem;">Không có mũi tiêm phòng nào phù hợp bộ lọc.</td></tr>`;
            return;
        }

        tbody.innerHTML = vaccs.map(v => `
            <tr>
                <td><strong>🐾 ${v.pet_name || 'Bé'}</strong></td>
                <td>${v.owner_name || 'Khách'}<br><small style="color: var(--text-muted);">${v.owner_phone || ''}</small></td>
                <td><strong style="color: #ec4899;">${v.vaccine_name}</strong></td>
                <td>${v.administered_date || 'Chưa tiêm'}</td>
                <td><strong style="color: ${v.status === 'OVERDUE' ? '#ef4444' : '#38bdf8'};">${v.next_due_date}</strong></td>
                <td>${getVaccineBadge(v.status)}</td>
                <td><small style="color: var(--text-muted);">${v.notes || ''}</small></td>
                <td>
                    <button class="btn btn-ai btn-sm" onclick="triggerAIVaccineReminder(${JSON.stringify(v).replace(/"/g, '&quot;')})">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> Nhắc Tiêm
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger);">Lỗi tải sổ tiêm phòng: ${e.message}</td></tr>`;
    }
}

function getVaccineBadge(status) {
    if (status === 'OVERDUE') return '<span class="badge badge-overdue"><i class="fa-solid fa-triangle-exclamation"></i> QUÁ HẠN TIÊM</span>';
    if (status === 'COMPLETED') return '<span class="badge badge-completed"><i class="fa-solid fa-check-double"></i> Đã tiêm</span>';
    return '<span class="badge badge-pending"><i class="fa-solid fa-clock"></i> Sắp đến hạn</span>';
}

function openAddVaccineModal() {
    populateModalDropdowns();
    const today = new Date().toISOString().split('T')[0];
    const dueInput = document.getElementById('modal-vac-due');
    if (dueInput) dueInput.value = today;

    openModal('modal-add-vaccine');
}

async function submitAddVaccine() {
    const petId = document.getElementById('modal-vac-pet')?.value;
    const name = document.getElementById('modal-vac-name')?.value;
    const adminDate = document.getElementById('modal-vac-administered')?.value;
    const dueDate = document.getElementById('modal-vac-due')?.value;
    const notes = document.getElementById('modal-vac-notes')?.value;

    if (!petId || !name || !dueDate) {
        showToast('Vui lòng điền đủ thông tin thú cưng, tên vaccine và ngày hẹn tiêm nhắc!', 'error');
        return;
    }

    try {
        const payload = {
            pet_id: parseInt(petId),
            vaccine_name: name,
            administered_date: adminDate || null,
            next_due_date: dueDate,
            notes: notes || null,
            status: adminDate ? 'COMPLETED' : 'SCHEDULED'
        };

        await apiCall('/vaccinations', 'POST', payload);
        closeModal('modal-add-vaccine');
        showToast('Đã lưu lịch tiêm phòng thành công!', 'success');
        
        loadVaccinations();
    } catch (e) {
        showToast('Lỗi lưu lịch tiêm: ' + e.message, 'error');
    }
}

function triggerAIVaccineReminder(v) {
    switchTab('ai_studio');
    setTimeout(() => {
        const petInput = document.getElementById('ai-rem-pet');
        const ownerInput = document.getElementById('ai-rem-owner');
        const serviceInput = document.getElementById('ai-rem-service');
        const timeInput = document.getElementById('ai-rem-time');

        if (petInput) petInput.value = v.pet_name || '';
        if (ownerInput) ownerInput.value = v.owner_name || '';
        if (serviceInput) serviceInput.value = `Tiêm nhắc lại: ${v.vaccine_name}`;
        if (timeInput) timeInput.value = `Ngày ${v.next_due_date}`;

        generateAIReminder('vaccine');
    }, 150);
}
