// PetCare AI Pro - Inventory & Supplies Management Module

let inventoryItemsCache = [];

/**
 * Tải dữ liệu toàn bộ kho hàng & thống kê
 */
async function loadInventory() {
    try {
        // 1. Tải thống kê KPI kho
        const stats = await apiCall('/inventory/stats');
        renderInventoryStats(stats);

        // 2. Tải danh sách mặt hàng
        const items = await apiCall('/inventory/items');
        inventoryItemsCache = items;
        renderInventoryTable(items);

    } catch (err) {
        console.error('Lỗi tải dữ liệu kho hàng:', err);
        showToast('Không thể tải dữ liệu kho: ' + err.message, 'error');
    }
}

/**
 * Hiển thị thẻ KPI & Thống kê Kho Hàng
 */
function renderInventoryStats(stats) {
    const elTotalItems = document.getElementById('kpi-inv-total-items');
    const elTotalQty = document.getElementById('kpi-inv-total-qty');
    const elTotalValue = document.getElementById('kpi-inv-total-value');
    const elLowStock = document.getElementById('kpi-inv-low-stock');
    const elExpiring = document.getElementById('kpi-inv-expiring');

    if (elTotalItems) elTotalItems.textContent = stats.total_items_count || 0;
    if (elTotalQty) elTotalQty.textContent = `${stats.total_stock_quantity || 0} đơn vị`;
    if (elTotalValue) elTotalValue.textContent = formatCurrency(stats.total_inventory_value_vnd || 0);
    if (elLowStock) elLowStock.textContent = stats.low_stock_count || 0;
    if (elExpiring) elExpiring.textContent = (stats.expiring_soon_count || 0) + (stats.expired_count || 0);
}

/**
 * Hiển thị bảng danh sách mặt hàng kho
 */
function renderInventoryTable(items) {
    const tbody = document.getElementById('inventory-table-tbody');
    const countBadge = document.getElementById('inventory-list-count');
    if (countBadge) countBadge.textContent = `${items.length} mặt hàng`;

    if (!tbody) return;
    tbody.innerHTML = '';

    if (!items || items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 2.5rem; color: var(--text-dim);">
                    <i class="fa-solid fa-boxes-stacked" style="font-size: 2.5rem; margin-bottom: 0.8rem; opacity: 0.4;"></i>
                    <p style="font-size: 0.95rem;">Không tìm thấy mặt hàng nào phù hợp với bộ lọc.</p>
                </td>
            </tr>
        `;
        return;
    }

    items.forEach((item, index) => {
        const tr = document.createElement('tr');

        // Status Badge & Color
        let statusBadge = '';
        let rowClass = '';
        if (item.stock_status === 'OUT_OF_STOCK') {
            statusBadge = '<span class="badge" style="background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4);"><i class="fa-solid fa-circle-xmark"></i> Hết Hàng</span>';
            rowClass = 'style="background: rgba(239,68,68,0.03);"';
        } else if (item.stock_status === 'LOW_STOCK') {
            statusBadge = '<span class="badge" style="background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4);"><i class="fa-solid fa-triangle-exclamation"></i> Sắp Hết</span>';
        } else if (item.stock_status === 'EXPIRED') {
            statusBadge = '<span class="badge" style="background: rgba(239,68,68,0.25); color: #f87171; border: 1px solid #ef4444;"><i class="fa-solid fa-skull-crossbones"></i> Đã Hết Hạn</span>';
        } else {
            statusBadge = '<span class="badge" style="background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.4);"><i class="fa-solid fa-circle-check"></i> An Toàn</span>';
        }

        // Expiry Date Badge
        let expiryBadge = '<span style="color: var(--text-dim);">Không có</span>';
        if (item.expiry_date) {
            const expDateStr = new Date(item.expiry_date).toLocaleDateString('vi-VN');
            if (item.days_to_expiry < 0) {
                expiryBadge = `<span style="color: #ef4444; font-weight: 700;" title="Quá hạn ${Math.abs(item.days_to_expiry)} ngày"><i class="fa-solid fa-triangle-exclamation"></i> ${expDateStr} (Hết hạn)</span>`;
            } else if (item.is_expiring_soon) {
                expiryBadge = `<span style="color: #f59e0b; font-weight: 700;" title="Còn ${item.days_to_expiry} ngày"><i class="fa-solid fa-hourglass-half"></i> ${expDateStr} (${item.days_to_expiry} ngày)</span>`;
            } else {
                expiryBadge = `<span style="color: var(--text-muted);">${expDateStr}</span>`;
            }
        }

        // Category Icon & Color
        let catIcon = 'fa-capsules';
        if (item.category === 'Vắc xin thú y') catIcon = 'fa-syringe';
        else if (item.category.includes('Spa') || item.category.includes('Mỹ phẩm')) catIcon = 'fa-pump-soap';
        else if (item.category.includes('Thức ăn') || item.category.includes('Dinh dưỡng')) catIcon = 'fa-bowl-food';
        else if (item.category.includes('Vật tư')) catIcon = 'fa-stethoscope';

        // Tỷ lệ tồn kho so với mức tối thiểu
        const percent = Math.min(100, Math.round((item.quantity / Math.max(1, item.min_threshold * 2)) * 100));
        let progressColor = '#10b981';
        if (item.quantity <= 0) progressColor = '#ef4444';
        else if (item.quantity <= item.min_threshold) progressColor = '#f59e0b';

        tr.innerHTML = `
            <td style="font-weight: 700; color: #818cf8; font-family: monospace; font-size: 0.88rem;">${item.sku}</td>
            <td>
                <div style="font-weight: 700; color: var(--text-main); font-size: 0.92rem;">${item.name}</div>
                <div style="font-size: 0.76rem; color: var(--text-dim); margin-top: 2px;">
                    <i class="fa-solid fa-truck-field"></i> ${item.supplier || 'Chưa cập nhật NCC'} • Lô: <strong>${item.batch_number || 'N/A'}</strong>
                </div>
            </td>
            <td>
                <span class="badge" style="background: rgba(255,255,255,0.06); color: var(--text-main); font-size: 0.78rem;">
                    <i class="fa-solid ${catIcon}" style="color: #38bdf8; margin-right: 4px;"></i> ${item.category}
                </span>
            </td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.05rem; font-weight: 800; color: ${progressColor};">${item.quantity}</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${item.unit}</span>
                </div>
                <div style="width: 75px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 4px; overflow: hidden;">
                    <div style="width: ${percent}%; height: 100%; background: ${progressColor};"></div>
                </div>
                <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 2px;">Tối thiểu: ${item.min_threshold}</div>
            </td>
            <td>
                <div style="font-size: 0.85rem; color: var(--text-muted);">Vốn: <strong>${formatCurrency(item.cost_price)}</strong></div>
                <div style="font-size: 0.88rem; color: #34d399; font-weight: 700; margin-top: 2px;">Bán: ${formatCurrency(item.selling_price)}</div>
            </td>
            <td>${expiryBadge}</td>
            <td>
                <span style="font-size: 0.82rem; color: var(--text-muted); background: rgba(255,255,255,0.04); padding: 3px 8px; border-radius: 4px; border: 1px solid var(--border-color);">
                    <i class="fa-solid fa-location-dot" style="color: #fb923c;"></i> ${item.shelf_location || 'Kho chung'}
                </span>
            </td>
            <td>${statusBadge}</td>
            <td>
                <div style="display: flex; gap: 4px; align-items: center;">
                    <button class="btn btn-success btn-sm" style="padding: 4px 8px; font-size: 0.78rem;" onclick="openStockInModal(${item.id})" title="Nhập thêm hàng">
                        <i class="fa-solid fa-plus"></i> Nhập
                    </button>
                    <button class="btn btn-warning btn-sm" style="padding: 4px 8px; font-size: 0.78rem;" onclick="openStockOutModal(${item.id})" title="Xuất kho sử dụng / Bán lẻ">
                        <i class="fa-solid fa-minus"></i> Xuất
                    </button>
                    <button class="btn btn-secondary btn-sm" style="padding: 4px 8px; font-size: 0.78rem;" onclick="openEditInventoryModal(${item.id})" title="Chỉnh sửa thông tin">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" style="padding: 4px 8px; font-size: 0.78rem;" onclick="deleteInventoryItem(${item.id})" title="Xóa mặt hàng">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Bộ lọc tìm kiếm Kho Hàng
 */
function filterInventory() {
    const searchVal = (document.getElementById('inv-search-input')?.value || '').toLowerCase().trim();
    const categoryVal = document.getElementById('inv-filter-category')?.value || 'ALL';
    const statusVal = document.getElementById('inv-filter-status')?.value || 'ALL';

    const filtered = inventoryItemsCache.filter(item => {
        // 1. Filter Category
        if (categoryVal !== 'ALL' && item.category !== categoryVal) return false;

        // 2. Filter Status
        if (statusVal === 'LOW_STOCK' && item.stock_status !== 'LOW_STOCK') return false;
        if (statusVal === 'OUT_OF_STOCK' && item.stock_status !== 'OUT_OF_STOCK') return false;
        if (statusVal === 'EXPIRING' && !item.is_expiring_soon && item.stock_status !== 'EXPIRED') return false;
        if (statusVal === 'IN_STOCK' && item.stock_status !== 'IN_STOCK') return false;

        // 3. Search Keyword
        if (searchVal) {
            const matchName = item.name.toLowerCase().includes(searchVal);
            const matchSku = item.sku.toLowerCase().includes(searchVal);
            const matchSupplier = (item.supplier || '').toLowerCase().includes(searchVal);
            const matchShelf = (item.shelf_location || '').toLowerCase().includes(searchVal);
            if (!matchName && !matchSku && !matchSupplier && !matchShelf) return false;
        }

        return true;
    });

    renderInventoryTable(filtered);
}

/**
 * Mở modal Thêm mặt hàng mới
 */
function openAddInventoryModal() {
    document.getElementById('inv-item-form')?.reset();
    document.getElementById('inv-item-id').value = '';
    document.getElementById('inv-modal-title').innerHTML = '<i class="fa-solid fa-box-open" style="color: #6366f1;"></i> Thêm Mặt Hàng / Dược Phẩm Mới';
    openModal('modal-inventory-item');
}

/**
 * Mở modal Chỉnh sửa mặt hàng
 */
function openEditInventoryModal(itemId) {
    const item = inventoryItemsCache.find(x => x.id === itemId);
    if (!item) return;

    document.getElementById('inv-item-id').value = item.id;
    document.getElementById('inv-sku').value = item.sku;
    document.getElementById('inv-name').value = item.name;
    document.getElementById('inv-category').value = item.category;
    document.getElementById('inv-unit').value = item.unit;
    document.getElementById('inv-quantity').value = item.quantity;
    document.getElementById('inv-min-threshold').value = item.min_threshold;
    document.getElementById('inv-cost-price').value = item.cost_price;
    document.getElementById('inv-selling-price').value = item.selling_price;
    document.getElementById('inv-batch').value = item.batch_number || '';
    document.getElementById('inv-expiry').value = item.expiry_date || '';
    document.getElementById('inv-supplier').value = item.supplier || '';
    document.getElementById('inv-shelf').value = item.shelf_location || '';
    document.getElementById('inv-notes').value = item.notes || '';

    document.getElementById('inv-modal-title').innerHTML = `<i class="fa-solid fa-pen-to-square" style="color: #38bdf8;"></i> Cập Nhật Mặt Hàng: ${item.sku}`;
    openModal('modal-inventory-item');
}

/**
 * Lưu mặt hàng (Thêm mới hoặc Cập nhật)
 */
async function saveInventoryItem(event) {
    if (event) event.preventDefault();

    const id = document.getElementById('inv-item-id')?.value;
    const payload = {
        sku: document.getElementById('inv-sku').value.trim().toUpperCase(),
        name: document.getElementById('inv-name').value.trim(),
        category: document.getElementById('inv-category').value,
        unit: document.getElementById('inv-unit').value.trim(),
        quantity: parseFloat(document.getElementById('inv-quantity').value) || 0,
        min_threshold: parseFloat(document.getElementById('inv-min-threshold').value) || 5,
        cost_price: parseFloat(document.getElementById('inv-cost-price').value) || 0,
        selling_price: parseFloat(document.getElementById('inv-selling-price').value) || 0,
        batch_number: document.getElementById('inv-batch').value.trim() || null,
        expiry_date: document.getElementById('inv-expiry').value || null,
        supplier: document.getElementById('inv-supplier').value.trim() || null,
        shelf_location: document.getElementById('inv-shelf').value.trim() || null,
        notes: document.getElementById('inv-notes').value.trim() || null
    };

    try {
        if (id) {
            await apiCall(`/inventory/items/${id}`, 'PUT', payload);
            showToast('✅ Đã cập nhật mặt hàng thành công!', 'success');
        } else {
            await apiCall('/inventory/items', 'POST', payload);
            showToast('🎉 Đã thêm mới mặt hàng vào kho thành công!', 'success');
        }
        closeModal('modal-inventory-item');
        loadInventory();
    } catch (err) {
        showToast('Lỗi lưu mặt hàng: ' + err.message, 'error');
    }
}

/**
 * Xóa mặt hàng khỏi kho
 */
async function deleteInventoryItem(itemId) {
    const item = inventoryItemsCache.find(x => x.id === itemId);
    if (!item) return;

    if (!confirm(`Bạn có chắc chắn muốn xóa mặt hàng "${item.name} (${item.sku})" khỏi hệ thống kho?`)) {
        return;
    }

    try {
        await apiCall(`/inventory/items/${itemId}`, 'DELETE');
        showToast(`Đã xóa mặt hàng "${item.name}"`, 'success');
        loadInventory();
    } catch (err) {
        showToast('Lỗi khi xóa: ' + err.message, 'error');
    }
}

/**
 * Mở modal Phiếu Nhập Kho
 */
function openStockInModal(itemId = null) {
    document.getElementById('stock-in-form')?.reset();
    populateItemSelectOptions('stock-in-item-select', itemId);

    if (itemId) {
        onStockInItemSelected(itemId);
    }
    openModal('modal-stock-in');
}

function onStockInItemSelected(itemId) {
    const item = inventoryItemsCache.find(x => x.id == itemId);
    if (item) {
        document.getElementById('stock-in-unit-cost').value = item.cost_price;
        document.getElementById('stock-in-batch').value = item.batch_number || '';
        document.getElementById('stock-in-expiry').value = item.expiry_date || '';
        document.getElementById('stock-in-supplier').value = item.supplier || '';
        document.getElementById('stock-in-cur-stock').textContent = `Tồn hiện tại: ${item.quantity} ${item.unit}`;
    }
}

/**
 * Xử lý xác nhận Nhập kho
 */
async function handleStockInSubmit(event) {
    if (event) event.preventDefault();

    const itemId = parseInt(document.getElementById('stock-in-item-select').value);
    const qty = parseFloat(document.getElementById('stock-in-qty').value);
    const cost = parseFloat(document.getElementById('stock-in-unit-cost').value);
    const batch = document.getElementById('stock-in-batch').value.trim();
    const expiry = document.getElementById('stock-in-expiry').value;
    const supplier = document.getElementById('stock-in-supplier').value.trim();
    const notes = document.getElementById('stock-in-notes').value.trim();

    if (!itemId || isNaN(qty) || qty <= 0) {
        showToast('Vui lòng chọn mặt hàng và nhập số lượng hợp lệ.', 'error');
        return;
    }

    const payload = {
        item_id: itemId,
        quantity: qty,
        unit_cost: !isNaN(cost) ? cost : null,
        batch_number: batch || null,
        expiry_date: expiry || null,
        supplier: supplier || null,
        performer_name: State.currentUser ? State.currentUser.full_name : 'Thủ kho',
        notes: notes || 'Nhập hàng từ nhà cung cấp'
    };

    try {
        const res = await apiCall('/inventory/stock-in', 'POST', payload);
        showToast(res.message || 'Nhập kho thành công!', 'success');
        closeModal('modal-stock-in');
        loadInventory();
    } catch (err) {
        showToast('Lỗi nhập kho: ' + err.message, 'error');
    }
}

/**
 * Mở modal Phiếu Xuất Kho
 */
function openStockOutModal(itemId = null) {
    document.getElementById('stock-out-form')?.reset();
    populateItemSelectOptions('stock-out-item-select', itemId);

    if (itemId) {
        onStockOutItemSelected(itemId);
    }
    openModal('modal-stock-out');
}

function onStockOutItemSelected(itemId) {
    const item = inventoryItemsCache.find(x => x.id == itemId);
    if (item) {
        document.getElementById('stock-out-cur-stock').innerHTML = `Tồn kho khả dụng: <strong style="color:#34d399;">${item.quantity} ${item.unit}</strong> (Đơn giá vốn: ${formatCurrency(item.cost_price)})`;
        const qtyInput = document.getElementById('stock-out-qty');
        if (qtyInput) qtyInput.max = item.quantity;
    }
}

/**
 * Xử lý xác nhận Xuất kho
 */
async function handleStockOutSubmit(event) {
    if (event) event.preventDefault();

    const itemId = parseInt(document.getElementById('stock-out-item-select').value);
    const qty = parseFloat(document.getElementById('stock-out-qty').value);
    const reason = document.getElementById('stock-out-reason').value;
    const refCode = document.getElementById('stock-out-ref').value.trim();
    const notes = document.getElementById('stock-out-notes').value.trim();

    if (!itemId || isNaN(qty) || qty <= 0) {
        showToast('Vui lòng chọn mặt hàng và số lượng xuất hợp lệ.', 'error');
        return;
    }

    const payload = {
        item_id: itemId,
        quantity: qty,
        reason: reason,
        performer_name: State.currentUser ? State.currentUser.full_name : 'Kỹ thuật viên',
        reference_code: refCode || null,
        notes: notes || null
    };

    try {
        const res = await apiCall('/inventory/stock-out', 'POST', payload);
        showToast(res.message || 'Xuất kho thành công!', 'success');
        closeModal('modal-stock-out');
        loadInventory();
    } catch (err) {
        showToast('Lỗi xuất kho: ' + err.message, 'error');
    }
}

/**
 * Điền danh sách mặt hàng vào dropdown select
 */
function populateItemSelectOptions(selectId, selectedId = null) {
    const select = document.getElementById(selectId);
    if (!select) return;

    select.innerHTML = '<option value="">-- Chọn mặt hàng dược phẩm / vật tư --</option>';
    inventoryItemsCache.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.id;
        opt.textContent = `[${item.sku}] ${item.name} (Tồn: ${item.quantity} ${item.unit})`;
        if (selectedId && item.id == selectedId) {
            opt.selected = true;
        }
        select.appendChild(opt);
    });
}

/**
 * Mở modal Lịch sử Xuất / Nhập / Tồn
 */
async function openTransactionHistoryModal(itemId = null) {
    try {
        const url = itemId ? `/inventory/transactions?item_id=${itemId}` : '/inventory/transactions';
        const txs = await apiCall(url);
        renderTransactionHistoryTable(txs);
        openModal('modal-inventory-history');
    } catch (err) {
        showToast('Không thể tải lịch sử giao dịch: ' + err.message, 'error');
    }
}

function renderTransactionHistoryTable(txs) {
    const tbody = document.getElementById('inv-history-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!txs || txs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-dim);">Chưa có lịch sử giao dịch nào.</td></tr>';
        return;
    }

    txs.forEach(t => {
        const tr = document.createElement('tr');
        let typeBadge = '';
        if (t.transaction_type === 'IMPORT') {
            typeBadge = '<span class="badge" style="background: rgba(16,185,129,0.2); color: #34d399;"><i class="fa-solid fa-arrow-down"></i> Nhập Kho</span>';
        } else if (t.transaction_type === 'EXPORT') {
            typeBadge = '<span class="badge" style="background: rgba(245,158,11,0.2); color: #fbbf24;"><i class="fa-solid fa-arrow-up"></i> Xuất Kho</span>';
        } else {
            typeBadge = '<span class="badge" style="background: rgba(99,102,241,0.2); color: #818cf8;"><i class="fa-solid fa-arrows-rotate"></i> Cân Chỉnh</span>';
        }

        const timeStr = t.created_at ? new Date(t.created_at).toLocaleString('vi-VN') : 'N/A';

        tr.innerHTML = `
            <td style="font-size: 0.8rem; color: var(--text-muted);">${timeStr}</td>
            <td><strong style="color: #818cf8; font-family: monospace;">${t.reference_code || 'N/A'}</strong></td>
            <td>
                <div style="font-weight: 700; color: var(--text-main); font-size: 0.88rem;">${t.item_name}</div>
                <div style="font-size: 0.75rem; color: var(--text-dim); font-family: monospace;">SKU: ${t.item_sku}</div>
            </td>
            <td>${typeBadge}</td>
            <td style="font-weight: 800; font-size: 0.95rem; text-align: right;">${t.quantity}</td>
            <td style="text-align: right; color: #38bdf8; font-weight: 700;">${formatCurrency(t.total_price)}</td>
            <td>
                <div style="font-size: 0.82rem; font-weight: 600;">${t.performer_name}</div>
                <div style="font-size: 0.75rem; color: var(--text-dim);">${t.notes || ''}</div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * In Báo cáo tồn kho
 */
function printInventoryReport() {
    window.print();
}
