(function () {
    const CODES = {
        '+380': {
        len: 9
        },
    };

    const codeSelect = document.getElementById('id_phone_code');
    const suffix     = document.getElementById('id_phone_suffix');
    const hidden     = document.getElementById('id_phone');
    const errorEl    = document.getElementById('phone-error');
    if (!codeSelect || !suffix || !hidden) return;

    function currentLen() {
        return (CODES[codeSelect.value] || { len: 9 }).len;
    }

    function showError(msg) {
        if (!errorEl) return;
        errorEl.textContent = msg;
        errorEl.style.display = msg ? '' : 'none';
    }

    function validate(digits) {
        const len = currentLen();
        if (digits.length > 0 && digits.length < len) {
            showError(`Занадто мало цифр: введіть рівно ${len} цифр після ${codeSelect.value}.`);
            return false;
        }
        if (digits.length > len) {
            showError(`Забагато цифр: максимум ${len} цифр після ${codeSelect.value}.`);
            return false;
        }
        showError('');
        return true;
    }

    function syncHidden() {
        const digits = suffix.value.replace(/\D/g, '').slice(0, currentLen());
        suffix.value = digits;
        hidden.value = digits ? codeSelect.value + digits : '';
    }

    const saved = suffix.dataset.saved || '';
    const matchedCode = Object.keys(CODES).find(c => saved.startsWith(c));
    if (matchedCode) {
        codeSelect.value = matchedCode;
        suffix.value = saved.slice(matchedCode.length);
    } else {
        suffix.value = saved.replace(/\D/g, '').slice(0, currentLen());
    }
    syncHidden();

    codeSelect.addEventListener('change', function () {
        const digits = suffix.value.replace(/\D/g, '').slice(0, currentLen());
        suffix.value = digits;
        syncHidden();
        if (digits.length > 0) validate(digits);
    });

    suffix.addEventListener('input', function () {
        const digits = this.value.replace(/\D/g, '').slice(0, currentLen());
        this.value = digits;
        hidden.value = digits ? codeSelect.value + digits : '';
        if (digits.length > 0) validate(digits);
        else showError('');
    });

    suffix.addEventListener('blur', function () {
        const digits = this.value.replace(/\D/g, '');
        if (digits.length > 0) validate(digits);
    });

    suffix.addEventListener('keydown', function (e) {
        const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
        if (allowed.includes(e.key) || e.ctrlKey || e.metaKey) return;
        if (!/^\d$/.test(e.key)) e.preventDefault();
    });

    const form = suffix.closest('form');
    if (form) {
        form.addEventListener('submit', function (e) {
            const digits = suffix.value.replace(/\D/g, '').slice(0, currentLen());
            hidden.value = digits ? codeSelect.value + digits : '';
            if (digits.length > 0 && !validate(digits)) {
                e.preventDefault();
            }
        });
    }
})();