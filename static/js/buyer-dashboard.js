/* ============================================================
   AgriConnect – Buyer Marketplace
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('buyer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);

  // Notification bell (connects WebSocket internally)
  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  // Search & filters
  document.getElementById('search-btn').addEventListener('click', doSearch);
  document.getElementById('search-input').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
  document.getElementById('filter-category').addEventListener('change', doSearch);
  document.getElementById('filter-location').addEventListener('input', debounce(doSearch, 400));
  document.getElementById('filter-min').addEventListener('input', debounce(doSearch, 500));
  document.getElementById('filter-max').addEventListener('input', debounce(doSearch, 500));

  await loadProducts();
});

async function loadProducts(params = {}) {
  const container = document.getElementById('products-container');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><span>Loading marketplace…</span></div>`;

  try {
    const qs  = new URLSearchParams();
    if (params.search)   qs.set('search',    params.search);
    if (params.category) qs.set('category',  params.category);
    if (params.location) qs.set('location',  params.location);
    if (params.min)      qs.set('min_price', params.min);
    if (params.max)      qs.set('max_price', params.max);

    const products = await apiFetch(`/api/products?${qs}`);

    document.getElementById('result-count').textContent =
      `${products.length} product${products.length !== 1 ? 's' : ''} found`;

    if (products.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>No products found</h3>
          <p>Try adjusting your search or filters.</p>
        </div>`;
      return;
    }

    container.innerHTML = `<div class="products-grid">${products.map(p => buyerCard(p)).join('')}</div>`;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><p>Failed to load products.</p></div>`;
    showToast('Failed to load products', 'error');
  }
}

function buyerCard(p) {
  return productCardHTML(p, `
    <div class="product-actions">
      <a href="/buyer/product/${p.id}" class="btn btn-primary btn-sm" style="flex:2">👁 View Details</a>
    </div>`);
}

function doSearch() {
  loadProducts({
    search:   document.getElementById('search-input').value.trim(),
    category: document.getElementById('filter-category').value,
    location: document.getElementById('filter-location').value.trim(),
    min:      document.getElementById('filter-min').value,
    max:      document.getElementById('filter-max').value,
  });
}

function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}
