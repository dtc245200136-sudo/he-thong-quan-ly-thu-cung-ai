// ============================================================
// UI COMPONENTS & RENDERERS
// ============================================================

const components = {
  renderAppointmentRow(apt) {
    const statusLabels = {
      pending: 'Chờ xử lý',
      confirmed: 'Đã xác nhận',
      in_progress: 'Đang làm dịch vụ',
      completed: 'Hoàn thành',
      cancelled: 'Đã hủy'
    };

    return `
      <tr>
        <td>
          <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">${apt.appointment_time}</div>
          <div style="font-size: 0.8rem; color: #64748b; font-weight: 500;">${formatDateVN(apt.appointment_date)}</div>
        </td>
        <td>
          <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">${apt.pet_name || 'Bé cưng'}</div>
          <span class="pet-breed-tag">${apt.pet_species || 'Thú cưng'} - ${apt.pet_breed || ''}</span>
        </td>
        <td>
          <div style="font-weight: 600; color: #1e293b; font-size: 0.92rem;">${apt.owner_name || 'Khách'}</div>
          <div style="font-size: 0.8rem; color: #475569; font-weight: 600;">${apt.owner_phone || ''}</div>
        </td>
        <td>
          <div style="font-weight: 700; color: #0284c7; font-size: 0.92rem;">${apt.service_name || 'Dịch vụ'}</div>
          <div style="font-size: 0.82rem; color: #059669; font-weight: 700;">${formatCurrency(apt.service_price)}</div>
        </td>
        <td>
          <span class="badge badge-${apt.status}">
            <span class="badge-dot"></span>
            ${statusLabels[apt.status] || apt.status}
          </span>
        </td>
        <td>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            <!-- AI Reminder Button -->
            <button class="quick-action-btn btn-ai-magic" style="padding: 4px 10px; font-size: 0.75rem;" onclick="app.openAiReminderModal('appointment', ${apt.id})">
              AI Nhắc
            </button>

            ${apt.status !== 'completed' && apt.status !== 'cancelled' ? `
              <button class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; border-color: #cbd5e1; color: #334155;" onclick="app.openRescheduleModal(${apt.id})">
                Đổi giờ
              </button>
              <button class="quick-action-btn btn-primary" style="padding: 4px 8px; font-size: 0.75rem; background: var(--success);" onclick="app.completeAppointment(${apt.id})">
                Xong
              </button>
              <button class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; color: var(--danger); border-color: #fca5a5;" onclick="app.cancelAppointment(${apt.id})">
                Hủy
              </button>
            ` : ''}

            ${apt.status === 'completed' && !apt.has_invoice ? `
              <button class="quick-action-btn btn-primary" style="padding: 4px 8px; font-size: 0.75rem;" onclick="app.openCreateInvoiceModal(${apt.id}, ${apt.owner_id}, ${apt.service_price || 0})">
                Lập hóa đơn
              </button>
            ` : ''}

            ${apt.status === 'completed' && !apt.has_care_record ? `
              <button class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; border-color: var(--accent); color: #4f46e5;" onclick="app.openCareRecordModal(${apt.pet_id}, ${apt.id})">
                Ghi hồ sơ
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  },

  renderPetCard(pet) {
    const defaultAvatar = pet.species === 'Mèo' 
      ? 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=150&auto=format&fit=crop&q=80'
      : 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=150&auto=format&fit=crop&q=80';

    return `
      <div class="pet-card">
        <div class="pet-card-top">
          <img src="${pet.avatar_url || defaultAvatar}" alt="${pet.name}" class="pet-avatar" onerror="this.src='${defaultAvatar}'" />
          <div class="pet-info-header">
            <h3>${pet.name}</h3>
            <span class="pet-breed-tag">${pet.species} • ${pet.breed || 'Chưa rõ'}</span>
            <div style="font-size: 0.76rem; color: var(--text-dim); margin-top: 4px;">Chủ: <strong>${pet.owner_name || 'Khách vãng lai'}</strong></div>
          </div>
        </div>

        <div class="pet-details-list">
          <div class="pet-detail-item">
            <span class="lbl">Tuổi:</span>
            <span class="val">${pet.age_months || 0} tháng</span>
          </div>
          <div class="pet-detail-item">
            <span class="lbl">Cân nặng:</span>
            <span class="val">${pet.weight_kg || 0} kg</span>
          </div>
          <div class="pet-detail-item">
            <span class="lbl">Giới tính:</span>
            <span class="val">${pet.gender || 'Chưa rõ'}</span>
          </div>
          <div class="pet-detail-item">
            <span class="lbl">Dị ứng:</span>
            <span class="val" style="color: ${pet.allergies && pet.allergies !== 'Không có' ? 'var(--danger)' : 'var(--success)'};">${pet.allergies || 'Không'}</span>
          </div>
        </div>

        <div class="pet-card-actions">
          <button class="quick-action-btn btn-ai-magic" style="flex: 1; justify-content: center; font-size: 0.78rem;" onclick="app.triggerAiSummary(${pet.id})">
            Tóm tắt AI
          </button>
          <button class="quick-action-btn btn-primary" style="font-size: 0.78rem;" onclick="app.openBookingModal(${pet.id}, ${pet.owner_id})">
            Đặt lịch
          </button>
          <button class="quick-action-btn btn-outline" style="padding: 8px 10px;" onclick="app.openCareHistoryModal(${pet.id})">
            Xem hồ sơ
          </button>
        </div>
      </div>
    `;
  },

  renderVaccineRow(vac) {
    const isOverdue = vac.status === 'overdue';
    return `
      <tr>
        <td>
          <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">${vac.pet_name}</div>
          <div style="font-size: 0.8rem; color: #475569; font-weight: 600;">${vac.owner_name} • ${vac.owner_phone}</div>
        </td>
        <td>
          <div style="font-weight: 700; color: #0284c7; font-size: 0.92rem;">${vac.vaccine_name}</div>
          <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Mũi số: ${vac.dose_number}</div>
        </td>
        <td>
          <div style="font-size: 0.85rem; color: #334155; font-weight: 500;">Lần trước: ${formatDateVN(vac.administered_date) || 'Chưa tiêm'}</div>
        </td>
        <td>
          <div style="font-weight: 700; font-size: 0.95rem; color: ${isOverdue ? '#dc2626' : '#0f172a'};">
            ${formatDateVN(vac.next_due_date)}
          </div>
        </td>
        <td>
          <span class="badge badge-${vac.status}">
            <span class="badge-dot"></span>
            ${vac.status === 'overdue' ? 'ĐÃ QUÁ HẠN' : (vac.status === 'completed' ? 'Đã tiêm' : 'Đến hạn')}
          </span>
        </td>
        <td>
          <div style="display: flex; gap: 8px;">
            <button class="quick-action-btn btn-ai-magic" style="padding: 4px 10px; font-size: 0.75rem;" onclick="app.openAiReminderModal('vaccine', ${vac.id})">
              AI Soạn tin nhắc
            </button>
            ${vac.status !== 'completed' ? `
              <button class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; color: #059669; border-color: #86efac;" onclick="app.completeVaccine(${vac.id})">
                Đã tiêm
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  },

  renderInvoiceRow(inv) {
    return `
      <tr>
        <td style="font-weight: 800; color: #0284c7; font-size: 0.92rem;">${inv.invoice_code}</td>
        <td>
          <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">${inv.owner_name || 'Khách'}</div>
          <div style="font-size: 0.8rem; color: #475569; font-weight: 600;">${inv.owner_phone || ''}</div>
        </td>
        <td>
          <div style="font-weight: 600; color: #1e293b;">${inv.pet_name ? `Bé ${inv.pet_name}` : ''}</div>
          <div style="font-size: 0.8rem; color: #64748b;">${inv.service_name || 'Dịch vụ'}</div>
        </td>
        <td style="font-weight: 800; color: #059669; font-size: 0.95rem;">
          ${formatCurrency(inv.final_amount)}
          ${inv.discount_amount > 0 ? `<div style="font-size: 0.75rem; color: #94a3b8; text-decoration: line-through;">${formatCurrency(inv.total_amount)}</div>` : ''}
        </td>
        <td>
          <span class="badge badge-${inv.payment_status === 'paid' ? 'completed' : 'pending'}">
            <span class="badge-dot"></span>
            ${inv.payment_status === 'paid' ? 'Đã thanh toán' : 'Chờ thanh toán'}
          </span>
          <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; margin-top: 3px;">${inv.payment_method}</div>
        </td>
        <td>
          <div style="display: flex; gap: 6px;">
            <button class="quick-action-btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem; border-color: #cbd5e1; color: #334155;" onclick="app.viewInvoiceDetail(${inv.id})">
              Chi tiết / In
            </button>
            ${inv.payment_status !== 'paid' ? `
              <button class="quick-action-btn btn-primary" style="padding: 4px 8px; font-size: 0.75rem;" onclick="app.markInvoicePaid(${inv.id})">
                Thanh toán
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  }
};
