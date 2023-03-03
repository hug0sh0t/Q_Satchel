# Generated by Django 3.0 on 2021-01-23 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pockets', '0011_pocket_pocket_time_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pocket',
            name='pocket_time_instance',
            field=models.DateTimeField(verbose_name='Exact Date & Time of Pocket '),
        ),
        migrations.AlterField(
            model_name='pocket',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='current Pocket Price $'),
        ),
    ]