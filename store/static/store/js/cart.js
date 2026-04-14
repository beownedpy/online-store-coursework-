function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function updateCartCount(count) {
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

function postCart(url, body, onSuccess) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(body),
    })
        .then(r => r.json())
        .then(data => {
            updateCartCount(data.cart_count);
            if (onSuccess) onSuccess(data);
        });
}

function removeRow(pk, data) {
    const row = document.querySelector(`.cart-row[data-pk="${pk}"]`);
    if (row) row.remove();
    recalcTotal(data);
    if (data.cart_count === 0) {
        const container = document.querySelector('.cart-container');
        if (container) {
            container.innerHTML =
                '<p class="empty-message">Кошик порожній. <a href="/">Перейти до каталогу</a></p>';
        }
    }
}

document.querySelectorAll('.btn-add-cart').forEach(btn => {
    btn.addEventListener('click', () => {
        const pk = btn.dataset.pk;
        const qtyInput = document.querySelector(`.product-qty[data-pk="${pk}"]`);
        const quantity = qtyInput ? parseInt(qtyInput.value) : 1;
        postCart(`/cart/add/${pk}/`, { quantity }, () => {
            btn.textContent = 'Додано ✓';
            setTimeout(() => (btn.textContent = 'До кошика'), 1500);
        });
    });
});

function recalcTotal(data) {
    const totalEl = document.getElementById('cart-total');
    if (totalEl && data.total_price !== undefined) {
        totalEl.textContent = data.total_price + ' грн';
    }
}

document.querySelectorAll('.qty-dec').forEach(btn => {
    btn.addEventListener('click', () => {
        const pk = btn.dataset.pk;
        const input = document.querySelector(`.qty-input[data-pk="${pk}"]`);
        const newVal = Math.max(0, parseInt(input.value) - 1);
        input.value = newVal;

        if (newVal === 0) {
            postCart(`/cart/remove/${pk}/`, {}, data => removeRow(pk, data));
        } else {
            postCart(`/cart/update/${pk}/`, { quantity: newVal }, data => {
                const itemTotalEl = document.querySelector(`.item-total[data-pk="${pk}"]`);
                if (itemTotalEl) itemTotalEl.textContent = data.item_total + ' грн';
                recalcTotal(data);
            });
        }
    });
});

document.querySelectorAll('.qty-inc').forEach(btn => {
    btn.addEventListener('click', () => {
        const pk = btn.dataset.pk;
        const input = document.querySelector(`.qty-input[data-pk="${pk}"]`);
        const newVal = Math.min(99, parseInt(input.value) + 1);
        input.value = newVal;
        postCart(`/cart/update/${pk}/`, { quantity: newVal }, data => {
            const itemTotalEl = document.querySelector(`.item-total[data-pk="${pk}"]`);
            if (itemTotalEl) itemTotalEl.textContent = data.item_total + ' грн';
            recalcTotal(data);
        });
    });
});

document.querySelectorAll('.qty-input').forEach(input => {
    input.addEventListener('change', () => {
        const pk = input.dataset.pk;
        const parsed = parseInt(input.value);
        const newVal = isNaN(parsed) ? 0 : Math.max(0, Math.min(99, parsed));
        input.value = newVal;

        if (newVal === 0) {
            postCart(`/cart/remove/${pk}/`, {}, data => removeRow(pk, data));
        } else {
            postCart(`/cart/update/${pk}/`, { quantity: newVal }, data => {
                const itemTotalEl = document.querySelector(`.item-total[data-pk="${pk}"]`);
                if (itemTotalEl) itemTotalEl.textContent = data.item_total + ' грн';
                recalcTotal(data);
            });
        }
    });
});

document.querySelectorAll('.btn-remove').forEach(btn => {
    btn.addEventListener('click', () => {
        const pk = btn.dataset.pk;
        postCart(`/cart/remove/${pk}/`, {}, data => removeRow(pk, data));
    });
});

function updateFavCount(delta) {
    const badge = document.getElementById('fav-count');
    if (!badge) return;
    const next = (parseInt(badge.textContent) || 0) + delta;
    badge.textContent = next;
    badge.style.display = next > 0 ? 'inline' : 'none';
}

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-fav');
    if (!btn) return;

    const url = btn.dataset.url;
    if (!url) return;

    fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    })
    .then(function(r) {
        if (r.status === 401) { window.location.href = '/login/'; return null; }
        return r.json();
    })
    .then(function(data) {
        if (!data) return;
        btn.classList.toggle('btn-fav--active', data.is_favorite);
        updateFavCount(data.is_favorite ? 1 : -1);

        // на сторінці обраного — видаляємо картку
        if (!data.is_favorite && btn.classList.contains('btn-fav-remove')) {
            const card = btn.closest('.card-wrapper');
            if (card) card.remove();
            if (!document.querySelector('.card-wrapper')) location.reload();
        }
    })
    .catch(function(err) {
        console.error('Favorite error:', err);
    });
});