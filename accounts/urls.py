from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, LogoutView

urlpatterns = [
  path('register/', RegisterView.as_view(), name='register'),
  path('login/', LoginView.as_view(), name='token_obtain_pair'),
  path('profile/', ProfileView.as_view(), name='profile'),
  path('change-password/', ChangePasswordView.as_view(), name='change_password'),
  path('logout/', LogoutView.as_view(), name='logout'),

]