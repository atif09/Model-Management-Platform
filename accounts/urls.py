from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from mlplatform.core.views import JobViewSet
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, LogoutView

# What is DefaultRouter?
# It automatically creates URL patterns from ViewSet methods
# Instead of manually writing 10+ URL patterns, we register once

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
# The router.urls will include:
# /jobs/ [name='job-list']  -> JobViewSet.list()
# /jobs/{pk}/ [name='job-detail'] -> JobViewSet.retrieve()
# /jobs/{pk}/status/ [name='job-status'] -> JobViewSet.status


urlpatterns = [
  path('register/', RegisterView.as_view(), name='register'),
  path('login/', LoginView.as_view(), name='token_obtain_pair'),
  path('profile/', ProfileView.as_view(), name='profile'),
  path('change-password/', ChangePasswordView.as_view(), name='change_password'),
  path('logout/', LogoutView.as_view(), name='logout'),
  

]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)