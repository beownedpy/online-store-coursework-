(function () {
    const btn  = document.getElementById('nav-profile-btn');
    const wrap = document.getElementById('nav-profile-wrap');
    if (!btn) return;

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        wrap.classList.toggle('nav-profile-wrap--open');
    });

    document.addEventListener('click', function () {
        wrap.classList.remove('nav-profile-wrap--open');
    });
})();