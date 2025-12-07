document.addEventListener('DOMContentLoaded', function() {
    initQuantityControls();
    initAddToCart();
    initProductGallery();
});

function initQuantityControls() {
    document.querySelectorAll('.quantity-control').forEach(control => {
        const minusBtn = control.querySelector('.qty-minus');
        const plusBtn = control.querySelector('.qty-plus');
        const input = control.querySelector('input');
        
        if (minusBtn) {
            minusBtn.addEventListener('click', function() {
                let value = parseInt(input.value) || 1;
                if (value > 1) {
                    input.value = value - 1;
                    updateCartItem(control);
                }
            });
        }
        
        if (plusBtn) {
            plusBtn.addEventListener('click', function() {
                let value = parseInt(input.value) || 1;
                input.value = value + 1;
                updateCartItem(control);
            });
        }
        
        if (input) {
            input.addEventListener('change', function() {
                let value = parseInt(input.value) || 1;
                if (value < 1) value = 1;
                input.value = value;
                updateCartItem(control);
            });
        }
    });
}

function updateCartItem(control) {
    const form = control.closest('form');
    if (form && form.classList.contains('update-cart-form')) {
        const input = control.querySelector('input');
        const formData = new FormData(form);
        formData.set('quantity', input.value);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function initAddToCart() {
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (form.dataset.ajax === 'true') {
                e.preventDefault();
                
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const cartBadge = document.querySelector('.btn-primary-yellow .badge');
                        if (cartBadge) {
                            cartBadge.textContent = data.cart_count;
                        } else {
                            const cartBtn = document.querySelector('.btn-primary-yellow');
                            if (cartBtn) {
                                const badge = document.createElement('span');
                                badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
                                badge.textContent = data.cart_count;
                                cartBtn.appendChild(badge);
                            }
                        }
                        
                        showToast('Added to cart!', 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error adding to cart', 'error');
                });
            }
        });
    });
}

function initProductGallery() {
    const mainImage = document.querySelector('.main-product-image');
    const thumbnails = document.querySelectorAll('.product-gallery .thumbnail');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            mainImage.src = this.src;
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
