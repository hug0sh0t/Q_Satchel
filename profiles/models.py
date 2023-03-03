from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from django.core.cache import cache 
from django.conf import settings
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter


import datetime
import random
import string

User = settings.AUTH_USER_MODEL 


class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        path = "/"
        return path.format(username=request.user.username)
    
    def get_email_confirmation_redirect_url(self, request):
      path = "/oauth/email/"
      return path


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        allowed_chars = ''.join((string.ascii_letters, string.digits))
        random_aplhanumeric = ''.join(random.choice(allowed_chars) for _ in range(15))
        user.username = (random_aplhanumeric).upper()
        return user

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following',blank=True) 
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', default='anonimage.png', null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
  
    bio = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    style_value = models.CharField(max_length=200, null=True)
    satchel = models.DecimalField(max_digits=10,decimal_places=2, default=0.0)
    pos_satchel = models.DecimalField(max_digits=10,decimal_places=2, default=0.0)
    neg_satchel = models.DecimalField(max_digits=10,decimal_places=2, default=0.0)
    is_online = models.BooleanField(default=False)


    order_matrix = models.CharField(max_length=70, null=True, blank=True, default='-timestamp')


    def __str__(self):
        return self.user.username



    def user_did_save(sender, instance, created, *args, **kwargs):
        Profile.objects.get_or_create(user=instance)
        if created:
            Profile.objects.get_or_create(user=instance)

    post_save.connect(user_did_save, sender=User)