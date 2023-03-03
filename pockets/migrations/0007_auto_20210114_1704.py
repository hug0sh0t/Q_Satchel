# Generated by Django 3.0 on 2021-01-15 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pockets', '0006_auto_20210113_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='pocket',
            name='category',
            field=models.CharField(choices=[('Miscellaneous', 'Miscellaneous'), ('Recreation & Entertainment', 'Recreation & Entertainment'), ('Personal Spending', 'Personal Spending'), ('Investments ( Stocks, Bonds ,Etc.)', 'Investments ( Stocks, Bonds ,Etc.)'), ('Medical | Healthcare', 'Medical | Healthcare'), ('Insurance', 'Insurance'), ('Utilities', 'Utilities'), ('Food', 'Food'), ('Transportation', 'Transportation'), ('Housing', 'Housing')], default='Miscellaneous', max_length=27, verbose_name='current Category'),
        ),
        migrations.AlterField(
            model_name='pocket',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='current Pocket Price'),
        ),
        migrations.AlterField(
            model_name='pocket',
            name='summary',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='current Description'),
        ),
        migrations.AlterField(
            model_name='pocket',
            name='title',
            field=models.CharField(blank=True, max_length=70, null=True, verbose_name='current Pocket Name'),
        ),
    ]
