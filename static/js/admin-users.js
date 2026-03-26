/* ============================================================
   AgriConnect – Admin User Management
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('admin');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);

  document.getElementById('search-btn').addEventListener('click', doSearch);
  document.getElementById('search-input').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
  document.getElementById('filter-role').addEventListener('change', doSearch);
  document.getElementById('filter-status').addEventListener('change', doSearch);

  await loadUsers();
});

async function loadUsers(params = {}) {
  const container = document.getElementById('users-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading…</span></div>`;

  try {
    const qs = new URLSearchParams();
    if (params.search)    qs.set('search',    params.search);
    if (params.role)      qs.set('role',      params.role);
    if (params.is_active !== undefined && params.is_active !== '')
      qs.set('is_active', params.is_active);

    const users = await apiFetch(`/api/admin/users?${qs}`);

    if (users.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>No users found</h3>
          <p>Try adjusting your filters.</p>
        </div>`;
      return;
    }

    container.innerHTML = `
      <div style="background:var(--white);border-radius:var(--r-md);border:1px solid var(--gray-200);overflow:hidden;box-shadow:var(--shadow-sm);">
        <table style="width:100%;border-collapse:collapse;">
          <thead>
            <tr style="background:var(--gray-50);border-bottom:2px solid var(--gray-200);">
              <th style="${th()}">User</th>
              <th style="${th()}">Email</th>
              <th style="${th()}">Role</th>
              <th style="${th()}">Status</th>
              <th style="${th()}">Joined</th>
              <th style="${th()}">Actions</th>
            </tr>
          </thead>
          <tbody id="user-table-body">
            ${users.map(u => userRow(u)).join('')}
          </tbody>
        </table>
      </div>`;

    attachActions();
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load users. ${err.message}</p></div>`;
  }
}

function th() {
  return 'padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:var(--gray-500);text-transform:uppercase;';
}

function td() {
  return 'padding:12px 16px;';
}

function userRow(u) {
  const init      = (u.full_name[0] || '?').toUpperCase();
  const roleBg    = { farmer: 'var(--green-tint)', buyer: 'var(--harvest-light)', admin: 'var(--danger-light)' }[u.role] || 'var(--gray-100)';
  const roleColor = { farmer: 'var(--green-dark)', buyer: 'var(--harvest-dark)',  admin: 'var(--danger)'        }[u.role] || 'var(--gray-600)';
  const roleIcon  = { farmer: '🧑‍🌾', buyer: '🛒', admin: '🛡️' }[u.role] || '';

  const statusBadge = u.is_active
    ? `<span style="background:var(--success-light);color:var(--success);padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;">● Active</span>`
    : `<span style="background:var(--danger-light);color:var(--danger);padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;">● Inactive</span>`;

  const actionBtn = u.role === 'admin'
    ? `<span style="font-size:12px;color:var(--gray-400);">Protected</span>`
    : u.is_active
      ? `<button class="btn btn-danger btn-sm" data-uid="${u.id}" data-action="deactivate">🔒 Deactivate</button>`
      : `<button class="btn btn-primary btn-sm" data-uid="${u.id}" data-action="activate">✅ Activate</button>`;

  return `
    <tr style="border-bottom:1px solid var(--gray-100);" data-row="${u.id}">
      <td style="${td()}">
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--green-mid),var(--green-light));color:#fff;font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">${init}</div>
          <div>
            <div style="font-weight:600;font-size:14px;">${u.full_name}</div>
            <div style="font-size:12px;color:var(--gray-400);">@${u.username}</div>
          </div>
        </div>
      </td>
      <td style="${td()};font-size:13px;color:var(--gray-600);">${u.email}</td>
      <td style="${td()}">
        <span style="background:${roleBg};color:${roleColor};padding:3px 10px;border-radius:var(--r-full);font-size:12px;font-weight:600;">${roleIcon} ${u.role}</span>
      </td>
      <td style="${td()}">${statusBadge}</td>
      <td style="${td()};font-size:13px;color:var(--gray-500);">${new Date(u.created_at).toLocaleDateString()}</td>
      <td style="${td()}">${actionBtn}</td>
    </tr>`;
}

function attachActions() {
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const uid    = btn.dataset.uid;
      const action = btn.dataset.action;   // "activate" | "deactivate"
      const label  = action === 'activate' ? 'activate' : 'deactivate';

      showConfirm(
        `${action === 'activate' ? 'Activate' : 'Deactivate'} User`,
        `Are you sure you want to ${label} this account? The user will be notified.`,
        async () => {
          btn.disabled = true;
          try {
            await apiFetch(`/api/admin/users/${uid}/${action}`, { method: 'PUT' });
            showToast(`User ${label}d successfully.`);
            doSearch();   // refresh list
          } catch (err) {
            showToast(err.message, 'error');
            btn.disabled = false;
          }
        }
      );
    });
  });
}

function doSearch() {
  loadUsers({
    search:    document.getElementById('search-input').value.trim(),
    role:      document.getElementById('filter-role').value,
    is_active: document.getElementById('filter-status').value,
  });
}
