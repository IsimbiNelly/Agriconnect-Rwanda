/* ============================================================
   AgriConnect – Shared Config & Utilities
   ============================================================ */

const API_BASE = '';   // same-origin; server serves both HTML and API

const CATEGORY_ICONS = {
  Grains: '🌾', Vegetables: '🥬', Fruits: '🍎',
  Dairy: '🥛', Livestock: '🐄', Other: '📦'
};

// ── Auth helpers ──────────────────────────────────────────────
function getToken() { return localStorage.getItem('agri_token'); }
function getUser()  {
  try { return JSON.parse(localStorage.getItem('agri_user') || 'null'); }
  catch { return null; }
}

function saveAuth(token, user) {
  localStorage.setItem('agri_token', token);
  localStorage.setItem('agri_user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('agri_token');
  localStorage.removeItem('agri_user');
}

function logout() {
  clearAuth();
  window.location.href = '/';
}

function requireAuth(role = null) {
  const token = getToken();
  const user  = getUser();
  if (!token || !user) { window.location.href = '/'; return null; }
  if (role && user.role !== role) {
    // Send to the correct dashboard for the user's actual role
    redirectByRole(user.role);
    return null;
  }
  return user;
}

// ── API fetch wrapper ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();

  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let body = options.body;
  if (body && !(body instanceof FormData) && typeof body === 'object') {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }

  const fetchOptions = {
    method:  options.method || 'GET',
    headers: { ...headers, ...(options.headers || {}) },
  };
  if (body !== undefined) fetchOptions.body = body;

  const url = `${API_BASE}${path}`;
  console.log(`[API] ${fetchOptions.method} ${url}`);

  let res;
  try {
    res = await fetch(url, fetchOptions);
  } catch (networkErr) {
    console.error('[API] Network error:', networkErr);
    throw new Error('Cannot reach server. Make sure the app is running on port 8000.');
  }

  console.log(`[API] ← ${res.status} ${res.statusText}`);

  if (res.status === 401) {
    clearAuth();
    window.location.href = '/';
    return;
  }

  let data;
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (!res.ok) {
    const msg = data.detail
      ? (Array.isArray(data.detail) ? data.detail.map(e => e.msg).join(', ') : data.detail)
      : `Server error ${res.status}`;
    console.error('[API] Error response:', data);
    throw new Error(msg);
  }

  return data;
}

// ── Currency ──────────────────────────────────────────────────
function formatPrice(p) {
  return `RWF ${Number(p).toLocaleString('en-RW')}`;
}

// ── WebSocket real-time notifications ─────────────────────────
let _ws = null;

function connectWS(onMessage) {
  const token = getToken();
  if (!token) return;

  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const url   = `${proto}://${location.host}/ws?token=${encodeURIComponent(token)}`;

  function open() {
    _ws = new WebSocket(url);

    _ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        onMessage(data);
      } catch { /* ignore */ }
    };

    _ws.onclose = () => {
      // Reconnect after 3 s
      setTimeout(open, 3000);
    };

    _ws.onerror = () => _ws.close();
  }

  open();
}

// ── Notification bell ─────────────────────────────────────────
async function initNotificationBell(bellId, badgeId, listId) {
  const bell  = document.getElementById(bellId);
  const badge = document.getElementById(badgeId);
  const list  = document.getElementById(listId);
  if (!bell) return;

  async function refresh() {
    try {
      const notifs = await apiFetch('/api/products/notifications/list');
      const unread = notifs.filter(n => !n.is_read).length;
      badge.textContent = unread > 9 ? '9+' : unread || '';
      badge.style.display = unread ? 'flex' : 'none';

      if (list) {
        list.innerHTML = notifs.length === 0
          ? '<div class="notif-empty">No notifications yet</div>'
          : notifs.slice(0, 20).map(n => `
              <div class="notif-item${n.is_read ? '' : ' notif-unread'}">
                <span class="notif-icon">${ntypeIcon(n.ntype)}</span>
                <div class="notif-body">
                  <div class="notif-title">${n.title}</div>
                  <div class="notif-text">${n.body}</div>
                  <div class="notif-time">${timeAgo(n.created_at)}</div>
                </div>
              </div>`).join('');
      }
    } catch { /* ignore */ }
  }

  bell.addEventListener('click', async (e) => {
    e.stopPropagation();
    const panel = document.getElementById('notif-panel');
    if (!panel) return;
    const open = panel.classList.toggle('open');
    if (open) {
      await refresh();
      await apiFetch('/api/products/notifications/mark-read', { method: 'POST' });
      badge.style.display = 'none';
      badge.textContent = '';
    }
  });

  document.addEventListener('click', () => {
    const panel = document.getElementById('notif-panel');
    if (panel) panel.classList.remove('open');
  });

  await refresh();

  // Real-time: bump badge on incoming notification
  connectWS((data) => {
    if (data.type === 'product' || data.type === 'order' || data.type === 'transaction' || data.type === 'message' || data.type === 'rating') {
      const cur = parseInt(badge.textContent) || 0;
      const next = cur + 1;
      badge.textContent = next > 9 ? '9+' : next;
      badge.style.display = 'flex';
      showToast(data.body, data.type === 'transaction' ? 'success' : 'info');
    }
  });
}

function ntypeIcon(t) {
  return { product: '🌱', order: '🛒', transaction: '✅', message: '💬', rating: '⭐', info: 'ℹ️' }[t] || '🔔';
}

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Toast notifications ───────────────────────────────────────
function _getToastContainer() {
  let c = document.getElementById('toast-container');
  if (!c) {
    c = document.createElement('div');
    c.className = 'toast-container';
    c.id = 'toast-container';
    document.body.appendChild(c);
  }
  return c;
}

function showToast(msg, type = 'success') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${icons[type] || '💬'}</span><span>${msg}</span>`;
  _getToastContainer().appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 350);
  }, 3800);
}

// ── Confirm modal ─────────────────────────────────────────────
function showConfirm(title, message, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <span class="modal-icon">⚠️</span>
      <h3>${title}</h3>
      <p>${message}</p>
      <div class="modal-actions">
        <button class="btn btn-ghost" id="modal-cancel">Cancel</button>
        <button class="btn btn-danger" id="modal-confirm">Delete</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('show'));

  const close = () => {
    overlay.classList.remove('show');
    setTimeout(() => overlay.remove(), 250);
  };
  overlay.querySelector('#modal-cancel').addEventListener('click', close);
  overlay.querySelector('#modal-confirm').addEventListener('click', () => { close(); onConfirm(); });
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
}

// ── DOM / display helpers ─────────────────────────────────────
function placeholderHTML(category) {
  const icon = CATEGORY_ICONS[category] || '📦';
  return `<div class="product-placeholder" style="height:100%">${icon}<span>${category || 'Product'}</span></div>`;
}

function productImageHTML(imageUrl, category) {
  if (imageUrl) {
    return `<img src="${imageUrl}" alt="product"
                 style="width:100%;height:100%;object-fit:cover;"
                 onerror="this.parentElement.innerHTML=placeholderHTML('${category}')">`;
  }
  return placeholderHTML(category);
}

function ratingStars(avg, count) {
  if (avg === null || avg === undefined) return '';
  const filled = Math.round(avg / 2);  // 0-10 → 0-5 stars
  const stars = Array.from({length: 5}, (_, i) =>
    `<span style="color:${i < filled ? '#F4A261' : '#D1D5DB'}">★</span>`
  ).join('');
  return `<div class="product-rating">${stars} <span>${avg}/10</span> <span class="rating-count">(${count})</span></div>`;
}

function productCardHTML(p, actions = '') {
  return `
    <div class="product-card" data-id="${p.id}">
      <div class="product-img-wrap">
        <span class="category-badge">${p.category}</span>
        ${productImageHTML(p.image_url, p.category)}
      </div>
      <div class="product-body">
        <div class="product-name">${p.name}</div>
        ${ratingStars(p.avg_rating, p.rating_count)}
        <div class="product-price">${formatPrice(p.price_per_kg)} <span>/ kg</span></div>
        <div class="product-meta">
          <div class="product-meta-item">📍 ${p.location}</div>
          <div class="product-meta-item">📦 ${p.quantity_available} kg available</div>
          <div class="product-meta-item">🧑‍🌾 ${p.farmer?.full_name || 'Unknown'}</div>
        </div>
        ${actions}
      </div>
    </div>`;
}

// ── Change Password modal ─────────────────────────────────────
function showChangePasswordModal() {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal" style="max-width:400px;">
      <span class="modal-icon">🔐</span>
      <h3>Change Password</h3>
      <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:20px;">
        <input id="cp-current" type="password" placeholder="Current password"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;">
        <input id="cp-new" type="password" placeholder="New password (min 6 chars)"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;">
        <input id="cp-confirm" type="password" placeholder="Confirm new password"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;">
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost" id="cp-cancel">Cancel</button>
        <button class="btn btn-primary" id="cp-submit">Update Password</button>
      </div>
      <p style="text-align:center;margin-top:12px;font-size:13px;">
        <a href="#" id="cp-forgot" style="color:var(--green-primary);">Forgot current password?</a>
      </p>
    </div>`;
  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('show'));

  const close = () => {
    overlay.classList.remove('show');
    setTimeout(() => overlay.remove(), 250);
  };

  overlay.querySelector('#cp-cancel').addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });

  overlay.querySelector('#cp-forgot').addEventListener('click', (e) => {
    e.preventDefault();
    const user = getUser();
    close();
    showForgotPasswordModal(user ? user.email : '');
  });

  overlay.querySelector('#cp-submit').addEventListener('click', async () => {
    const current = overlay.querySelector('#cp-current').value;
    const newPw   = overlay.querySelector('#cp-new').value;
    const confirm = overlay.querySelector('#cp-confirm').value;

    if (!current || !newPw || !confirm) { showToast('Please fill in all fields', 'error'); return; }
    if (newPw !== confirm)              { showToast('New passwords do not match', 'error'); return; }
    if (newPw.length < 6)              { showToast('Password must be at least 6 characters', 'error'); return; }

    const btn  = overlay.querySelector('#cp-submit');
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Updating…';

    try {
      await apiFetch('/api/auth/change-password', {
        method: 'PUT',
        body: { current_password: current, new_password: newPw },
      });
      showToast('Password updated! A confirmation email has been sent. ✅');
      close();
    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = orig;
    }
  });
}

// ── Forgot Password modal (OTP flow) ─────────────────────────
function showForgotPasswordModal(prefillEmail = '') {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal" style="max-width:420px;">
      <span class="modal-icon">🔑</span>
      <h3 id="fp-title">Forgot Password</h3>
      <p id="fp-desc" style="font-size:14px;color:#6b7280;margin-bottom:16px;">
        Enter your registered email and we'll send you a 6-digit OTP code.
      </p>

      <!-- Step 1: email -->
      <div id="fp-step1">
        <input id="fp-email" type="email" placeholder="your@email.com" value="${prefillEmail}"
          style="width:100%;box-sizing:border-box;padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;margin-bottom:16px;">
        <div class="modal-actions">
          <button class="btn btn-ghost" id="fp-cancel">Cancel</button>
          <button class="btn btn-primary" id="fp-send">Send OTP</button>
        </div>
      </div>

      <!-- Step 2: OTP + new password -->
      <div id="fp-step2" style="display:none;flex-direction:column;gap:12px;">
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px;font-size:13px;color:#1d4ed8;">
          A 6-digit code was sent to <strong id="fp-email-label"></strong>. Check your inbox.
        </div>
        <input id="fp-otp" type="text" inputmode="numeric" maxlength="6" placeholder="Enter 6-digit OTP"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:20px;letter-spacing:8px;text-align:center;">
        <input id="fp-newpass" type="password" placeholder="New password (min 6 chars)"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;">
        <input id="fp-confirm" type="password" placeholder="Confirm new password"
          style="padding:10px 14px;border:1px solid var(--gray-200);border-radius:var(--r-sm);font-size:14px;">
        <div class="modal-actions" style="margin-top:4px;">
          <button class="btn btn-ghost" id="fp-resend" style="font-size:13px;">Resend OTP</button>
          <button class="btn btn-primary" id="fp-reset">Reset Password</button>
        </div>
      </div>
    </div>`;

  document.body.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('show'));

  const close = () => {
    overlay.classList.remove('show');
    setTimeout(() => overlay.remove(), 250);
  };

  overlay.querySelector('#fp-cancel').addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });

  let sentEmail = '';

  const goStep2 = (email) => {
    sentEmail = email;
    overlay.querySelector('#fp-step1').style.display = 'none';
    const s2 = overlay.querySelector('#fp-step2');
    s2.style.display = 'flex';
    overlay.querySelector('#fp-email-label').textContent = email;
    overlay.querySelector('#fp-title').textContent = 'Enter OTP';
    overlay.querySelector('#fp-desc').textContent = 'Enter the code from your email and choose a new password.';
    overlay.querySelector('#fp-otp').focus();
  };

  const sendOtp = async () => {
    const email = overlay.querySelector('#fp-email').value.trim();
    if (!email) { showToast('Please enter your email address', 'error'); return; }
    const btn = overlay.querySelector('#fp-send');
    btn.disabled = true; btn.textContent = 'Sending…';
    try {
      await apiFetch('/api/auth/forgot-password', { method: 'POST', body: { email } });
      showToast('OTP sent! Check your email inbox.');
      goStep2(email);
    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false; btn.textContent = 'Send OTP';
    }
  };

  overlay.querySelector('#fp-send').addEventListener('click', sendOtp);

  overlay.querySelector('#fp-resend').addEventListener('click', async () => {
    const btn = overlay.querySelector('#fp-resend');
    btn.disabled = true; btn.textContent = 'Sending…';
    try {
      await apiFetch('/api/auth/forgot-password', { method: 'POST', body: { email: sentEmail } });
      showToast('New OTP sent! Check your email.');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Resend OTP';
    }
  });

  overlay.querySelector('#fp-reset').addEventListener('click', async () => {
    const otp     = overlay.querySelector('#fp-otp').value.trim();
    const newPass = overlay.querySelector('#fp-newpass').value;
    const confirm = overlay.querySelector('#fp-confirm').value;
    if (!otp)            { showToast('Please enter the OTP code', 'error'); return; }
    if (!newPass)        { showToast('Please enter a new password', 'error'); return; }
    if (newPass !== confirm) { showToast('Passwords do not match', 'error'); return; }
    if (newPass.length < 6)  { showToast('Password must be at least 6 characters', 'error'); return; }

    const btn = overlay.querySelector('#fp-reset');
    btn.disabled = true; btn.textContent = 'Resetting…';
    try {
      await apiFetch('/api/auth/reset-password', {
        method: 'POST',
        body: { email: sentEmail, otp, new_password: newPass },
      });
      showToast('Password reset! You can now log in with your new password. ✅');
      close();
    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false; btn.textContent = 'Reset Password';
    }
  });
}

// ── Role-based redirect (global, used by auth.js + any page) ─
function redirectByRole(role) {
  if      (role === 'farmer') window.location.href = '/farmer/dashboard';
  else if (role === 'buyer')  window.location.href = '/buyer/dashboard';
  else if (role === 'admin')  window.location.href = '/admin/dashboard';
  else                        window.location.href = '/';
}

// ── Navbar user info ──────────────────────────────────────────
function populateNavUser() {
  const user = getUser();
  if (!user) return;
  const nameEl = document.getElementById('nav-user-name');
  const initEl = document.getElementById('nav-user-init');
  if (nameEl) nameEl.textContent = user.full_name.split(' ')[0];
  if (initEl) initEl.textContent = (user.full_name[0] || '?').toUpperCase();

  const cpBtn = document.getElementById('btn-changepw');
  if (cpBtn) cpBtn.addEventListener('click', showChangePasswordModal);
}
