from django.urls import path
from .views import (
    product_list, product_detail,
    cart_detail, cart_add, cart_remove, cart_update,
    register_view, login_view, logout_view, profile_view,
    favorites_list, favorite_toggle,
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:pk>/', cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', cart_remove, name='cart_remove'),
    path('cart/update/<int:pk>/', cart_update, name='cart_update'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorites/toggle/<int:pk>/', favorite_toggle, name='favorite_toggle'),
]