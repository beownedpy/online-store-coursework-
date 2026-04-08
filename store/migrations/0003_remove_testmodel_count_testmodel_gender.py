from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_testmodel_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testmodel',
            name='count',
        ),
        migrations.AddField(
            model_name='testmodel',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=10),
            preserve_default=False,
        ),
    ]
