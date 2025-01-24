from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Profile

class UserRegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=True)
    country = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'phone', 'country','address']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        country = validated_data.pop('country')
        address = validated_data.pop('address')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, phone=phone, country=country,address=address)
        return user
