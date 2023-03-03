from django.db import models
from django.conf import settings
from django.urls import reverse
User = settings.AUTH_USER_MODEL


class Pocket(models.Model):
    POCKET_CATEGORY = (
        ('Futures', 'Futures'),
        ('Cryptocurrency', 'Cryptocurrency'),
        ('FXCurrency', 'FXCurrency'),

        ('NFT Valuation', 'NFT Valuation'),
        ('Stock','Stock'),
        ('Fund Allocation','Fund Allocation')

    )
    CURRENCY_TYPE = (
        ('USD', 'USD'),

    )
    DIRECTION = (
        ('NFT Valuation', 'NFT Valuation'),
        ('Short', 'Short'),
        ('Long', 'Long'),
        ('Fund Allocation','Fund Allocation')



    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20,blank=True, null=True, verbose_name= ('Title'))
    exchange = models.CharField(max_length=20,blank=True, null=True, verbose_name= ('Exchange'))
    
    summary  = models.TextField(max_length=200,blank=True, null=True, verbose_name= ('Description'))
    price = models.DecimalField(max_digits=10, decimal_places=2 , verbose_name= ('Current Value'))
    # Price refelcts the Trades Profit or Loss 
    cost_basis = models.DecimalField(max_digits=10, decimal_places=2 , null=True, verbose_name= ('Cost Basis'))
    profit_or_loss = models.DecimalField(max_digits=10, decimal_places=2 , null=True, verbose_name= ('Trade Profit or Loss'))
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=('Date of Creation'))
    pocket_time_instance = models.DateField(auto_now_add=False, verbose_name=('Date of Trade'))
    category = models.CharField(max_length=40, choices=POCKET_CATEGORY, default='Spot Trade', verbose_name= ('Category'))
    direction = models.CharField(max_length=20, choices=DIRECTION, default='Long', verbose_name= ('Direction'))
    receipt = models.ImageField(upload_to='receipt/%Y/%m/%d/', default='firstImageEntry.svg', null=True, blank=True)
    currency = models.CharField(blank=True, null=True, max_length=10, choices=CURRENCY_TYPE, default='USD', verbose_name= ('currency'))


# Create your models here.
    
    # class Meta:
    #     ordering = ['-price']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auth_home') 

