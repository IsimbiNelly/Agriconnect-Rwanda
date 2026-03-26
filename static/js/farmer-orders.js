/* ============================================================
   AgriConnect – Farmer Orders
   ============================================================ */

let _allOrders = [];
let _activeFilter = '';

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('farmer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active', 'btn-primary'));
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.add('btn-outline'));
      btn.classList.add('active', 'btn-primary');
      btn.classList.remove('btn-outline');
      _activeFilter = btn.dataset.status;
      renderOrders();
    });
  });

  await loadOrders();
});

async function loadOrders() {
  const container = document.getElementById('orders-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading…</span></div>`;
  try {
    _allOrders = await apiFetch('/api/orders/incoming');
    renderOrders();
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load orders.</p></div>`;
    showToast('Failed to load orders', 'error');
  }
}

function renderOrders() {
  const container = document.getElementById('orders-container');
  const filtered  = _activeFilter
    ? _allOrders.filter(o => o.status === _activeFilter)
    : _allOrders;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No orders here</h3>
        <p>No ${_activeFilter || ''} orders found.</p>
      </div>`;
    return;
  }

  container.innerHTML = filtered.map(o => orderCard(o)).join('');
  attachActions();
}

function orderCard(o) {
  const img = o.product.image_url
    ? `<img src="${o.product.image_url}" class="order-card-img" style="width:72px;height:72px;border-radius:var(--r-sm);object-fit:cover;">`
    : `<div class="order-card-img">${CATEGORY_ICONS[o.product.category] || '📦'}</div>`;

  const statusBadge = `<span class="order-status ${o.status}">${statusLabel(o.status)}</span>`;

  const actions = actionsHTML(o);

  return `
    <div class="order-card">
      ${img}
      <div class="order-card-body">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
          <div class="order-card-name">${o.product.name}</div>
          ${statusBadge}
        </div>
        <div class="order-card-meta">
          🧑 Buyer: <strong>${o.buyer.full_name}</strong>
          ${o.buyer.phone ? ` · 📞 ${o.buyer.phone}` : ''}
        </div>
        <div class="order-card-meta">
          📦 Qty: <strong>${o.quantity} kg</strong>
          &nbsp;·&nbsp; 📅 ${new Date(o.created_at).toLocaleDateString()}
        </div>
        ${o.note ? `<div class="order-card-meta" style="font-style:italic;">"${o.note}"</div>` : ''}
        ${o.payment_ref ? `<div class="order-card-meta" style="color:var(--green-dark);font-weight:600;">🧾 Ref: ${o.payment_ref} · via ${o.payment_provider}</div>` : ''}
        ${o.delivery_date ? `<div class="order-card-meta">🚚 Delivery due: <strong>${o.delivery_date}</strong></div>` : ''}
        <div class="order-card-price">${formatPrice(o.total_price)}</div>
        <div class="order-actions">${actions}</div>
      </div>
    </div>`;
}

function actionsHTML(o) {
  const msgBtn = `<a href="/messages?to=${o.buyer_id}" class="btn btn-outline btn-sm">💬 Message</a>`;

  if (o.status === 'pending') {
    return `
      <button class="btn btn-primary btn-sm" data-action="accept" data-id="${o.id}">✅ Accept</button>
      <button class="btn btn-danger btn-sm"  data-action="reject" data-id="${o.id}">❌ Reject</button>
      ${msgBtn}`;
  }
  if (o.status === 'accepted') {
    return `<span style="font-size:13px;color:var(--gray-500);">⏳ Awaiting buyer payment…</span> ${msgBtn}`;
  }
  if (o.status === 'paid') {
    return `
      <button class="btn btn-harvest btn-sm" data-action="complete" data-id="${o.id}">🚚 Mark Delivered</button>
      ${msgBtn}`;
  }
  return msgBtn;
}

function statusLabel(s) {
  return {
    pending:   '⏳ Pending',
    accepted:  '✅ Accepted',
    paid:      '💳 Paid',
    completed: '🎉 Delivered',
    rejected:  '❌ Rejected',
  }[s] || s;
}

function attachActions() {
  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      const id     = btn.dataset.id;
      btn.disabled = true;

      try {
        await apiFetch(`/api/orders/${id}/${action}`, { method: 'PUT' });
        showToast(
          action === 'accept'   ? 'Order accepted!'
        : action === 'reject'   ? 'Order rejected.'
        : 'Transaction completed! Both parties notified.',
          action === 'complete' ? 'success' : 'info'
        );
        await loadOrders();
      } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
      }
    });
  });
}
