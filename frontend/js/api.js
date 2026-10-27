// ============================================================
// API CLIENT - PetCare AI System
// ============================================================

const API_BASE = '/api';

const api = {
  async get(endpoint, params = {}) {
    const url = new URL(API_BASE + endpoint, window.location.origin);
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        url.searchParams.append(k, params[k]);
      }
    });

    const resp = await fetch(url.toString());
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Có lỗi xảy ra khi gọi máy chủ.');
    }
    return data;
  },

  async post(endpoint, body = {}) {
    const resp = await fetch(API_BASE + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Lỗi xử lý dữ liệu.');
    }
    return data;
  },

  async put(endpoint, body = {}) {
    const resp = await fetch(API_BASE + endpoint, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Lỗi cập nhật dữ liệu.');
    }
    return data;
  },

  async patch(endpoint, params = {}) {
    const url = new URL(API_BASE + endpoint, window.location.origin);
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        url.searchParams.append(k, params[k]);
      }
    });

    const resp = await fetch(url.toString(), { method: 'PATCH' });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Lỗi cập nhật trạng thái.');
    }
    return data;
  },

  async delete(endpoint) {
    const resp = await fetch(API_BASE + endpoint, { method: 'DELETE' });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'Lỗi xóa dữ liệu.');
    }
    return data;
  }
};
