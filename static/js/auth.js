/* ============================================================
   AgriConnect – Login / Register page logic
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // If already logged in with a VALID session, offer to continue
  // but do NOT hard-redirect — the user may want to switch roles.
  const _cached = getUser();
  const _token  = getToken();
  if (_cached && _token) {
    const banner = document.createElement('div');
    banner.id = 'session-banner';
    banner.innerHTML = `
      <span>Signed in as <strong>${_cached.full_name}</strong> (${_cached.role})</span>
      <div style="display:flex;gap:8px;">
        <button id="banner-continue" class="btn btn-sm btn-primary" style="padding:4px 12px;font-size:13px;">
          Go to my dashboard →
        </button>
        <button id="banner-switch" class="btn btn-sm btn-ghost" style="padding:4px 12px;font-size:13px;">
          Switch account
        </button>
      </div>`;
    banner.style.cssText =
      'background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;' +
      'display:flex;align-items:center;justify-content:space-between;gap:12px;' +
      'margin-bottom:20px;font-size:14px;color:#166534;flex-wrap:wrap;';
    document.querySelector('.login-card').prepend(banner);

    document.getElementById('banner-continue').addEventListener('click', () => {
      redirectByRole(_cached.role);
    });
    document.getElementById('banner-switch').addEventListener('click', () => {
      clearAuth();
      banner.remove();
    });
  }

  let activeRole = 'farmer';

  // ── Role selector ─────────────────────────────────────────
  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeRole = btn.dataset.role;
      document.querySelectorAll('.role-btn').forEach(b =>
        b.classList.toggle('active', b.dataset.role === activeRole)
      );
    });
  });

  // ── Tab switcher ──────────────────────────────────────────
  const loginForm    = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  document.querySelectorAll('.auth-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      document.querySelectorAll('.auth-tab').forEach(b =>
        b.classList.toggle('active', b.dataset.tab === tab)
      );
      loginForm.classList.toggle('hidden', tab !== 'login');
      registerForm.classList.toggle('hidden', tab !== 'register');
    });
  });

  // ── LOGIN ─────────────────────────────────────────────────
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('l-username').value.trim();
    const password = document.getElementById('l-password').value;

    if (!username || !password) {
      showToast('Please enter username and password', 'error');
      return;
    }

    const btn  = loginForm.querySelector('[type="submit"]');
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Signing in…';

    try {
      const data = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: { username, password, role: activeRole },
      });

      saveAuth(data.access_token, data.user);
      showToast(`Welcome back, ${data.user.full_name.split(' ')[0]}! 👋`);
      setTimeout(() => redirectByRole(data.user.role), 600);

    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = orig;
    }
  });

  // ── REGISTER ──────────────────────────────────────────────
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const full_name = document.getElementById('r-fullname').value.trim();
    const username  = document.getElementById('r-username').value.trim();
    const email     = document.getElementById('r-email').value.trim();
    const password  = document.getElementById('r-pass').value;
    const confirm   = document.getElementById('r-confirm').value;
    const location  = document.getElementById('r-location').value.trim() || null;
    const phone     = document.getElementById('r-phone').value.trim()    || null;

    if (password !== confirm) {
      showToast('Passwords do not match', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }

    const btn  = registerForm.querySelector('[type="submit"]');
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Creating account…';

    try {
      const data = await apiFetch('/api/auth/register', {
        method: 'POST',
        body: { username, email, full_name, password, role: activeRole, location, phone },
      });

      saveAuth(data.access_token, data.user);
      showToast(`Account created! Welcome, ${data.user.full_name.split(' ')[0]}! 🎉`);
      setTimeout(() => redirectByRole(data.user.role), 700);

    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = orig;
    }
  });

});
