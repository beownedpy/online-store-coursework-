from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_productvariant_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Матеріал'),
        ),
    ]