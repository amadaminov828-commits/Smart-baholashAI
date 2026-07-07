from rest_framework import serializers
from .models import User, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'phone_number', 'role', 'created_by', 'last_name', 'is_active', 'license_number', 'pinfl', 'company', 'company_details', 'signature')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'full_name', 'phone_number', 'role')

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        temp_password = get_random_string(length=14)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=temp_password,
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'user')
        )
        user.is_active = False 
        user.save()
        return user

class UserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'phone_number', 'role', 'password', 'last_name', 'is_active')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Get request user to set created_by
        request = self.context.get('request')
        
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.last_name = password # Store plain text for admin visibility as requested
        
        if request and request.user:
            user.created_by = request.user
            
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            instance.last_name = password # Update plain text for admin visibility
            
        instance.save()
        return instance
