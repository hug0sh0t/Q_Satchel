from rest_framework import serializers

from .models import Profile


class SharedProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    style_value = serializers.SerializerMethodField(read_only=True)
    satchel = serializers.SerializerMethodField(read_only=True)

    
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'bio',
            'location',
            'username',
            'id',
            'satchel',
            'style_value',
            'order_matrix',
        ]


    def get_first_name(self, obj): 
        return obj.user.first_name

    def get_last_name(self, obj): 
        return obj.user.last_name

    def get_username(self, obj): 
        return obj.user.username
        
    def get_style_value(self, obj): 
        return obj.style_value

    def get_satchel(self, obj): 
        return obj.satchel

    def get_order_matrix(self, obj): 
        return obj.order_matrix