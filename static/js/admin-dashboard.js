/* ============================================================
   AgriConnect – Admin Dashboard
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('admin');
  if (!user) return;

  populateNavUser();
  document.getElementById('welcome-name').textContent = user.full_name.split(' ')[0];
  document.getElementById('btn-logout').addEventListener('click', logout);

  await Promise.all([loadStats(), loadRecentUsers()]);
});

async function loadStats() {
  try {
    const s = await apiFetch('/api/admin/stats');
    document.getElementById('s-total-users').textContent = s.total_users;
    document.getElementById('s-farmers').textContent     = s.total_farmers;
    document.getElementById('s-buyers').textContent      = s.total_buyers;
    document.getElementById('s-inactive').textContent    = s.inactive_users;
    document.getElementById('s-products').textContent    = s.total_products;
    document.getElementById('s-orders').textContent      = s.total_orders;
    document.getElementById('s-completed').textContent   = s.completed_orders;
    document.getElementById('s-pending').textContent     = s.pending_orders;
  } catch (err) {
    showToast('Failed to load stats', 'error');
  }
}

async function loadRecentUsers() {
  const container = document.getElementById('recent-users');
  try {
    const users = await apiFetch('/api/admin/users');
    const recent = users.slice(0, 8);

    if (recent.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">👥</div><h3>No users yet</h3></div>`;
      return;
    }

    container.innerHTML = `
      <div style="background:var(--white);border-radius:var(--r-md);border:1px solid var(--gray-200);overflow:hidden;box-shadow:var(--shadow-sm);">
        <table style="width:100%;border-collapse:collapse;">
          <thead>
            <tr style="background:var(--gray-50);border-bottom:1px solid var(--gray-200);">
              <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;">User</th>
              <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;">Role</th>
              <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;">Status</th>
              <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;">Joined</th>
            </tr>
          </thead>
          <tbody>
            ${recent.map(userRow).join('')}
          </tbody>
        </table>
      </div>`;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load users.</p></div>`;
  }
}

function userRow(u) {
  const init   = (u.full_name[0] || '?').toUpperCase();
  const roleBg = { farmer: 'var(--green-tint)', buyer: 'var(--harvest-light)', admin: 'var(--danger-light)' }[u.role] || 'var(--gray-100)';
  const roleColor = { farmer: 'var(--green-dark)', buyer: 'var(--harvest-dark)', admin: 'var(--danger)' }[u.role] || 'var(--gray-600)';
  const statusBadge = u.is_active
    ? `<span style="background:var(--success-light);color:var(--success);padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;">● Active</span>`
    : `<span style="background:var(--danger-light);color:var(--danger);padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;">● Inactive</span>`;

  return `
    <tr style="border-bottom:1px solid var(--gray-100);">
      <td style="padding:12px 16px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--green-mid),var(--green-light));color:#fff;font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">${init}</div>
          <div>
            <div style="font-weight:600;font-size:14px;">${u.full_name}</div>
            <div style="font-size:12px;color:var(--gray-400);">@${u.username}</div>
          </div>
        </div>
      </td>
      <td style="padding:12px 16px;">
        <span style="background:${roleBg};color:${roleColor};padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;text-transform:capitalize;">${u.role}</span>
      </td>
      <td style="padding:12px 16px;">${statusBadge}</td>
      <td style="padding:12px 16px;font-size:13px;color:var(--gray-500);">${new Date(u.created_at).toLocaleDateString()}</td>
    </tr>`;
}
