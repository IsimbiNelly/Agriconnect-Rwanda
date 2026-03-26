/* ============================================================
   AgriConnect – Login / Register page logic
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // Already logged in → go to dashboard
  const user = getUser();
  if (user && getToken()) {
    redirectByRole(user.role);
    return;
  }

  let activeRole = 'farmer';

  // ── Role selector ─────────────────────────────────────────
  document.querySelectorAll('.role-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeRole = btn.dataset.role;
      document.querySelectorAll('.role-btn').forEach(b =>
        b.classList.toggle('active', b.dataset.role === activeRole)
      );

      // Admin can only login, not self-register
      const registerTab = document.querySelector('[data-tab="register"]');
      const registerForm = document.getElementById('register-form');
      if (activeRole === 'admin') {
        registerTab.style.display = 'none';
        registerForm.classList.add('hidden');
        document.getElementById('login-form').classList.remove('hidden');
        document.querySelectorAll('.auth-tab').forEach(b => b.classList.remove('active'));
        document.querySelector('[data-tab="login"]').classList.add('active');
      } else {
        registerTab.style.display = '';
      }
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
