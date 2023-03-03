# Generated by Django 3.0 on 2021-01-18 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pockets', '0008_auto_20210114_1735'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pocket',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='pocket',
            name='title',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='current Pocket Name'),
        ),
    ]
