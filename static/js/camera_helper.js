// PetCare AI Pro - Camera & Photo Capture Module
// Manages real-time Webcam streaming, snapshot capturing, and file uploads

let activeCameraStream = null;
let activeCameraContext = 'chat'; // 'chat' | 'pet-avatar'
let activeCapturedDataUrl = null;
let currentChatAttachedImage = null;

/**
 * Open the camera snapshot modal
 * @param {string} targetContext - 'chat' | 'pet-avatar'
 */
async function openCameraModal(targetContext = 'chat') {
    activeCameraContext = targetContext;
    activeCapturedDataUrl = null;

    const modal = document.getElementById('modal-camera-capture');
    if (!modal) {
        console.error('Camera capture modal not found');
        return;
    }

    // Reset UI state
    document.getElementById('camera-viewfinder-box')?.classList.remove('hidden');
    document.getElementById('camera-preview-box')?.classList.add('hidden');
    document.getElementById('camera-capture-actions')?.classList.remove('hidden');
    document.getElementById('camera-confirm-actions')?.classList.add('hidden');
    document.getElementById('camera-error-message')?.classList.add('hidden');

    modal.classList.add('active');

    // Check mediaDevices support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showCameraError('Trình duyệt của bạn chưa hỗ trợ truy cập Camera trực tiếp. Vui lòng sử dụng tính năng "Tải ảnh từ máy" bên dưới.');
        return;
    }

    try {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        activeCameraStream = stream;

        const videoEl = document.getElementById('camera-feed-video');
        if (videoEl) {
            videoEl.srcObject = stream;
            videoEl.play().catch(e => console.warn('Autoplay error:', e));
        }
    } catch (err) {
        console.error('Camera access error:', err);
        let errorMsg = 'Không thể mở Camera. ';
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            errorMsg += 'Vui lòng cấp quyền truy cập Camera cho trình duyệt trong cài đặt trang web.';
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            errorMsg += 'Không tìm thấy thiết bị Camera nào trên máy tính / điện thoại của bạn.';
        } else {
            errorMsg += 'Lỗi: ' + (err.message || 'Không mở được luồng video.');
        }
        showCameraError(errorMsg);
    }
}

/**
 * Display camera error message with fallback button
 */
function showCameraError(message) {
    const errorDiv = document.getElementById('camera-error-message');
    const errorText = document.getElementById('camera-error-text');
    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    document.getElementById('camera-capture-actions')?.classList.add('hidden');
}

/**
 * Shutter action: take snapshot from live stream
 */
function takeCameraSnapshot() {
    const video = document.getElementById('camera-feed-video');
    const canvas = document.getElementById('camera-snapshot-canvas');
    const previewImg = document.getElementById('camera-preview-img');
    const flash = document.getElementById('camera-flash-effect');

    if (!video || !canvas || !previewImg) return;

    // Flash animation
    if (flash) {
        flash.classList.add('flash-active');
        setTimeout(() => flash.classList.remove('flash-active'), 250);
    }

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    // Mirror image horizontally to match webcam mirror preview
    ctx.translate(width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, width, height);

    // Get DataURL JPEG (compact, 85% quality)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
    activeCapturedDataUrl = dataUrl;

    previewImg.src = dataUrl;

    // Switch view to review mode
    document.getElementById('camera-viewfinder-box')?.classList.add('hidden');
    document.getElementById('camera-preview-box')?.classList.remove('hidden');
    document.getElementById('camera-capture-actions')?.classList.add('hidden');
    document.getElementById('camera-confirm-actions')?.classList.remove('hidden');
}

/**
 * Retake photo: return to live video stream
 */
function retakeCameraSnapshot() {
    activeCapturedDataUrl = null;
    document.getElementById('camera-viewfinder-box')?.classList.remove('hidden');
    document.getElementById('camera-preview-box')?.classList.add('hidden');
    document.getElementById('camera-capture-actions')?.classList.remove('hidden');
    document.getElementById('camera-confirm-actions')?.classList.add('hidden');
}

/**
 * Accept captured snapshot and apply to context
 */
function confirmCameraSnapshot() {
    if (!activeCapturedDataUrl) return;

    applyPhotoToContext(activeCapturedDataUrl, activeCameraContext);
    closeCameraModal();
}

/**
 * Close camera modal and stop media tracks
 */
function closeCameraModal() {
    const modal = document.getElementById('modal-camera-capture');
    if (modal) modal.classList.remove('active');

    if (activeCameraStream) {
        activeCameraStream.getTracks().forEach(track => {
            try {
                track.stop();
            } catch (e) {
                console.warn(e);
            }
        });
        activeCameraStream = null;
    }

    const videoEl = document.getElementById('camera-feed-video');
    if (videoEl) videoEl.srcObject = null;
}

/**
 * Dispatch photo data to destination (Chat or Pet Avatar)
 */
function applyPhotoToContext(dataUrl, context) {
    if (context === 'chat') {
        currentChatAttachedImage = dataUrl;
        const previewWrap = document.getElementById('chat-attachment-preview');
        const previewImg = document.getElementById('chat-attachment-thumb');
        if (previewWrap && previewImg) {
            previewImg.src = dataUrl;
            previewWrap.classList.remove('hidden');
            previewWrap.style.display = 'flex';
        }
        // Focus chat input for easy typing
        const input = document.getElementById('chat-input-field');
        if (input) {
            input.focus();
            if (!input.value) {
                input.placeholder = 'Nhập câu hỏi hoặc tình trạng cho ảnh này...';
            }
        }
        if (typeof showToast === 'function') {
            showToast('Đã đính kèm ảnh thú cưng! Hãy gửi tin nhắn để Bác sĩ AI phân tích.', 'success');
        }
    } else if (context === 'pet-avatar') {
        const preview = document.getElementById('modal-pet-avatar-preview');
        const inputUrl = document.getElementById('modal-pet-custom-avatar');
        if (preview) preview.src = dataUrl;
        if (inputUrl) inputUrl.value = dataUrl;
        if (typeof currentSelectedAvatarUrl !== 'undefined') {
            currentSelectedAvatarUrl = dataUrl;
        }
        if (typeof showToast === 'function') {
            showToast('Đã cập nhật ảnh đại diện thú cưng từ Camera!', 'success');
        }
    }
}

/**
 * Trigger file picker for chat
 */
function triggerChatImageUpload() {
    const fileInput = document.getElementById('chat-photo-input');
    if (fileInput) fileInput.click();
}

/**
 * Handle image file selection for chat
 */
function handleChatPhotoSelected(event) {
    const file = event.target?.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Vui lòng chọn tệp định dạng hình ảnh (JPEG, PNG, WEBP).');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const dataUrl = e.target.result;
        applyPhotoToContext(dataUrl, 'chat');
    };
    reader.readAsDataURL(file);
    event.target.value = ''; // Reset input
}

/**
 * Remove attached photo from chat
 */
function removeChatPhotoAttachment() {
    currentChatAttachedImage = null;
    const previewWrap = document.getElementById('chat-attachment-preview');
    if (previewWrap) {
        previewWrap.classList.add('hidden');
        previewWrap.style.display = 'none';
    }
    const input = document.getElementById('chat-input-field');
    if (input) input.placeholder = 'Hỏi bác sĩ AI về thú cưng...';
}

/**
 * Trigger file picker for Pet Avatar
 */
function triggerPetAvatarUpload() {
    const fileInput = document.getElementById('pet-avatar-file-input');
    if (fileInput) fileInput.click();
}

/**
 * Handle image file selection for Pet Avatar
 */
function handlePetAvatarSelected(event) {
    const file = event.target?.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Vui lòng chọn tệp định dạng hình ảnh (JPEG, PNG, WEBP).');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const dataUrl = e.target.result;
        applyPhotoToContext(dataUrl, 'pet-avatar');
    };
    reader.readAsDataURL(file);
    event.target.value = '';
}
