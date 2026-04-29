(function () {
    const colorMap = window.__variantsData__ || {};

    // ── DOM refs ──
    const track        = document.getElementById('carousel-track');
    const dotsEl       = document.getElementById('carousel-dots');
    const prevBtn      = document.getElementById('carousel-prev');
    const nextBtn      = document.getElementById('carousel-next');
    const placeholder  = document.getElementById('carousel-placeholder');
    const colorButtons = document.querySelectorAll('.btn-color');
    const colorNameEl  = document.getElementById('selected-color-name');
    const sizeSection  = document.getElementById('size-section');
    const sizeBtnWrap  = document.getElementById('size-buttons');
    const stockRow     = document.getElementById('stock-row');
    const stockStatus  = document.getElementById('stock-status');
    const lowStockMsg  = document.getElementById('low-stock-msg');
    const qtyInput     = document.getElementById('qty-input');
    const qtyDec       = document.getElementById('qty-dec');
    const qtyInc       = document.getElementById('qty-inc');
    const btnAddCart   = document.getElementById('btn-add-cart');
    const priceEl      = document.getElementById('detail-price');

    //Carousel state
    let currentIndex   = 0;
    let images         = [];
    let selectedColor  = null;
    let selectedVariant = null;

    //Carousel helpers
    function buildCarousel(urls) {
        images = urls;
        currentIndex = 0;
        track.innerHTML = '';
        dotsEl.innerHTML = '';

        if (!urls.length) {
            const ph = document.createElement('div');
            ph.className = 'carousel-placeholder';
            ph.innerHTML = '<span>Немає фото</span>';
            track.appendChild(ph);
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            return;
        }

        urls.forEach((url, i) => {
            const img = document.createElement('img');
            img.src = url;
            img.alt = '';
            img.className = 'carousel-img' + (i === 0 ? ' carousel-img--active' : '');
            track.appendChild(img);

            const dot = document.createElement('button');
            dot.className = 'carousel-dot' + (i === 0 ? ' carousel-dot--active' : '');
            dot.addEventListener('click', () => goTo(i));
            dotsEl.appendChild(dot);
        });

        const showArrows = urls.length > 1;
        prevBtn.style.display = showArrows ? '' : 'none';
        nextBtn.style.display = showArrows ? '' : 'none';
    }

    function goTo(index) {
        const imgs = track.querySelectorAll('.carousel-img');
        const dots = dotsEl.querySelectorAll('.carousel-dot');
        imgs[currentIndex].classList.remove('carousel-img--active');
        dots[currentIndex]?.classList.remove('carousel-dot--active');
        currentIndex = (index + images.length) % images.length;
        imgs[currentIndex].classList.add('carousel-img--active');
        dots[currentIndex]?.classList.add('carousel-dot--active');
    }

    if (prevBtn) prevBtn.addEventListener('click', () => goTo(currentIndex - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goTo(currentIndex + 1));

    //Swipe support
    let touchStartX = 0;
    if (track) {
        track.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
        track.addEventListener('touchend', e => {
            const dx = e.changedTouches[0].clientX - touchStartX;
            if (Math.abs(dx) > 40) goTo(currentIndex + (dx < 0 ? 1 : -1));
        });
    }

    //Color selection
    function selectColor(btn, color) {
        colorButtons.forEach(b => b.classList.remove('btn-color--active'));
        btn.classList.add('btn-color--active');
        selectedColor = color;
        selectedVariant = null;
        colorNameEl.textContent = color;

        const data = colorMap[color];
        buildCarousel(data ? data.images : []);
        buildSizes(data ? data.variants : []);

        //Show min price for this color
        if (data && data.variants.length) {
            const minPrice = data.variants.reduce((m, v) => {
                const p = parseFloat(v.price);
                return p < m ? p : m;
            }, Infinity);
            priceEl.textContent = minPrice + ' грн';
        } else {
            priceEl.textContent = '—';
        }

        stockRow.style.display = 'none';
        if (lowStockMsg) lowStockMsg.style.display = 'none';
        if (btnAddCart) { btnAddCart.disabled = true; btnAddCart.dataset.pk = ''; }
        if (qtyInput) { qtyInput.dataset.pk = ''; qtyInput.value = 1; }
    }

    colorButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            selectColor(this, this.dataset.color);
        });
    });

    //Size buttons
    function buildSizes(variants) {
        sizeBtnWrap.innerHTML = '';
        if (!variants.length) { sizeSection.style.display = 'none'; return; }
        sizeSection.style.display = '';

        variants.forEach(v => {
            const btn = document.createElement('button');
            btn.className = 'btn-size' + (v.stock <= 0 ? ' btn-size--out' : '');
            btn.textContent = v.size;
            btn.dataset.pk    = v.pk;
            btn.dataset.price = v.price;
            btn.dataset.stock = v.stock;
            btn.addEventListener('click', function () {
                selectSize(this);
            });
            sizeBtnWrap.appendChild(btn);
        });
    }

    function selectSize(btn) {
        sizeBtnWrap.querySelectorAll('.btn-size').forEach(b => b.classList.remove('btn-size--active'));
        btn.classList.add('btn-size--active');

        selectedVariant = {
            pk:    btn.dataset.pk,
            price: btn.dataset.price,
            stock: parseInt(btn.dataset.stock),
        };

        priceEl.textContent = selectedVariant.price + ' грн';

        const stock = selectedVariant.stock;
        stockRow.style.display = '';
        if (stock <= 0) {
            stockStatus.textContent = 'Немає в наявності';
            stockStatus.className   = 'stock-status stock-out';
        } else if (stock < 3) {
            stockStatus.textContent = 'Залишилось ' + stock + ' шт. — встигни купити!';
            stockStatus.className   = 'stock-status stock-low';
        } else {
            stockStatus.textContent = 'В наявності: ' + stock + ' шт.';
            stockStatus.className   = 'stock-status stock-in';
        }

        if (lowStockMsg) lowStockMsg.style.display = 'none';

        if (qtyInput) {
            qtyInput.max        = stock > 0 ? stock : 1;
            qtyInput.value      = stock > 0 ? 1 : 0;
            qtyInput.dataset.pk = selectedVariant.pk;
        }
        if (btnAddCart) {
            btnAddCart.dataset.pk = selectedVariant.pk;
            btnAddCart.disabled   = stock === 0;
        }
    }

    // Qty controls
    if (qtyDec && qtyInput) {
        qtyDec.addEventListener('click', function () {
            const val = parseInt(qtyInput.value);
            if (val > parseInt(qtyInput.min || 1)) qtyInput.value = val - 1;
        });
    }
    if (qtyInc && qtyInput) {
        qtyInc.addEventListener('click', function () {
            const val = parseInt(qtyInput.value);
            const max = parseInt(qtyInput.max);
            if (val < max) qtyInput.value = val + 1;
        });
    }
    if (qtyInput) {
        qtyInput.addEventListener('change', function () {
            const max = parseInt(this.max);
            let val = parseInt(this.value) || 1;
            if (val < 1) val = 1;
            if (val > max) val = max;
            this.value = val;
        });
    }

    const firstColorBtn = document.querySelector('.btn-color');
    if (firstColorBtn) selectColor(firstColorBtn, firstColorBtn.dataset.color);
})();