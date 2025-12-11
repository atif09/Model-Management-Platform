from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Dataset, Job
from .serializers import ProjectSerializer, DatasetSerializer, JobSerializer
from rest_framework import parsers

# Create your views here.
class IsOwnerOrReadOnly(IsAuthenticated):
  def has_object_permission(self, request, view, obj):
    return obj.owner == request.user
  

class ProjectViewSet(viewsets.ModelViewSet):
  queryset = Project.objects.all()
  serializer_class = ProjectSerializer
  permission_classes = [IsAuthenticated]
  filter_backends = [DjangoFilterBackend]
  filterset_fields = ['owner']

  def perform_create(self, serializer):
    serializer.save(owner=self.request.user)

  def get_queryset(self):
    return self.queryset.filter(owner=self.request.user)


class DatasetViewSet(viewsets.ModelViewSet):
  queryset = Dataset.objects.all()
  serializer_class = DatasetSerializer
  permission_classes = [IsAuthenticated]
  filter_backends = [DjangoFilterBackend]
  filterset_fields = ['project']

  def get_queryset(self):
    # return only datasets for projects owned by the user
    return self.queryset.filter(project__owner=self.request.user)

  def perform_create(self, serializer):
    parser_class = [parsers.MultiPartParser, parsers.FormParser]
    if not parser_class:
      raise PermissionError("No file uploaded")
    

    project = serializer.validated_data['project']
    if project.owner != self.request.user:
      raise PermissionError("Cannot upload to a project you do not own")
    
    # serializer.create already saves file and metadata
    serializer.save()




class JobViewSet(viewsets.ModelViewSet):
  queryset = Job.objects.all()
  serializer_class = JobSerializer
  permission_classes = [IsAuthenticated]
  filter_backends = [DjangoFilterBackend]
  filterset_fields = ['project', 'status']

  def get_queryset(self):
    return self.queryset.filter(project__owner=self.request.user)
  