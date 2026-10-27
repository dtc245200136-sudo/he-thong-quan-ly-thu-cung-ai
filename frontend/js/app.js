// PetCare AI Pro - Core Application Script
const API_BASE = '/api/v1';

// Global State
const State = {
    currentUser: null,
    token: localStorage.getItem('petcare_token') || null,
    pets: [],
    owners: [],
    services: [],
    staff: [],
    activeTab: 'dashboard'
};

// API Fetch Helper with Auto Bearer Auth
async function apiCall(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    if (State.token) {
        headers['Authorization'] = `Bearer ${State.token}`;
    }

    const options = {
        method,
        headers
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (response.status === 401) {
            console.warn('Session expired or unauthorized');
            State.token = null;
            State.currentUser = null;
            localStorage.removeItem('petcare_token');
            updateUserUI();
            openLoginModal();
            throw new Error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
        }
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Lỗi HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (err) {
        console.error(`API Error [${method} ${endpoint}]:`, err);
        throw err;
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'triangle-exclamation';
    
    toast.innerHTML = `<i class="fa-solid fa-${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Modal Control
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        if (typeof window.replaceIconsWithSvg === 'function') {
            window.replaceIconsWithSvg(modal);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

// Tab Switching with Strict RBAC Route Guard
function switchTab(tabName) {
    const role = State.currentUser ? State.currentUser.role : 'CUSTOMER';
    
    // RBAC Permission Map
    const rolePermissions = {
        'CUSTOMER': ['customer_portal'],
        'STAFF': ['appointments', 'pets', 'care', 'ai_studio', 'customer_portal'],
        'RECEPTIONIST': ['dashboard', 'appointments', 'pets', 'vaccinations', 'invoices', 'customer_portal'],
        'ADMIN': ['dashboard', 'appointments', 'pets', 'care', 'vaccinations', 'invoices', 'inventory', 'ai_studio', 'customer_portal']
    };

    const allowedTabs = rolePermissions[role] || ['customer_portal'];

    // Kiểm tra nếu tab yêu cầu vượt quyền
    if (!allowedTabs.includes(tabName)) {
        console.warn(`[RBAC Guard] Quyền ${role} không được phép truy cập tab: ${tabName}`);
        
        let tabLabel = 'Khu vực quản trị';
        if (tabName === 'inventory') tabLabel = 'Kho Hàng & Dược Phẩm';
        if (tabName === 'invoices') tabLabel = 'Hóa Đơn & Tài Chính';
        if (tabName === 'dashboard') tabLabel = 'Tổng Quan KPI & Doanh Thu';

        const msgEl = document.getElementById('access-denied-message');
        if (msgEl) {
            if (role === 'CUSTOMER') {
                msgEl.innerHTML = `Khu vực <strong style="color: #fb7185;">${tabLabel}</strong> chỉ dành riêng cho Ban Quản Trị và Nhân viên PetCare. Quý khách hàng vui lòng thực hiện dịch vụ tại <strong>Cổng Khách Hàng</strong>!`;
            } else {
                msgEl.innerHTML = `Vai trò hiện tại của bạn (<strong style="color: #60a5fa;">${role}</strong>) không có quyền truy cập <strong style="color: #fb7185;">${tabLabel}</strong>. Vui lòng liên hệ Quản Trị Viên (Admin).`;
            }
        }
        
        openModal('modal-access-denied');
        showToast(`🔒 Quyền truy cập bị từ chối: Không thể vào ${tabLabel}`, 'error');
        return;
    }

    State.activeTab = tabName;
    
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    const activeNav = document.getElementById(`nav-${tabName}`);
    if (activeNav) activeNav.classList.add('active');

    // Update customer nav items if in customer mode
    if (role === 'CUSTOMER') {
        const custPortalNav = document.getElementById('nav-customer_portal');
        if (custPortalNav) custPortalNav.classList.add('active');
    }

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(section => section.classList.remove('active'));
    const activeSection = document.getElementById(`tab-${tabName}`);
    if (activeSection) activeSection.classList.add('active');

    // Trigger tab-specific refresh
    if (tabName === 'dashboard') loadDashboard();
    if (tabName === 'appointments') loadAppointments();
    if (tabName === 'pets') loadPets();
    if (tabName === 'care') loadCareRecords();
    if (tabName === 'vaccinations') loadVaccinations();
    if (tabName === 'invoices') loadInvoices();
    if (tabName === 'inventory') loadInventory();
    if (tabName === 'ai_studio') initAIStudio();
    if (tabName === 'customer_portal') {
        // Cổng khách hàng sẵn sàng, người dùng nhập SĐT để tra cứu chủ động
    }
}

// Theme Toggle (Dark / Light)
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('petcare_theme', newTheme);

    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        btn.innerHTML = newTheme === 'light' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
        btn.title = newTheme === 'light' ? 'Chuyển chế độ Tối (Dark Mode)' : 'Chuyển chế độ Sáng (Light Mode)';
    }
}

// Workflow Pipeline Status Filter for Appointments
function filterApptByPipeline(status, btnElement) {
    const select = document.getElementById('filter-appt-status');
    if (select) {
        select.value = status;
    }
    
    // Update active pill button
    document.querySelectorAll('.appt-pipeline-pill').forEach(b => b.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }
    
    loadAppointments();
}

// Workflow Hub Stream Filter
function filterWorkflowHub(streamName) {
    document.querySelectorAll('.workflow-stream-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.getElementById(`wf-btn-${streamName}`);
    if (activeBtn) activeBtn.classList.add('active');

    document.querySelectorAll('.workflow-stream-panel').forEach(p => p.style.display = 'none');
    const targetPanel = document.getElementById(`wf-panel-${streamName}`);
    if (targetPanel) targetPanel.style.display = 'grid';
}

// Format Currency VNĐ
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount || 0);
}

// Format DateTime
function formatDateTime(dtStr) {
    if (!dtStr) return '';
    const d = new Date(dtStr);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')} ${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

// Global App Initialization
document.addEventListener('DOMContentLoaded', async () => {
    // Restore Theme (Default to Light)
    const savedTheme = localStorage.getItem('petcare_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.innerHTML = savedTheme === 'light' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
        themeBtn.title = savedTheme === 'light' ? 'Chuyển chế độ Tối (Dark Mode)' : 'Chuyển chế độ Sáng (Light Mode)';
    }

    // Check token authentication
    if (State.token) {
        try {
            const me = await apiCall('/auth/me');
            State.currentUser = me;
            updateUserUI();
            await loadGlobalMetadata();
            
            if (me.role === 'CUSTOMER') {
                switchTab('customer_portal');
                if (me.phone) lookupCustomerByPhone(me.phone);
            } else if (me.role === 'STAFF') {
                switchTab('appointments');
            } else {
                switchTab('dashboard');
            }
        } catch (e) {
            console.warn('Session expired or guest visitor');
            State.token = null;
            State.currentUser = null;
            localStorage.removeItem('petcare_token');
            updateUserUI();
            await loadGlobalMetadata();
            switchTab('customer_portal');
        }
    } else {
        updateUserUI();
        await loadGlobalMetadata();
        switchTab('customer_portal');
    }
});

async function loadGlobalMetadata() {
    try {
        // Services is public and loaded for everyone (guests and logged-in users)
        const services = await apiCall('/services').catch(() => []);
        State.services = services || [];

        if (State.token) {
            const [pets, owners, users] = await Promise.all([
                apiCall('/pets').catch(() => []),
                apiCall('/owners').catch(() => []),
                apiCall('/auth/users').catch(() => [])
            ]);
            State.pets = pets || [];
            State.owners = owners || [];
            State.staff = (users || []).filter(u => u.role === 'STAFF' || u.role === 'ADMIN');
        } else {
            State.pets = [];
            State.owners = [];
            State.staff = [];
        }
        
        populateModalDropdowns();
    } catch (e) {
        console.error('Lỗi tải metadata:', e);
    }
}

function populateModalDropdowns() {
    // Book Pet dropdown
    const bookPetSelect = document.getElementById('modal-book-pet');
    if (bookPetSelect) {
        bookPetSelect.innerHTML = State.pets.map(p => 
            `<option value="${p.id}">🐾 ${p.name} (${p.breed || p.species}) - Chủ: ${p.owner_name || 'Khách'}</option>`
        ).join('');
    }

    // Book Service dropdown
    const bookServiceSelect = document.getElementById('modal-book-service');
    if (bookServiceSelect) {
        bookServiceSelect.innerHTML = State.services.map(s => 
            `<option value="${s.id}">${s.name} - ${formatCurrency(s.price)} (${s.duration_minutes} phút)</option>`
        ).join('');
    }

    // Staff dropdown
    const bookStaffSelect = document.getElementById('modal-book-staff');
    if (bookStaffSelect) {
        bookStaffSelect.innerHTML = `<option value="">-- Tự động phân bổ --</option>` + State.staff.map(u => 
            `<option value="${u.id}">✂️ ${u.full_name}</option>`
        ).join('');
    }

    // Pet Owner dropdown
    const petOwnerSelect = document.getElementById('modal-pet-owner');
    if (petOwnerSelect) {
        petOwnerSelect.innerHTML = State.owners.map(o => 
            `<option value="${o.id}">${o.full_name} (${o.phone})</option>`
        ).join('');
    }

    // Care Pet dropdown
    const carePetSelect = document.getElementById('modal-care-pet');
    if (carePetSelect) {
        carePetSelect.innerHTML = State.pets.map(p => 
            `<option value="${p.id}">🐾 ${p.name} (${p.breed || p.species})</option>`
        ).join('');
    }

    // Care Filter Pet dropdown
    const careFilterSelect = document.getElementById('care-filter-pet');
    if (careFilterSelect) {
        careFilterSelect.innerHTML = `<option value="">Tất cả thú cưng</option>` + State.pets.map(p => 
            `<option value="${p.id}">${p.name} (${p.owner_name || 'Chủ'})</option>`
        ).join('');
    }

    // Vac Pet dropdown
    const vacPetSelect = document.getElementById('modal-vac-pet');
    if (vacPetSelect) {
        vacPetSelect.innerHTML = State.pets.map(p => 
            `<option value="${p.id}">🐾 ${p.name} (${p.breed || p.species})</option>`
        ).join('');
    }

    // AI Summary Pet dropdown
    const aiSumSelect = document.getElementById('ai-summary-pet-select');
    if (aiSumSelect) {
        aiSumSelect.innerHTML = State.pets.map(p => 
            `<option value="${p.id}">🐾 ${p.name} (${p.breed || p.species}) - ${p.owner_name || 'Chủ'}</option>`
        ).join('');
    }

    // Online Customer Booking Service dropdown
    const onlineServiceSelect = document.getElementById('book-service-select');
    if (onlineServiceSelect) {
        onlineServiceSelect.innerHTML = `<option value="">-- Chọn gói dịch vụ mong muốn --</option>` + State.services.map(s => 
            `<option value="${s.id}">${s.name} &bull; ${formatCurrency(s.price)}</option>`
        ).join('');
    }

    // Customer Booking Modal Service dropdown
    const custModalService = document.getElementById('modal-custbook-service');
    if (custModalService) {
        custModalService.innerHTML = `<option value="">-- Chọn gói dịch vụ mong muốn --</option>` + State.services.map(s => 
            `<option value="${s.id}">${s.name} &bull; ${formatCurrency(s.price)}</option>`
        ).join('');
    }

    // Default dates for booking forms (Tomorrow)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];

    const bookDateInput = document.getElementById('book-date');
    if (bookDateInput && !bookDateInput.value) {
        bookDateInput.value = tomorrowStr;
    }

    const modalBookDate = document.getElementById('modal-custbook-date');
    if (modalBookDate && !modalBookDate.value) {
        modalBookDate.value = tomorrowStr;
    }
}

// ==========================================================================
// PET WEIGHT TRACKING & UPDATE CONTROLLER
// ==========================================================================

function openUpdateWeightModal(petId, petName, currentWeight) {
    const modal = document.getElementById('modal-update-weight');
    if (!modal) {
        console.error('Modal update weight not found');
        return;
    }

    const idInput = document.getElementById('modal-weight-pet-id');
    const nameEl = document.getElementById('modal-weight-pet-name');
    const oldValEl = document.getElementById('modal-weight-old-val');
    const input = document.getElementById('modal-weight-input');
    const dateInput = document.getElementById('modal-weight-date');
    const notesInput = document.getElementById('modal-weight-notes');

    if (idInput) idInput.value = petId;
    if (nameEl) nameEl.textContent = petName;
    if (oldValEl) oldValEl.textContent = currentWeight ? `${currentWeight} kg` : 'Chưa cân';

    if (input) {
        input.value = currentWeight || 3.5;
        setTimeout(() => input.focus(), 150);
    }

    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    if (notesInput) {
        notesInput.value = '';
    }

    modal.classList.add('active');
}

function adjustWeightInput(delta) {
    const input = document.getElementById('modal-weight-input');
    if (!input) return;
    let val = parseFloat(input.value) || 0;
    val = Math.max(0.1, Math.round((val + delta) * 100) / 100);
    input.value = val;
}

async function submitUpdatePetWeight() {
    const petId = document.getElementById('modal-weight-pet-id')?.value;
    const input = document.getElementById('modal-weight-input');
    const notes = document.getElementById('modal-weight-notes')?.value?.trim();
    const dateVal = document.getElementById('modal-weight-date')?.value;

    if (!petId) {
        showToast('Không xác định được mã thú cưng.', 'error');
        return;
    }

    const weightKg = parseFloat(input?.value);
    if (!weightKg || weightKg <= 0 || weightKg > 200) {
        showToast('Vui lòng nhập số cân nặng hợp lệ (0.1 kg - 200 kg).', 'error');
        input?.focus();
        return;
    }

    try {
        const payload = {
            weight_kg: weightKg,
            notes: notes || 'Cập nhật cân nặng định kỳ',
            record_date: dateVal ? new Date(dateVal).toISOString() : new Date().toISOString()
        };

        const res = await apiCall(`/customer/pets/${petId}/weight`, 'POST', payload);
        showToast(res.message || `🎉 Đã cập nhật cân nặng mới: ${weightKg} kg!`, 'success');
        closeModal('modal-update-weight');

        // Refresh Customer Portal data if phone is looked up
        const currentPhone = document.getElementById('customer-lookup-phone')?.value?.trim();
        if (currentPhone && typeof lookupCustomerByPhone === 'function') {
            lookupCustomerByPhone(currentPhone);
        }

        // Refresh Pet Management tab if active
        if (typeof loadPets === 'function') {
            loadPets();
        }

        // Refresh Pet Profile modal if open
        const profileWeightEl = document.getElementById('modal-profile-weight');
        if (profileWeightEl) {
            profileWeightEl.textContent = `${weightKg} kg`;
        }
    } catch (err) {
        console.error('Error updating weight:', err);
        showToast('Lỗi cập nhật cân nặng: ' + err.message, 'error');
    }
}
