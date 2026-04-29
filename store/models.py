from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    GENDER_CHOICES = (
        ('male',   'Чоловік'),
        ('female', 'Жінка'),
        ('child',  'Діти'),
    )
    gender  = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    phone   = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Профіль: {self.user.email}"


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    GENDER_CHOICES = (
        ('male', 'Чоловіки'),
        ('female', 'Жінки'),
        ('child', 'Діти'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='child')

    CATEGORY_CHOICES = (
        ('tshirts', 'Футболки'),
        ('shirts', 'Сорочка'),
        ('hoodies', 'Кофта'),
        ('sweaters', 'Светри'),
        ('jackets', 'Куртки'),
        ('coats', 'Пальто'),
        ('pants', 'Штани'),
        ('jeans', 'Джинси'),
        ('shorts', 'Шорти'),
        ('socks', 'Шкарпетки'),
        ('shoes', 'Взуття'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tshirts')
    material = models.CharField(max_length=255, blank=True, default='', verbose_name='Матеріал')
    # price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    CLOTHING_SIZES = (
        ('XS',  'XS'),
        ('S',   'S'),
        ('M',   'M'),
        ('L',   'L'),
        ('XL',  'XL'),
        ('XXL', 'XXL'),
    )

    SHOE_SIZES = tuple(
        (s, s) for s in [
            '28', '29', '30', '31', '31.5', '32', '32.5', '33', '34', '34.5',
            '35', '35.5', '36', '37', '37.5', '38', '38.5', '39', '40', '40.5',
            '41', '42', '42.5', '43', '44', '44.5', '46', '47', '48', '48.5', '49.5',
        ]
    )

    ALL_SIZES = CLOTHING_SIZES + SHOE_SIZES

    size = models.CharField(max_length=5, choices=ALL_SIZES)
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    class Meta:
        unique_together = ('product', 'size', 'color')
        ordering = ['price']

    def __str__(self):
        return f"{self.product.title} / {self.size} / {self.color}"


class ProductVariantImage(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='products/variants/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f"Фото для {self.product_variant}"


class Favorite(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} → {self.product.title}"


class Watchlist(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='watchers')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} відстежує {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending',    'Очікує'),
        ('processing', 'В обробці'),
        ('shipped',    'Відправлено'),
        ('delivered',  'Доставлено'),
        ('cancelled',  'Скасовано'),
    )

    PAYMENT_CHOICES = (
        ('card',   'Карткою онлайн'),
        ('cash',   'Готівкою при отриманні'),
        ('postal', 'Накладний платіж'),
    )

    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders',
    )
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20)
    city        = models.CharField(max_length=100)
    address     = models.TextField()
    payment     = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='card')
    comment     = models.TextField(blank=True, default='')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.pk} — {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant  = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    title    = models.CharField(max_length=255)
    size     = models.CharField(max_length=10)
    color    = models.CharField(max_length=50)
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.title} × {self.quantity}"