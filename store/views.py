import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Min, OuterRef, Subquery, Prefetch, Sum
from .models import Product, ProductVariant, ProductVariantImage, UserProfile, Favorite, Watchlist, Order, OrderItem
from .cart import Cart
from .forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm, CheckoutForm

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


def _watch_ids(request):
    if request.user.is_authenticated:
        return set(request.user.watchlist.values_list('product_id', flat=True))
    return set()


def home_view(request):
    featured = (
        Product.objects
        .filter(variants__stock__gt=0)
        .distinct()
        .annotate(min_price=Subquery(_min_price_sq))
        .prefetch_related(Prefetch('variants', queryset=ProductVariant.objects.order_by('price')))
        .order_by('-pk')[:6]
    )
    return render(request, 'home.html', {
        'featured': featured,
        'categories': Product.CATEGORY_CHOICES,
        'favorite_ids': _favorite_ids(request),
    })


def product_list(request):
    qs = Product.objects.annotate(
        min_price=Subquery(_min_price_sq),
        total_stock=Sum('variants__stock'),
    ).prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.order_by('price'))
    )

    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(title__icontains=search)

    category = request.GET.get('category', '')
    if category:
        qs = qs.filter(category=category)

    gender = request.GET.get('gender', '')
    if gender:
        qs = qs.filter(gender=gender)

    size = request.GET.get('size', '')
    if size:
        qs = qs.filter(variants__size=size).distinct()

    color = request.GET.get('color', '').strip()
    if color:
        qs = qs.filter(variants__color__iexact=color).distinct()

    sort = request.GET.get('sort', 'price_asc')
    sort_field = SORT_OPTIONS.get(sort, ('min_price', ''))[0]
    qs = qs.order_by(sort_field)

    paginator = Paginator(qs, 2)
    page_obj = paginator.get_page(request.GET.get('page'))

    get_copy = request.GET.copy()
    get_copy.pop('page', None)

    available_colors = (
        ProductVariant.objects
        .values_list('color', flat=True)
        .distinct()
        .order_by('color')
    )

    context = {
        'page_obj': page_obj,
        'category_choices': Product.CATEGORY_CHOICES,
        'gender_choices': Product.GENDER_CHOICES,
        'size_choices': ProductVariant.CLOTHING_SIZES,
        'sort_options': SORT_OPTIONS,
        'available_colors': available_colors,
        'current_search': search,
        'current_category': category,
        'current_gender': gender,
        'current_size': size,
        'current_color': color,
        'current_sort': sort,
        'filter_params': get_copy.urlencode(),
        'favorite_ids': _favorite_ids(request),
        'watch_ids': _watch_ids(request),
    }
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.prefetch_related(
                    Prefetch('images', queryset=ProductVariantImage.objects.order_by('order', 'pk'))
                ).order_by('color', 'price'),
            )
        ),
        pk=pk,
    )
    is_favorite = pk in _favorite_ids(request)
    is_watching = pk in _watch_ids(request)

    # Group by color: collect images from all variants of that color, list sizes
    color_map = {}
    for v in product.variants.all():
        c = v.color
        if c not in color_map:
            color_map[c] = {'images': [], 'variants': []}
        # Collect images from ProductVariantImage; fallback to variant.image
        if not color_map[c]['images']:
            imgs = [i.img.url for i in v.images.all()]
            if not imgs and v.image:
                imgs = [v.image.url]
            color_map[c]['images'] = imgs
        color_map[c]['variants'].append({
            'pk':    v.pk,
            'size':  v.size,
            'price': str(v.price),
            'stock': v.stock,
        })

    total_stock = sum(v.stock for v in product.variants.all())

    return render(request, 'product_detail.html', {
        'product':      product,
        'is_favorite':  is_favorite,
        'is_watching':  is_watching,
        'total_stock':  total_stock,
        'variants_json': json.dumps(color_map),
    })


@login_required
def order_history(request):
    return render(request, 'order_history.html')


def help_view(request):
    return render(request, 'help.html')


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


@require_POST
def watch_toggle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required'}, status=401)
    product = get_object_or_404(Product, pk=pk)
    watch, created = Watchlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        watch.delete()
        watching = False
    else:
        watching = True
    return JsonResponse({'watching': watching})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


@require_POST
def cart_add(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(variant, quantity)
    in_cart = cart.cart.get(str(pk), 0)
    return JsonResponse({
        'cart_count': len(cart),
        'in_cart': in_cart,
        'stock': variant.stock,
    })


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
    actual_qty = cart.cart.get(str(pk), 0)
    item_total = str(variant.price * actual_qty) if actual_qty > 0 else '0'
    return JsonResponse({
        'cart_count': len(cart),
        'total_price': str(cart.get_total_price()),
        'item_total': item_total,
        'quantity': actual_qty,
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


def checkout_view(request):
    cart = Cart(request)
    if not len(cart):
        return redirect('cart_detail')

    initial = {}
    if request.user.is_authenticated:
        up = getattr(request.user, 'profile', None)
        initial = {
            'first_name': request.user.first_name,
            'last_name':  request.user.last_name,
            'email':      request.user.email,
            'phone':      up.phone if up else '',
            'address':    up.address if up else '',
        }

    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=cd['first_name'],
            last_name=cd['last_name'],
            email=cd['email'],
            phone=cd['phone'],
            city=cd['city'],
            address=cd['address'],
            payment=cd['payment'],
            comment=cd.get('comment', ''),
            total_price=cart.get_total_price(),
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                variant=item['variant'],
                title=item['product'].title,
                size=item['variant'].size,
                color=item['variant'].color,
                price=item['variant'].price,
                quantity=item['quantity'],
            )
        cart.clear()
        return redirect('order_success', pk=order.pk)

    return render(request, 'checkout.html', {'form': form, 'cart': cart})


def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_success.html', {'order': order})


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