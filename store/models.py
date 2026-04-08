from django.db import models

class TestModel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unisex'
    )

    SIZE_CHOICES = (
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    )

    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)

    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.title