from django.urls import path
from .views import (
    home_view, product_list, product_detail,
    cart_detail, cart_add, cart_remove, cart_update,
    checkout_view, order_success_view,
    register_view, login_view, logout_view, profile_view,
    favorites_list, favorite_toggle,
    order_history, help_view,
    watch_toggle,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('catalog/', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:pk>/', cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', cart_remove, name='cart_remove'),
    path('cart/update/<int:pk>/', cart_update, name='cart_update'),
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/success/<int:pk>/', order_success_view, name='order_success'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorites/toggle/<int:pk>/', favorite_toggle, name='favorite_toggle'),
    path('orders/', order_history, name='order_history'),
    path('help/', help_view, name='help'),
    path('catalog/watch/<int:pk>/', watch_toggle, name='watch_toggle'),
]