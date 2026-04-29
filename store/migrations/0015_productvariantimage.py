from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='products/variants/')),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('product_variant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='images',
                    to='store.productvariant',
                )),
            ],
            options={
                'ordering': ['order', 'pk'],
            },
        ),
    ]