from django.conf import settings
from rest_framework import serializers
from profiles.serializers import SharedProfileSerializer

MAX_TITLE_LENGTH = settings.MAX_TITLE_LENGTH
MAX_SUMMARY_LENGTH = settings.MAX_SUMMARY_LENGTH

from .models import Pocket

import base64

from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,') # format ~= data:image/X,
            ext = format.split('/')[-1] # guess file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class PocketCreateSerializer(serializers.ModelSerializer):
    user = SharedProfileSerializer(source='user.profile', read_only=True) #serializers.SerializerMethodField(read_only=True)
    receipt = Base64ImageField(max_length=None, use_url=True, required=False)


    class Meta:
        model = Pocket
        fields = [
          'id', 
          'user', 
          'cost_basis',
          'profit_or_loss', 
          'pocket_time_instance', 
          'category',
          'title', 
          'summary',
          'price', 
          'receipt', 
          'currency',
          'direction',
          'exchange']

    def validate_content(self, value):
        if len(value) > MAX_TITLE_LENGTH:
            raise serializers.ValidationError("This Title is too Long ... ")
        return value   
  

class PocketSerializer(serializers.ModelSerializer):
    user = SharedProfileSerializer(source='user.profile', read_only=True) #serializers.SerializerMethodField(read_only=True)
    title = serializers.SerializerMethodField(read_only=True)
    summary = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    pocket_time_instance = serializers.SerializerMethodField(read_only=True)
    receipt = Base64ImageField(max_length=None, use_url=True, required=False)
    currency = serializers.SerializerMethodField(read_only=True)
    direction = serializers.SerializerMethodField(read_only=True)
    cost_basis = serializers.SerializerMethodField(read_only=True)
    profit_or_loss = serializers.SerializerMethodField(read_only=True)
    exchange = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pocket
        fields = ['user', 
        'pocket_time_instance', 
        'profit_or_loss', 
        'cost_basis', 
        'category', 
        'id', 
        'title', 
        'summary', 
        'price', 
        'timestamp', 
        'receipt', 
        'currency',
        'direction',
        'exchange']

    def get_category(self, obj):
        return obj.get_category_display()
        
    def get_pocket_time_instance(self, obj):
        return obj.pocket_time_instance

    def get_timestamp(self, obj):
        return obj.timestamp

    def get_title(self, obj):
        return obj.title

    def get_exchange(self, obj):
        return obj.exchange
    
    def get_summary(self, obj):
        return obj.summary
    
    def get_price(self, obj):
        return obj.price

    def get_cost_basis(self, obj):
        return obj.cost_basis

    def get_profit_or_loss(self, obj):
        return obj.profit_or_loss
        
    def get_receipt(self, obj):
        return obj.receipt.image
        
    def get_currency(self, obj):
        return obj.currency

                
    def get_direction(self, obj):
        return obj.get_direction_display()