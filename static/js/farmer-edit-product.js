/* ============================================================
   AgriConnect – Edit Product page
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  const user = requireAuth('farmer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);

  // Extract product ID from URL  e.g. /farmer/edit-product/5
  const parts     = window.location.pathname.split('/');
  const productId = parts[parts.length - 1];

  if (!productId || isNaN(productId)) {
    showToast('Invalid product ID', 'error');
    window.location.href = '/farmer/products';
    return;
  }

  await loadProduct(productId);

  // Image preview
  const imageInput   = document.getElementById('image-input');
  const imagePreview = document.getElementById('image-preview');

  imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { showToast('Image must be under 5 MB', 'error'); return; }
    imagePreview.src = URL.createObjectURL(file);
    imagePreview.classList.add('show');
    document.getElementById('upload-content').style.display = 'none';
  });

  // Form submit
  document.getElementById('edit-product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const btn  = form.querySelector('[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Saving changes…';

    const fd = new FormData();
    fd.append('name',               form.name.value.trim());
    fd.append('description',        form.description.value.trim());
    fd.append('price_per_kg',       form.price_per_kg.value);
    fd.append('quantity_available', form.quantity_available.value);
    fd.append('category',           form.category.value);
    fd.append('location',           form.location.value.trim());
    fd.append('is_active',          form.is_active.value);
    if (imageInput.files[0]) fd.append('image', imageInput.files[0]);

    try {
      await apiFetch(`/api/products/${productId}`, { method: 'PUT', body: fd });
      showToast('Product updated successfully! ✅');
      setTimeout(() => window.location.href = '/farmer/products', 800);
    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Save Changes';
    }
  });
});

async function loadProduct(id) {
  const form = document.getElementById('edit-product-form');
  try {
    const p = await apiFetch(`/api/products/${id}`);
    document.getElementById('page-title').textContent = `Edit: ${p.name}`;

    form.name.value               = p.name;
    form.description.value        = p.description || '';
    form.price_per_kg.value       = p.price_per_kg;
    form.quantity_available.value = p.quantity_available;
    form.category.value           = p.category;
    form.location.value           = p.location;
    form.is_active.value          = p.is_active.toString();

    if (p.image_url) {
      const imagePreview = document.getElementById('image-preview');
      imagePreview.src = p.image_url;
      imagePreview.classList.add('show');
      document.getElementById('upload-content').style.display = 'none';
    }
  } catch (err) {
    showToast('Failed to load product', 'error');
    setTimeout(() => window.location.href = '/farmer/products', 1000);
  }
}
