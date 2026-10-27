// PetCare AI Pro - Invoices & POS Billing Module

let pendingApptsList = [];

async function loadInvoices() {
    const tbody = document.getElementById('invoices-tbody');
    if (!tbody) return;

    const statusFilter = document.getElementById('invoice-filter-status')?.value;
    const searchFilter = document.getElementById('invoice-search-input')?.value?.trim();

    let url = '/invoices?';
    if (statusFilter) url += `payment_status=${encodeURIComponent(statusFilter)}&`;
    if (searchFilter) url += `search=${encodeURIComponent(searchFilter)}&`;

    try {
        const invoices = await apiCall(url);

        // Calculate KPI metrics
        let totalPaid = 0;
        let totalUnpaid = 0;
        let countPaid = 0;

        invoices.forEach(inv => {
            if (inv.payment_status === 'Đã thanh toán') {
                totalPaid += (inv.total_amount || 0);
                countPaid++;
            } else if (inv.payment_status === 'Chưa thanh toán') {
                totalUnpaid += (inv.total_amount || 0);
            }
        });

        const kpiPaid = document.getElementById('kpi-invoice-paid-total');
        const kpiUnpaid = document.getElementById('kpi-invoice-unpaid-total');
        const kpiCount = document.getElementById('kpi-invoice-count');
        const kpiPaidCount = document.getElementById('kpi-invoice-paid-count');
        const kpiRate = document.getElementById('kpi-invoice-rate');

        if (kpiPaid) kpiPaid.textContent = formatCurrency(totalPaid);
        if (kpiUnpaid) kpiUnpaid.textContent = formatCurrency(totalUnpaid);
        if (kpiCount) kpiCount.textContent = invoices.length;
        if (kpiPaidCount) kpiPaidCount.textContent = `${countPaid} phiếu thu hoàn tất`;
        if (kpiRate) {
            const rate = invoices.length > 0 ? Math.round((countPaid / invoices.length) * 100) : 100;
            kpiRate.textContent = `${rate}%`;
        }

        if (invoices.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-dim); padding: 2.5rem;">Không tìm thấy hóa đơn nào phù hợp.</td></tr>`;
            return;
        }

        tbody.innerHTML = invoices.map(inv => {
            const isPaid = inv.payment_status === 'Đã thanh toán';
            const isCancelled = inv.payment_status === 'Đã hủy';

            let statusBadge = '<span class="badge badge-confirmed"><i class="fa-solid fa-check"></i> Đã thanh toán</span>';
            if (inv.payment_status === 'Chưa thanh toán') {
                statusBadge = '<span class="badge badge-pending"><i class="fa-solid fa-clock"></i> Chưa thanh toán</span>';
            } else if (isCancelled) {
                statusBadge = '<span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;"><i class="fa-solid fa-ban"></i> Đã hủy</span>';
            }

            return `
                <tr>
                    <td>
                        <strong style="color: #4f46e5;">${inv.invoice_code}</strong>
                        ${inv.appointment_id ? `<br><small class="text-slate-400">Lịch hẹn #${inv.appointment_id}</small>` : ''}
                    </td>
                    <td>
                        <strong class="text-slate-900">${inv.owner_name || 'Khách vãng lai'}</strong><br>
                        <small class="text-slate-500"><i class="fa-solid fa-phone" style="font-size: 0.7rem;"></i> ${inv.owner_phone || '---'}</small>
                    </td>
                    <td><small class="text-slate-600">${formatDateTime(inv.created_at)}</small></td>
                    <td>
                        <ul style="padding-left: 1.1rem; margin: 0; font-size: 0.82rem; color: #334155;">
                            ${inv.items.map(i => `<li><strong>${i.item_name}</strong> (x${i.quantity}) &bull; ${formatCurrency(i.total_price)}</li>`).join('')}
                        </ul>
                    </td>
                    <td><span style="color: #ef4444; font-weight: 600;">-${formatCurrency(inv.discount_amount)}</span></td>
                    <td><strong style="color: #10b981; font-size: 0.98rem;">${formatCurrency(inv.total_amount)}</strong></td>
                    <td><span class="badge" style="background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0;">${inv.payment_method}</span></td>
                    <td>${statusBadge}</td>
                    <td style="text-align: center;">
                        <div style="display: inline-flex; gap: 5px; flex-wrap: wrap; justify-content: center;">
                            <button class="btn btn-secondary btn-sm" style="padding: 3px 8px; font-size: 0.75rem;" onclick="printInvoiceBill(${JSON.stringify(inv).replace(/"/g, '&quot;')})" title="Xem & In phiếu thu">
                                <i class="fa-solid fa-print"></i> In Bill
                            </button>
                            ${!isPaid && !isCancelled ? `
                                <button class="btn btn-success btn-sm" style="padding: 3px 8px; font-size: 0.75rem;" onclick="quickPayInvoice(${inv.id})" title="Xác nhận thu tiền ngay">
                                    <i class="fa-solid fa-money-bill-wave"></i> Thu tiền
                                </button>
                            ` : ''}
                            <button class="btn btn-danger btn-sm" style="padding: 3px 6px; font-size: 0.75rem;" onclick="deleteInvoice(${inv.id}, '${inv.invoice_code}')" title="Xóa hóa đơn">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--danger);">Lỗi tải hóa đơn: ${e.message}</td></tr>`;
    }
}

async function openCreateInvoiceModal() {
    // 1. Populate Customer Dropdown
    const ownerSelect = document.getElementById('modal-inv-owner');
    if (ownerSelect) {
        ownerSelect.innerHTML = '<option value="">-- Đang tải danh sách khách hàng... --</option>';
        try {
            const owners = await apiCall('/owners');
            ownerSelect.innerHTML = '<option value="">-- Chọn khách hàng / chủ nuôi --</option>' +
                owners.map(o => `<option value="${o.id}">${o.full_name} (${o.phone})</option>`).join('');
        } catch (e) {
            ownerSelect.innerHTML = '<option value="">Lỗi tải khách hàng</option>';
        }
    }

    // 2. Populate Pending Appointments Shortcut
    const apptSelect = document.getElementById('modal-inv-select-appt');
    if (apptSelect) {
        apptSelect.innerHTML = '<option value="">-- Đang tải lịch hẹn chờ thu tiền... --</option>';
        try {
            pendingApptsList = await apiCall('/invoices/pending-appointments');
            if (pendingApptsList.length === 0) {
                apptSelect.innerHTML = '<option value="">(Không có lịch hẹn nào đang chờ thu tiền - Lập hóa đơn tự do)</option>';
            } else {
                apptSelect.innerHTML = '<option value="">-- Chọn lịch hẹn để tự động điền thông tin --</option>' +
                    pendingApptsList.map(a => `<option value="${a.id}">#${a.id} - ${a.owner_name} (${a.pet_name} - ${a.service_name}) [${a.appointment_time}]</option>`).join('');
            }
        } catch (e) {
            apptSelect.innerHTML = '<option value="">(Bỏ qua bước này để lập tự do)</option>';
        }
    }

    // 3. Reset form inputs
    document.getElementById('modal-inv-appt-id').value = '';
    document.getElementById('modal-inv-discount').value = '0';
    document.getElementById('modal-inv-tax').value = '0';
    document.getElementById('modal-inv-notes').value = '';

    // 4. Initialize Table with 1 empty row
    const tbody = document.getElementById('modal-inv-items-tbody');
    if (tbody) {
        tbody.innerHTML = '';
        addInvoiceItemRow('Gói Spa Tắm & Cắt Tỉa Lông', 1, 250000);
    }

    calculateInvoiceModalTotals();
    openModal('modal-create-invoice');
}

function onSelectPendingApptForInvoice() {
    const select = document.getElementById('modal-inv-select-appt');
    const apptId = parseInt(select?.value);
    if (!apptId) return;

    const found = pendingApptsList.find(a => a.id === apptId);
    if (!found) return;

    // Set Owner
    const ownerSelect = document.getElementById('modal-inv-owner');
    if (ownerSelect) ownerSelect.value = found.owner_id;

    // Set Appt ID
    document.getElementById('modal-inv-appt-id').value = found.id;

    // Set line item
    const tbody = document.getElementById('modal-inv-items-tbody');
    if (tbody) {
        tbody.innerHTML = '';
        addInvoiceItemRow(found.service_name, 1, found.service_price);
    }

    // Set notes
    document.getElementById('modal-inv-notes').value = `Thanh toán dịch vụ cho bé ${found.pet_name} theo lịch hẹn #${found.id}`;
    calculateInvoiceModalTotals();
}

function addInvoiceItemRow(name = '', qty = 1, price = 0) {
    const tbody = document.getElementById('modal-inv-items-tbody');
    if (!tbody) return;

    const tr = document.createElement('tr');
    tr.className = 'inv-item-row';
    tr.innerHTML = `
        <td style="padding: 4px;">
            <input type="text" class="form-control item-name" value="${name}" placeholder="Tên dịch vụ/sản phẩm..." required style="font-size: 0.82rem; padding: 4px 8px;">
        </td>
        <td style="padding: 4px;">
            <input type="number" class="form-control item-qty" value="${qty}" min="1" oninput="calculateInvoiceModalTotals()" style="font-size: 0.82rem; padding: 4px 6px; text-align: center;">
        </td>
        <td style="padding: 4px;">
            <input type="number" class="form-control item-price" value="${price}" min="0" step="5000" oninput="calculateInvoiceModalTotals()" style="font-size: 0.82rem; padding: 4px 8px; text-align: right;">
        </td>
        <td style="padding: 4px; text-align: center;">
            <button type="button" class="btn btn-secondary btn-sm" onclick="removeInvoiceItemRow(this)" style="padding: 3px 7px; color: #ef4444;" title="Xóa dòng này">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
    calculateInvoiceModalTotals();
}

function removeInvoiceItemRow(btn) {
    const tbody = document.getElementById('modal-inv-items-tbody');
    if (!tbody) return;
    if (tbody.children.length <= 1) {
        showToast('Hóa đơn phải có ít nhất 1 dòng dịch vụ hoặc sản phẩm!', 'error');
        return;
    }
    btn.closest('tr')?.remove();
    calculateInvoiceModalTotals();
}

function calculateInvoiceModalTotals() {
    const rows = document.querySelectorAll('.inv-item-row');
    let subtotal = 0;

    rows.forEach(r => {
        const qty = parseFloat(r.querySelector('.item-qty')?.value) || 0;
        const price = parseFloat(r.querySelector('.item-price')?.value) || 0;
        subtotal += (qty * price);
    });

    const discount = parseFloat(document.getElementById('modal-inv-discount')?.value) || 0;
    const tax = parseFloat(document.getElementById('modal-inv-tax')?.value) || 0;
    const grandTotal = Math.max(0, subtotal - discount + tax);

    const subDisp = document.getElementById('modal-inv-subtotal-disp');
    const disDisp = document.getElementById('modal-inv-discount-disp');
    const totDisp = document.getElementById('modal-inv-total-disp');

    if (subDisp) subDisp.textContent = formatCurrency(subtotal);
    if (disDisp) disDisp.textContent = `-${formatCurrency(discount)}`;
    if (totDisp) totDisp.textContent = formatCurrency(grandTotal);
}

async function submitCreateInvoice() {
    const ownerId = document.getElementById('modal-inv-owner')?.value;
    if (!ownerId) {
        showToast('Vui lòng chọn khách hàng / chủ nuôi!', 'error');
        return;
    }

    const rows = document.querySelectorAll('.inv-item-row');
    const items = [];

    for (const r of rows) {
        const name = r.querySelector('.item-name')?.value?.trim();
        const qty = parseInt(r.querySelector('.item-qty')?.value) || 0;
        const price = parseFloat(r.querySelector('.item-price')?.value) || 0;

        if (!name) {
            showToast('Tên mặt hàng/dịch vụ không được để trống!', 'error');
            return;
        }
        if (qty <= 0) {
            showToast(`Số lượng của "${name}" phải lớn hơn 0!`, 'error');
            return;
        }
        if (price < 0) {
            showToast(`Đơn giá của "${name}" không được âm!`, 'error');
            return;
        }

        items.push({
            item_name: name,
            quantity: qty,
            unit_price: price,
            total_price: qty * price
        });
    }

    if (items.length === 0) {
        showToast('Vui lòng thêm ít nhất một mặt hàng hoặc dịch vụ!', 'error');
        return;
    }

    const apptIdVal = document.getElementById('modal-inv-appt-id')?.value;
    const discount = parseFloat(document.getElementById('modal-inv-discount')?.value) || 0;
    const tax = parseFloat(document.getElementById('modal-inv-tax')?.value) || 0;
    const paymentMethod = document.getElementById('modal-inv-payment-method')?.value || 'Tiền mặt';
    const paymentStatus = document.getElementById('modal-inv-payment-status')?.value || 'Đã thanh toán';
    const notes = document.getElementById('modal-inv-notes')?.value?.trim();

    try {
        const payload = {
            owner_id: parseInt(ownerId),
            appointment_id: apptIdVal ? parseInt(apptIdVal) : null,
            discount_amount: discount,
            tax_amount: tax,
            payment_method: paymentMethod,
            payment_status: paymentStatus,
            notes: notes || null,
            items: items
        };

        const newInv = await apiCall('/invoices', 'POST', payload);
        closeModal('modal-create-invoice');
        showToast(`🎉 Đã lập hóa đơn ${newInv.invoice_code} thành công!`, 'success');

        loadInvoices();
        loadAppointments();
        loadDashboard();

        // Mở luôn bản in phiếu thu cho nhân viên
        printInvoiceBill(newInv);
    } catch (e) {
        showToast('Lỗi lưu hóa đơn: ' + e.message, 'error');
    }
}

async function quickPayInvoice(invId) {
    if (!confirm('Xác nhận thu tiền cho hóa đơn này?')) return;
    try {
        const res = await apiCall(`/invoices/${invId}/pay`, 'PUT', { payment_method: 'Tiền mặt' });
        showToast(`✅ Đã thu tiền thành công cho hóa đơn ${res.invoice_code}!`, 'success');
        loadInvoices();
        loadDashboard();
    } catch (e) {
        showToast('Lỗi thu tiền: ' + e.message, 'error');
    }
}

async function deleteInvoice(invId, invCode) {
    if (!confirm(`Bạn có chắc chắn muốn xóa hóa đơn "${invCode}" không?\nThao tác này không thể hoàn tác!`)) return;
    try {
        await apiCall(`/invoices/${invId}`, 'DELETE');
        showToast(`Đã xóa hóa đơn ${invCode}`, 'success');
        loadInvoices();
        loadDashboard();
    } catch (e) {
        showToast('Lỗi xóa hóa đơn: ' + e.message, 'error');
    }
}

function printInvoiceBill(inv) {
    const codeDate = document.getElementById('bill-code-date');
    if (codeDate) codeDate.textContent = `Mã HĐ: ${inv.invoice_code} • Ngày: ${formatDateTime(inv.created_at)}`;
    
    const ownerName = document.getElementById('bill-owner-name');
    if (ownerName) ownerName.textContent = inv.owner_name || 'Khách hàng';
    
    const ownerPhone = document.getElementById('bill-owner-phone');
    if (ownerPhone) ownerPhone.textContent = inv.owner_phone || '---';
    
    const ownerAddr = document.getElementById('bill-owner-address');
    if (ownerAddr) ownerAddr.textContent = inv.owner_address || 'TP. Thái Nguyên';

    const tbody = document.getElementById('bill-items-tbody');
    if (tbody) {
        tbody.innerHTML = (inv.items || []).map(item => `
            <tr style="border-bottom: 1px dashed #eee;">
                <td style="padding: 6px 0;">${item.item_name}</td>
                <td style="padding: 6px 0; text-align: center;">${item.quantity}</td>
                <td style="padding: 6px 0; text-align: right;">${formatCurrency(item.unit_price)}</td>
                <td style="padding: 6px 0; text-align: right;"><strong>${formatCurrency(item.total_price)}</strong></td>
            </tr>
        `).join('');
    }

    const sub = document.getElementById('bill-subtotal');
    if (sub) sub.textContent = formatCurrency(inv.subtotal);

    const disc = document.getElementById('bill-discount');
    if (disc) disc.textContent = `-${formatCurrency(inv.discount_amount)}`;

    const tot = document.getElementById('bill-total');
    if (tot) tot.textContent = formatCurrency(inv.total_amount);

    const meth = document.getElementById('bill-payment-method');
    if (meth) meth.textContent = `${inv.payment_method || 'Tiền mặt'} (${inv.payment_status})`;

    openModal('modal-invoice-bill');
}
