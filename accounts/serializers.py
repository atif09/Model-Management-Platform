from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
  password_confirm = serializers.CharField(write_only=True, required=True)

  class Meta:
    model = User
    fields = ('username', 'email', 'password', 'password_confirm')

  def validate(self, attrs):
    if attrs['password'] != attrs['password_confirm']:
      raise serializers.ValidationError({"password": "Password fields didn't match."})
    return attrs
  
  def create(self, validated_data):
    validated_data.pop('password_confirm')
    user = User.objects.create_user(**validated_data)
    return user
  
