// PetCare AI Pro - Dashboard & Analytics Module
let revenueChartInstance = null;
let serviceChartInstance = null;

async function loadDashboard() {
    try {
        const stats = await apiCall('/stats/summary');
        
        // Update KPI Cards
        const kpiAppt = document.getElementById('kpi-today-appointments');
        const kpiRev = document.getElementById('kpi-today-revenue');
        const kpiPets = document.getElementById('kpi-total-pets');
        const kpiOwners = document.getElementById('kpi-total-owners');
        const kpiRet = document.getElementById('kpi-retention-rate');

        if (kpiAppt) kpiAppt.textContent = stats.today_appointments || 0;
        if (kpiRev) kpiRev.textContent = formatCurrency(stats.today_revenue || 0);
        if (kpiPets) kpiPets.textContent = stats.total_pets || 0;
        if (kpiOwners) kpiOwners.textContent = stats.total_owners || 0;
        if (kpiRet) kpiRet.textContent = `${stats.retention_rate || 0}%`;

        // Render Charts
        renderRevenueChart(stats.daily_revenue || []);
        renderServiceChart(stats.service_distribution || []);

        // Load today's schedule table
        loadTodayAppointments();
    } catch (e) {
        console.error('Lỗi tải dữ liệu Dashboard:', e);
    }
}

function renderRevenueChart(dailyData) {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;

    const labels = dailyData.map(d => d.date);
    const dataValues = dailyData.map(d => d.revenue);

    if (revenueChartInstance) {
        revenueChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, 'rgba(6, 182, 212, 0.45)');
    gradient.addColorStop(0.5, 'rgba(99, 102, 241, 0.25)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    revenueChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.length > 0 ? labels : ['Hôm nay'],
            datasets: [{
                label: 'Doanh thu (VNĐ)',
                data: dataValues.length > 0 ? dataValues : [0],
                borderColor: '#22d3ee',
                backgroundColor: gradient,
                borderWidth: 3.5,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8,
                pointHoverBackgroundColor: '#22d3ee',
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f8fafc',
                    bodyColor: '#38bdf8',
                    bodyFont: { weight: 'bold', size: 13 },
                    borderColor: 'rgba(99, 102, 241, 0.4)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (ctx) => ` Doanh thu: ${formatCurrency(ctx.raw)}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8', font: { weight: '600' } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: {
                        color: '#94a3b8',
                        font: { weight: '600' },
                        callback: (val) => val >= 1000 ? `${(val/1000).toFixed(0)}k` : val
                    }
                }
            }
        }
    });
}

function renderServiceChart(distData) {
    const canvas = document.getElementById('serviceChart');
    if (!canvas) return;

    if (serviceChartInstance) {
        serviceChartInstance.destroy();
    }

    const labels = distData.map(d => d.category);
    const counts = distData.map(d => d.count);

    const colors = ['#10b981', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#3b82f6'];

    const ctx = canvas.getContext('2d');
    serviceChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.length > 0 ? labels : ['Chưa có dịch vụ'],
            datasets: [{
                data: counts.length > 0 ? counts : [1],
                backgroundColor: colors.slice(0, Math.max(labels.length, 1)),
                borderWidth: 3,
                borderColor: '#111827',
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { 
                        color: '#cbd5e1', 
                        boxWidth: 12, 
                        boxHeight: 12, 
                        borderRadius: 6,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 14, 
                        font: { size: 12, weight: '600' } 
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f8fafc',
                    bodyColor: '#34d399',
                    bodyFont: { weight: 'bold', size: 13 },
                    borderColor: 'rgba(16, 185, 129, 0.4)',
                    borderWidth: 1,
                    padding: 10
                }
            },
            cutout: '72%'
        }
    });
}

async function loadTodayAppointments() {
    const tbody = document.getElementById('today-appointments-tbody');
    if (!tbody) return;

    try {
        const todayStr = new Date().toISOString().split('T')[0];
        const appts = await apiCall(`/appointments?date_str=${todayStr}`);

        if (appts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 2rem;">Chưa có lịch hẹn nào trong hôm nay.</td></tr>`;
            return;
        }

        tbody.innerHTML = appts.map(a => `
            <tr>
                <td><strong>${formatDateTime(a.appointment_time)}</strong></td>
                <td><i class="fa-solid fa-paw" style="color: #6366f1;"></i> <strong>${a.pet_name || 'Bé'}</strong> (${a.pet_species || ''})</td>
                <td>${a.owner_name || 'Khách'} <br><small style="color: var(--text-muted);">${a.owner_phone || ''}</small></td>
                <td><span style="color: #38bdf8;">${a.service_name}</span> <br><small>${formatCurrency(a.service_price)}</small></td>
                <td><span class="badge" style="background: rgba(255,255,255,0.08);">${a.staff_name || 'Tự do'}</span></td>
                <td>${getStatusBadge(a.status)}</td>
                <td style="min-width: 150px;">
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
                        ${a.status === 'PENDING' ? `
                            <button class="btn btn-primary btn-sm" onclick="updateApptStatus(${a.id}, 'CONFIRMED')" title="Duyệt lịch hẹn">
                                <i class="fa-solid fa-check"></i> Duyệt
                            </button>
                        ` : ''}
                        ${a.status === 'CONFIRMED' ? `
                            <button class="btn btn-success btn-sm" onclick="updateApptStatus(${a.id}, 'IN_PROGRESS')" title="Bắt đầu chăm sóc">
                                <i class="fa-solid fa-play"></i> Bắt đầu
                            </button>
                        ` : ''}
                        ${a.status === 'IN_PROGRESS' ? `
                            <button class="btn btn-success btn-sm" onclick="quickCompleteAppt(${a.id})" title="Hoàn thành & Lập hóa đơn">
                                <i class="fa-solid fa-check-double"></i> Hoàn thành
                            </button>
                        ` : ''}
                        ${a.status === 'COMPLETED' ? `
                            <button class="btn btn-secondary btn-sm" onclick="switchTab('invoices')" title="Xem hóa đơn">
                                <i class="fa-solid fa-receipt"></i> Hóa đơn
                            </button>
                        ` : ''}
                        ${a.status !== 'COMPLETED' && a.status !== 'CANCELLED' ? `
                            <button class="btn-icon btn-danger-icon" onclick="cancelAppt(${a.id})" title="Hủy lịch hẹn">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        ` : ''}
                        <div class="dropdown-action-wrapper" style="position: relative; display: inline-block;">
                            <button class="btn-icon btn-more-icon" onclick="toggleApptMenu(event, ${a.id})" title="Thao tác khác (...)">
                                <i class="fa-solid fa-ellipsis"></i>
                            </button>
                            <div id="appt-menu-${a.id}" class="appt-dropdown-menu" style="display: none;">
                                <button class="appt-dropdown-item" onclick="triggerAIReminderForAppt(${JSON.stringify(a).replace(/"/g, '&quot;')})">
                                    <i class="fa-solid fa-paper-plane" style="color: #6366f1;"></i> Gửi tin nhắc hẹn
                                </button>
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
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--danger);">Lỗi tải lịch hẹn: ${e.message}</td></tr>`;
    }
}

function getStatusBadge(status) {
    switch (status) {
        case 'CONFIRMED': return '<span class="badge badge-confirmed"><i class="fa-solid fa-check"></i> Đã xác nhận</span>';
        case 'PENDING': return '<span class="badge badge-pending"><i class="fa-solid fa-hourglass-half"></i> Chờ duyệt</span>';
        case 'IN_PROGRESS': return '<span class="badge badge-inprogress"><i class="fa-solid fa-spinner fa-spin"></i> Đang làm</span>';
        case 'COMPLETED': return '<span class="badge badge-completed"><i class="fa-solid fa-check-double"></i> Hoàn thành</span>';
        case 'CANCELLED': return '<span class="badge badge-cancelled"><i class="fa-solid fa-ban"></i> Đã hủy</span>';
        default: return `<span class="badge">${status}</span>`;
    }
}
