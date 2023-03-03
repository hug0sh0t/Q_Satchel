import django_filters
from django import forms
from .models import Pocket
from profiles.models import Profile

from django.conf import settings
from crispy_forms.helper import FormHelper

MAX_TITLE_LENGTH = settings.MAX_TITLE_LENGTH
MAX_SUMMARY_LENGTH = settings.MAX_SUMMARY_LENGTH

class ProfileFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = ['user__username', 'user__first_name', 'user__last_name']


class PocketFilter(django_filters.FilterSet):
    class Meta:
        model = Pocket
        fields = ['title', 'summary', 'price', 'category', 'direction']
    # no need to query prices
    def get_title(self, obj):
        return obj.title

    def get_price(self, obj):
        return obj.price

    def get_category(self, obj):
        return obj.category
        
    def get_direction(self, obj):
        return obj.direction

    def get_summary(self, obj):
        return obj.summary




