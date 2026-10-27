// PetCare AI Pro - Pets & Owners Module

let searchPetTimeout = null;
let currentSelectedAvatarUrl = 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80';

// Avatar Presets for Dogs & Cats
const AVATAR_PRESETS = [
    { name: "Poodle", url: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80" },
    { name: "Mèo Anh (BSH)", url: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80" },
    { name: "Corgi", url: "https://images.unsplash.com/photo-1612536057832-2ff7ead58194?auto=format&fit=crop&w=400&q=80" },
    { name: "Golden", url: "https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400&q=80" },
    { name: "Husky", url: "https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?auto=format&fit=crop&w=400&q=80" },
    { name: "Mèo Vàng Tabby", url: "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=400&q=80" },
    { name: "Phốc Sóc Pomeranian", url: "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=400&q=80" },
    { name: "Mèo Ba Tư", url: "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=400&q=80" }
];

async function loadPets(searchTerm = '') {
    const container = document.getElementById('pets-cards-container');
    if (!container) return;

    let url = '/pets?';
    if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;

    try {
        const pets = await apiCall(url);
        State.pets = pets;

        if (pets.length === 0) {
            container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 3rem;">Không tìm thấy hồ sơ thú cưng nào.</div>`;
            return;
        }

        container.innerHTML = pets.map(p => `
            <div class="glass-panel pet-card" style="cursor: pointer;" onclick="viewPetDetailModal(${p.id})">
                <div class="pet-card-header">
                    <img src="${p.avatar_url || 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=200&q=80'}" 
                         alt="${p.name}" 
                         class="pet-avatar"
                         onerror="this.src='https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=200&q=80'">
                    <div style="flex: 1;">
                        <div class="pet-name">${p.name} <span class="badge" style="background: rgba(99,102,241,0.15); color: #818cf8;">${p.species}</span></div>
                        <div class="pet-meta">${p.breed || 'Chưa rõ giống'} • ${p.gender || 'Đực'} • ${p.age_years}t ${p.age_months}th</div>
                    </div>
                </div>

                <div style="font-size: 0.82rem; margin-bottom: 0.75rem;">
                    <div class="pet-details-row">
                        <span>Chủ nuôi:</span>
                        <span><strong>${p.owner_name || 'N/A'}</strong> (${p.owner_phone || ''})</span>
                    </div>
                    <div class="pet-details-row">
                        <span>Cân nặng hiện tại:</span>
                        <span style="display: flex; align-items: center; gap: 6px;">
                            <strong style="color: #38bdf8;">${p.weight_kg ? p.weight_kg + ' kg' : 'Chưa cân'}</strong>
                            <button type="button" class="btn btn-secondary btn-sm" onclick="openUpdateWeightModal(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.weight_kg || 3.5})" title="Cập nhật cân nặng mới cho bé" style="padding: 1px 7px; font-size: 0.72rem; border-radius: 6px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; cursor: pointer; font-weight: 700;">
                                <i class="fa-solid fa-pen-to-square"></i> Cân
                            </button>
                        </span>
                    </div>
                    <div class="pet-details-row">
                        <span>Mã Microchip:</span>
                        <span>${p.microchip_id || 'Chưa gắn'}</span>
                    </div>
                    ${p.allergies ? `
                    <div style="margin-top: 6px; padding: 6px 8px; background: rgba(239,68,68,0.1); border-radius: var(--radius-sm); color: #fca5a5; font-size: 0.78rem;">
                        <strong><i class="fa-solid fa-triangle-exclamation"></i> Dị ứng:</strong> ${p.allergies}
                    </div>` : ''}
                    ${p.medical_notes ? `
                    <div style="margin-top: 4px; padding: 6px 8px; background: rgba(245,158,11,0.1); border-radius: var(--radius-sm); color: #fbbf24; font-size: 0.78rem;">
                        <strong><i class="fa-solid fa-notes-medical"></i> Lưu ý:</strong> ${p.medical_notes}
                    </div>` : ''}
                </div>

                <div style="margin-top: auto; display: flex; gap: 0.5rem; pt-2;" onclick="event.stopPropagation()">
                    <button class="btn btn-ai btn-sm" style="flex: 1; justify-content: center;" onclick="quickSummarizePet(${p.id})">
                        <i class="fa-solid fa-file-medical-alt"></i> AI Báo Cáo
                    </button>
                    <button class="btn btn-primary btn-sm" style="flex: 1; justify-content: center;" onclick="quickBookForPet(${p.id})">
                        <i class="fa-solid fa-calendar-plus"></i> Đặt Lịch
                    </button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = `<div style="color: var(--danger); padding: 2rem;">Lỗi tải thú cưng: ${e.message}</div>`;
    }
}

function debounceSearchPets() {
    clearTimeout(searchPetTimeout);
    searchPetTimeout = setTimeout(() => {
        const val = document.getElementById('search-pet-input')?.value || '';
        loadPets(val);
    }, 300);
}

function openAddPetModal() {
    populateModalDropdowns();
    renderAvatarPresets();
    openModal('modal-add-pet');
}

function renderAvatarPresets() {
    const container = document.getElementById('pet-avatar-presets');
    if (!container) return;

    container.innerHTML = AVATAR_PRESETS.map((p, idx) => `
        <div style="cursor: pointer; text-align: center; border: 2px solid ${idx === 0 ? '#6366f1' : 'transparent'}; border-radius: var(--radius-sm); padding: 2px;"
             class="avatar-preset-item ${idx === 0 ? 'selected' : ''}"
             onclick="selectAvatarPreset('${p.url}', this)">
            <img src="${p.url}" alt="${p.name}" style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover; display: block; margin: 0 auto;">
            <span style="font-size: 0.65rem; color: var(--text-dim); display: block; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 50px;">${p.name}</span>
        </div>
    `).join('');
    currentSelectedAvatarUrl = AVATAR_PRESETS[0].url;
}

function selectAvatarPreset(url, element) {
    currentSelectedAvatarUrl = url;
    document.querySelectorAll('.avatar-preset-item').forEach(el => el.style.borderColor = 'transparent');
    if (element) element.style.borderColor = '#6366f1';
    const preview = document.getElementById('modal-pet-avatar-preview');
    if (preview) preview.src = url;
}

function openAddOwnerModal() {
    openModal('modal-add-owner');
}

async function submitAddOwner() {
    const name = document.getElementById('modal-owner-name')?.value;
    const phone = document.getElementById('modal-owner-phone')?.value;
    const address = document.getElementById('modal-owner-address')?.value;
    const email = document.getElementById('modal-owner-email')?.value;

    if (!name || !phone) {
        showToast('Vui lòng nhập họ tên và số điện thoại chủ nuôi!', 'error');
        return;
    }

    try {
        const newOwner = await apiCall('/owners', 'POST', {
            full_name: name,
            phone,
            address: address || null,
            email: email || null
        });
        closeModal('modal-add-owner');
        showToast(`Đã thêm chủ nuôi ${newOwner.full_name}!`, 'success');
        
        await loadGlobalMetadata();
    } catch (e) {
        showToast('Lỗi thêm chủ nuôi: ' + e.message, 'error');
    }
}

async function submitAddPet() {
    const ownerId = document.getElementById('modal-pet-owner')?.value;
    const name = document.getElementById('modal-pet-name')?.value;
    const species = document.getElementById('modal-pet-species')?.value;
    const breed = document.getElementById('modal-pet-breed')?.value;
    const gender = document.getElementById('modal-pet-gender')?.value;
    const weight = document.getElementById('modal-pet-weight')?.value;
    const ageYears = document.getElementById('modal-pet-age-years')?.value;
    const ageMonths = document.getElementById('modal-pet-age-months')?.value;
    const chip = document.getElementById('modal-pet-chip')?.value;
    const allergies = document.getElementById('modal-pet-allergies')?.value;
    const notes = document.getElementById('modal-pet-notes')?.value;
    const customAvatar = document.getElementById('modal-pet-custom-avatar')?.value?.trim();

    if (!ownerId || !name) {
        showToast('Vui lòng chọn chủ nuôi và nhập tên bé thú cưng!', 'error');
        return;
    }

    try {
        const payload = {
            owner_id: parseInt(ownerId),
            name,
            species,
            breed: breed || null,
            gender: gender || 'Đực',
            weight_kg: weight ? parseFloat(weight) : 3.5,
            age_years: ageYears ? parseInt(ageYears) : 1,
            age_months: ageMonths ? parseInt(ageMonths) : 0,
            microchip_id: chip || null,
            allergies: allergies || null,
            medical_notes: notes || null,
            avatar_url: customAvatar || currentSelectedAvatarUrl
        };

        const newPet = await apiCall('/pets', 'POST', payload);
        closeModal('modal-add-pet');
        showToast(`Đã thêm hồ sơ bé ${newPet.name}!`, 'success');
        
        await loadGlobalMetadata();
        loadPets();
    } catch (e) {
        showToast('Lỗi thêm thú cưng: ' + e.message, 'error');
    }
}

async function viewPetDetailModal(petId) {
    const pet = State.pets.find(p => p.id === petId);
    if (!pet) return;

    const modal = document.getElementById('modal-pet-profile');
    if (!modal) return;

    document.getElementById('modal-profile-avatar').src = pet.avatar_url || 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=400&q=80';
    document.getElementById('modal-profile-name').textContent = pet.name;
    document.getElementById('modal-profile-species-badge').textContent = pet.species;
    document.getElementById('modal-profile-meta').textContent = `${pet.breed || 'Chưa rõ giống'} • Giới tính: ${pet.gender || 'Đực'} • Tuổi: ${pet.age_years} tuổi ${pet.age_months} tháng`;
    document.getElementById('modal-profile-owner').textContent = `${pet.owner_name || 'N/A'} (${pet.owner_phone || 'Chưa có SĐT'})`;
    document.getElementById('modal-profile-weight').textContent = pet.weight_kg ? `${pet.weight_kg} kg` : 'Chưa cân';
    document.getElementById('modal-profile-chip').textContent = pet.microchip_id || 'Chưa cấy chip';
    document.getElementById('modal-profile-allergies').textContent = pet.allergies || 'Không có ghi nhận dị ứng';
    document.getElementById('modal-profile-notes').textContent = pet.medical_notes || 'Không có tiền sử bệnh lý đặc biệt';

    const btnWeight = document.getElementById('modal-profile-btn-weight');
    if (btnWeight) {
        btnWeight.onclick = () => {
            openUpdateWeightModal(pet.id, pet.name, pet.weight_kg || 3.5);
        };
    }

    // Set buttons
    document.getElementById('modal-profile-btn-ai').onclick = () => {
        closeModal('modal-pet-profile');
        quickSummarizePet(pet.id);
    };
    document.getElementById('modal-profile-btn-book').onclick = () => {
        closeModal('modal-pet-profile');
        quickBookForPet(pet.id);
    };

    openModal('modal-pet-profile');
}

function quickBookForPet(petId) {
    openBookingModal();
    const select = document.getElementById('modal-book-pet');
    if (select) select.value = petId;
}

function quickSummarizePet(petId) {
    switchTab('ai_studio');
    setTimeout(() => {
        const select = document.getElementById('ai-summary-pet-select');
        if (select) {
            select.value = petId;
            generateAICareSummary();
        }
    }, 150);
}
