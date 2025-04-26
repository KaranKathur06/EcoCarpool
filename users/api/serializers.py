from rest_framework import serializers
from ..models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'bio', 'address', 'phone_number', 'profile_picture',
            'is_active', 'is_verified', 'registration_date',
            'password', 'confirm_password'
        ]
        read_only_fields = ['is_active', 'is_verified', 'registration_date']
    
    def validate(self, data):
        if 'password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords don't match")
            data.pop('confirm_password')
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance