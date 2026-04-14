from .models import ProductVariant

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, variant, quantity=1):
        vid = str(variant.pk)
        if vid not in self.cart:
            self.cart[vid] = 0
        self.cart[vid] += quantity
        if self.cart[vid] <= 0:
            del self.cart[vid]
        self._save()

    def update(self, variant, quantity):
        vid = str(variant.pk)
        if quantity <= 0:
            self.remove(variant)
            return
        self.cart[vid] = quantity
        self._save()

    def remove(self, variant):
        vid = str(variant.pk)
        if vid in self.cart:
            del self.cart[vid]
            self._save()

    def _save(self):
        self.session.modified = True

    def __iter__(self):
        variant_ids = list(self.cart.keys())
        variants = {
            str(v.pk): v
            for v in ProductVariant.objects.filter(pk__in=variant_ids).select_related('product')
        }
        for vid, qty in self.cart.items():
            variant = variants.get(vid)
            if variant:
                yield {
                    'variant': variant,
                    'product': variant.product,
                    'quantity': qty,
                    'total_price': variant.price * qty,
                }

    def __len__(self):
        return sum(self.cart.values())

    def get_total_price(self):
        variant_ids = list(self.cart.keys())
        variants = {
            str(v.pk): v
            for v in ProductVariant.objects.filter(pk__in=variant_ids)
        }
        return sum(
            variants[vid].price * qty
            for vid, qty in self.cart.items()
            if vid in variants
        )

    def clear(self):
        del self.session[CART_SESSION_KEY]
        self.session.modified = True