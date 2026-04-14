from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def favorites_count(request):
    if request.user.is_authenticated:
        return {'favorites_count': request.user.favorites.count()}
    return {'favorites_count': 0}