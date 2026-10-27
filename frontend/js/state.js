// ============================================================
// STATE MANAGEMENT & TOAST UTILITIES
// ============================================================

const state = {
  currentRole: 'admin', // 'admin', 'receptionist', 'staff'
  currentUser: {
    username: 'admin',
    name: 'Nguyễn Văn Quản Lý',
    role: 'admin'
  },
  activeTab: 'dashboard',
  owners: [],
  pets: [],
  services: [],
  appointments: [],
  careRecords: [],
  vaccines: [],
  invoices: [],
  aiLogs: []
};

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  toast.innerHTML = `<div>${message}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount || 0);
}

function formatDateVN(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
}
