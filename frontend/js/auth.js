// PetCare AI Pro - Auth & RBAC Module

/**
 * Xử lý đăng nhập thủ công từ form Username/Password
 */
async function handleManualLogin(event) {
    if (event) event.preventDefault();

    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const submitBtn = document.getElementById('login-submit-btn');
    const errorAlert = document.getElementById('login-error-alert');

    const username = usernameInput ? usernameInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    if (!username || !password) {
        showLoginError('Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu.');
        return;
    }

    // Hiệu ứng loading nút
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xác thực...';
    }
    hideLoginError();

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Tên đăng nhập hoặc mật khẩu không chính xác.');
        }

        // Lưu thông tin đăng nhập
        State.token = data.access_token;
        State.currentUser = data.user;
        localStorage.setItem('petcare_token', data.access_token);

        // Đóng modal đăng nhập
        closeModal('modal-login');

        // Cập nhật giao diện
        updateUserUI();
        // Tải lại metadata và điều hướng theo vai trò
        await loadGlobalMetadata();
        if (data.user.role === 'ADMIN' || data.user.role === 'RECEPTIONIST') {
            switchTab('dashboard');
        } else if (data.user.role === 'STAFF') {
            switchTab('appointments');
        } else {
            switchTab('customer_portal');
        }

    } catch (err) {
        showLoginError(err.message || 'Lỗi kết nối máy chủ.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Đăng Nhập Hệ Thống';
        }
    }
}

/**
 * Đăng nhập nhanh 1-chạm (Dành cho Giảng viên / Chấm điểm nhanh)
 */
async function quickLogin(username, password) {
    try {
        const data = await apiCall('/auth/login', 'POST', { username, password });
        State.token = data.access_token;
        State.currentUser = data.user;
        localStorage.setItem('petcare_token', data.access_token);
        
        // Đóng modal login nếu đang mở
        closeModal('modal-login');

        // Cập nhật giao diện
        updateUserUI();
        showToast(`Đã chuyển sang tài khoản: ${data.user.full_name} [${data.user.role}]`, 'success');
        
        // Làm mới dữ liệu
        await loadGlobalMetadata();
        switchTab(State.activeTab || 'dashboard');
    } catch (e) {
        showToast('Lỗi đăng nhập nhanh: ' + e.message, 'error');
    }
}

/**
 * Chuyển đổi giữa các chế độ: 'login', 'register', 'forgot'
 */
function switchAuthView(mode) {
    hideLoginError();
    hideLoginSuccess();

    const viewLogin = document.getElementById('auth-view-login');
    const viewRegister = document.getElementById('auth-view-register');
    const viewForgot = document.getElementById('auth-view-forgot');

    const modalTitle = document.getElementById('auth-modal-title');
    const modalSubtitle = document.getElementById('auth-modal-subtitle');

    // Ẩn tất cả view
    if (viewLogin) viewLogin.style.display = 'none';
    if (viewRegister) viewRegister.style.display = 'none';
    if (viewForgot) viewForgot.style.display = 'none';

    if (mode === 'register') {
        if (viewRegister) viewRegister.style.display = 'block';
        if (modalTitle) modalTitle.textContent = 'Tạo Tài Khoản Mới';
        if (modalSubtitle) modalSubtitle.textContent = 'Gia nhập đội ngũ PetCare AI Pro';
        const firstInput = document.getElementById('reg-fullname');
        if (firstInput) setTimeout(() => firstInput.focus(), 100);
    } else if (mode === 'forgot') {
        if (viewForgot) viewForgot.style.display = 'block';
        if (modalTitle) modalTitle.textContent = 'Khôi Phục Mật Khẩu';
        if (modalSubtitle) modalSubtitle.textContent = 'Đặt lại mật khẩu truy cập hệ thống';
        const firstInput = document.getElementById('reset-username');
        if (firstInput) setTimeout(() => firstInput.focus(), 100);
    } else {
        if (viewLogin) viewLogin.style.display = 'block';
        if (modalTitle) modalTitle.textContent = 'PetCare AI Pro';
        if (modalSubtitle) modalSubtitle.textContent = 'Hệ Thống Quản Lý Thú Cưng Tích Hợp AI';
        const firstInput = document.getElementById('login-username');
        if (firstInput) setTimeout(() => firstInput.focus(), 100);
    }

    if (typeof window.replaceIconsWithSvg === 'function') {
        const modal = document.getElementById('modal-login');
        if (modal) window.replaceIconsWithSvg(modal);
    }
}


/**
 * Xử lý đăng ký tài khoản người dùng mới
 */
async function handleManualRegister(event) {
    if (event) event.preventDefault();

    const fullname = (document.getElementById('reg-fullname')?.value || '').trim();
    const username = (document.getElementById('reg-username')?.value || '').trim();
    const phone = (document.getElementById('reg-phone')?.value || '').trim();
    const email = (document.getElementById('reg-email')?.value || '').trim();
    const role = document.getElementById('reg-role')?.value || 'CUSTOMER';
    const password = document.getElementById('reg-password')?.value || '';
    const confirmPassword = document.getElementById('reg-confirm-password')?.value || '';
    const submitBtn = document.getElementById('reg-submit-btn');

    hideLoginError();
    hideLoginSuccess();

    if (!fullname || !username || !password) {
        showLoginError('Vui lòng điền đầy đủ Họ tên, Tên đăng nhập và Mật khẩu.');
        return;
    }

    if (password.length < 6) {
        showLoginError('Mật khẩu phải chứa ít nhất 6 ký tự.');
        return;
    }

    if (password !== confirmPassword) {
        showLoginError('Mật khẩu xác nhận không trùng khớp.');
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang khởi tạo tài khoản...';
    }

    try {
        const payload = {
            username: username,
            password: password,
            full_name: fullname,
            role: role,
            phone: phone || null,
            email: email || null
        };

        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Không thể tạo tài khoản. Vui lòng thử lại.');
        }

        // Tự động lưu token & đăng nhập
        State.token = data.access_token;
        State.currentUser = data.user;
        localStorage.setItem('petcare_token', data.access_token);

        closeModal('modal-login');
        updateUserUI();
        
        const isCustomer = data.user.role === 'CUSTOMER';
        const roleTitle = isCustomer ? 'Khách Hàng' : data.user.role;
        showToast(`🎉 Chào mừng ${data.user.full_name}! Bạn đã đăng ký tài khoản ${roleTitle} thành công!`, 'success');

        await loadGlobalMetadata();
        
        if (isCustomer) {
            switchTab('customer_portal');
            if (data.user.phone) {
                lookupCustomerByPhone(data.user.phone);
            }
        } else {
            switchTab('dashboard');
        }

    } catch (err) {
        showLoginError(err.message || 'Lỗi kết nối máy chủ khi đăng ký.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Đăng Ký Tài Khoản Mới';
        }
    }
}

/**
 * Xử lý đặt lại mật khẩu / Quên mật khẩu
 */
async function handleManualResetPassword(event) {
    if (event) event.preventDefault();

    const username = (document.getElementById('reset-username')?.value || '').trim();
    const verifyInfo = (document.getElementById('reset-verify')?.value || '').trim();
    const newPassword = document.getElementById('reset-new-password')?.value || '';
    const confirmPassword = document.getElementById('reset-confirm-password')?.value || '';
    const submitBtn = document.getElementById('reset-submit-btn');

    hideLoginError();
    hideLoginSuccess();

    if (!username) {
        showLoginError('Vui lòng nhập Tên đăng nhập cần khôi phục mật khẩu.');
        return;
    }

    if (!newPassword) {
        showLoginError('Vui lòng nhập mật khẩu mới.');
        return;
    }

    if (newPassword.length < 6) {
        showLoginError('Mật khẩu mới phải có ít nhất 6 ký tự.');
        return;
    }

    if (newPassword !== confirmPassword) {
        showLoginError('Mật khẩu xác nhận không trùng khớp.');
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xác minh & đổi mật khẩu...';
    }

    try {
        const payload = {
            username: username,
            verify_info: verifyInfo || null,
            new_password: newPassword
        };

        const response = await fetch(`${API_BASE}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Không thể đặt lại mật khẩu.');
        }

        showLoginSuccess(data.message || '✅ Đặt lại mật khẩu thành công! Hãy đăng nhập ngay.');
        
        // Tự động điền lại form đăng nhập và chuyển qua tab Đăng nhập sau 1.5s
        setTimeout(() => {
            switchAuthView('login');
            const uInput = document.getElementById('login-username');
            const pInput = document.getElementById('login-password');
            if (uInput) uInput.value = username;
            if (pInput) {
                pInput.value = newPassword;
                pInput.focus();
            }
            showToast('Đã cập nhật mật khẩu mới, bạn có thể đăng nhập ngay.', 'success');
        }, 1500);

    } catch (err) {
        showLoginError(err.message || 'Lỗi đặt lại mật khẩu.');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Đặt Lại Mật Khẩu';
        }
    }
}

/**
 * Điền nhanh tài khoản vào form đăng nhập
 */
function fillLoginForm(username, password) {
    switchAuthView('login');
    const u = document.getElementById('login-username');
    const p = document.getElementById('login-password');
    if (u) u.value = username;
    if (p) p.value = password;
    hideLoginError();
    hideLoginSuccess();
    // Tự động submit
    handleManualLogin();
}

const AUTH_SVG_EYE = `<svg style="width:16px;height:16px;display:block;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`;
const AUTH_SVG_EYE_SLASH = `<svg style="width:16px;height:16px;display:block;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/></svg>`;

/**
 * Bật / tắt ẩn hiện mật khẩu cho bất kỳ input nào
 */
function togglePasswordVisibility(inputId = 'login-password', iconId = 'password-toggle-icon') {
    const pwdInput = document.getElementById(inputId);
    const eyeIcon = document.getElementById(iconId);
    if (!pwdInput) return;

    const isPassword = pwdInput.type === 'password';
    pwdInput.type = isPassword ? 'text' : 'password';

    if (eyeIcon) {
        eyeIcon.innerHTML = isPassword ? AUTH_SVG_EYE_SLASH : AUTH_SVG_EYE;
    }
}

/**
 * Mở modal Đăng nhập
 */
function openLoginModal() {
    switchAuthView('login');
    openModal('modal-login');
    if (typeof window.replaceIconsWithSvg === 'function') {
        window.replaceIconsWithSvg(document.getElementById('modal-login'));
    }
}

/**
 * Hiển thị / Ẩn thông báo lỗi trên form auth
 */
function showLoginError(msg) {
    const alertBox = document.getElementById('login-error-alert');
    const textSpan = document.getElementById('login-error-text');
    if (alertBox && textSpan) {
        textSpan.textContent = msg;
        alertBox.style.display = 'flex';
    } else {
        showToast(msg, 'error');
    }
}

function hideLoginError() {
    const alertBox = document.getElementById('login-error-alert');
    if (alertBox) alertBox.style.display = 'none';
}

function showLoginSuccess(msg) {
    const alertBox = document.getElementById('login-success-alert');
    const textSpan = document.getElementById('login-success-text');
    if (alertBox && textSpan) {
        textSpan.textContent = msg;
        alertBox.style.display = 'flex';
    }
}

function hideLoginSuccess() {
    const alertBox = document.getElementById('login-success-alert');
    if (alertBox) alertBox.style.display = 'none';
}


/**
 * Chuyển sang Giao diện Khách Hàng (Customer Mode)
 */
function switchToCustomerMode() {
    State.token = null;
    State.currentUser = null;
    localStorage.removeItem('petcare_token');

    // Cập nhật giao diện
    updateUserUI();
    
    // Chuyển tab sang Cổng Khách Hàng
    switchTab('customer_portal');
}

/**
 * Xử lý khi click vào Logo PetCare
 */
function handleBrandClick() {
    if (State.currentUser) {
        if (State.currentUser.role === 'ADMIN' || State.currentUser.role === 'RECEPTIONIST') {
            switchTab('dashboard');
        } else {
            switchTab('appointments');
        }
    } else {
        switchTab('customer_portal');
    }
}

/**
 * Mở cửa sổ Đặt Lịch Online trực tiếp (Modal Popup) - Không làm nhảy hay cuộn trang!
 */
function openCustomerBookingModal(serviceName = '') {
    // Populate service dropdown in modal if not yet populated
    const select = document.getElementById('modal-custbook-service');
    if (select && State.services && State.services.length > 0) {
        select.innerHTML = `<option value="">-- Chọn gói dịch vụ mong muốn --</option>` + State.services.map(s => 
            `<option value="${s.id}">${s.name} - ${formatCurrency(s.price)}</option>`
        ).join('');
    }

    // Set default date to tomorrow if empty
    const dateInput = document.getElementById('modal-custbook-date');
    if (dateInput && !dateInput.value) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }

    // Pre-select service if provided
    if (serviceName && select) {
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].text.toLowerCase().includes(serviceName.toLowerCase())) {
                select.selectedIndex = i;
                break;
            }
        }
    }

    // Auto-fill from current looked-up customer or logged in user
    const lookupPhone = document.getElementById('customer-lookup-phone')?.value;
    const modalPhone = document.getElementById('modal-custbook-phone');
    if (modalPhone && lookupPhone && !modalPhone.value) {
        modalPhone.value = lookupPhone;
    }

    openModal('modal-customer-online-booking');
}

/**
 * Cuộn tới section cụ thể hoặc mở Modal nếu là Đặt lịch
 */
function scrollToCustomerSection(sectionId) {
    if (sectionId === 'online-booking-section') {
        openCustomerBookingModal();
        return;
    }

    if (State.activeTab !== 'customer_portal') {
        switchTab('customer_portal');
    }
    setTimeout(() => {
        const el = document.getElementById(sectionId);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

/**
 * Chọn dịch vụ từ Bảng giá để đặt lịch nhanh - Mở Popup Modal ngay, không nhảy trang
 */
function selectServiceToBook(serviceName) {
    openCustomerBookingModal(serviceName);
}

/**
 * Đăng xuất khỏi hệ thống
 */
function logout(showLoginAfter = false) {
    State.token = null;
    State.currentUser = null;
    localStorage.removeItem('petcare_token');
    
    // Đóng tất cả modal thông tin tài khoản nếu đang mở
    closeModal('modal-user-profile');
    
    updateUserUI();
    switchTab('customer_portal');
    
    if (showLoginAfter) {
        openLoginModal();
        showToast('Đã đăng xuất. Vui lòng đăng nhập bằng tài khoản mới.', 'info');
    } else {
        showToast('Bạn đã đăng xuất an toàn khỏi hệ thống.', 'info');
    }
}

/**
 * Đổi sang tài khoản khác (Đăng xuất & Mở modal Đăng Nhập)
 */
function switchAccount() {
    logout(true);
}

/**
 * Cập nhật giao diện người dùng theo trạng thái đăng nhập & RBAC
 */
function updateUserUI() {
    const userBadge = document.getElementById('user-profile-badge');
    const userNameSpan = document.getElementById('current-user-name');
    const loginPromptBtn = document.getElementById('nav-login-btn');
    const registerPromptBtn = document.getElementById('nav-register-btn');
    const logoutBtn = document.getElementById('nav-logout-btn');
    const brandBadge = document.getElementById('brand-mode-badge');
    const adminNavMenu = document.getElementById('nav-menu-admin');
    const customerNavMenu = document.getElementById('nav-menu-customer');

    if (State.currentUser && State.currentUser.role !== 'CUSTOMER') {
        // ========== ĐÃ ĐĂNG NHẬP NHÂN VIÊN / QUẢN TRỊ (ADMIN / RECEPTIONIST / STAFF) ==========
        const role = State.currentUser.role;

        if (adminNavMenu) adminNavMenu.style.display = 'flex';
        if (customerNavMenu) customerNavMenu.style.display = 'none';

        if (userNameSpan) userNameSpan.textContent = State.currentUser.full_name;
        if (userBadge) {
            userBadge.style.display = 'inline-flex';
            userBadge.className = `role-badge ${role.toLowerCase()} cursor-pointer flex items-center gap-1.5 px-3 py-1 rounded-full font-bold text-xs`;
            let roleIcon = 'fa-user-shield';
            if (role === 'RECEPTIONIST') roleIcon = 'fa-headset';
            if (role === 'STAFF') roleIcon = 'fa-scissors';
            userBadge.innerHTML = `<i class="fa-solid ${roleIcon}"></i> <span>${State.currentUser.full_name} (${role})</span>`;
            userBadge.onclick = () => openProfileModal();
        }
        if (loginPromptBtn) loginPromptBtn.style.display = 'none';
        if (registerPromptBtn) registerPromptBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-flex';

        if (brandBadge) {
            brandBadge.textContent = `${role} • QUẢN TRỊ`;
            brandBadge.style.background = role === 'ADMIN' ? 'rgba(244, 63, 94, 0.2)' : (role === 'RECEPTIONIST' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(59, 130, 246, 0.2)');
            brandBadge.style.color = role === 'ADMIN' ? '#fb7185' : (role === 'RECEPTIONIST' ? '#34d399' : '#60a5fa');
        }

    } else {
        // ========== GIAO DIỆN KHÁCH HÀNG (CUSTOMER / CHƯA ĐĂNG NHẬP) ==========
        if (adminNavMenu) adminNavMenu.style.display = 'none';
        if (customerNavMenu) customerNavMenu.style.display = 'flex';

        if (State.currentUser) {
            // Đã đăng nhập vai trò CUSTOMER
            if (userBadge) {
                userBadge.style.display = 'inline-flex';
                userBadge.className = 'role-badge customer cursor-pointer flex items-center gap-1.5 px-3 py-1 rounded-full font-bold text-xs';
                userBadge.innerHTML = `<i class="fa-solid fa-paw"></i> <span>${State.currentUser.full_name}</span>`;
                userBadge.onclick = () => openProfileModal();
            }
            if (loginPromptBtn) loginPromptBtn.style.display = 'none';
            if (registerPromptBtn) registerPromptBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'inline-flex';
        } else {
            // Khách vãng lai chưa đăng nhập
            if (userBadge) userBadge.style.display = 'none';
            if (loginPromptBtn) loginPromptBtn.style.display = 'inline-flex';
            if (registerPromptBtn) registerPromptBtn.style.display = 'inline-flex';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }

        if (brandBadge) {
            brandBadge.textContent = '🐾 CỔNG KHÁCH HÀNG';
            brandBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            brandBadge.style.color = '#34d399';
        }
    }

    // Role-based visibility for Admin Navigation Tabs
    enforceRBAC();
}

/**
 * Phân quyền hiển thị theo Role (RBAC)
 */
function enforceRBAC() {
    const role = State.currentUser ? State.currentUser.role : 'CUSTOMER';
    console.log(`[RBAC] Áp dụng phân quyền cho vai trò: ${role}`);

    // Lọc hiển thị các item trong Menu Quản Trị
    const adminNavItems = document.querySelectorAll('#nav-menu-admin .nav-item');
    adminNavItems.forEach(item => {
        const allowedRoles = (item.getAttribute('data-role') || '').split(',').map(r => r.trim());
        if (role === 'ADMIN' || allowedRoles.includes(role)) {
            item.style.display = 'inline-flex';
        } else {
            item.style.display = 'none';
        }
    });

    // Nếu là Khách Hàng hoặc chưa đăng nhập mà đang ở tab quản trị cấm -> Chuyển về Cổng Khách Hàng
    if (role === 'CUSTOMER') {
        const forbiddenTabs = ['dashboard', 'inventory', 'invoices', 'care', 'vaccinations', 'pets', 'appointments', 'ai_studio'];
        if (forbiddenTabs.includes(State.activeTab)) {
            switchTab('customer_portal');
        }
    } else if (role === 'STAFF') {
        const staffForbiddenTabs = ['inventory', 'invoices', 'dashboard'];
        if (staffForbiddenTabs.includes(State.activeTab)) {
            switchTab('appointments');
        }
    } else if (role === 'RECEPTIONIST') {
        const receptionForbiddenTabs = ['inventory'];
        if (receptionForbiddenTabs.includes(State.activeTab)) {
            switchTab('dashboard');
        }
    }
}

/**
 * Mở modal Thông tin tài khoản người dùng
 */
function openProfileModal() {
    if (!State.currentUser) {
        openLoginModal();
        return;
    }

    const u = State.currentUser;
    const nameEl = document.getElementById('profile-modal-fullname');
    const userEl = document.getElementById('profile-modal-username');
    const roleEl = document.getElementById('profile-modal-role');
    const phoneEl = document.getElementById('profile-modal-phone');
    const emailEl = document.getElementById('profile-modal-email');
    const statusEl = document.getElementById('profile-modal-status');
    const iconEl = document.getElementById('profile-modal-icon');

    if (nameEl) nameEl.textContent = u.full_name;
    if (userEl) userEl.textContent = u.username;
    if (phoneEl) phoneEl.textContent = u.phone || 'Chưa cập nhật';
    if (emailEl) emailEl.textContent = u.email || 'Chưa cập nhật';
    if (statusEl) statusEl.innerHTML = u.is_active ? '<span style="color: #10b981;"><i class="fa-solid fa-circle-check"></i> Đang hoạt động</span>' : '<span style="color: #ef4444;"><i class="fa-solid fa-ban"></i> Đang khóa</span>';

    const adminMgmtBtn = document.getElementById('btn-open-user-mgmt');
    if (adminMgmtBtn) {
        adminMgmtBtn.style.display = u.role === 'ADMIN' ? 'inline-flex' : 'none';
    }

    if (roleEl) {
        let roleName = 'Quản trị viên (Admin)';
        let roleColor = 'red';
        let iconName = 'fa-user-shield';
        if (u.role === 'RECEPTIONIST') {
            roleName = 'Lễ tân tiếp đón (Receptionist)';
            roleColor = 'green';
            iconName = 'fa-headset';
        } else if (u.role === 'STAFF') {
            roleName = 'Kỹ thuật viên chăm sóc (Groomer / Staff)';
            roleColor = 'blue';
            iconName = 'fa-scissors';
        } else if (u.role === 'CUSTOMER') {
            roleName = 'Khách Hàng (Chủ thú cưng / VIP)';
            roleColor = 'emerald';
            iconName = 'fa-paw';
        }
        roleEl.innerHTML = `<span class="role-badge ${u.role.toLowerCase()}"><i class="fa-solid ${iconName}"></i> ${roleName}</span>`;
        if (iconEl) iconEl.className = `fa-solid ${iconName}`;
    }

    openModal('modal-user-profile');
}

/**
 * ================= ADMIN USER MANAGEMENT MODULE =================
 */

function openUserManagementModal() {
    openModal('modal-user-management');
    loadAllUsersForAdmin();
}

let _cachedAdminUsers = [];

async function loadAllUsersForAdmin() {
    const tbody = document.getElementById('admin-users-table-body');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem; color: #818cf8;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p style="margin-top: 8px;">Đang tải danh sách tài khoản...</p></td></tr>`;

    try {
        const users = await apiCall('/auth/users');
        _cachedAdminUsers = users || [];
        filterAdminUsers();
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #fb7185; padding: 1.5rem;">Lỗi tải dữ liệu: ${e.message}</td></tr>`;
    }
}

function filterAdminUsers() {
    const search = (document.getElementById('admin-user-search')?.value || '').toLowerCase().trim();
    const roleFilter = document.getElementById('admin-user-role-filter')?.value || '';

    let filtered = _cachedAdminUsers;
    if (roleFilter) {
        filtered = filtered.filter(u => u.role === roleFilter);
    }
    if (search) {
        filtered = filtered.filter(u => 
            (u.full_name && u.full_name.toLowerCase().includes(search)) ||
            (u.username && u.username.toLowerCase().includes(search)) ||
            (u.phone && u.phone.includes(search)) ||
            (u.email && u.email.toLowerCase().includes(search))
        );
    }
    renderAdminUsersTable(filtered);
}

function renderAdminUsersTable(users) {
    const tbody = document.getElementById('admin-users-table-body');
    if (!tbody) return;

    if (!users || users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 1.8rem; color: var(--text-muted);"><i class="fa-solid fa-circle-info" style="margin-right: 6px;"></i> Không tìm thấy tài khoản người dùng phù hợp.</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map(u => {
        const statusBadge = u.is_active 
            ? `<span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Hoạt động</span>`
            : `<span class="badge badge-danger"><i class="fa-solid fa-ban"></i> Đang khóa</span>`;

        return `
            <tr>
                <td>
                    <strong style="color: #fff;">${u.full_name}</strong>
                    <div style="font-size: 0.78rem; color: var(--text-dim); font-family: monospace;">@${u.username}</div>
                </td>
                <td>
                    <div><i class="fa-solid fa-phone" style="font-size: 0.75rem; color: var(--text-dim);"></i> ${u.phone || 'Chưa cập nhật'}</div>
                    <div style="font-size: 0.78rem; color: var(--text-muted);">${u.email || ''}</div>
                </td>
                <td>
                    <select onchange="handleAdminChangeRole(${u.id}, this.value)" class="form-control" style="padding: 4px 8px; font-size: 0.8rem; width: auto; display: inline-block; font-weight: 600;">
                        <option value="STAFF" ${u.role === 'STAFF' ? 'selected' : ''}>✂️ Kỹ Thuật Viên (Staff)</option>
                        <option value="RECEPTIONIST" ${u.role === 'RECEPTIONIST' ? 'selected' : ''}>🎧 Lễ Tân (Nhân viên)</option>
                        <option value="ADMIN" ${u.role === 'ADMIN' ? 'selected' : ''}>👑 Quản Trị Viên (Admin)</option>
                        <option value="CUSTOMER" ${u.role === 'CUSTOMER' ? 'selected' : ''}>🐾 Khách Hàng</option>
                    </select>
                </td>
                <td>${statusBadge}</td>
                <td style="text-align: right;">
                    <button class="btn btn-secondary btn-sm" onclick="handleAdminToggleStatus(${u.id})" title="${u.is_active ? 'Khóa tài khoản' : 'Mở khóa'}">
                        <i class="fa-solid ${u.is_active ? 'fa-lock' : 'fa-lock-open'}"></i> ${u.is_active ? 'Khóa' : 'Mở'}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function handleAdminCreateUser(event) {
    if (event) event.preventDefault();

    const fullname = document.getElementById('admin-create-fullname')?.value?.trim();
    const username = document.getElementById('admin-create-username')?.value?.trim();
    const role = document.getElementById('admin-create-role')?.value || 'STAFF';
    const phone = document.getElementById('admin-create-phone')?.value?.trim();
    const email = document.getElementById('admin-create-email')?.value?.trim();
    const password = document.getElementById('admin-create-password')?.value || '';
    const confirmPassword = document.getElementById('admin-create-confirm-password')?.value || '';
    const submitBtn = document.getElementById('admin-create-submit-btn');

    if (!fullname || !username || !password) {
        showToast('Vui lòng nhập đầy đủ Họ tên, Tên đăng nhập và Mật khẩu!', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Mật khẩu phải chứa ít nhất 6 ký tự!', 'error');
        return;
    }

    if (confirmPassword && password !== confirmPassword) {
        showToast('Mật khẩu xác nhận không trùng khớp!', 'error');
        document.getElementById('admin-create-confirm-password')?.focus();
        return;
    }

    const roleNameMap = {
        'STAFF': '✂️ Kỹ Thuật Viên / Groomer (Staff)',
        'RECEPTIONIST': '🎧 Lễ Tân (Nhân viên tiếp đón)',
        'ADMIN': '👑 Quản Trị Viên (Admin)',
        'CUSTOMER': '🐾 Khách Hàng (Customer)'
    };
    const roleText = roleNameMap[role] || role;

    // Hộp thoại xác nhận trước khi cấp tài khoản
    const confirmed = confirm(
        `XÁC NHẬN CẤP TÀI KHOẢN MỚI:\n\n` +
        `• Họ và tên: ${fullname}\n` +
        `• Tên đăng nhập: @${username}\n` +
        `• Vai trò cấp: ${roleText}\n` +
        `• Số điện thoại: ${phone || 'Chưa có'}\n` +
        `• Email: ${email || 'Chưa có'}\n\n` +
        `Bạn có chắc chắn muốn xác nhận cấp tài khoản cho nhân viên này?`
    );

    if (!confirmed) return;

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang khởi tạo...';
    }

    try {
        const payload = {
            username,
            password,
            full_name: fullname,
            role,
            phone: phone || null,
            email: email || null,
            is_active: true
        };

        const res = await apiCall('/auth/users', 'POST', payload);
        showToast(`🎉 Đã cấp tài khoản thành công cho: ${res.full_name} (${res.role})`, 'success');

        // Reset form inputs
        document.getElementById('admin-create-fullname').value = '';
        document.getElementById('admin-create-username').value = '';
        document.getElementById('admin-create-phone').value = '';
        document.getElementById('admin-create-email').value = '';
        document.getElementById('admin-create-password').value = '';
        if (document.getElementById('admin-create-confirm-password')) {
            document.getElementById('admin-create-confirm-password').value = '';
        }

        // Tải lại bảng
        loadAllUsersForAdmin();

    } catch (e) {
        showToast('Lỗi cấp tài khoản: ' + e.message, 'error');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-user-check"></i> Xác Nhận Cấp Tài Khoản';
        }
    }
}

async function handleAdminChangeRole(userId, newRole) {
    try {
        await apiCall(`/auth/users/${userId}/role`, 'PUT', { role: newRole });
        showToast(`Đã cập nhật vai trò mới thành: ${newRole}`, 'success');
        loadAllUsersForAdmin();
    } catch (e) {
        showToast('Lỗi cập nhật vai trò: ' + e.message, 'error');
        loadAllUsersForAdmin();
    }
}

async function handleAdminToggleStatus(userId) {
    try {
        const res = await apiCall(`/auth/users/${userId}/toggle-status`, 'PUT');
        showToast(res.message, 'success');
        loadAllUsersForAdmin();
    } catch (e) {
        showToast('Lỗi thay đổi trạng thái: ' + e.message, 'error');
    }
}


