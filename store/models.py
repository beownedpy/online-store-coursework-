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
        ('other',  'Інше'),
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
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')

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

    size = models.CharField(max_length=5, choices=CLOTHING_SIZES)
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    class Meta:
        unique_together = ('product', 'size', 'color')
        ordering = ['price']

    def __str__(self):
        return f"{self.product.title} / {self.size} / {self.color}"


class Favorite(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} → {self.product.title}"