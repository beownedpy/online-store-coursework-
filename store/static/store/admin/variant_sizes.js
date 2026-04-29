(function () {
    const CLOTHING_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];
    const SHOE_SIZES = [
        '28', '29', '30', '31', '31.5', '32', '32.5', '33', '34', '34.5',
        '35', '35.5', '36', '37', '37.5', '38', '38.5', '39', '40', '40.5',
        '41', '42', '42.5', '43', '44', '44.5', '46', '47', '48', '48.5', '49.5',
    ];

    function buildOptions(sizes, currentValue) {
        return sizes.map(function (s) {
            var sel = s === currentValue ? ' selected' : '';
            return '<option value="' + s + '"' + sel + '>' + s + '</option>';
        }).join('');
    }

    function updateSizeSelects(isShoes) {
        var sizes = isShoes ? SHOE_SIZES : CLOTHING_SIZES;
        document.querySelectorAll('select[name$="-size"]').forEach(function (sel) {
            var current = sel.value;
            sel.innerHTML = buildOptions(sizes, current);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var categorySelect = document.getElementById('id_category');
        if (!categorySelect) return;

        updateSizeSelects(categorySelect.value === 'shoes');

        categorySelect.addEventListener('change', function () {
            updateSizeSelects(this.value === 'shoes');
        });

        document.addEventListener('formset:added', function () {
            updateSizeSelects(categorySelect.value === 'shoes');
        });
    });
})();