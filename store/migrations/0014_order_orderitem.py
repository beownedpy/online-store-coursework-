from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_product_gender_alter_productvariant_size_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('phone', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('payment', models.CharField(
                    choices=[('card', 'Карткою онлайн'), ('cash', 'Готівкою при отриманні'), ('postal', 'Накладний платіж')],
                    default='card', max_length=10,
                )),
                ('comment', models.TextField(blank=True, default='')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(
                    choices=[('pending', 'Очікує'), ('processing', 'В обробці'), ('shipped', 'Відправлено'), ('delivered', 'Доставлено'), ('cancelled', 'Скасовано')],
                    default='pending', max_length=15,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='orders',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('size', models.CharField(max_length=10)),
                ('color', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='store.order',
                )),
                ('variant', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='store.productvariant',
                )),
            ],
        ),
    ]