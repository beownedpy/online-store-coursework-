import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Min, OuterRef, Subquery, Prefetch
from .models import Product, ProductVariant, UserProfile, Favorite
from .cart import Cart
from .forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm

User = get_user_model()

SORT_OPTIONS = {
    'price_asc':  ('min_price',  'Ціна: від низької'),
    'price_desc': ('-min_price', 'Ціна: від високої'),
    'name_asc':   ('title',      'Назва: А → Я'),
    'name_desc':  ('-title',     'Назва: Я → А'),
}

_min_price_sq = ProductVariant.objects.filter(
    product_id=OuterRef('pk')
).order_by('price').values('price')[:1]


def _favorite_ids(request):
    if request.user.is_authenticated:
        return set(request.user.favorites.values_list('product_id', flat=True))
    return set()


def product_list(request):
    qs = Product.objects.annotate(min_price=Subquery(_min_price_sq)).prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.order_by('price'))
    )

    category = request.GET.get('category', '')
    if category:
        qs = qs.filter(category=category)

    gender = request.GET.get('gender', '')
    if gender:
        qs = qs.filter(gender=gender)

    size = request.GET.get('size', '')
    if size:
        qs = qs.filter(variants__size=size).distinct()

    sort = request.GET.get('sort', 'price_asc')
    sort_field = SORT_OPTIONS.get(sort, ('min_price', ''))[0]
    qs = qs.order_by(sort_field)

    paginator = Paginator(qs, 2)
    page_obj = paginator.get_page(request.GET.get('page'))

    get_copy = request.GET.copy()
    get_copy.pop('page', None)

    context = {
        'page_obj': page_obj,
        'category_choices': Product.CATEGORY_CHOICES,
        'gender_choices': Product.GENDER_CHOICES,
        'size_choices': ProductVariant.CLOTHING_SIZES,
        'sort_options': SORT_OPTIONS,
        'current_category': category,
        'current_gender': gender,
        'current_size': size,
        'current_sort': sort,
        'filter_params': get_copy.urlencode(),
        'favorite_ids': _favorite_ids(request),
    }
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('variants'),
        pk=pk,
    )
    is_favorite = pk in _favorite_ids(request)

    # Build variants data grouped by size for JS
    size_map = {}
    for v in product.variants.all():
        if v.size not in size_map:
            size_map[v.size] = []
        size_map[v.size].append({
            'pk': v.pk,
            'color': v.color,
            'price': str(v.price),
            'stock': v.stock,
            'image': v.image.url if v.image else '',
        })

    return render(request, 'product_detail.html', {
        'product': product,
        'is_favorite': is_favorite,
        'variants_json': json.dumps(size_map),
    })


@login_required
def favorites_list(request):
    favorites = (
        Favorite.objects
        .filter(user=request.user)
        .select_related('product')
        .prefetch_related('product__variants')
    )
    return render(request, 'favorites.html', {'favorites': favorites})


@require_POST
def favorite_toggle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True
    return JsonResponse({'is_favorite': is_favorite})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


@require_POST
def cart_add(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(variant, quantity)
    return JsonResponse({'cart_count': len(cart)})


@require_POST
def cart_remove(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    cart = Cart(request)
    cart.remove(variant)
    return JsonResponse({'cart_count': len(cart)})


@require_POST
def cart_update(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(variant, quantity)
    item_total = str(variant.price * quantity) if quantity > 0 else '0'
    return JsonResponse({
        'cart_count': len(cart),
        'total_price': str(cart.get_total_price()),
        'item_total': item_total,
    })


# ── Auth ──

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create_user(username=email, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('product_list')
    return render(request, 'register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].strip().lower()
        password = form.cleaned_data['password']
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or 'product_list')
        form.add_error(None, 'Невірний email або пароль.')
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('product_list')


@login_required
def profile_view(request):
    user = request.user
    up, _ = UserProfile.objects.get_or_create(user=user)

    profile_form = ProfileForm(initial={
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'gender':     up.gender,
        'phone':      up.phone,
        'address':    up.address,
    })
    password_form = ChangePasswordForm(user)
    profile_saved = False
    password_saved = False

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST)
            if profile_form.is_valid():
                cd = profile_form.cleaned_data
                user.first_name = cd['first_name']
                user.last_name  = cd['last_name']
                user.save()
                up.gender  = cd['gender']
                up.phone   = cd['phone']
                up.address = cd['address']
                up.save()
                profile_saved = True
        elif 'change_password' in request.POST:
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data['new_password'])
                user.save()
                login(request, user)
                password_saved = True

    return render(request, 'profile.html', {
        'profile_form':  profile_form,
        'password_form': password_form,
        'profile_saved': profile_saved,
        'password_saved': password_saved,
    })