(function () {
    const variantsData = {{ variants_json|safe }};

    let selectedSize = null;
    let selectedVariant = null;

    const sizeButtons = document.querySelectorAll('.btn-size');
    const stockRow    = document.getElementById('stock-row');
    const stockStatus = document.getElementById('stock-status');
    const cartActions = document.getElementById('cart-actions');
    const qtyInput    = document.getElementById('qty-input');
    const qtyDec      = document.getElementById('qty-dec');
    const qtyInc      = document.getElementById('qty-inc');
    const btnAddCart  = document.getElementById('btn-add-cart');
    const priceEl     = document.getElementById('detail-price');
    const imgEl       = document.getElementById('detail-image');

    sizeButtons.forEach(btn => {
        const size = btn.dataset.size;
        const variants = variantsData[size] || [];
        const hasStock = variants.some(v => v.stock > 0);
        if (!hasStock) btn.classList.add('btn-size--out');
    });

    sizeButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            sizeButtons.forEach(b => b.classList.remove('btn-size--active'));
            this.classList.add('btn-size--active');
            selectedSize = this.dataset.size;
            const variants = variantsData[selectedSize] || [];
            selectedVariant = variants.find(v => v.stock > 0) || variants[0];
            if (!selectedVariant) return;
            priceEl.textContent = selectedVariant.price + ' грн';
            if (selectedVariant.image) {
                imgEl.src = selectedVariant.image;
                imgEl.style.display = '';
            }

            const stock = selectedVariant.stock;
            stockRow.style.display = '';
            if (stock > 0) {
                stockStatus.textContent = 'В наявності: ' + stock + ' шт.';
                stockStatus.className = 'stock-status stock-in';
            } else {
                stockStatus.textContent = 'Немає в наявності';
                stockStatus.className = 'stock-status stock-out';
            }

            qtyInput.max = stock > 0 ? stock : 1;
            qtyInput.value = stock > 0 ? 1 : 0;
            qtyInput.dataset.pk = selectedVariant.pk;
            btnAddCart.dataset.pk = selectedVariant.pk;
            btnAddCart.disabled = stock === 0;

            cartActions.style.display = '';
        });
    });

    qtyDec.addEventListener('click', function () {
        const val = parseInt(qtyInput.value);
        if (val > 1) qtyInput.value = val - 1;
    });

    qtyInc.addEventListener('click', function () {
        const val = parseInt(qtyInput.value);
        const max = parseInt(qtyInput.max);
        if (val < max) qtyInput.value = val + 1;
    });

    qtyInput.addEventListener('change', function () {
        const max = parseInt(this.max);
        let val = parseInt(this.value) || 1;
        if (val < 1) val = 1;
        if (val > max) val = max;
        this.value = val;
    });
})();