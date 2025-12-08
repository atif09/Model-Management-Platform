from django.shortcuts import render
from django.http import HttpResponse
from .models import User
from .serializers import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class RegisterView(APIView):
  def post(self, request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class LoginView(TokenObtainPairView):
  pass

class ProfileView(RetrieveUpdateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = UserRegistrationSerializer

  def get_object(self):
    return self.request.user
  

class ChangePasswordView(UpdateAPIView):
  permission_classes = [IsAuthenticated]

  def update(self, request, *args, **kwargs):
    user = self.request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    if not user.check_password(old_password):
      return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)
    return Response({"message": "Password changed successfully"})
  
class LogoutView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    try:
      refresh_token = request.data["refresh"]
      token = RefreshToken(refresh_token)
      token.blacklist()
      return Response({"message": "Successfully logged out"})
    except Exception as e:
      return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    

  