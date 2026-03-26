/* ============================================================
   AgriConnect – Farmer My Products Page
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('farmer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  // Search filter
  document.getElementById('search-products').addEventListener('input', filterProducts);
  document.getElementById('filter-status').addEventListener('change', filterProducts);

  await loadProducts();
});

let allProducts = [];

async function loadProducts() {
  const container = document.getElementById('products-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading…</span></div>`;

  try {
    allProducts = await apiFetch('/api/products/my-products');
    renderProducts(allProducts);
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load products.</p></div>`;
    showToast('Failed to load products', 'error');
  }
}

function filterProducts() {
  const search = document.getElementById('search-products').value.toLowerCase();
  const status = document.getElementById('filter-status').value;

  let filtered = allProducts;
  if (search) filtered = filtered.filter(p => p.name.toLowerCase().includes(search) || p.location.toLowerCase().includes(search));
  if (status === 'active')   filtered = filtered.filter(p => p.is_active);
  if (status === 'inactive') filtered = filtered.filter(p => !p.is_active);

  renderProducts(filtered);
}

function renderProducts(products) {
  const container = document.getElementById('products-container');
  document.getElementById('product-count').textContent = `${products.length} product${products.length !== 1 ? 's' : ''}`;

  if (products.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🌱</div>
        <h3>No products found</h3>
        <p>Try a different search or add a new product.</p>
        <a href="/farmer/add-product" class="btn btn-primary">+ Add Product</a>
      </div>`;
    return;
  }

  container.innerHTML = `<div class="products-grid">${products.map(p => farmerCard(p)).join('')}</div>`;
  attachActions();
}

function farmerCard(p) {
  const status = p.is_active
    ? `<span class="badge badge-active">● Active</span>`
    : `<span class="badge badge-inactive">● Inactive</span>`;

  return productCardHTML(p, `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;padding-top:12px;border-top:1px solid var(--gray-200);">
      ${status}
      <div style="display:flex;gap:6px;">
        <a href="/farmer/edit-product/${p.id}" class="btn btn-outline btn-sm">✏️ Edit</a>
        <button class="btn btn-danger btn-sm" data-delete="${p.id}" data-name="${p.name}">🗑️</button>
      </div>
    </div>`);
}

function attachActions() {
  document.querySelectorAll('[data-delete]').forEach(btn => {
    btn.addEventListener('click', () => {
      const { delete: id, name } = btn.dataset;
      showConfirm(`Delete "${name}"`, 'This will permanently remove the product from the marketplace.', async () => {
        try {
          await apiFetch(`/api/products/${id}`, { method: 'DELETE' });
          showToast('Product deleted successfully');
          await loadProducts();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });
  });
}
