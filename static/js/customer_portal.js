// PetCare AI Pro - Customer Portal & Online Booking Module

async function lookupCustomerByPhone(presetPhone = null, silent = false) {
    const input = document.getElementById('customer-lookup-phone');
    const phone = (presetPhone || input?.value || '').trim();

    if (!phone) {
        if (!silent) showToast('Vui lòng nhập số điện thoại để tra cứu!', 'error');
        return;
    }

    if (input) input.value = phone;

    const resultContainer = document.getElementById('customer-portal-results');
    const emptyState = document.getElementById('customer-portal-empty');
    if (!resultContainer) return;

    try {
        resultContainer.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #818cf8;">
                <i class="fa-solid fa-circle-notch fa-spin fa-3x" style="color: #6366f1;"></i>
                <p style="margin-top: 14px; font-size: 1rem; font-weight: 600;">Đang tra cứu hồ sơ & thẻ thành viên điện tử...</p>
            </div>`;
        resultContainer.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

        const data = await apiCall(`/customer/lookup?phone=${encodeURIComponent(phone)}`);
        renderCustomerPortalData(data);
        if (!silent) {
            showToast(`Tra cứu thành công: Khách hàng ${data.owner.full_name}`, 'success');
        }
    } catch (e) {
        resultContainer.innerHTML = `
            <div class="glass-panel" style="text-align: center; padding: 3.5rem 2rem; border: 1px dashed rgba(244, 63, 94, 0.5); background: rgba(244, 63, 94, 0.05);">
                <div style="width: 72px; height: 72px; background: rgba(244, 63, 94, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.25rem auto; color: #fb7185; font-size: 2rem;">
                    <i class="fa-solid fa-user-xmark"></i>
                </div>
                <h3 style="color: #fb7185; margin-bottom: 0.5rem; font-size: 1.3rem;">Chưa có hồ sơ với SĐT: ${phone}</h3>
                <p style="color: var(--text-muted); font-size: 0.92rem; max-width: 500px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
                    Số điện thoại này chưa đăng ký tại hệ thống. Quý khách có thể sử dụng biểu mẫu đặt lịch trực tuyến bên dưới để nhận ngay ưu đãi thành viên mới!
                </p>
                <button class="btn btn-primary" onclick="scrollToBookingForm('${phone}')">
                    <i class="fa-solid fa-calendar-plus"></i> Đặt Lịch Hẹn Trực Tuyến Ngay
                </button>
            </div>
        `;
    }
}

function renderCustomerPortalData(data) {
    const container = document.getElementById('customer-portal-results');
    if (!container) return;

    const owner = data.owner;
    const loyalty = owner.loyalty;
    const pets = data.pets || [];
    const appts = data.appointments || [];
    const vacs = data.vaccinations || [];
    const cares = data.care_records || [];

    // Loyalty Tier Color & Icon
    let tierColor = '#cbd5e1';
    let tierIcon = 'fa-medal';
    let tierBg = 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)';
    let tierBorder = 'rgba(255, 255, 255, 0.15)';
    let tierGlow = 'rgba(255, 255, 255, 0.1)';

    if (loyalty.tier_badge === 'silver') {
        tierColor = '#94a3b8';
        tierIcon = 'fa-award';
        tierBg = 'linear-gradient(135deg, #334155 0%, #1e293b 100%)';
        tierBorder = 'rgba(148, 163, 184, 0.4)';
        tierGlow = 'rgba(148, 163, 184, 0.2)';
    } else if (loyalty.tier_badge === 'gold') {
        tierColor = '#fbbf24';
        tierIcon = 'fa-crown';
        tierBg = 'linear-gradient(135deg, #78350f 0%, #b45309 50%, #451a03 100%)';
        tierBorder = 'rgba(245, 158, 11, 0.5)';
        tierGlow = 'rgba(245, 158, 11, 0.3)';
    } else if (loyalty.tier_badge === 'diamond') {
        tierColor = '#38bdf8';
        tierIcon = 'fa-gem';
        tierBg = 'linear-gradient(135deg, #0369a1 0%, #0284c7 50%, #0c4a6e 100%)';
        tierBorder = 'rgba(56, 189, 248, 0.5)';
        tierGlow = 'rgba(56, 189, 248, 0.3)';
    }

    container.innerHTML = `
        <!-- VIP Loyalty Membership Card -->
        <div class="glass-panel" style="background: ${tierBg}; border: 1px solid ${tierBorder}; box-shadow: 0 16px 40px -10px ${tierGlow}; padding: 2rem; border-radius: var(--radius-lg); margin-bottom: 2rem; color: #ffffff; position: relative; overflow: hidden;">
            <div style="position: absolute; right: -25px; bottom: -25px; font-size: 10rem; opacity: 0.12; pointer-events: none; color: ${tierColor};">
                <i class="fa-solid ${tierIcon}"></i>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem; position: relative; z-index: 1;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 1.8px; opacity: 0.9; font-weight: 700; color: ${tierColor};">
                        <i class="fa-solid fa-paw"></i> PetCare Pro VIP Membership
                    </div>
                    <h2 style="font-size: 1.85rem; font-weight: 800; margin: 8px 0; display: flex; align-items: center; gap: 10px; letter-spacing: -0.5px;">
                        ${owner.full_name}
                        <span class="badge" style="background: rgba(0, 0, 0, 0.35); color: ${tierColor}; font-size: 0.8rem; border: 1px solid ${tierColor}; padding: 5px 12px; box-shadow: 0 0 12px ${tierGlow};">
                            <i class="fa-solid ${tierIcon}"></i> ${loyalty.tier_name}
                        </span>
                    </h2>
                    <div style="font-size: 0.92rem; opacity: 0.9; display: flex; gap: 1.25rem; flex-wrap: wrap; margin-top: 6px;">
                        <span><i class="fa-solid fa-phone" style="color: #38bdf8;"></i> ${owner.phone}</span>
                        ${owner.email ? `<span><i class="fa-solid fa-envelope" style="color: #a78bfa;"></i> ${owner.email}</span>` : ''}
                        ${owner.address ? `<span><i class="fa-solid fa-location-dot" style="color: #34d399;"></i> ${owner.address}</span>` : ''}
                    </div>
                </div>

                <div style="text-align: right; background: rgba(15, 23, 42, 0.65); padding: 1rem 1.6rem; border-radius: var(--radius-md); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.8px; color: #94a3b8; font-weight: 600;">Điểm thưởng tích lũy</div>
                    <div style="font-size: 2.2rem; font-weight: 900; color: #fbbf24; line-height: 1.2; text-shadow: 0 2px 10px rgba(251, 191, 36, 0.4);">
                        ${loyalty.points.toLocaleString()} <span style="font-size: 1rem; font-weight: 600; color: #fde68a;">pts</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #34d399; font-weight: 700; margin-top: 4px; display: flex; align-items: center; justify-content: flex-end; gap: 4px;">
                        <i class="fa-solid fa-tags"></i> Giảm giá VIP: <strong>${loyalty.discount_percent}%</strong> cho mọi dịch vụ
                    </div>
                </div>
            </div>
        </div>

        <!-- Section: Pets Managed by this Customer -->
        <div style="margin-bottom: 2rem;">
            <div class="section-header" style="margin-bottom: 1.25rem;">
                <div class="section-title"><i class="fa-solid fa-paw" style="color: #6366f1;"></i> Thú Cưng Của Bạn (${pets.length} bé)</div>
                <button class="btn btn-primary btn-sm" onclick="quickBookForCustomer('${owner.phone}', '${owner.full_name}')">
                    <i class="fa-solid fa-calendar-plus"></i> Đặt Lịch Chăm Sóc Cho Bé
                </button>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.35rem;">
                ${pets.map(p => `
                    <div class="glass-panel" style="padding: 1.4rem; border-radius: var(--radius-md); display: flex; flex-direction: column; background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(15, 23, 42, 0.6) 100%); border: 1px solid var(--border-color); transition: var(--transition);">
                        <div style="display: flex; gap: 1.1rem; align-items: center; margin-bottom: 1rem;">
                            <img src="${p.avatar_url || 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=200&q=80'}"
                                 alt="${p.name}"
                                 onerror="this.src='https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=200&q=80'"
                                 style="width: 68px; height: 68px; border-radius: 50%; object-fit: cover; border: 2.5px solid #6366f1; box-shadow: 0 4px 14px var(--primary-glow);">
                            <div>
                                <h4 style="font-size: 1.25rem; font-weight: 800; margin-bottom: 3px; display: flex; align-items: center; gap: 6px;">
                                    ${p.name} 
                                    <span class="badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; font-size: 0.72rem; border: 1px solid rgba(99, 102, 241, 0.35);">${p.species}</span>
                                </h4>
                                <div style="font-size: 0.84rem; color: var(--text-muted);">${p.breed || 'Chưa rõ giống'} • ${p.gender || 'Đực'} • ${p.age_years} tuổi ${p.age_months ? p.age_months + ' tháng' : ''}</div>
                            </div>
                        </div>
                        
                        <div style="font-size: 0.85rem; line-height: 1.7; margin-bottom: 1rem; background: rgba(0,0,0,0.2); padding: 0.75rem 1rem; border-radius: var(--radius-sm);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="color: var(--text-muted); display: flex; align-items: center; gap: 5px;">
                                    <i class="fa-solid fa-weight-scale" style="color: #38bdf8;"></i> Cân nặng:
                                </span>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <strong style="color: #38bdf8; font-size: 0.95rem;">${p.weight_kg ? p.weight_kg + ' kg' : 'Chưa cập nhật'}</strong>
                                    <button type="button" class="btn btn-secondary btn-sm" onclick="openUpdateWeightModal(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.weight_kg || 3.5})" title="Thêm / Cập nhật số cân nặng mới cho bé" style="padding: 2px 7px; font-size: 0.72rem; border-radius: 6px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; cursor: pointer; font-weight: 700; display: inline-flex; align-items: center; gap: 3px;">
                                        <i class="fa-solid fa-pen-to-square"></i> Cập nhật
                                    </button>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-muted);">Mã chip:</span>
                                <span style="font-family: monospace; color: #cbd5e1;">${p.microchip_id || 'Chưa gắn'}</span>
                            </div>
                            ${p.allergies ? `
                            <div style="margin-top: 4px; color: #fb7185; font-size: 0.8rem;">
                                <i class="fa-solid fa-triangle-exclamation"></i> <strong>Dị ứng:</strong> ${p.allergies}
                            </div>` : ''}
                        </div>

                        <div style="margin-top: auto; display: flex; gap: 0.45rem;">
                            <button class="btn btn-secondary btn-sm" style="flex: 1; justify-content: center; font-size: 0.76rem; padding: 6px 2px; background: #f0f9ff; border: 1px solid #bae6fd; color: #0369a1; font-weight: 700;" onclick="openUpdateWeightModal(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.weight_kg || 3.5})" title="Thêm số cân nặng mới cho bé">
                                <i class="fa-solid fa-weight-scale" style="color: #0284c7;"></i> Cân Nặng
                            </button>
                            <button class="btn btn-ai btn-sm" style="flex: 1; justify-content: center; font-size: 0.76rem; padding: 6px 2px;" onclick="quickSummarizePet(${p.id})">
                                <i class="fa-solid fa-wand-magic-sparkles"></i> AI Tóm Tắt
                            </button>
                            <button class="btn btn-primary btn-sm" style="flex: 1.1; justify-content: center; font-size: 0.76rem; padding: 6px 2px;" onclick="selectPetForBooking(${p.id}, '${p.name.replace(/'/g, "\\'")}', '${p.species}')">
                                <i class="fa-solid fa-calendar-check"></i> Đặt Lịch
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Section: Vaccination & Appointment History -->
        <div class="charts-grid" style="margin-bottom: 2rem;">
            <!-- Electronic Vaccination Book -->
            <div class="glass-panel" style="padding: 1.5rem;">
                <div class="section-header">
                    <div class="section-title"><i class="fa-solid fa-syringe" style="color: #06b6d4;"></i> Sổ Tiêm Phòng Điện Tử</div>
                    <span class="badge" style="background: rgba(6, 182, 212, 0.2); color: #22d3ee;"><i class="fa-solid fa-shield-halved"></i> Miễn dịch</span>
                </div>
                ${vacs.length === 0 ? `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">Chưa có dữ liệu mũi tiêm nào được ghi nhận.</div>` : `
                <div style="max-height: 280px; overflow-y: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Bé cưng</th>
                                <th>Mũi Vaccine</th>
                                <th>Ngày tiêm nhắc</th>
                                <th style="text-align: right;">Trạng thái</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${vacs.map(v => {
                                let badgeClass = 'badge-pending';
                                let statusText = 'Sắp đến hạn';
                                if (v.status === 'COMPLETED') { badgeClass = 'badge-confirmed'; statusText = 'Đã tiêm'; }
                                if (v.status === 'OVERDUE') { badgeClass = 'badge-cancelled'; statusText = 'Quá hạn'; }
                                return `
                                <tr>
                                    <td><strong>🐾 ${v.pet_name}</strong></td>
                                    <td>${v.vaccine_name}</td>
                                    <td><strong style="color: #38bdf8;">${v.next_due_date ? new Date(v.next_due_date).toLocaleDateString('vi-VN') : '---'}</strong></td>
                                    <td style="text-align: right;"><span class="badge ${badgeClass}">${statusText}</span></td>
                                </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>`}
            </div>

            <!-- Appointments Log -->
            <div class="glass-panel" style="padding: 1.5rem;">
                <div class="section-header">
                    <div class="section-title"><i class="fa-solid fa-calendar-days" style="color: #10b981;"></i> Lịch Hẹn Đã Đặt</div>
                    <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;"><i class="fa-solid fa-clock-rotate-left"></i> Lịch sử</span>
                </div>
                ${appts.length === 0 ? `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">Chưa có lịch hẹn nào.</div>` : `
                <div style="max-height: 280px; overflow-y: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Bé cưng</th>
                                <th>Dịch vụ</th>
                                <th>Thời gian</th>
                                <th style="text-align: right;">Trạng thái</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${appts.map(a => {
                                let badgeClass = 'badge-pending';
                                let statusText = 'Chờ duyệt';
                                if (a.status === 'CONFIRMED') { badgeClass = 'badge-confirmed'; statusText = 'Đã xác nhận'; }
                                if (a.status === 'COMPLETED') { badgeClass = 'badge-completed'; statusText = 'Hoàn thành'; }
                                if (a.status === 'CANCELLED') { badgeClass = 'badge-cancelled'; statusText = 'Đã hủy'; }
                                return `
                                <tr>
                                    <td><strong>🐾 ${a.pet_name}</strong></td>
                                    <td><span style="color: #818cf8;">${a.service_name}</span></td>
                                    <td><span style="color: #fbbf24; font-weight: 600;">${a.appointment_time ? new Date(a.appointment_time).toLocaleString('vi-VN', {hour: '2-digit', minute:'2-digit', day:'2-digit', month:'2-digit'}) : ''}</span></td>
                                    <td style="text-align: right;"><span class="badge ${badgeClass}">${statusText}</span></td>
                                </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>`}
            </div>
        </div>
    `;

    // Auto-fill booking form with current customer details
    const bookPhone = document.getElementById('book-phone');
    const bookName = document.getElementById('book-owner-name');
    const bookEmail = document.getElementById('book-email');
    if (bookPhone) bookPhone.value = owner.phone;
    if (bookName) bookName.value = owner.full_name;
    if (bookEmail && owner.email) bookEmail.value = owner.email;

    // Update Pet Dropdown in Online Booking
    const petSelect = document.getElementById('book-pet-select');
    if (petSelect) {
        petSelect.innerHTML = `<option value="">-- Đăng ký bé mới (Nhập ở dưới) --</option>` + pets.map(p => `
            <option value="${p.id}" data-species="${p.species}" data-name="${p.name}">🐾 ${p.name} (${p.species} - ${p.breed || 'Chưa rõ'})</option>
        `).join('');
    }
}

function scrollToBookingForm(phone = '') {
    if (typeof openCustomerBookingModal === 'function') {
        openCustomerBookingModal();
        if (phone) {
            const p = document.getElementById('modal-custbook-phone');
            if (p) p.value = phone;
        }
    } else {
        const bookPhone = document.getElementById('book-phone');
        if (bookPhone && phone) bookPhone.value = phone;
        const form = document.getElementById('online-booking-section');
        if (form) form.scrollIntoView({ behavior: 'smooth' });
    }
}

function quickBookForCustomer(phone, name) {
    if (typeof openCustomerBookingModal === 'function') {
        openCustomerBookingModal();
        const p = document.getElementById('modal-custbook-phone');
        const n = document.getElementById('modal-custbook-owner');
        if (p && phone) p.value = phone;
        if (n && name) n.value = name;
    } else {
        const bookPhone = document.getElementById('book-phone');
        const bookName = document.getElementById('book-owner-name');
        if (bookPhone) bookPhone.value = phone;
        if (bookName) bookName.value = name;
        scrollToBookingForm();
    }
}

function selectPetForBooking(petId, petName, species) {
    if (typeof openCustomerBookingModal === 'function') {
        openCustomerBookingModal();
        const pn = document.getElementById('modal-custbook-pet-name');
        const ps = document.getElementById('modal-custbook-species');
        if (pn && petName) pn.value = petName;
        if (ps && species) ps.value = species;
    } else {
        const petSelect = document.getElementById('book-pet-select');
        if (petSelect) petSelect.value = petId;
        scrollToBookingForm();
    }
}

async function submitOnlineBooking() {
    const ownerName = document.getElementById('book-owner-name')?.value?.trim();
    const phone = document.getElementById('book-phone')?.value?.trim();
    const email = document.getElementById('book-email')?.value?.trim();
    const petIdVal = document.getElementById('book-pet-select')?.value;
    const petName = document.getElementById('book-pet-name')?.value?.trim();
    const species = document.getElementById('book-pet-species')?.value || 'Chó';
    const breed = document.getElementById('book-pet-breed')?.value?.trim();
    const serviceId = document.getElementById('book-service-select')?.value;
    const date = document.getElementById('book-date')?.value;
    const time = document.getElementById('book-time')?.value;
    const notes = document.getElementById('book-notes')?.value?.trim();

    if (!ownerName || !phone || !serviceId || !date || !time) {
        showToast('Vui lòng điền đầy đủ: Tên, SĐT, Dịch vụ và Thời gian hẹn!', 'error');
        return;
    }

    const apptTime = `${date}T${time}:00`;

    const payload = {
        owner_name: ownerName,
        phone: phone,
        email: email || null,
        pet_id: petIdVal ? parseInt(petIdVal) : null,
        pet_name: petIdVal ? null : (petName || 'Bé cưng'),
        species: species,
        breed: breed || null,
        service_id: parseInt(serviceId),
        appointment_time: apptTime,
        notes: notes || null
    };

    try {
        const res = await apiCall('/customer/book-appointment', 'POST', payload);
        const apptId = res.appointment_id || res.appointment?.id || 'Mới';
        showToast(`🎉 Đặt lịch hẹn trực tuyến thành công! Mã hẹn: #${apptId}`, 'success');
        
        // Refresh customer data
        lookupCustomerByPhone(phone);
        
        // Clear pet name input & notes if any
        const pnInput = document.getElementById('book-pet-name');
        if (pnInput) pnInput.value = '';
        const notesInput = document.getElementById('book-notes');
        if (notesInput) notesInput.value = '';
    } catch (e) {
        showToast('Lỗi đặt lịch: ' + e.message, 'error');
    }
}

async function submitCustomerOnlineModalBooking() {
    const ownerName = document.getElementById('modal-custbook-owner')?.value?.trim();
    const phone = document.getElementById('modal-custbook-phone')?.value?.trim();
    const petName = document.getElementById('modal-custbook-pet-name')?.value?.trim();
    const species = document.getElementById('modal-custbook-species')?.value || 'Chó';
    const breed = document.getElementById('modal-custbook-breed')?.value?.trim();
    const serviceId = document.getElementById('modal-custbook-service')?.value;
    const date = document.getElementById('modal-custbook-date')?.value;
    const time = document.getElementById('modal-custbook-time')?.value;
    const notes = document.getElementById('modal-custbook-notes')?.value?.trim();

    if (!ownerName || !phone || !serviceId || !date || !time) {
        showToast('Vui lòng điền đầy đủ: Tên, SĐT, Dịch vụ và Thời gian hẹn!', 'error');
        return;
    }

    const apptTime = `${date}T${time}:00`;

    const payload = {
        owner_name: ownerName,
        phone: phone,
        email: null,
        pet_name: petName || 'Bé cưng',
        species: species,
        breed: breed || null,
        service_id: parseInt(serviceId),
        appointment_time: apptTime,
        notes: notes || null
    };

    try {
        const res = await apiCall('/customer/book-appointment', 'POST', payload);
        const apptId = res.appointment_id || res.appointment?.id || 'Mới';
        closeModal('modal-customer-online-booking');
        showToast(`🎉 Đặt lịch trực tuyến thành công! Mã hẹn: #${apptId}`, 'success');
        
        // Refresh customer data if phone is entered
        if (typeof lookupCustomerByPhone === 'function' && phone) {
            lookupCustomerByPhone(phone);
        }
    } catch (e) {
        showToast('Lỗi đặt lịch: ' + e.message, 'error');
    }
}

/**
 * VIP Card Tilt & Interactive Experience
 */
function initVIPCardTilt() {
    const card = document.getElementById('vip-digital-card');
    if (!card) return;

    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((y - centerY) / centerY) * -10;
        const rotateY = ((x - centerX) / centerX) * 12;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;

        const glare = card.querySelector('.vip-card-glare');
        if (glare) {
            glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0) 65%)`;
            glare.style.opacity = '1';
        }
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        const glare = card.querySelector('.vip-card-glare');
        if (glare) glare.style.opacity = '0';
    });
}

function updateVIPCalculator(val) {
    const spend = parseInt(val);
    const spendText = document.getElementById('calc-spend-amount');
    const tierBadge = document.getElementById('calc-tier-badge');
    const discountText = document.getElementById('calc-discount-val');
    const pointsText = document.getElementById('calc-points-val');
    const yearlySavings = document.getElementById('calc-yearly-savings');

    if (spendText) spendText.textContent = `${(spend).toLocaleString('vi-VN')} đ / tháng`;

    let discount = 5;
    let tier = 'Thành Viên Bạc (Silver)';
    let tierColor = '#94a3b8';

    if (spend >= 3000000) {
        discount = 15;
        tier = '👑 Kim Cương (Diamond VIP)';
        tierColor = '#38bdf8';
    } else if (spend >= 1500000) {
        discount = 10;
        tier = '🥇 Thành Viên Vàng (Gold VIP)';
        tierColor = '#f59e0b';
    }

    const pointsEarned = Math.round(spend / 10000);
    const savings = Math.round((spend * 12 * discount) / 100);

    if (tierBadge) {
        tierBadge.textContent = tier;
        tierBadge.style.color = tierColor;
    }
    if (discountText) discountText.textContent = `Giảm ngay ${discount}%`;
    if (pointsText) pointsText.textContent = `+${pointsEarned} pts / tháng`;
    if (yearlySavings) yearlySavings.textContent = `${savings.toLocaleString('vi-VN')} đ`;
}

function switchLifeStageTab(stageKey) {
    document.querySelectorAll('.stage-tab-btn').forEach(btn => {
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-md');
        btn.classList.add('bg-white', 'text-slate-700');
    });
    const activeBtn = document.getElementById(`btn-stage-${stageKey}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-white', 'text-slate-700');
        activeBtn.classList.add('bg-indigo-600', 'text-white', 'shadow-md');
    }

    document.querySelectorAll('.stage-content-card').forEach(card => {
        card.style.display = 'none';
    });
    const targetCard = document.getElementById(`stage-content-${stageKey}`);
    if (targetCard) {
        targetCard.style.display = 'block';
    }
}

function toggleFaqItem(idx) {
    const answer = document.getElementById(`faq-ans-${idx}`);
    const icon = document.getElementById(`faq-icon-${idx}`);
    if (!answer) return;

    const isHidden = answer.classList.contains('hidden');
    if (isHidden) {
        answer.classList.remove('hidden');
        if (icon) icon.style.transform = 'rotate(180deg)';
    } else {
        answer.classList.add('hidden');
        if (icon) icon.style.transform = 'rotate(0deg)';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initVIPCardTilt();
});


