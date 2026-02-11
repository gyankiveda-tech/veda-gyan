/**
 * VEDA VERSE - Core Logic Engine
 * Architect: Gyan Vardhan
 */

const API_URL = "http://localhost:8000";

// --- 1. Identity Management ---
function saveUserIdentity() {
    const nameInput = document.getElementById('userNameInput').value.trim();
    if (!nameInput) {
        alert("🚨 ACCESS DENIED: Identity required to initialize system.");
        return;
    }
    localStorage.setItem('veda_alias', nameInput);
    
    document.getElementById('identityModal').classList.add('hidden');
    const badge = document.getElementById('userBadge');
    badge.classList.remove('hidden');
    badge.classList.add('flex');
    document.getElementById('activeUser').innerText = nameInput.toUpperCase();
}

// पेज लोड होते ही डेटा सिंक करना
window.addEventListener('load', () => {
    const savedName = localStorage.getItem('veda_alias');
    if (savedName) {
        document.getElementById('identityModal').classList.add('hidden');
        const badge = document.getElementById('userBadge');
        badge.classList.remove('hidden');
        badge.classList.add('flex');
        document.getElementById('activeUser').innerText = savedName.toUpperCase();
    }
    // Honor Wall लोड करें
    loadHonorWall();
});

// --- 2. Shagun & Payment Logic ---
let currentSelectedAmount = 0;

function openPaymentModal() {
    document.getElementById('paymentModal').classList.remove('hidden');
}

function closePaymentModal() {
    document.getElementById('paymentModal').classList.add('hidden');
}

function setShagun(amount) {
    currentSelectedAmount = amount;
    const upiID = "archanasinghjsr2-1@oksbi";
    const name = "GyanVardhan";
    
    /**
     * UPDATED: UPI Deep Link for Amount Lock
     * am=${amount} Google Pay/PhonePe में अमाउंट को फिक्स कर देता है।
     */
    const upiLink = `upi://pay?pa=${upiID}&pn=${encodeURIComponent(name)}&am=${amount}&cu=INR&tn=VEDA_VERSE_SHAGUN`;
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(upiLink)}`;
    
    const qrImg = document.getElementById('shagunQR');
    qrImg.style.opacity = '0.5';
    qrImg.src = qrUrl;
    
    qrImg.onload = () => {
        qrImg.style.opacity = '1';
    };
}

// Transaction Verify करके Admin को भेजने का लॉजिक
async function verifyTxn() {
    const txnIdInput = document.getElementById('txnId');
    const txnId = txnIdInput.value.trim();
    const userAlias = localStorage.getItem('veda_alias') || "Unknown User";

    if (!txnId) {
        alert("⚠️ Please enter a valid Transaction ID!");
        return;
    }

    // Amount चेक करें (कम से कम 1 होना चाहिए)
    const finalAmount = currentSelectedAmount || "51";

    const formData = new FormData();
    formData.append('name', userAlias);
    formData.append('amount', finalAmount); 
    formData.append('txn_id', txnId); // पक्का करें कि यह Admin को जा रहा है

    try {
        const response = await fetch(`${API_URL}/add-honor`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            alert(`✅ SENT: Request for Txn ID ${txnId} has been sent to Admin for verification.`);
            txnIdInput.value = ''; // Input साफ़ करें
            closePaymentModal();
            loadHonorWall(); // वेबसाइट लिस्ट रिफ्रेश करें
        } else {
            alert("❌ Server rejected the request. Please check if Python is running.");
        }
    } catch (error) {
        console.error("Verification Error:", error);
        alert("❌ CONNECTION FAILED: Make sure your Python server is running on localhost:8000");
    }
}

// Honor Wall को Backend से लोड करना
async function loadHonorWall() {
    try {
        const res = await fetch(`${API_URL}/get-honor-wall`);
        const data = await res.json();
        
        const wall = document.getElementById('leaderboard'); 
        if(!wall) return;

        wall.innerHTML = ''; // पुराने स्टैटिक नाम साफ़ करें

        if (data.length === 0) {
            wall.innerHTML = '<p class="text-[10px] text-gray-500 italic text-center w-full">No legends yet.</p>';
            return;
        }

        data.forEach(user => {
            // Transaction ID सिर्फ एडमिन को दिखे, यहाँ सिर्फ नाम और अमाउंट दिखेगा
            wall.innerHTML += `
                <div class="flex justify-between items-center bg-indigo-500/10 p-2 rounded-lg border border-indigo-500/20">
                    <span class="text-[10px] font-bold text-white uppercase">${user.name}</span>
                    <span class="text-[10px] font-mono text-indigo-400">₹${user.amount}</span>
                </div>
            `;
        });
    } catch (err) {
        console.error("Wall load error:", err);
    }
}

// --- 3. Image Processing Logic ---
let selectedFile = null;
let bgImageFile = null;
let currentCanvasSize = "original";

// Elements
const fileInput = document.getElementById('fileInput');
const bgImageInput = document.getElementById('bgImageInput');
const afterImg = document.getElementById('afterImg');
const placeholder = document.getElementById('placeholder');
const editTools = document.getElementById('editTools');
const canvasContainer = document.getElementById('canvasContainer');
const loading = document.getElementById('loading');
const scanner = document.getElementById('scanner');
const downloadBar = document.getElementById('downloadBar');
const downloadBtn = document.getElementById('downloadBtn');

function changeCanvas(aspect, apiSize) {
    currentCanvasSize = apiSize;
    if (aspect === 'auto') {
        canvasContainer.style.aspectRatio = "auto";
        canvasContainer.style.width = "auto";
    } else {
        canvasContainer.style.aspectRatio = aspect.replace('/', '/');
        canvasContainer.style.width = "100%";
        canvasContainer.style.height = "auto";
    }
}

document.getElementById('brightness').addEventListener('input', (e) => {
    document.getElementById('v-bright').innerText = e.target.value;
});

document.getElementById('contrast').addEventListener('input', (e) => {
    document.getElementById('v-contrast').innerText = e.target.value;
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        selectedFile = e.target.files[0];
        const url = URL.createObjectURL(selectedFile);
        placeholder.classList.add('hidden');
        afterImg.classList.remove('hidden');
        afterImg.src = url;
        editTools.classList.remove('opacity-50');
        editTools.style.pointerEvents = 'auto';
    }
});

bgImageInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        bgImageFile = e.target.files[0];
        alert("🎯 CUSTOM BACKGROUND LOADED");
    }
});

async function handleUpload() {
    if (!selectedFile) {
        alert("⚠️ CRITICAL ERROR: No asset found.");
        return;
    }

    loading.classList.remove('hidden');
    scanner.classList.remove('hidden');
    downloadBar.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('brightness', document.getElementById('brightness').value);
    formData.append('contrast', document.getElementById('contrast').value);
    formData.append('canvas_size', currentCanvasSize);
    formData.append('bg_color', document.getElementById('bgColor').value);

    const textOverlay = document.getElementById('textOverlay').value;
    if (textOverlay) formData.append('text_overlay', textOverlay);
    if (bgImageFile) formData.append('bg_image', bgImageFile);

    try {
        const response = await fetch(`${API_URL}/remove-bg`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Backend Offline');

        const blob = await response.blob();
        const finalUrl = URL.createObjectURL(blob);

        afterImg.src = finalUrl;
        downloadBtn.href = finalUrl;
        downloadBtn.download = `VEDA_RENDER_${Date.now()}.png`;
        downloadBar.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        alert("❌ NEURAL LINK FAILED: Check your Python server on port 8000.");
    } finally {
        loading.classList.add('hidden');
        scanner.classList.add('hidden');
    }
}