/* ============================================================
   AgriConnect – Farmer Dashboard
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('farmer');
  if (!user) return;

  populateNavUser();
  document.getElementById('welcome-name').textContent = user.full_name.split(' ')[0];
  document.getElementById('btn-logout').addEventListener('click', logout);

  // Notification bell
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  await loadStats();
  await loadRecentProducts();
});

async function loadStats() {
  try {
    const [products, orders] = await Promise.all([
      apiFetch('/api/products/my-products'),
      apiFetch('/api/orders/incoming'),
    ]);
    const active  = products.filter(p => p.is_active).length;
    const pending = orders.filter(o => o.status === 'pending').length;

    document.getElementById('stat-total').textContent   = products.length;
    document.getElementById('stat-active').textContent  = active;
    document.getElementById('stat-inactive').textContent = products.length - active;
    document.getElementById('stat-orders').textContent  = pending;
  } catch (err) {
    showToast('Failed to load stats', 'error');
  }
}

async function loadRecentProducts() {
  const container = document.getElementById('recent-products');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading products…</span></div>`;

  try {
    const products = await apiFetch('/api/products/my-products');
    const recent   = products.slice(0, 6);

    if (recent.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🌱</div>
          <h3>No products listed yet</h3>
          <p>Start by adding your first product to the marketplace.</p>
          <a href="/farmer/add-product" class="btn btn-primary">+ Add First Product</a>
        </div>`;
      return;
    }

    container.innerHTML = `<div class="products-grid">${recent.map(p => farmerCard(p)).join('')}</div>`;
    attachCardActions();
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load products.</p></div>`;
    showToast('Failed to load products', 'error');
  }
}

function farmerCard(p) {
  const status = p.is_active
    ? `<span class="badge badge-active">● Active</span>`
    : `<span class="badge badge-inactive">● Inactive</span>`;

  return productCardHTML(p, `
    <div style="display:flex;gap:6px;margin-top:10px;align-items:center;justify-content:space-between;">
      ${status}
      <div style="display:flex;gap:6px;">
        <a href="/farmer/edit-product/${p.id}" class="btn btn-outline btn-sm">✏️ Edit</a>
        <button class="btn btn-danger btn-sm" data-delete="${p.id}">🗑️</button>
      </div>
    </div>`);
}

function attachCardActions() {
  document.querySelectorAll('[data-delete]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.delete;
      showConfirm('Delete Product', 'Are you sure you want to delete this product? This cannot be undone.', async () => {
        try {
          await apiFetch(`/api/products/${id}`, { method: 'DELETE' });
          showToast('Product deleted');
          await loadStats();
          await loadRecentProducts();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });
  });
}
