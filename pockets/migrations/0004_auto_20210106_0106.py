# Generated by Django 3.0 on 2021-01-06 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pockets', '0003_pocket_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pocket',
            name='title',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]