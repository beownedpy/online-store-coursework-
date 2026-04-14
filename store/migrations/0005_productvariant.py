from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_delete_testmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=5)),
                ('color', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='store.product')),
            ],
            options={
                'ordering': ['price'],
                'unique_together': {('product', 'size', 'color')},
            },
        ),
        migrations.RemoveField(model_name='product', name='color'),
        migrations.RemoveField(model_name='product', name='image'),
        migrations.RemoveField(model_name='product', name='price'),
        migrations.RemoveField(model_name='product', name='size'),
    ]