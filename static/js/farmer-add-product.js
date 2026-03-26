/* ============================================================
   AgriConnect – Add Product page
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const user = requireAuth('farmer');
  if (!user) return;

  populateNavUser();
  document.getElementById('btn-logout').addEventListener('click', logout);

  // Image preview
  const imageInput   = document.getElementById('image-input');
  const imagePreview = document.getElementById('image-preview');
  const uploadArea   = document.getElementById('upload-area');

  imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { showToast('Image must be under 5 MB', 'error'); return; }
    const url = URL.createObjectURL(file);
    imagePreview.src = url;
    imagePreview.classList.add('show');
    uploadArea.querySelector('.upload-content').style.display = 'none';
  });

  // Form submit
  document.getElementById('add-product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const btn  = form.querySelector('[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Adding product…';

    const fd = new FormData();
    fd.append('name',               form.name.value.trim());
    fd.append('description',        form.description.value.trim());
    fd.append('price_per_kg',       form.price_per_kg.value);
    fd.append('quantity_available', form.quantity_available.value);
    fd.append('category',           form.category.value);
    fd.append('location',           form.location.value.trim());
    if (imageInput.files[0]) fd.append('image', imageInput.files[0]);

    try {
      await apiFetch('/api/products', { method: 'POST', body: fd });
      showToast('Product added successfully! 🎉');
      setTimeout(() => window.location.href = '/farmer/products', 800);
    } catch (err) {
      showToast(err.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Add Product';
    }
  });
});
