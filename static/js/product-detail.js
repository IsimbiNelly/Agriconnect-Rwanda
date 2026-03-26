/* ============================================================
   AgriConnect – Product Detail Page
   ============================================================ */

let _productId = null;
let _selectedRating = 0;

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('buyer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);
  document.getElementById('back-btn').addEventListener('click', () => history.back());

  initNotificationBell('notif-bell', 'notif-badge', 'notif-list');

  const parts = window.location.pathname.split('/');
  _productId  = parts[parts.length - 1];

  if (!_productId || isNaN(_productId)) {
    window.location.href = '/buyer/dashboard';
    return;
  }

  await loadProduct(_productId);
  buildStarPicker();
  await loadRatings(_productId);
  document.getElementById('rating-section').style.display = 'block';

  document.getElementById('submit-rating').addEventListener('click', submitRating);
});

async function loadProduct(id) {
  const container = document.getElementById('detail-container');

  try {
    const p = await apiFetch(`/api/products/${id}`);

    const imageHTML = p.image_url
      ? `<img src="${p.image_url}" alt="${p.name}"
              onerror="this.parentElement.innerHTML='<div class=\\'detail-placeholder\\'>${CATEGORY_ICONS[p.category] || '📦'}</div>'">`
      : `<div class="detail-placeholder">${CATEGORY_ICONS[p.category] || '📦'}</div>`;

    const farmerInit = (p.farmer.full_name || '?')[0].toUpperCase();

    const avgDisplay = p.avg_rating !== null && p.avg_rating !== undefined
      ? `<div style="font-size:15px;margin:8px 0;color:var(--harvest);">
           ${'★'.repeat(Math.round(p.avg_rating / 2))}${'☆'.repeat(5 - Math.round(p.avg_rating / 2))}
           <span style="color:var(--gray-600);font-size:13px;"> ${p.avg_rating}/10 (${p.rating_count} review${p.rating_count !== 1 ? 's' : ''})</span>
         </div>`
      : '<div style="font-size:13px;color:var(--gray-400);margin:8px 0;">No ratings yet</div>';

    container.innerHTML = `
      <div class="detail-grid">

        <!-- Image -->
        <div>
          <div class="detail-image-card">${imageHTML}</div>
        </div>

        <!-- Info -->
        <div class="detail-info-card">
          <div class="detail-category-badge">${CATEGORY_ICONS[p.category] || '📦'} ${p.category}</div>
          <h2>${p.name}</h2>
          ${avgDisplay}
          <div class="detail-price">${formatPrice(p.price_per_kg)}<span> / kg</span></div>

          <div class="detail-attrs">
            <div class="detail-attr">
              <span class="attr-icon">📦</span>
              <span><strong>${p.quantity_available} kg</strong> available in stock</span>
            </div>
            <div class="detail-attr">
              <span class="attr-icon">📍</span>
              <span>${p.location}</span>
            </div>
            <div class="detail-attr">
              <span class="attr-icon">🏷️</span>
              <span>${p.category}</span>
            </div>
            <div class="detail-attr">
              <span class="attr-icon">📅</span>
              <span>Listed ${new Date(p.created_at).toLocaleDateString('en-RW', {year:'numeric',month:'long',day:'numeric'})}</span>
            </div>
          </div>

          <!-- Farmer card -->
          <div class="farmer-info-card">
            <h4>🧑‍🌾 Sold by</h4>
            <div class="farmer-name-row">
              <div class="farmer-avatar-sm">${farmerInit}</div>
              <div>
                <div class="farmer-name">${p.farmer.full_name}</div>
                <div class="farmer-meta">${p.farmer.location ? '📍 ' + p.farmer.location : ''}</div>
              </div>
            </div>
            ${p.farmer.phone ? `<div class="farmer-meta" style="margin-top:6px;">📞 ${p.farmer.phone}</div>` : ''}
            <div style="margin-top:10px;">
              <a href="/messages?to=${p.farmer.id}" class="btn btn-outline btn-sm">💬 Message Farmer</a>
            </div>
          </div>

          <!-- Buy request section -->
          <div class="buy-section">
            <h4>🛒 Request to Buy</h4>
            <div class="qty-row">
              <label style="font-size:14px;font-weight:600;">Quantity (kg):</label>
              <input type="number" id="buy-qty" min="0.1" max="${p.quantity_available}"
                     step="0.1" value="1" style="width:100px;">
            </div>
            <div class="total-preview" id="total-preview">
              Total: ${formatPrice(p.price_per_kg)}
            </div>
            <textarea id="buy-note" rows="2" placeholder="Optional note to farmer…"
              style="width:100%;padding:8px 12px;border:1px solid var(--gray-300);border-radius:var(--r-sm);font-size:13px;resize:none;margin-bottom:10px;font-family:inherit;"></textarea>
            <button class="btn btn-harvest btn-full" id="btn-buy">
              🛒 Send Purchase Request
            </button>
          </div>
        </div>

      </div>

      ${p.description ? `
      <div style="background:var(--white);border-radius:var(--r-md);padding:28px 32px;margin-top:24px;border:1px solid var(--gray-200);box-shadow:var(--shadow-sm);">
        <h3 style="font-family:var(--font-display);font-size:17px;font-weight:700;margin-bottom:12px;color:var(--green-dark);">
          📋 About This Product
        </h3>
        <p style="color:var(--gray-600);line-height:1.75;font-size:15px;">${p.description}</p>
      </div>` : ''}`;

    // Wire up buy qty → total
    const qtyInput = document.getElementById('buy-qty');
    const totalEl  = document.getElementById('total-preview');
    qtyInput.addEventListener('input', () => {
      const qty   = parseFloat(qtyInput.value) || 0;
      const total = qty * p.price_per_kg;
      totalEl.textContent = `Total: ${formatPrice(total)}`;
    });

    // Buy button
    document.getElementById('btn-buy').addEventListener('click', () => sendBuyRequest(p));

  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">❌</span>
        <h3>Product Not Found</h3>
        <p>This product may have been removed or is no longer available.</p>
        <a href="/buyer/dashboard" class="btn btn-primary">← Back to Marketplace</a>
      </div>`;
  }
}

async function sendBuyRequest(product) {
  const qty  = parseFloat(document.getElementById('buy-qty').value);
  const note = document.getElementById('buy-note').value.trim();
  const btn  = document.getElementById('btn-buy');

  if (!qty || qty <= 0) {
    showToast('Enter a valid quantity', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Sending request…';
  try {
    await apiFetch('/api/orders', {
      method: 'POST',
      body: { product_id: product.id, quantity: qty, note: note || null },
    });
    showToast('Purchase request sent! The farmer will be notified.', 'success');
    btn.textContent = '✅ Request Sent';
  } catch (err) {
    showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = '🛒 Send Purchase Request';
  }
}

// ── Star picker (1–10) ────────────────────────────────────────
function buildStarPicker() {
  const picker = document.getElementById('star-picker');
  picker.innerHTML = '';
  for (let i = 1; i <= 10; i++) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '★';
    btn.dataset.val = i;
    btn.title = `${i}/10`;
    btn.addEventListener('click', () => {
      _selectedRating = i;
      updateStarUI();
      document.getElementById('score-label').textContent = `Rating: ${i}/10`;
    });
    picker.appendChild(btn);
  }
}

function updateStarUI() {
  document.querySelectorAll('#star-picker button').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.val) <= _selectedRating);
  });
}

async function submitRating() {
  if (_selectedRating === 0) {
    showToast('Please select a rating first', 'error');
    return;
  }
  const review = document.getElementById('review-text').value.trim();
  const btn    = document.getElementById('submit-rating');
  btn.disabled = true;
  btn.textContent = 'Submitting…';
  try {
    await apiFetch(`/api/products/${_productId}/rate`, {
      method: 'POST',
      body: { rating: _selectedRating, review: review || null },
    });
    showToast('Rating submitted!');
    btn.textContent = '✅ Rating Saved';
    await loadRatings(_productId);
    // Reload product to update average
    await loadProduct(_productId);
  } catch (err) {
    showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Submit Rating';
  }
}

// ── Load existing ratings ─────────────────────────────────────
async function loadRatings(id) {
  const list = document.getElementById('ratings-list');
  try {
    const ratings = await apiFetch(`/api/products/${id}/ratings`);
    if (ratings.length === 0) {
      list.innerHTML = '<p style="color:var(--gray-400);font-size:13px;margin-top:12px;">No reviews yet. Be the first!</p>';
      return;
    }
    list.innerHTML = '<h4 style="font-size:14px;font-weight:700;margin-bottom:12px;margin-top:8px;color:var(--green-dark);">Recent Reviews</h4>' +
      ratings.map(r => `
        <div class="rating-entry">
          <div class="rating-avatar">${(r.buyer.full_name[0] || '?').toUpperCase()}</div>
          <div>
            <div class="rating-name">${r.buyer.full_name}</div>
            <div class="rating-stars">${'★'.repeat(Math.round(r.rating / 2))}${'☆'.repeat(5 - Math.round(r.rating / 2))}
              <span style="color:var(--gray-500);font-size:12px;"> ${r.rating}/10</span>
            </div>
            ${r.review ? `<div class="rating-review">"${r.review}"</div>` : ''}
            <div class="rating-date">${timeAgo(r.created_at)}</div>
          </div>
        </div>`).join('');
  } catch { /* silent */ }
}
