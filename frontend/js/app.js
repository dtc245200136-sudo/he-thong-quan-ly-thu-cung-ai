// ============================================================
// MAIN APPLICATION CONTROLLER
// ============================================================

const app = {
  async init() {
    console.log('PetCare AI Application Initializing...');
    this.restoreUserSession();
    this.setupEventListeners();
    await this.loadInitialData();
    // Guests land on the customer portal; authenticated users go to dashboard
    const startPage = (state.currentRole === 'guest') ? 'portal' : 'dashboard';
    this.navigate(startPage);
  },

  restoreUserSession() {
    const isLoggedOut = localStorage.getItem('petcare_logged_out') === 'true';
    const savedUser = localStorage.getItem('petcare_user');
    if (isLoggedOut) {
      state.currentUser = null;
      state.currentRole = 'guest';
    } else if (savedUser) {
      try {
        state.currentUser = JSON.parse(savedUser);
        state.currentRole = state.currentUser.role;
      } catch (e) {
        console.error(e);
      }
    } else {
      state.currentUser = {
        username: 'admin',
        full_name: 'BS. Quản Lý',
        role: 'admin'
      };
      state.currentRole = 'admin';
    }
    this.updateUserUI();
  },


  setupEventListeners() {
    // Nav tab clicks
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const tab = item.getAttribute('data-tab');
        if (tab) this.navigate(tab);
      });
    });

    // Role switcher
    const roleSelect = document.getElementById('role-select');
    if (roleSelect) {
      roleSelect.addEventListener('change', (e) => {
        state.currentRole = e.target.value;
        showToast(`Đã chuyển sang vai trò: ${e.target.options[e.target.selectedIndex].text}`, 'info');
        this.updateRolePermissions();
      });
    }

    // AI Chat input
    const chatInput = document.getElementById('ai-chat-input');
    const chatSendBtn = document.getElementById('ai-chat-send');
    if (chatSendBtn && chatInput) {
      const sendAction = () => {
        const q = chatInput.value.trim();
        if (q) {
          this.sendAiConsultationMessage(q);
          chatInput.value = '';
        }
      };
      chatSendBtn.addEventListener('click', sendAction);
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendAction();
      });
    }
  },

  updateRolePermissions() {
    const role = state.currentRole || 'guest';
    const adminElements = document.querySelectorAll('.role-admin-only');
    const recElements = document.querySelectorAll('.role-receptionist-only');

    // Quick visibility adjust based on RBAC
    adminElements.forEach(el => {
      el.style.display = (role === 'admin') ? '' : 'none';
    });

    // Hide receptionist-only elements for guests
    recElements.forEach(el => {
      el.style.display = (role === 'guest') ? 'none' : '';
    });

    // Guest: hide management tabs, keep portal + ai-studio visible
    const managementTabs = ['appointments', 'pets', 'care-records', 'vaccines', 'invoices', 'services'];
    managementTabs.forEach(tab => {
      const navItem = document.querySelector(`.nav-item[data-tab="${tab}"]`);
      if (navItem) navItem.style.display = (role === 'guest') ? 'none' : '';
    });
    const dashTab = document.querySelector('.nav-item[data-tab="dashboard"]');
    if (dashTab) dashTab.style.display = (role === 'guest') ? 'none' : '';
  },

  navigate(tabName) {
    state.activeTab = tabName;

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-tab') === tabName);
    });

    // Update pages
    document.querySelectorAll('.page-view').forEach(view => {
      view.classList.toggle('active', view.id === `page-${tabName}`);
    });

    // Fetch tab-specific data
    if (tabName === 'dashboard') this.loadDashboard();
    if (tabName === 'portal') this.loadCustomerPortal();
    if (tabName === 'appointments') this.loadAppointments();
    if (tabName === 'pets') this.loadPets();
    if (tabName === 'owners') this.loadOwners();
    if (tabName === 'services') this.loadServices();
    if (tabName === 'vaccines') this.loadVaccines();
    if (tabName === 'care-records') this.loadCareRecords();
    if (tabName === 'invoices') this.loadInvoices();
    if (tabName === 'ai-studio') this.loadAiStudio();
  },

  async loadInitialData() {
    try {
      const [owners, pets, services] = await Promise.all([
        api.get('/owners'),
        api.get('/pets'),
        api.get('/services')
      ]);
      state.owners = owners;
      state.pets = pets;
      state.services = services;
      this.populateDropdowns();
    } catch (err) {
      console.error('Error loading initial data:', err);
    }
  },

  populateDropdowns() {
    // Populate select boxes in modals
    const petSelects = document.querySelectorAll('.pet-select');
    petSelects.forEach(sel => {
      sel.innerHTML = '<option value="">-- Chọn thú cưng --</option>' +
        state.pets.map(p => `<option value="${p.id}">${p.name} (${p.species} - Chủ: ${p.owner_name || 'Khách'})</option>`).join('');
    });

    const ownerSelects = document.querySelectorAll('.owner-select');
    ownerSelects.forEach(sel => {
      sel.innerHTML = '<option value="">-- Chọn chủ nuôi --</option>' +
        state.owners.map(o => `<option value="${o.id}">${o.name} - ${o.phone}</option>`).join('');
    });

    const serviceSelects = document.querySelectorAll('.service-select');
    serviceSelects.forEach(sel => {
      sel.innerHTML = '<option value="">-- Chọn dịch vụ --</option>' +
        state.services.map(s => `<option value="${s.id}" data-price="${s.price}">${s.name} - ${formatCurrency(s.price)}</option>`).join('');
    });
  },

  // ------------------------------------------------------------
  // DASHBOARD
  // ------------------------------------------------------------
  async loadDashboard() {
    try {
      const stats = await api.get('/analytics/dashboard');
      document.getElementById('stat-total-pets').innerText = stats.total_pets;
      document.getElementById('stat-today-apts').innerText = stats.today_appointments;
      document.getElementById('stat-revenue').innerText = formatCurrency(stats.total_revenue);
      document.getElementById('stat-return-rate').innerText = `${stats.repeat_customer_rate}%`;

      // Render Popular Services
      const popularContainer = document.getElementById('popular-services-list');
      if (popularContainer && stats.popular_services) {
        popularContainer.innerHTML = stats.popular_services.map(s => `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f5f9;">
            <div style="font-size: 0.9rem; color: #1e293b; font-weight: 600; display: flex; align-items: center; gap: 8px;">
              ${s.name}
            </div>
            <div style="font-size: 0.82rem; font-weight: 700; color: #0284c7; background: #e0f2fe; padding: 3px 12px; border-radius: 999px;">
              ${s.count} lượt
            </div>
          </div>
        `).join('');
      }

      // Load today's upcoming appointments
      const today = new Date().toISOString().split('T')[0];
      const todayApts = await api.get('/appointments', { date: today });
      const tbody = document.getElementById('dashboard-today-table');
      if (tbody) {
        if (todayApts.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 20px;">Hôm nay chưa có lịch hẹn nào.</td></tr>';
        } else {
          tbody.innerHTML = todayApts.map(a => components.renderAppointmentRow(a)).join('');
        }
      }
    } catch (err) {
      console.error('Error loading dashboard:', err);
    }
  },

  // ------------------------------------------------------------
  // APPOINTMENTS
  // ------------------------------------------------------------
  async loadAppointments() {
    try {
      const dateFilter = document.getElementById('filter-apt-date')?.value;
      const statusFilter = document.getElementById('filter-apt-status')?.value;
      const params = {};
      if (dateFilter) params.date = dateFilter;
      if (statusFilter) params.status = statusFilter;

      const apts = await api.get('/appointments', params);
      state.appointments = apts;
      const tbody = document.getElementById('appointments-table-body');
      if (tbody) {
        if (apts.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 24px;">Không tìm thấy lịch hẹn phù hợp.</td></tr>';
        } else {
          tbody.innerHTML = apts.map(a => components.renderAppointmentRow(a)).join('');
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openBookingModal(petId = null, ownerId = null) {
    this.populateDropdowns();
    const modal = document.getElementById('booking-modal');
    if (!modal) return;

    if (petId) {
      const petSelect = modal.querySelector('#booking-pet-id');
      if (petSelect) petSelect.value = petId;
    }
    if (ownerId) {
      const ownerSelect = modal.querySelector('#booking-owner-id');
      if (ownerSelect) ownerSelect.value = ownerId;
    }

    // Default to today
    const dateInput = modal.querySelector('#booking-date');
    if (dateInput && !dateInput.value) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }

    modal.classList.add('active');
  },

  async handleBookingSubmit(event) {
    event.preventDefault();
    const petId = parseInt(document.getElementById('booking-pet-id').value);
    const serviceId = parseInt(document.getElementById('booking-service-id').value);
    const date = document.getElementById('booking-date').value;
    const time = document.getElementById('booking-time').value;
    const notes = document.getElementById('booking-notes').value;

    if (!petId || !serviceId || !date || !time) {
      showToast('Vui lòng điền đầy đủ các thông tin bắt buộc!', 'warning');
      return;
    }

    // Find pet's owner
    const pet = state.pets.find(p => p.id === petId);
    const ownerId = pet ? pet.owner_id : 1;

    try {
      await api.post('/appointments', {
        pet_id: petId,
        owner_id: ownerId,
        service_id: serviceId,
        appointment_date: date,
        appointment_time: time,
        notes: notes
      });

      showToast('Đặt lịch hẹn thành công!', 'success');
      this.closeModal('booking-modal');
      this.loadAppointments();
      this.loadDashboard();
    } catch (err) {
      // Conflict detection or validation error
      showToast(err.message, 'error');
    }
  },

  async completeAppointment(id) {
    if (!confirm('Xác nhận hoàn thành buổi làm dịch vụ cho thú cưng?')) return;
    try {
      await api.patch(`/appointments/${id}/complete`);
      showToast('Đã đánh dấu hoàn thành dịch vụ!', 'success');
      this.loadAppointments();
      this.loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async cancelAppointment(id) {
    const reason = prompt('Nhập lý do hủy lịch hẹn:', 'Khách hàng đổi lịch / báo bận');
    if (reason === null) return;
    try {
      await api.patch(`/appointments/${id}/cancel`, { reason });
      showToast('Đã hủy lịch hẹn.', 'info');
      this.loadAppointments();
      this.loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openRescheduleModal(id) {
    const apt = state.appointments.find(a => a.id === id);
    if (!apt) return;

    const modal = document.getElementById('reschedule-modal');
    modal.querySelector('#reschedule-apt-id').value = id;
    modal.querySelector('#reschedule-date').value = apt.appointment_date;
    modal.querySelector('#reschedule-time').value = apt.appointment_time;
    modal.classList.add('active');
  },

  async handleRescheduleSubmit(event) {
    event.preventDefault();
    const id = document.getElementById('reschedule-apt-id').value;
    const newDate = document.getElementById('reschedule-date').value;
    const newTime = document.getElementById('reschedule-time').value;

    try {
      await api.put(`/appointments/${id}`, {
        appointment_date: newDate,
        appointment_time: newTime
      });
      showToast('Đổi lịch hẹn thành công!', 'success');
      this.closeModal('reschedule-modal');
      this.loadAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // ------------------------------------------------------------
  // PETS & OWNERS
  // ------------------------------------------------------------
  async loadPets() {
    try {
      const q = document.getElementById('search-pet-input')?.value;
      const species = document.getElementById('filter-pet-species')?.value;
      const params = {};
      if (q) params.q = q;
      if (species) params.species = species;

      const pets = await api.get('/pets', params);
      state.pets = pets;
      const grid = document.getElementById('pets-grid-container');
      if (grid) {
        if (pets.length === 0) {
          grid.innerHTML = '<div style="color: var(--text-dim); padding: 30px; grid-column: 1/-1; text-align: center;">Chưa có thú cưng nào.</div>';
        } else {
          grid.innerHTML = pets.map(p => components.renderPetCard(p)).join('');
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openAddPetModal() {
    this.populateDropdowns();
    document.getElementById('add-pet-modal').classList.add('active');
  },

  async handleAddPetSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('pet-name-input').value;
    const ownerId = parseInt(document.getElementById('pet-owner-select').value);
    const species = document.getElementById('pet-species-select').value;
    const breed = document.getElementById('pet-breed-input').value;
    const age = parseInt(document.getElementById('pet-age-input').value) || 12;
    const gender = document.getElementById('pet-gender-select').value;
    const weight = parseFloat(document.getElementById('pet-weight-input').value) || 3.0;
    const allergies = document.getElementById('pet-allergies-input').value || 'Không có';
    const medical = document.getElementById('pet-medical-input').value || '';
    const avatar = document.getElementById('pet-avatar-input').value;

    try {
      await api.post('/pets', {
        owner_id: ownerId,
        name: name,
        species: species,
        breed: breed,
        age_months: age,
        gender: gender,
        weight_kg: weight,
        allergies: allergies,
        medical_history: medical,
        avatar_url: avatar
      });

      showToast(`Đã thêm bé '${name}' thành công!`, 'success');
      this.closeModal('add-pet-modal');
      await this.loadInitialData();
      this.loadPets();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async loadOwners() {
    try {
      const q = document.getElementById('search-owner-input')?.value;
      const owners = await api.get('/owners', { q });
      state.owners = owners;
      const tbody = document.getElementById('owners-table-body');
      if (tbody) {
        tbody.innerHTML = owners.map(o => `
          <tr>
            <td style="font-weight: 800; color: #0f172a; font-size: 0.95rem;">${o.name}</td>
            <td style="color: #0284c7; font-weight: 700;">${o.phone}</td>
            <td style="color: #475569; font-weight: 500;">${o.email || '---'}</td>
            <td style="color: #334155; font-weight: 500;">${o.address || '---'}</td>
            <td>
              <span class="badge badge-confirmed">${o.pet_count || 0} bé</span>
            </td>
            <td>
              <button class="quick-action-btn btn-primary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="app.openBookingModal(null, ${o.id})">
                + Đặt lịch
              </button>
            </td>
          </tr>
        `).join('');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openAddOwnerModal() {
    document.getElementById('add-owner-modal').classList.add('active');
  },

  async handleAddOwnerSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('owner-name-input').value;
    const phone = document.getElementById('owner-phone-input').value;
    const email = document.getElementById('owner-email-input').value;
    const address = document.getElementById('owner-address-input').value;

    try {
      await api.post('/owners', { name, phone, email, address });
      showToast(`Đã thêm chủ nuôi '${name}' thành công!`, 'success');
      this.closeModal('add-owner-modal');
      await this.loadInitialData();
      this.loadOwners();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // ------------------------------------------------------------
  // CARE RECORDS
  // ------------------------------------------------------------
  async loadCareRecords() {
    try {
      const records = await api.get('/care-records');
      state.careRecords = records;
      const container = document.getElementById('care-records-timeline');
      if (container) {
        if (records.length === 0) {
          container.innerHTML = '<div style="color: #64748b; padding: 30px; text-align: center; font-weight: 600;">Chưa có hồ sơ chăm sóc nào được ghi nhận.</div>';
        } else {
          container.innerHTML = records.map(r => `
            <div class="card-box" style="margin-bottom: 20px; border: 1.5px solid #e2e8f0; border-left: 5px solid #6366f1; border-radius: 16px; padding: 22px; background: #ffffff; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; gap: 8px;">
                <div style="font-weight: 800; color: #0f172a; font-size: 1.15rem; display: flex; align-items: center; gap: 10px;">
                  <span>Bé <span style="color: #4f46e5;">${r.pet_name}</span></span>
                  <span style="font-weight: 600; font-size: 0.82rem; color: #475569; background: #f1f5f9; padding: 3px 10px; border-radius: 6px; border: 1px solid #e2e8f0;">Ngày: ${formatDateVN(r.record_date)}</span>
                </div>
                <div style="font-size: 0.82rem; color: #4338ca; background: #eef2ff; border: 1px solid #c7d2fe; padding: 4px 12px; border-radius: 999px; font-weight: 700;">
                  Kỹ thuật viên: ${r.staff_name ? r.staff_name.replace('Groomer', 'KTV') : 'PetCare KTV'}
                </div>
              </div>

              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 0.88rem; margin-bottom: 14px;">
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 10px; border: 1px solid #f1f5f9;">
                  <strong style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.3px;">Lông & Da:</strong>
                  <span style="color: #1e293b; font-weight: 600; line-height: 1.45;">${r.fur_skin_condition || 'Bình thường'}</span>
                </div>
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 10px; border: 1px solid #f1f5f9;">
                  <strong style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.3px;">Cân nặng đo được:</strong>
                  <span style="color: #059669; font-weight: 800; font-size: 1.05rem;">${r.weight_recorded_kg || '---'} kg</span>
                </div>
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 10px; border: 1px solid #f1f5f9;">
                  <strong style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.3px;">Hành vi:</strong>
                  <span style="color: #1e293b; font-weight: 600; line-height: 1.45;">${r.behavior_notes || 'Thân thiện, ngoan'}</span>
                </div>
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 10px; border: 1px solid #f1f5f9;">
                  <strong style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.3px;">Sản phẩm sử dụng:</strong>
                  <span style="color: #1e293b; font-weight: 600; line-height: 1.45;">${r.products_used || 'Dầu tắm spa chuyên dụng'}</span>
                </div>
              </div>

              ${r.staff_notes ? `
                <div style="font-size: 0.86rem; color: #1e293b; margin-bottom: 10px; padding: 10px 14px; background: #fefce8; border-left: 4px solid #eab308; border-radius: 8px; border: 1px solid #fef08a;">
                  <strong style="color: #854d0e;">Ghi chú KTV:</strong> <span style="font-weight: 600; color: #1e293b;">${r.staff_notes}</span>
                </div>
              ` : ''}

              ${r.home_care_instructions ? `
                <div style="font-size: 0.88rem; color: #1e1b4b; background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%); padding: 12px 16px; border-radius: 10px; border: 1.5px solid #bfdbfe; line-height: 1.55;">
                  <strong style="color: #1d4ed8; display: inline-flex; align-items: center; gap: 4px;">Lời khuyên chăm sóc tại nhà:</strong> 
                  <span style="color: #0f172a; font-weight: 600; margin-left: 4px;">${r.home_care_instructions}</span>
                </div>
              ` : ''}
            </div>
          `).join('');
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openCareRecordModal(petId, appointmentId = null) {
    const modal = document.getElementById('care-record-modal');
    modal.querySelector('#care-pet-id').value = petId;
    modal.querySelector('#care-apt-id').value = appointmentId || '';
    modal.querySelector('#care-date').value = new Date().toISOString().split('T')[0];
    modal.classList.add('active');
  },

  async handleCareRecordSubmit(event) {
    event.preventDefault();
    const petId = parseInt(document.getElementById('care-pet-id').value);
    const aptId = document.getElementById('care-apt-id').value ? parseInt(document.getElementById('care-apt-id').value) : null;
    const date = document.getElementById('care-date').value;
    const condition = document.getElementById('care-condition').value;
    const weight = parseFloat(document.getElementById('care-weight').value) || null;
    const behavior = document.getElementById('care-behavior').value;
    const products = document.getElementById('care-products').value;
    const notes = document.getElementById('care-staff-notes').value;
    const instructions = document.getElementById('care-instructions').value;

    try {
      await api.post('/care-records', {
        pet_id: petId,
        appointment_id: aptId,
        record_date: date,
        fur_skin_condition: condition,
        weight_recorded_kg: weight,
        behavior_notes: behavior,
        products_used: products,
        staff_notes: notes,
        home_care_instructions: instructions
      });

      showToast('Đã lưu hồ sơ chăm sóc thành công!', 'success');
      this.closeModal('care-record-modal');
      this.loadCareRecords();
      this.loadAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // ------------------------------------------------------------
  // VACCINES & PREVENTION
  // ------------------------------------------------------------
  async loadVaccines() {
    try {
      const status = document.getElementById('filter-vac-status')?.value;
      const params = {};
      if (status) params.status = status;

      const vaccines = await api.get('/vaccines', params);
      state.vaccines = vaccines;
      const tbody = document.getElementById('vaccines-table-body');
      if (tbody) {
        if (vaccines.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 24px;">Không có lịch nhắc tiêm phòng nào.</td></tr>';
        } else {
          tbody.innerHTML = vaccines.map(v => components.renderVaccineRow(v)).join('');
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async completeVaccine(id) {
    if (!confirm('Xác nhận thú cưng đã hoàn thành mũi tiêm/tẩy giun này?')) return;
    try {
      await api.patch(`/vaccines/${id}/complete`);
      showToast('Đã ghi nhận hoàn thành mũi tiêm!', 'success');
      this.loadVaccines();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openAddVaccineModal() {
    this.populateDropdowns();
    document.getElementById('add-vaccine-modal').classList.add('active');
  },

  async handleAddVaccineSubmit(event) {
    event.preventDefault();
    const petId = parseInt(document.getElementById('vac-pet-id').value);
    const name = document.getElementById('vac-name').value;
    const dose = parseInt(document.getElementById('vac-dose').value) || 1;
    const lastDate = document.getElementById('vac-last-date').value || null;
    const dueDate = document.getElementById('vac-due-date').value;
    const notes = document.getElementById('vac-notes').value;

    try {
      await api.post('/vaccines', {
        pet_id: petId,
        vaccine_name: name,
        dose_number: dose,
        administered_date: lastDate,
        next_due_date: dueDate,
        notes: notes
      });

      showToast('Đã thêm lịch nhắc tiêm thành công!', 'success');
      this.closeModal('add-vaccine-modal');
      this.loadVaccines();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // ------------------------------------------------------------
  // INVOICES & BILLING
  // ------------------------------------------------------------
  async loadInvoices() {
    try {
      const invoices = await api.get('/invoices');
      state.invoices = invoices;
      const tbody = document.getElementById('invoices-table-body');
      if (tbody) {
        if (invoices.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 24px;">Chưa có hóa đơn nào.</td></tr>';
        } else {
          tbody.innerHTML = invoices.map(i => components.renderInvoiceRow(i)).join('');
        }
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  openCreateInvoiceModal(appointmentId, ownerId, defaultTotal = 0) {
    const modal = document.getElementById('create-invoice-modal');
    modal.querySelector('#inv-apt-id').value = appointmentId || '';
    modal.querySelector('#inv-owner-id').value = ownerId;
    modal.querySelector('#inv-total').value = defaultTotal;
    modal.querySelector('#inv-discount').value = 0;
    modal.classList.add('active');
  },

  async handleCreateInvoiceSubmit(event) {
    event.preventDefault();
    const aptId = document.getElementById('inv-apt-id').value ? parseInt(document.getElementById('inv-apt-id').value) : null;
    const ownerId = parseInt(document.getElementById('inv-owner-id').value);
    const total = parseFloat(document.getElementById('inv-total').value) || 0;
    const discount = parseFloat(document.getElementById('inv-discount').value) || 0;
    const method = document.getElementById('inv-method').value;
    const status = document.getElementById('inv-status').value;
    const notes = document.getElementById('inv-notes').value;

    try {
      await api.post('/invoices', {
        appointment_id: aptId,
        owner_id: ownerId,
        total_amount: total,
        discount_amount: discount,
        payment_method: method,
        payment_status: status,
        notes: notes
      });

      showToast('Lập hóa đơn thanh toán thành công!', 'success');
      this.closeModal('create-invoice-modal');
      this.loadInvoices();
      this.loadAppointments();
      this.loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async markInvoicePaid(id) {
    try {
      await api.patch(`/invoices/${id}/pay`, { payment_method: 'Tiền mặt' });
      showToast('Đã xác nhận thanh toán hóa đơn!', 'success');
      this.loadInvoices();
      this.loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  viewInvoiceDetail(id) {
    const inv = state.invoices.find(i => i.id === id);
    if (!inv) return;

    const modal = document.getElementById('invoice-detail-modal');
    const container = modal.querySelector('#invoice-print-area');
    container.innerHTML = `
      <div style="border-bottom: 2px dashed #cbd5e1; padding-bottom: 16px; margin-bottom: 16px; display: flex; justify-content: space-between;">
        <div>
          <h3 style="color: #0f172a; margin-bottom: 4px;">PETCARE SPA & CLINIC</h3>
          <p style="font-size: 0.8rem; color: #64748b;">Trường ĐH CNTT & TT (ICTU) - ĐH Thái Nguyên</p>
          <p style="font-size: 0.8rem; color: #64748b;">Hotline: 0987.654.321 • Website: petcare.ictu.edu.vn</p>
        </div>
        <div style="text-align: right;">
          <h4 style="color: #0d9488; margin-bottom: 4px;">HÓA ĐƠN THANH TOÁN</h4>
          <div style="font-weight: 700; font-size: 0.85rem;">Mã: ${inv.invoice_code}</div>
          <div style="font-size: 0.75rem; color: #64748b;">Ngày lập: ${new Date(inv.created_at).toLocaleDateString('vi-VN')}</div>
        </div>
      </div>

      <div style="margin-bottom: 16px; font-size: 0.85rem; line-height: 1.6;">
        <div><strong>Khách hàng:</strong> ${inv.owner_name} - ${inv.owner_phone}</div>
        <div><strong>Thú cưng phục vụ:</strong> Bé ${inv.pet_name || 'Cưng'}</div>
        <div><strong>Dịch vụ:</strong> ${inv.service_name || 'Dịch vụ chăm sóc tổng hợp'}</div>
      </div>

      <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 0.85rem;">
        <thead>
          <tr style="background: #f1f5f9; border-bottom: 1px solid #cbd5e1;">
            <th style="padding: 8px; text-align: left;">Mô tả</th>
            <th style="padding: 8px; text-align: right;">Đơn giá</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding: 8px;">Dịch vụ chăm sóc (${inv.service_name || 'Gói Spa'})</td>
            <td style="padding: 8px; text-align: right;">${formatCurrency(inv.total_amount)}</td>
          </tr>
          ${inv.discount_amount > 0 ? `
            <tr style="color: #ef4444;">
              <td style="padding: 8px;">Ưu đãi / Giảm giá</td>
              <td style="padding: 8px; text-align: right;">- ${formatCurrency(inv.discount_amount)}</td>
            </tr>
          ` : ''}
          <tr style="font-weight: 700; border-top: 2px solid #0f172a; font-size: 0.95rem;">
            <td style="padding: 8px;">TỔNG THANH TOÁN:</td>
            <td style="padding: 8px; text-align: right; color: #0d9488;">${formatCurrency(inv.final_amount)}</td>
          </tr>
        </tbody>
      </table>

      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 14px;">
        <div style="font-size: 0.8rem; color: #64748b;">
          <div>Hình thức: <strong>${inv.payment_method}</strong></div>
          <div>Trạng thái: <strong style="color: ${inv.payment_status === 'paid' ? '#10b981' : '#f59e0b'};">${inv.payment_status === 'paid' ? 'ĐÃ THANH TOÁN' : 'CHỜ THANH TOÁN'}</strong></div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 0.72rem; color: #94a3b8; margin-bottom: 4px;">Quét mã VietQR</div>
          <div style="width: 70px; height: 70px; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 4px;">
            [ QR Code ]
          </div>
        </div>
      </div>
    `;
    modal.classList.add('active');
  },

  // ------------------------------------------------------------
  // SERVICES
  // ------------------------------------------------------------
  async loadServices() {
    try {
      const services = await api.get('/services');
      state.services = services;
      const tbody = document.getElementById('services-table-body');
      if (tbody) {
        tbody.innerHTML = services.map(s => `
          <tr>
            <td style="font-weight: 800; color: #0f172a; font-size: 0.95rem;">${s.name}</td>
            <td><span class="pet-breed-tag">${s.category}</span></td>
            <td style="color: #334155; font-weight: 600;">${s.duration_minutes} phút</td>
            <td style="font-weight: 800; color: #0284c7;">${formatCurrency(s.price)}</td>
            <td style="font-size: 0.85rem; color: #475569; max-width: 300px; font-weight: 500;">${s.description || ''}</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  // ------------------------------------------------------------
  // AI STUDIO (Reminders, Summaries, Consultation Chat)
  // ------------------------------------------------------------
  async loadAiStudio() {
    this.switchAiTab('chat');
    this.populateDropdowns();
    this.loadAiSettings();
    this.loadAiLogs();
  },

  switchAiTab(tab) {
    document.querySelectorAll('.ai-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-ai-tab') === tab);
    });

    document.querySelectorAll('.ai-tab-panel').forEach(panel => {
      panel.style.display = (panel.id === `ai-panel-${tab}`) ? 'flex' : 'none';
    });
  },

  // AI Feature 1: Reminder Generator Modal & Logic
  openAiReminderModal(type, targetId) {
    const modal = document.getElementById('ai-reminder-modal');
    modal.querySelector('#ai-rem-type').value = type;
    modal.querySelector('#ai-rem-target-id').value = targetId;
    modal.querySelector('#ai-rem-output').style.display = 'none';
    modal.classList.add('active');

    // Auto generate default friendly reminder
    this.generateAiReminder();
  },

  async generateAiReminder() {
    const modal = document.getElementById('ai-reminder-modal');
    const type = modal.querySelector('#ai-rem-type').value;
    const targetId = parseInt(modal.querySelector('#ai-rem-target-id').value);
    const tone = modal.querySelector('#ai-rem-tone').value;
    const customNote = modal.querySelector('#ai-rem-note').value;

    const outputBox = modal.querySelector('#ai-rem-output');
    outputBox.style.display = 'block';
    outputBox.innerHTML = '<div style="color: var(--accent); padding: 10px;">AI đang phân tích dữ liệu và soạn tin nhắn phù hợp...</div>';

    try {
      const payload = {
        reminder_type: type,
        tone: tone,
        custom_note: customNote
      };
      if (type === 'appointment') payload.appointment_id = targetId;
      else payload.vaccine_reminder_id = targetId;

      const resp = await api.post('/ai/reminder', payload);

      outputBox.innerHTML = `
        <div style="background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius-md); padding: 16px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.8rem; color: var(--text-dim);">
            <span>Đích gửi: <strong>${resp.recipient_name}</strong> (${resp.recipient_phone})</span>
            <span style="color: var(--primary);">Engine: ${resp.model_used}</span>
          </div>
          <div id="ai-reminder-message-text" style="white-space: pre-line; color: #f8fafc; font-size: 0.88rem; line-height: 1.6; background: rgba(0,0,0,0.25); padding: 12px; border-radius: var(--radius-sm); margin-bottom: 12px;">${resp.message}</div>
          <div style="display: flex; gap: 8px;">
            <button class="quick-action-btn btn-primary" onclick="app.copyToClipboard('ai-reminder-message-text')">
              Sao chép tin nhắn
            </button>
            <button class="quick-action-btn btn-ai-magic" onclick="alert('Mô phỏng: Đã gửi tin nhắn nhắc nhở qua Zalo OA tới khách hàng ${resp.recipient_name}!')">
              Gửi Zalo OA
            </button>
          </div>
        </div>
      `;
    } catch (err) {
      outputBox.innerHTML = `<div style="color: var(--danger); padding: 10px;">Lỗi: ${err.message}</div>`;
    }
  },

  // AI Feature 2: Pet Care Summary
  async triggerAiSummary(petId) {
    this.navigate('ai-studio');
    this.switchAiTab('summary');
    const petSelect = document.getElementById('ai-summary-pet-select');
    if (petSelect) {
      petSelect.value = petId;
      this.generatePetSummary();
    }
  },

  async generatePetSummary() {
    const petId = parseInt(document.getElementById('ai-summary-pet-select').value);
    if (!petId) {
      showToast('Vui lòng chọn một thú cưng để tóm tắt hồ sơ!', 'warning');
      return;
    }

    const container = document.getElementById('ai-summary-result');
    container.innerHTML = '<div style="color: var(--accent); padding: 24px; text-align: center;">AI đang đọc toàn bộ lịch sử chăm sóc và phân tích tình trạng da lông, thể chất...</div>';

    try {
      const resp = await api.post('/ai/summary', { pet_id: petId });

      let alertsHtml = '';
      if (resp.health_alerts && resp.health_alerts.length > 0) {
        alertsHtml = `
          <div class="ai-disclaimer-box" style="margin: 0 0 16px 0; background: rgba(245, 158, 11, 0.15); border-left-color: var(--warning);">
            <span class="badge badge-warning" style="font-weight: 700; font-size: 0.75rem;">LƯU Ý</span>
            <div style="color: #fde68a; font-size: 0.82rem; line-height: 1.5;">
              <strong>Cảnh báo sức khỏe đáng lưu ý:</strong>
              <ul style="margin-left: 18px; margin-top: 4px;">
                ${resp.health_alerts.map(a => `<li>${a}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      }

      container.innerHTML = `
        <div style="padding: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <h3 style="color: #0f172a; font-family: var(--font-heading); font-weight: 800;">Báo cáo Tóm tắt Hồ sơ Bé ${resp.pet_name}</h3>
            <span style="font-size: 0.78rem; color: #0284c7; background: #e0f2fe; padding: 4px 12px; border-radius: var(--radius-full); font-weight: 700; border: 1px solid #bae6fd;">Engine: ${resp.model_used}</span>
          </div>

          ${alertsHtml}

          <div style="white-space: pre-line; line-height: 1.65; color: #1e293b; font-size: 0.92rem; font-weight: 500; background: #ffffff; padding: 18px; border-radius: var(--radius-md); border: 1.5px solid #e2e8f0; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);">
            ${resp.summary_markdown}
          </div>

          ${resp.suggested_actions && resp.suggested_actions.length > 0 ? `
            <div style="margin-top: 14px; padding: 14px 16px; background: #ecfdf5; border-radius: var(--radius-sm); border-left: 4px solid #059669; border: 1px solid #a7f3d0; font-size: 0.86rem; color: #065f46;">
              <strong style="color: #047857; font-size: 0.9rem;">Đề xuất dịch vụ tiếp theo từ AI:</strong>
              <ul style="margin-left: 18px; margin-top: 6px; color: #1e293b; font-weight: 500;">
                ${resp.suggested_actions.map(act => `<li>${act}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<div style="color: var(--danger); padding: 20px;">Lỗi: ${err.message}</div>`;
    }
  },

  // AI Feature 3: Consultation Chat with Emergency Guardrail
  async sendAiConsultationMessage(questionText) {
    const messagesBox = document.getElementById('ai-chat-messages');
    if (!messagesBox) return;

    // Append User Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.innerText = questionText;
    messagesBox.appendChild(userBubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    // Append AI Typing indicator
    const aiBubble = document.createElement('div');
    aiBubble.className = 'chat-bubble ai';
    aiBubble.innerHTML = '<span style="color: var(--accent);">PetCare AI đang suy nghĩ...</span>';
    messagesBox.appendChild(aiBubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
      const resp = await api.post('/ai/consultation', {
        question: questionText
      });

      // Check if dangerous emergency
      let alertBanner = '';
      if (resp.is_urgent_medical_alert) {
        const hotline = resp.emergency_hotline || '0988.111.222';
        alertBanner = `
          <div class="emergency-triage-banner" style="margin: 0 0 14px 0;">
            <div class="emergency-triage-header">
              <div class="emergency-triage-title">
                <span style="font-size: 1.3rem;">🚨</span>
                <span>BÁO ĐỘNG ĐỎ: CA CẤP CỨU THÚ Y KHẨN CẤP (EMERGENCY TRIAGE)</span>
              </div>
              <span class="emergency-triage-badge">Ưu tiên cấp 1</span>
            </div>
            <div style="font-size: 0.84rem; color: #fee2e2; line-height: 1.5; margin-bottom: 8px;">
              Hệ thống Guardrail AI phát hiện triệu chứng nguy kịch đe dọa trực tiếp đến tính mạng! <strong>Không tự ý điều trị tại nhà - Đưa bé đến bệnh viện ngay.</strong>
            </div>
            <div class="emergency-hotline-box">
              <div class="emergency-hotline-info">
                <span style="font-size: 1.5rem;">📞</span>
                <div>
                  <div style="font-size: 0.72rem; color: #fca5a5; font-weight: 700; text-transform: uppercase;">Hotline Cấp Cứu Thú Y Trực Tiếp 24/7:</div>
                  <div class="emergency-hotline-num">${hotline}</div>
                </div>
              </div>
              <a href="tel:${hotline.replace(/\./g, '')}" class="emergency-call-btn">
                <span>GỌI BÁC SĨ CẤP CỨU NGAY</span>
              </a>
            </div>
          </div>
        `;
      }

      let topicsHtml = '';
      if (resp.recommended_topics && resp.recommended_topics.length > 0) {
        topicsHtml = `
          <div class="topic-pills">
            <span style="font-size: 0.72rem; color: var(--text-dim); display: flex; align-items: center;">Gợi ý:</span>
            ${resp.recommended_topics.map(t => `<span class="topic-pill" onclick="app.sendAiConsultationMessage('${t}')">${t}</span>`).join('')}
          </div>
        `;
      }

      aiBubble.innerHTML = `
        ${alertBanner}
        <div style="white-space: pre-line;">${resp.answer}</div>
        <div class="chat-bubble-model">
          <span>Cảnh báo: ${resp.medical_disclaimer}</span>
        </div>
        <div class="chat-bubble-model" style="margin-top: 4px; color: var(--primary);">
          <span>Động cơ AI: ${resp.model_used}</span>
        </div>
        ${topicsHtml}
      `;
      messagesBox.scrollTop = messagesBox.scrollHeight;
    } catch (err) {
      aiBubble.innerHTML = `<span style="color: var(--danger);">Lỗi kết nối AI: ${err.message}</span>`;
    }
  },

  // AI Settings & Audit Logs
  async loadAiSettings() {
    try {
      const cfg = await api.get('/ai/settings');
      const statusText = document.getElementById('ai-engine-status');
      if (statusText) {
        if (cfg.has_gemini_key) {
          statusText.innerHTML = 'Đang dùng Gemini 1.5 Flash (API Key đã kích hoạt)';
        } else if (cfg.has_openai_key) {
          statusText.innerHTML = 'Đang dùng OpenAI GPT-3.5 (API Key đã kích hoạt)';
        } else {
          statusText.innerHTML = 'Đang dùng PetCare Heuristic Rule Engine (Chạy nội bộ an toàn 100%)';
        }
      }
    } catch (err) {
      console.error(err);
    }
  },

  async handleSaveAiSettings(event) {
    event.preventDefault();
    const geminiKey = document.getElementById('ai-gemini-key').value;
    const openaiKey = document.getElementById('ai-openai-key').value;

    try {
      await api.post('/ai/settings', {
        gemini_key: geminiKey,
        openai_key: openaiKey
      });
      showToast('Cập nhật cấu hình AI Engine thành công!', 'success');
      this.loadAiSettings();
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async loadAiLogs() {
    try {
      const logs = await api.get('/ai/logs');
      const tbody = document.getElementById('ai-logs-table-body');
      if (tbody) {
        tbody.innerHTML = logs.map(l => `
          <tr>
            <td style="font-weight: 800; color: #0f172a;">${l.feature_type}</td>
            <td style="font-size: 0.82rem; color: #334155; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500;">${l.user_prompt}</td>
            <td style="font-size: 0.78rem; color: #0284c7; font-weight: 700;">${l.model_name}</td>
            <td style="font-size: 0.78rem; color: #64748b; font-weight: 600;">${new Date(l.created_at).toLocaleTimeString('vi-VN')}</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error(err);
    }
  },

  // ------------------------------------------------------------
  // HELPERS
  // ------------------------------------------------------------
  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  },

  openAuthModal(mode = 'login') {
    const modal = document.getElementById('login-modal');
    if (!modal) return;
    this.switchAuthView(mode);
    modal.classList.add('active');
  },

  openStaffProvisionModal() {
    this.openAuthModal('register');
  },

  switchAuthView(mode) {
    const loginView = document.getElementById('auth-view-login');
    const regView = document.getElementById('auth-view-register');
    const modalTitle = document.getElementById('auth-modal-title');
    const modalSubtitle = document.getElementById('auth-modal-subtitle');

    if (mode === 'register') {
      if (loginView) loginView.style.display = 'none';
      if (regView) regView.style.display = 'block';
      if (modalTitle) modalTitle.innerText = 'Cấp Tài Khoản Nhân Viên';
      if (modalSubtitle) modalSubtitle.innerText = 'Admin cấp tài khoản cho Lễ tân & Kỹ thuật viên (KTV)';
    } else {
      if (loginView) loginView.style.display = 'block';
      if (regView) regView.style.display = 'none';
      if (modalTitle) modalTitle.innerText = 'PetCare AI Pro';
      if (modalSubtitle) modalSubtitle.innerText = 'Hệ Thống Quản Lý Thú Cưng Tích Hợp AI';
    }
  },

  togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isPw = (input.type === 'password');
    input.type = isPw ? 'text' : 'password';
    const btn = input.parentElement ? input.parentElement.querySelector('.login-eye-btn') : null;
    if (btn) {
      if (isPw) {
        btn.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
      } else {
        btn.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
      }
    }
  },

  async quickLogin(username, password) {
    try {
      const resp = await api.post('/auth/login', { username, password });
      this.applyLoginSuccess(resp);
    } catch (err) {
      showToast('Lỗi đăng nhập nhanh: ' + err.message, 'error');
    }
  },

  async handleLoginSubmit(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    try {
      const resp = await api.post('/auth/login', { username, password });
      this.applyLoginSuccess(resp);
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  async handleRegisterSubmit(event) {
    event.preventDefault();
    const fullname = document.getElementById('reg-fullname').value.trim();
    const username = document.getElementById('reg-username').value.trim();
    const role = document.getElementById('reg-role').value;
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value.trim();
    const confirmPassword = document.getElementById('reg-confirm-password').value.trim();

    if (password !== confirmPassword) {
      showToast('Mật khẩu và Xác nhận mật khẩu không trùng khớp!', 'warning');
      return;
    }

    const roleName = (role === 'receptionist') ? 'Lễ tân' : 'Kỹ thuật viên (KTV)';

    try {
      const resp = await api.post('/auth/register', {
        full_name: fullname,
        username: username,
        role: role,
        email: email || null,
        password: password
      });

      // Clear input fields
      document.getElementById('reg-fullname').value = '';
      document.getElementById('reg-username').value = '';
      document.getElementById('reg-email').value = '';
      document.getElementById('reg-password').value = '';
      document.getElementById('reg-confirm-password').value = '';

      if (state.currentUser && state.currentUser.role === 'admin') {
        showToast(`Admin đã cấp tài khoản thành công cho ${roleName}: ${fullname} (User: ${username})!`, 'success');
        this.closeModal('login-modal');
      } else {
        showToast(`Cấp tài khoản thành công cho ${roleName}: ${fullname}! Đang đăng nhập...`, 'success');
        this.applyLoginSuccess(resp);
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  },

  applyLoginSuccess(authResp) {
    state.currentUser = authResp.user;
    state.currentRole = authResp.user.role;
    localStorage.setItem('petcare_user', JSON.stringify(authResp.user));
    localStorage.setItem('petcare_token', authResp.access_token);
    localStorage.removeItem('petcare_logged_out');

    this.closeModal('login-modal');
    this.updateUserUI();
    showToast(`Đăng nhập thành công! Vai trò: ${authResp.user.role.toUpperCase()}`, 'success');

    // Auto navigate to relevant page based on role
    if (authResp.user.role === 'admin') {
      this.navigate('dashboard');
    } else if (authResp.user.role === 'staff') {
      this.navigate('appointments');
    }
  },

  logout() {
    state.currentUser = null;
    state.currentRole = 'guest';
    localStorage.removeItem('petcare_user');
    localStorage.removeItem('petcare_token');
    localStorage.setItem('petcare_logged_out', 'true');
    this.updateUserUI();
    showToast('Đã đăng xuất tài khoản thành công.', 'info');
    // Open login modal with options to login or register
    this.openAuthModal('login');
  },

  updateUserUI() {
    const unauthActions = document.getElementById('unauth-actions');
    const authActions = document.getElementById('auth-actions');
    const userBadge = document.getElementById('auth-user-badge');
    const fullnameSpan = document.getElementById('topbar-user-fullname');
    const roleSpan = document.getElementById('topbar-user-role');
    const roleSelect = document.getElementById('role-select');
    const avatarCircle = document.querySelector('.user-avatar-circle');

    if (state.currentUser) {
      if (unauthActions) unauthActions.style.display = 'none';
      if (authActions) authActions.style.display = 'inline-flex';
      if (userBadge) userBadge.style.display = 'inline-flex';
      
      let name = state.currentUser.full_name || state.currentUser.name;
      if (!name || name === 'admin') {
        name = 'BS. Quản Lý';
      }
      if (fullnameSpan) fullnameSpan.innerText = name;
      
      let role = (state.currentUser.role || 'admin').toLowerCase();
      let roleTitle = 'Bác Sĩ Quản Trị';
      if (role === 'receptionist') roleTitle = 'Lễ Tân Phòng Khám';
      else if (role === 'staff') roleTitle = 'Kỹ Thuật Viên';
      if (roleSpan) roleSpan.innerText = roleTitle;

      if (roleSelect) roleSelect.value = state.currentUser.role || 'admin';
      if (avatarCircle) {
        avatarCircle.innerText = 'BS';
      }
    } else {
      if (unauthActions) unauthActions.style.display = 'inline-flex';
      if (authActions) authActions.style.display = 'none';
      if (userBadge) userBadge.style.display = 'none';
    }

    this.updateRolePermissions();
  },

  copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText).then(() => {
      showToast('Đã sao chép nội dung tin nhắn vào bộ nhớ đệm!', 'success');
    }).catch(err => {
      showToast('Lỗi khi sao chép: ' + err, 'error');
    });
  },

  openBookingModal() {
    this.populateDropdowns();
    const modal = document.getElementById('booking-modal');
    if (modal) modal.classList.add('active');
  },

  toggleTheme() {
    document.body.classList.toggle('theme-dark');
    const isDark = document.body.classList.contains('theme-dark');
    localStorage.setItem('petcare_theme', isDark ? 'dark' : 'light');
    showToast(isDark ? 'Đã chuyển sang giao diện Tối' : 'Đã chuyển sang giao diện Sáng', 'info');
  },

  // ------------------------------------------------------------
  // ============================================================
  // DEDICATED CUSTOMER PORTAL & VIP PASS
  // ============================================================
  currentPortalPhone: '0987654321',
  currentPortalTab: 'pets',
  portalCardTiltBound: false,

  initPortal3DCard() {
    const cardWrapper = document.getElementById('portal-vip-card-wrapper');
    const card = document.getElementById('portal-vip-card-element');
    if (!cardWrapper || !card || this.portalCardTiltBound) return;

    this.portalCardTiltBound = true;
    cardWrapper.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -10;
      const rotateY = ((x - centerX) / centerX) * 12;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
    });

    cardWrapper.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  },

  switchPortalTab(tabName) {
    this.currentPortalTab = tabName;
    document.querySelectorAll('.portal-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-portal-tab') === tabName);
    });
    document.querySelectorAll('.portal-tab-pane').forEach(pane => {
      pane.classList.toggle('active', pane.id === `pane-portal-${tabName}`);
    });
  },

  selectPortalOwner(phone) {
    this.currentPortalPhone = phone;
    const input = document.getElementById('portal-phone-input');
    if (input) input.value = phone;

    // Update active chip
    document.querySelectorAll('.portal-quick-chips .portal-chip-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('onclick')?.includes(phone));
    });

    this.loadCustomerPortal(phone);
  },

  searchPortalOwner() {
    const input = document.getElementById('portal-phone-input');
    const phone = input ? input.value.trim() : '';
    if (!phone) {
      showToast('Vui lòng nhập số điện thoại cần tra cứu!', 'warning');
      return;
    }
    this.currentPortalPhone = phone;
    this.loadCustomerPortal(phone);
  },

  openPortalQrModal() {
    const modal = document.getElementById('portal-qr-modal');
    if (modal) modal.style.display = 'flex';
  },

  closePortalQrModal() {
    const modal = document.getElementById('portal-qr-modal');
    if (modal) modal.style.display = 'none';
  },

  downloadOrShareVipPass() {
    const name = document.getElementById('modal-qr-owner-name')?.innerText || 'Hội Viên';
    showToast(`Đã lưu Thẻ VIP điện tử của ${name} thành công!`, 'success');
    this.closePortalQrModal();
  },

  async loadCustomerPortal(targetPhone) {
    const phone = targetPhone || this.currentPortalPhone || '0987654321';
    const input = document.getElementById('portal-phone-input');
    if (input && !input.value) input.value = phone;

    this.initPortal3DCard();

    try {
      // Ensure data is ready
      if (!state.owners || !state.owners.length) {
        await this.loadInitialData();
      }

      // Find owner
      let owner = (state.owners || []).find(o => o.phone && o.phone.replace(/\D/g, '') === phone.replace(/\D/g, ''));
      if (!owner) {
        // Fallback or partial match
        owner = (state.owners || []).find(o => o.phone && o.phone.includes(phone.slice(-4))) || state.owners[0];
      }

      if (!owner) {
        showToast('Chưa tìm thấy dữ liệu chủ nuôi.', 'info');
        return;
      }

      // Filter pets
      const pets = (state.pets || []).filter(p => p.owner_id === owner.id || (p.owner_name && p.owner_name.toLowerCase() === owner.name.toLowerCase()));
      const isDiamond = pets.length >= 2;

      // Update Header Greeting
      const greetingTitle = document.getElementById('portal-greeting-title');
      const greetingSubtitle = document.getElementById('portal-greeting-subtitle');
      if (greetingTitle) {
        greetingTitle.innerHTML = `Chào Mừng <span style="background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${owner.name.toUpperCase()}</span>!`;
      }
      if (greetingSubtitle) {
        const petNames = pets.map(p => `bé <strong>${p.name}</strong>`).join(', ');
        greetingSubtitle.innerHTML = `Hội viên đặc quyền <strong>${isDiamond ? 'Diamond VIP' : 'Gold VIP'}</strong>. Đang kết nối dữ liệu y khoa của ${pets.length > 0 ? petNames : 'các bé cưng'}.`;
      }

      // Update 3D VIP Card
      const nameEl = document.getElementById('portal-vip-owner-name');
      const phoneEl = document.getElementById('portal-vip-phone');
      const pointsEl = document.getElementById('portal-vip-points');
      const petsCountEl = document.getElementById('portal-vip-pets-count');
      const badgeEl = document.getElementById('portal-vip-badge');

      if (nameEl) nameEl.innerText = owner.name.toUpperCase();
      if (phoneEl) {
        const pStr = owner.phone.replace(/\D/g, '');
        phoneEl.innerText = pStr.length >= 7 ? `${pStr.slice(0, 4)} ••• ${pStr.slice(-3)}` : owner.phone;
      }
      if (petsCountEl) petsCountEl.innerText = `${pets.length} BÉ CƯNG`;
      
      const badgeText = isDiamond ? 'DIAMOND VIP' : 'GOLD VIP';
      const pointsText = isDiamond ? '1,450 PTS (Giảm 10%)' : '850 PTS (Giảm 5%)';
      if (badgeEl) badgeEl.innerText = badgeText;
      if (pointsEl) pointsEl.innerText = pointsText;

      // Update QR Modal data
      const qrNameEl = document.getElementById('modal-qr-owner-name');
      const qrPhoneEl = document.getElementById('modal-qr-phone');
      const qrBadgeEl = document.getElementById('modal-qr-tier-badge');
      if (qrNameEl) qrNameEl.innerText = owner.name.toUpperCase();
      if (qrPhoneEl) qrPhoneEl.innerText = owner.phone;
      if (qrBadgeEl) qrBadgeEl.innerText = badgeText;

      // Update KPI Ribbons
      const kpiPets = document.getElementById('portal-kpi-pets');
      const kpiPetsSub = document.getElementById('portal-kpi-pets-sub');
      const kpiPoints = document.getElementById('portal-kpi-points');
      const kpiTierSub = document.getElementById('portal-kpi-tier-sub');
      if (kpiPets) kpiPets.innerText = `${pets.length} Bé Cưng`;
      if (kpiPetsSub) kpiPetsSub.innerText = pets.length > 0 ? pets.map(p => p.name).join(', ') : 'Chưa có bé nào';
      if (kpiPoints) kpiPoints.innerText = isDiamond ? '1,450 PTS' : '850 PTS';
      if (kpiTierSub) kpiTierSub.innerText = isDiamond ? 'Chiết khấu 10% trọn đời' : 'Chiết khấu 5% trọn đời';

      // Update Tab Pill Count
      const tabPetsCount = document.getElementById('tab-count-pets');
      if (tabPetsCount) tabPetsCount.innerText = pets.length;

      // Ensure care records are loaded for rich clinical preview
      if (!state.careRecords || !state.careRecords.length) {
        state.careRecords = await api.get('/care-records').catch(() => []);
      }

      // Render Pets with rich clinical passport
      this.renderPortalPets(pets);

      // Render Vaccines, Appointments, Invoices
      await Promise.all([
        this.renderPortalVaccines(pets),
        this.renderPortalAppointments(owner.id, pets.map(p => p.id)),
        this.renderPortalInvoices(owner.id)
      ]);

      showToast(`Đã mở hồ sơ Cổng Khách Hàng: ${owner.name}`, 'success');
    } catch (err) {
      console.error('Error loading customer portal:', err);
    }
  },

  renderPortalPets(pets) {
    const container = document.getElementById('portal-client-pets-list');
    if (!container) return;

    if (!pets || !pets.length) {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px 20px; color: #64748b;">
          <h4 style="margin: 0 0 6px 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">Chưa có bé cưng nào được liên kết</h4>
          <p style="margin: 0 0 16px 0; font-size: 0.88rem;">Hãy đăng ký lịch dịch vụ đầu tiên để khởi tạo thẻ y bạ sức khoẻ điện tử chuẩn hóa cho bé!</p>
          <button type="button" class="quick-action-btn btn-primary" onclick="app.openBookingModal()">
            Đăng ký lịch chăm sóc đầu tiên
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = pets.map(pet => {
      const isCat = pet.species && (pet.species.toLowerCase().includes('mèo') || pet.species.toLowerCase().includes('cat'));
      const avatarChar = (pet.name || 'P').charAt(0).toUpperCase();
      const avatarClass = isCat ? 'cat' : '';
      const genderText = pet.gender === 'female' ? 'Cái' : 'Đực';
      const weightDisplay = pet.weight_kg ? `${pet.weight_kg} kg` : '3.5 kg';
      
      // Match clinical care record
      const latestCare = (state.careRecords || []).find(r => r.pet_id === pet.id);

      return `
        <div class="portal-pet-passport-card">
          <!-- 1. Top Identity Row -->
          <div class="pet-passport-header">
            <div class="pet-passport-profile">
              <div class="pet-passport-avatar ${avatarClass}">
                ${avatarChar}
              </div>
              <div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <h3 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #0f172a;">${pet.name}</h3>
                  <span class="pet-pill-tag tag-healthy" style="font-size: 0.7rem; font-weight: 800;">Y BẠ SỐ ĐỒNG BỘ</span>
                  <span class="pet-pill-tag" style="background: #f1f5f9; color: #475569; font-size: 0.7rem;">${genderText}</span>
                  <span class="pet-pill-tag" style="background: #e0f2fe; color: #0284c7; font-size: 0.7rem;">${pet.species}</span>
                </div>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                  Giống loài: <strong style="color: #1e293b;">${pet.breed || 'Chưa rõ giống'}</strong> • 
                  Tuổi: <strong style="color: #1e293b;">${pet.age_months ? `${pet.age_months} tháng tuổi` : 'Trưởng thành'}</strong>
                </div>
              </div>
            </div>

            <div class="pet-actions-group">
              <button type="button" class="quick-action-btn btn-primary" style="padding: 8px 16px; font-size: 0.82rem;" onclick="app.openBookingModalForPet(${pet.id})">
                Đặt Lịch Riêng Bé
              </button>
              <button type="button" class="quick-action-btn btn-outline" style="padding: 8px 14px; font-size: 0.82rem;" onclick="app.consultAiForPet('${pet.name}', '${pet.species}')">
                Tư Vấn Bác Sĩ
              </button>
            </div>
          </div>

          <!-- 2. 4-Box Clinical Vitals Grid -->
          <div class="pet-vitals-grid">
            <div class="pet-vital-box">
              <span class="pet-vital-label">Cân Nặng & Thể Trạng</span>
              <div class="pet-vital-value">${weightDisplay}</div>
              <span class="pet-vital-sub">Thể trạng đạt chuẩn</span>
            </div>

            <div class="pet-vital-box">
              <span class="pet-vital-label">Tình Trạng Da & Lông</span>
              <div class="pet-vital-value" style="font-size: 0.84rem; line-height: 1.3;" title="${latestCare ? latestCare.fur_skin_condition : 'Khỏe mạnh, sạch sẽ'}">
                ${latestCare ? (latestCare.fur_skin_condition.length > 28 ? latestCare.fur_skin_condition.slice(0, 28) + '...' : latestCare.fur_skin_condition) : 'Bình thường, lông tơ mượt'}
              </div>
              <span class="pet-vital-sub" style="color: #0284c7;">Đã kiểm tra lâm sàng</span>
            </div>

            <div class="pet-vital-box">
              <span class="pet-vital-label">Tiền Sử Dị Ứng</span>
              <div class="pet-vital-value" style="font-size: 0.84rem; color: ${pet.allergies && pet.allergies !== 'Không' && pet.allergies !== 'None' ? '#dc2626' : '#059669'};">
                ${pet.allergies && pet.allergies !== 'Không' && pet.allergies !== 'None' ? pet.allergies : 'Không ghi nhận dị ứng'}
              </div>
              <span class="pet-vital-sub" style="color: #64748b;">An toàn mỹ phẩm Spa</span>
            </div>

            <div class="pet-vital-box">
              <span class="pet-vital-label">Mã Y Bạ & Microchip</span>
              <div class="pet-vital-value" style="font-size: 0.84rem; color: #4338ca;">
                ${pet.microchip_id ? `Chip ${pet.microchip_id}` : `MED-${String(pet.id).padStart(5, '0')}`}
              </div>
              <span class="pet-vital-sub" style="color: #4338ca;">Định danh y tế quốc tế</span>
            </div>
          </div>

          <!-- 3. Latest Clinical & Grooming Record -->
          <div class="pet-care-record-box">
            <div class="care-record-header-row">
              <span class="care-record-badge">Hồ sơ khám & Chăm sóc gần nhất</span>
              <span class="care-record-date">
                ${latestCare ? formatDateVN(latestCare.record_date) : 'Định kỳ gần nhất'} • KTV/BS: <strong>${latestCare?.staff_name ? latestCare.staff_name.replace('Groomer', 'KTV') : 'BS. CKI Trần Quang Hải'}</strong>
              </span>
            </div>
            <div class="care-record-content-row">
              <div>
                <span style="font-weight: 700; color: #334155;">Chẩn đoán thể trạng & Da lông:</span>
                <span style="color: #475569; display: block; margin-top: 2px;">
                  ${latestCare ? latestCare.fur_skin_condition : 'Lông da sạch sẽ, không phát hiện ve rận hay nấm ngứa, tuyến mồ hôi thông thoáng.'}
                </span>
              </div>
              <div>
                <span style="font-weight: 700; color: #1d4ed8;">Lời khuyên chăm sóc tại nhà:</span>
                <span style="color: #1e3a8a; display: block; margin-top: 2px;">
                  ${latestCare?.home_care_instructions ? latestCare.home_care_instructions : 'Chải lông hàng ngày bằng lược chuyên dụng, sấy khô bàn chân sau khi dạo chơi ngoài trời.'}
                </span>
              </div>
            </div>
            ${latestCare?.products_used ? `
              <div style="font-size: 0.78rem; color: #64748b; border-top: 1px dashed #cbd5e1; padding-top: 6px; margin-top: 2px;">
                <strong>Sản phẩm chuyên dụng đã sử dụng:</strong> ${latestCare.products_used}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  },

  consultAiForPet(petName, species) {
    const prompt = `Bé ${species} ${petName} của tôi dạo này cần lưu ý gì về dinh dưỡng và tiêm phòng?`;
    this.setPortalAiPrompt(prompt);
  },

  async renderPortalVaccines(pets) {
    const container = document.getElementById('portal-client-vaccines-list');
    const kpiVaccines = document.getElementById('portal-kpi-vaccines');
    const kpiVaccinesSub = document.getElementById('portal-kpi-vaccines-sub');
    const tabVaccinesCount = document.getElementById('tab-count-vaccines');
    if (!container) return;

    try {
      const allVaccines = await api.get('/vaccines');
      const petIds = pets.map(p => p.id);
      const myVaccines = (allVaccines || []).filter(v => petIds.includes(v.pet_id));

      if (tabVaccinesCount) tabVaccinesCount.innerText = myVaccines.length;

      const hasOverdue = myVaccines.some(v => v.status === 'overdue');
      if (kpiVaccines) {
        kpiVaccines.innerText = hasOverdue ? 'Có mũi quá hạn' : 'An Toàn 100%';
        kpiVaccines.style.color = hasOverdue ? '#dc2626' : '#059669';
      }
      if (kpiVaccinesSub) {
        kpiVaccinesSub.innerText = hasOverdue ? 'Cần tiêm phòng gấp' : 'Đã phòng ngừa đầy đủ';
      }

      if (!myVaccines.length) {
        container.innerHTML = `
          <div style="text-align: center; padding: 40px 20px; color: #64748b;">
            <h4 style="margin: 0 0 6px 0; color: #1e293b; font-size: 1.05rem; font-weight: 700;">Chưa có lịch tiêm chủng cần nhắc</h4>
            <p style="margin: 0 0 16px 0; font-size: 0.88rem;">Các bé cưng hiện đã được cập nhật an toàn. Quý khách có thể đăng ký mũi vắc-xin mới bất kỳ lúc nào.</p>
            <button type="button" class="quick-action-btn btn-primary" onclick="app.openBookingModal()">
              + Đăng Ký Lịch Tiêm Phòng Mới
            </button>
          </div>
        `;
        return;
      }

      container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 14px;">
            <span style="font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Tổng Mũi Đã Khởi Tạo</span>
            <div style="font-size: 1.15rem; font-weight: 800; color: #0f172a; margin-top: 2px;">${myVaccines.length} Mũi Tiêm</div>
          </div>
          <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 12px 14px;">
            <span style="font-size: 0.7rem; font-weight: 700; color: #065f46; text-transform: uppercase;">Độ Bao Phủ Miễn Dịch</span>
            <div style="font-size: 1.15rem; font-weight: 800; color: #047857; margin-top: 2px;">${hasOverdue ? 'Cần bổ sung' : '100% Đạt Chuẩn'}</div>
          </div>
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 12px 14px;">
            <span style="font-size: 0.7rem; font-weight: 700; color: #1d4ed8; text-transform: uppercase;">Tiêu Chuẩn Vaccine</span>
            <div style="font-size: 1.15rem; font-weight: 800; color: #1e40af; margin-top: 2px;">Quốc Tế (ISO/WHO)</div>
          </div>
        </div>

        <div class="table-container">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Bé Cưng</th>
                <th>Vắc-xin & Phòng Bệnh</th>
                <th>Mũi Số</th>
                <th>Ngày Tiêm Gần Nhất</th>
                <th>Hạn Tiêm Nhắc</th>
                <th>Trạng Thái</th>
                <th>Thao Tác</th>
              </tr>
            </thead>
            <tbody>
              ${myVaccines.map(v => {
                const isOverdue = v.status === 'overdue';
                const isCompleted = v.status === 'completed';
                const statusBadge = isCompleted ?
                  `<span class="badge badge-success">Đã tiêm</span>` :
                  isOverdue ?
                  `<span class="badge badge-danger">Quá hạn tiêm</span>` :
                  `<span class="badge badge-warning">Sắp đến lịch</span>`;

                return `
                  <tr>
                    <td><strong>${v.pet_name || 'Bé cưng'}</strong></td>
                    <td style="color: #0369a1; font-weight: 700;">${v.vaccine_name}</td>
                    <td><span class="badge" style="background: #f1f5f9; color: #475569;">Mũi ${v.dose_number || 1}</span></td>
                    <td>${formatDateVN(v.administered_date) || 'Chưa tiêm'}</td>
                    <td><strong style="color: ${isOverdue ? '#dc2626' : '#0284c7'};">${formatDateVN(v.next_due_date) || 'Theo chỉ định'}</strong></td>
                    <td>${statusBadge}</td>
                    <td>
                      <button type="button" class="quick-action-btn btn-primary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="app.openBookingModalForPet(${v.pet_id})">
                        Đặt lịch tiêm
                      </button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
        <div style="margin-top: 14px; padding: 12px 16px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; font-size: 0.78rem; color: #64748b; line-height: 1.5;">
          <strong>Khuyến cáo theo dõi sau tiêm:</strong> Sau khi tiêm phòng, quý khách giữ ấm cho bé, kiêng tắm trong vòng 3 ngày, theo dõi phản ứng nhiệt độ và liên hệ ngay bác sĩ nếu bé mệt mỏi quá 24h.
        </div>
      `;
    } catch (err) {
      console.error('Error loading portal vaccines:', err);
    }
  },

  async renderPortalAppointments(ownerId, petIds) {
    const container = document.getElementById('portal-client-appointments-list');
    const kpiNextApt = document.getElementById('portal-kpi-next-apt');
    const kpiNextAptSub = document.getElementById('portal-kpi-next-apt-sub');
    const tabAptCount = document.getElementById('tab-count-appointments');
    if (!container) return;

    try {
      const allApts = await api.get('/appointments');
      const myApts = (allApts || []).filter(a => a.owner_id === ownerId || petIds.includes(a.pet_id));

      if (tabAptCount) tabAptCount.innerText = myApts.length;

      // Find upcoming appointment
      const upcomingApt = myApts.find(a => a.status === 'confirmed' || a.status === 'in_progress');
      if (kpiNextApt) {
        if (upcomingApt) {
          kpiNextApt.innerText = `${upcomingApt.appointment_time || '09:00'} (${formatDateVN(upcomingApt.appointment_date)})`;
          kpiNextApt.style.color = '#0284c7';
        } else {
          kpiNextApt.innerText = 'Chưa có lịch';
          kpiNextApt.style.color = '#0f172a';
        }
      }
      if (kpiNextAptSub) {
        kpiNextAptSub.innerText = upcomingApt ? `${upcomingApt.pet_name}: ${upcomingApt.service_name || 'Dịch vụ'}` : 'Bấm đặt lịch ngay';
      }

      let liveTrackerHtml = '';
      if (upcomingApt) {
        const isInProgress = upcomingApt.status === 'in_progress';
        liveTrackerHtml = `
          <div class="portal-tracker-container">
            <div class="portal-tracker-header">
              <div>
                <span style="font-size: 0.72rem; font-weight: 800; color: #0284c7; text-transform: uppercase; letter-spacing: 0.05em;">TIẾN TRÌNH DỊCH VỤ TRỰC TIẾP</span>
                <h4 style="margin: 2px 0 0 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">Bé ${upcomingApt.pet_name} • ${upcomingApt.service_name}</h4>
              </div>
              <span class="badge ${isInProgress ? 'badge-info' : 'badge-warning'}" style="font-size: 0.78rem; padding: 4px 12px;">
                ${isInProgress ? 'Đang Chăm Sóc' : 'Đã Xác Nhận - Chờ Tiếp Đón'}
              </span>
            </div>
            <div class="portal-tracker-steps">
              <div class="tracker-step-item completed">
                <div class="tracker-step-dot">1</div>
                <span class="tracker-step-name">Tiếp đón</span>
              </div>
              <div class="tracker-step-item ${isInProgress ? 'completed' : 'active'}">
                <div class="tracker-step-dot">2</div>
                <span class="tracker-step-name">Khám da lông</span>
              </div>
              <div class="tracker-step-item ${isInProgress ? 'active' : ''}">
                <div class="tracker-step-dot">3</div>
                <span class="tracker-step-name">Tắm Spa thảo mộc</span>
              </div>
              <div class="tracker-step-item">
                <div class="tracker-step-dot">4</div>
                <span class="tracker-step-name">Sấy & Cắt tỉa</span>
              </div>
              <div class="tracker-step-item">
                <div class="tracker-step-dot">5</div>
                <span class="tracker-step-name">Sẵn sàng đón bé</span>
              </div>
            </div>
          </div>
        `;
      }

      if (!myApts.length) {
        container.innerHTML = `
          <div style="text-align: center; padding: 36px 20px; color: #64748b;">
            <h4 style="margin: 0 0 6px 0; color: #1e293b; font-size: 1.05rem; font-weight: 700;">Chưa có lịch hẹn nào gần đây</h4>
            <p style="margin: 0 0 16px 0; font-size: 0.88rem;">Hãy chọn gói dịch vụ để chăm sóc bé chu đáo nhất với ưu đãi giảm giá 10% trọn đời!</p>
            <button type="button" class="quick-action-btn btn-primary" onclick="app.openBookingModal()">
              + Đặt Lịch Cho Bé Ngay
            </button>
          </div>
        `;
        return;
      }

      container.innerHTML = `
        ${liveTrackerHtml}
        <div class="table-container">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Ngày Hẹn</th>
                <th>Giờ</th>
                <th>Bé Cưng</th>
                <th>Gói Dịch Vụ</th>
                <th>Trạng Thái</th>
                <th>Thao Tác</th>
              </tr>
            </thead>
            <tbody>
              ${myApts.slice(0, 8).map(a => {
                const statusText = a.status === 'completed' ? 'Đã hoàn thành' :
                  a.status === 'in_progress' ? 'Đang chăm sóc' :
                  a.status === 'cancelled' ? 'Đã hủy' : 'Đã xác nhận';
                const badgeClass = a.status === 'completed' ? 'badge-success' :
                  a.status === 'in_progress' ? 'badge-info' :
                  a.status === 'cancelled' ? 'badge-danger' : 'badge-warning';

                return `
                  <tr>
                    <td><strong>${formatDateVN(a.appointment_date)}</strong></td>
                    <td><span style="color: #4f46e5; font-weight: 700;">${a.appointment_time || '09:00'}</span></td>
                    <td><strong>${a.pet_name || 'Bé cưng'}</strong></td>
                    <td style="color: #0369a1; font-weight: 600;">${a.service_name || 'Gói chăm sóc'}</td>
                    <td><span class="badge ${badgeClass}">${statusText}</span></td>
                    <td>
                      <div style="display: flex; gap: 6px;">
                        ${a.status !== 'completed' && a.status !== 'cancelled' ? `
                          <button type="button" class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem;" onclick="app.openRescheduleModal(${a.id})">
                            Đổi giờ
                          </button>
                        ` : ''}
                        <button type="button" class="quick-action-btn btn-primary" style="padding: 4px 8px; font-size: 0.75rem;" onclick="app.openBookingModalForPet(${a.pet_id})">
                          Đặt lại
                        </button>
                      </div>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      console.error('Error loading portal appointments:', err);
    }
  },

  async renderPortalInvoices(ownerId) {
    const container = document.getElementById('portal-client-invoices-list');
    if (!container) return;

    try {
      let invoices = state.invoices;
      if (!invoices || !invoices.length) {
        invoices = await api.get('/invoices');
      }

      const myInvoices = (invoices || []).filter(i => i.owner_id === ownerId);

      // Calculate total savings
      const totalSpent = myInvoices.reduce((sum, inv) => sum + (inv.final_amount || inv.total_amount || 0), 0);
      const totalSaved = Math.round(totalSpent * 0.1);

      if (!myInvoices.length) {
        container.innerHTML = `
          <div style="text-align: center; padding: 36px 20px; color: #64748b;">
            <h4 style="margin: 0 0 6px 0; color: #1e293b; font-size: 1.05rem; font-weight: 700;">Chưa có hóa đơn phát sinh</h4>
            <p style="margin: 0; font-size: 0.88rem;">Mọi hóa đơn dịch vụ spa, tiêm phòng sẽ tự động áp dụng ưu đãi VIP giảm 10% và tích lũy điểm thưởng.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px;">
          <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1.5px solid #86efac; border-radius: 14px; padding: 14px 18px;">
            <span style="font-size: 0.72rem; font-weight: 800; color: #065f46; text-transform: uppercase;">Tiết Kiệm VIP Đã Tích Lũy</span>
            <div style="font-size: 1.25rem; font-weight: 800; color: #047857; margin-top: 2px;">${formatCurrency(totalSaved)}</div>
            <span style="font-size: 0.74rem; color: #059669; font-weight: 600;">Chiết khấu 10% trọn đời</span>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 14px 18px;">
            <span style="font-size: 0.72rem; font-weight: 800; color: #64748b; text-transform: uppercase;">Tổng Chi Tiêu Dịch Vụ</span>
            <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-top: 2px;">${formatCurrency(totalSpent)}</div>
            <span style="font-size: 0.74rem; color: #64748b; font-weight: 600;">${myInvoices.length} lượt giao dịch</span>
          </div>

          <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1.5px solid #93c5fd; border-radius: 14px; padding: 14px 18px;">
            <span style="font-size: 0.72rem; font-weight: 800; color: #1e40af; text-transform: uppercase;">Điểm Thưởng Tích Lũy</span>
            <div style="font-size: 1.25rem; font-weight: 800; color: #1d4ed8; margin-top: 2px;">1,450 PTS</div>
            <span style="font-size: 0.74rem; color: #2563eb; font-weight: 600;">Được đổi voucher Spa</span>
          </div>
        </div>

        <div class="table-container">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Mã Hóa Đơn</th>
                <th>Ngày Tạo</th>
                <th>Dịch Vụ / Nội Dung</th>
                <th>Tổng Tiền</th>
                <th>Tiết Kiệm VIP</th>
                <th>Thực Thu</th>
                <th>Trạng Thái</th>
                <th>Thao Tác</th>
              </tr>
            </thead>
            <tbody>
              ${myInvoices.map(inv => {
                const total = inv.total_amount || 0;
                const discount = inv.discount_amount || Math.round(total * 0.1);
                const finalAmt = inv.final_amount || (total - discount);

                return `
                  <tr>
                    <td><strong style="color: #0284c7;">${inv.invoice_code || `#INV-${inv.id}`}</strong></td>
                    <td>${formatDateVN(inv.created_at?.slice(0, 10) || '')}</td>
                    <td style="color: #0f172a; font-weight: 600;">${inv.service_name || 'Gói Dịch Vụ Chăm Sóc'}</td>
                    <td>${formatCurrency(total)}</td>
                    <td><strong style="color: #059669;">-${formatCurrency(discount)}</strong></td>
                    <td><strong style="color: #0f172a; font-size: 0.95rem;">${formatCurrency(finalAmt)}</strong></td>
                    <td><span class="badge badge-success">Đã thanh toán</span></td>
                    <td>
                      <button type="button" class="quick-action-btn btn-outline" style="padding: 4px 10px; font-size: 0.75rem;" onclick="app.viewInvoiceDetail(${inv.id})">
                        Chi tiết / In
                      </button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      console.error('Error rendering portal invoices:', err);
    }
  },

  openBookingModalForPet(petId) {
    this.openBookingModal();
    const petSelect = document.getElementById('apt-pet-id');
    if (petSelect && petId) {
      petSelect.value = petId;
    }
  },

  setPortalAiPrompt(question) {
    const input = document.getElementById('portal-ai-input');
    if (input) {
      input.value = question;
      this.askPortalAi();
    }
  },

  async askPortalAi() {
    const input = document.getElementById('portal-ai-input');
    const answerBox = document.getElementById('portal-ai-answer');
    const btn = document.getElementById('portal-ai-btn');

    const question = input ? input.value.trim() : '';
    if (!question) {
      showToast('Vui lòng nhập câu hỏi sức khỏe thú cưng!', 'warning');
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ Đang kiểm tra...';
    }

    if (answerBox) {
      answerBox.style.display = 'block';
      answerBox.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px; color: #0284c7;">
          <span class="spinner" style="width: 16px; height: 16px; border: 2px solid #0284c7; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite;"></span>
          <span>Bác sĩ thú y đang đối chiếu triệu chứng và dữ liệu y bạ của bé...</span>
        </div>
      `;
    }

    try {
      const res = await api.post('/ai/consultation', {
        question: question,
        pet_id: null,
        chat_history: []
      });

      const answerText = res.answer || 'Xin lỗi, hiện tại hệ thống chưa thể phân tích câu hỏi này.';
      const formattedAnswer = answerText.replace(/\n/g, '<br>');

      if (answerBox) {
        let triageBanner = '';
        if (res.is_urgent_medical_alert) {
          const hotline = res.emergency_hotline || '0988.111.222';
          triageBanner = `
            <div class="emergency-triage-banner" style="margin-bottom: 12px;">
              <div class="emergency-triage-header">
                <div class="emergency-triage-title">
                  <span style="font-size: 1.3rem;">🚨</span>
                  <span>BÁO ĐỘNG ĐỎ: CA CẤP CỨU THÚ Y KHẨN CẤP</span>
                </div>
                <span class="emergency-triage-badge">Ưu Tiên Cấp 1</span>
              </div>
              <div class="emergency-hotline-box">
                <div class="emergency-hotline-info">
                  <span style="font-size: 1.4rem;">📞</span>
                  <div>
                    <div style="font-size: 0.72rem; color: #fca5a5; font-weight: 700;">HOTLINE BÁC SĨ TRỰC 24/7:</div>
                    <div class="emergency-hotline-num">${hotline}</div>
                  </div>
                </div>
                <a href="tel:${hotline.replace(/\./g, '')}" class="emergency-call-btn">
                  <span>GỌI CẤP CỨU NGAY</span>
                </a>
              </div>
            </div>
          `;
        }
        answerBox.innerHTML = `
          ${triageBanner}
          <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px;">
            <div style="flex: 1;">
              <strong style="color: ${res.is_urgent_medical_alert ? '#b91c1c' : '#0369a1'}; font-size: 0.95rem;">
                ${res.is_urgent_medical_alert ? '🚨 Báo Động Cấp Cứu Y Tế Khẩn Cấp:' : 'Cố Vấn Chăm Sóc Sức Khỏe Cho Bé:'}
              </strong>
              <div style="margin-top: 6px; color: #0f172a; line-height: 1.6;">${formattedAnswer}</div>
            </div>
          </div>
          <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed #cbd5e1; font-size: 0.78rem; color: #b91c1c; font-style: italic;">
            <strong>Lưu ý quan trọng:</strong> ${res.medical_disclaimer || 'Khi thú cưng có dấu hiệu co giật, nôn mửa hoặc bất thường, đưa bé đến bệnh viện thú y gần nhất ngay lập tức!'}
          </div>
        `;
      }
    } catch (err) {
      console.error('Error asking consultation:', err);
      if (answerBox) {
        answerBox.innerHTML = `<span style="color: #dc2626;">Đã có lỗi kết nối với máy chủ. Vui lòng thử lại sau giây lát!</span>`;
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = 'Gửi Câu Hỏi';
      }
    }
  }
};



// Start app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
