/* ============================================================
   AgriConnect – Buyer Orders
   ============================================================ */

let _allOrders   = [];
let _activeFilter = '';
let _payOrderId  = null;
let _selectedProvider = null;

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('buyer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab').forEach(b => {
        b.classList.remove('active', 'btn-primary');
        b.classList.add('btn-outline');
      });
      btn.classList.add('active', 'btn-primary');
      btn.classList.remove('btn-outline');
      _activeFilter = btn.dataset.status;
      renderOrders();
    });
  });

  // Momo modal wiring
  document.getElementById('momo-cancel').addEventListener('click', closeMomo);
  document.getElementById('momo-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('momo-overlay')) closeMomo();
  });
  document.getElementById('momo-pay-btn').addEventListener('click', submitPayment);

  // Receipt close
  document.getElementById('rec-close').addEventListener('click', () => {
    document.getElementById('receipt-overlay').style.display = 'none';
    loadOrders();
  });

  await loadOrders();
});

async function loadOrders() {
  const container = document.getElementById('orders-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading…</span></div>`;
  try {
    _allOrders = await apiFetch('/api/orders/my-orders');
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
        <h3>No orders yet</h3>
        <p>${_activeFilter ? `No ${_activeFilter} orders.` : 'You haven\'t placed any purchase requests yet.'}</p>
        <a href="/buyer/dashboard" class="btn btn-primary">Browse Products</a>
      </div>`;
    return;
  }

  container.innerHTML = filtered.map(o => orderCard(o)).join('');

  // Wire Pay Now buttons
  document.querySelectorAll('[data-pay-order]').forEach(btn => {
    btn.addEventListener('click', () => openMomo(parseInt(btn.dataset.payOrder), parseFloat(btn.dataset.payTotal)));
  });
}

function orderCard(o) {
  const img = o.product.image_url
    ? `<img src="${o.product.image_url}" style="width:72px;height:72px;border-radius:var(--r-sm);object-fit:cover;">`
    : `<div class="order-card-img">${CATEGORY_ICONS[o.product.category] || '📦'}</div>`;

  const statusBadge = `<span class="order-status ${o.status}">${statusLabel(o.status)}</span>`;

  const payBtn = o.status === 'accepted'
    ? `<button class="btn btn-primary btn-sm" data-pay-order="${o.id}" data-pay-total="${o.total_price}">💳 Pay Now</button>`
    : '';

  const reviewLink = o.status === 'completed'
    ? `<a href="/buyer/product/${o.product_id}" class="btn btn-outline btn-sm">⭐ Leave Review</a>`
    : '';

  const receiptLine = (o.status === 'paid' || o.status === 'completed') && o.payment_ref
    ? `<div class="order-card-meta" style="color:var(--green-dark);font-weight:600;">🧾 Ref: ${o.payment_ref}</div>`
    : '';

  const deliveryLine = o.delivery_date
    ? `<div class="order-card-meta">🚚 Delivery: <strong>${o.delivery_date}</strong></div>`
    : '';

  return `
    <div class="order-card">
      ${img}
      <div class="order-card-body">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
          <div class="order-card-name">${o.product.name}</div>
          ${statusBadge}
        </div>
        <div class="order-card-meta">
          📦 Qty: <strong>${o.quantity} kg</strong>
          &nbsp;·&nbsp; 📅 Placed: ${new Date(o.created_at).toLocaleDateString()}
        </div>
        ${o.note ? `<div class="order-card-meta" style="font-style:italic;">"${o.note}"</div>` : ''}
        ${receiptLine}
        ${deliveryLine}
        <div class="order-card-price">${formatPrice(o.total_price)}</div>
        <div class="order-actions">
          <a href="/buyer/product/${o.product_id}" class="btn btn-outline btn-sm">👁 View Product</a>
          ${payBtn}
          ${reviewLink}
        </div>
      </div>
    </div>`;
}

// ── Momo modal ────────────────────────────────────────────────────────────────

function openMomo(orderId, total) {
  _payOrderId       = orderId;
  _selectedProvider = null;
  document.getElementById('momo-overlay').style.display = 'flex';
  document.getElementById('momo-amount-label').textContent = `Amount: ${formatPrice(total)}`;
  document.getElementById('momo-phone').value  = '';
  document.getElementById('momo-name').value   = '';
  document.getElementById('momo-processing').style.display  = 'none';
  document.getElementById('momo-form-actions').style.display = 'flex';
  // Reset provider highlight
  document.getElementById('prov-mtn').style.borderColor    = 'var(--gray-200)';
  document.getElementById('prov-airtel').style.borderColor = 'var(--gray-200)';
}

function closeMomo() {
  document.getElementById('momo-overlay').style.display = 'none';
  _payOrderId = null;
}

function selectProvider(name) {
  _selectedProvider = name;
  document.getElementById('prov-mtn').style.borderColor    = name === 'MTN'    ? 'var(--green-mid)' : 'var(--gray-200)';
  document.getElementById('prov-airtel').style.borderColor = name === 'Airtel' ? 'var(--green-mid)' : 'var(--gray-200)';
}

async function submitPayment() {
  const phone = document.getElementById('momo-phone').value.trim();
  const name  = document.getElementById('momo-name').value.trim();

  if (!_selectedProvider) { showToast('Please select a provider (MTN or Airtel)', 'error'); return; }
  if (!phone)             { showToast('Please enter your phone number', 'error'); return; }
  if (!name)              { showToast('Please enter the account holder name', 'error'); return; }

  // Show processing
  document.getElementById('momo-form-actions').style.display = 'none';
  document.getElementById('momo-processing').style.display   = 'block';

  try {
    // Simulate a short "processing" delay
    await new Promise(r => setTimeout(r, 1800));

    const receipt = await apiFetch(`/api/orders/${_payOrderId}/pay`, {
      method: 'PUT',
      body: { phone, name, provider: _selectedProvider },
    });

    closeMomo();
    showReceipt(receipt);
  } catch (err) {
    document.getElementById('momo-form-actions').style.display = 'flex';
    document.getElementById('momo-processing').style.display  = 'none';
    showToast(err.message, 'error');
  }
}

// ── Receipt modal ─────────────────────────────────────────────────────────────

function showReceipt(r) {
  document.getElementById('rec-id').textContent       = `Receipt ID: ${r.receipt_id}`;
  document.getElementById('rec-product').textContent  = r.product_name;
  document.getElementById('rec-qty').textContent      = `${r.quantity} kg`;
  document.getElementById('rec-price').textContent    = formatPrice(r.price_per_kg) + ' / kg';
  document.getElementById('rec-total').textContent    = formatPrice(r.total);
  document.getElementById('rec-provider').textContent = `${r.payment_provider} — ${r.payment_phone}`;
  document.getElementById('rec-paid-at').textContent  = r.paid_at;
  document.getElementById('rec-delivery').textContent = r.delivery_date;
  document.getElementById('rec-buyer').textContent    = r.buyer_name;
  document.getElementById('rec-farmer').textContent   = r.farmer_name;
  document.getElementById('receipt-overlay').style.display = 'flex';
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusLabel(s) {
  return {
    pending:   '⏳ Pending',
    accepted:  '✅ Accepted',
    paid:      '💳 Paid',
    completed: '🎉 Completed',
    rejected:  '❌ Rejected',
  }[s] || s;
}
