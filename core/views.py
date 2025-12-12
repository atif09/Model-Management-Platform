from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Dataset, Job
from .serializers import ProjectSerializer, DatasetSerializer, JobSerializer, JobSubmitSerializer
from rest_framework import parsers
import logging

logger = logging.getLogger(__name__)

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
  

  def create(self, request, *args, **kwargs):
    # Step 1: Validate input data
    serializer = JobSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True) # raise error if validation fails

    dataset_id = serializer.validated_data['dataset_id']
    job_type = serializer.validated_data['job_type']
    target_format = serializer.validated_data.get('target_format')

    try:
      # Get the dataset
      dataset = Dataset.objects.get(id=dataset_id)

      # Step 3: Create job record in database
      job = Job.objects.create(
        name = f"{job_type} for Dataset {dataset.id}",
        project = dataset.project,
        status = 'PENDING'
      )

      # Step 4: Enqueue Celery task based on job type
      if job_type == 'validate_csv':
        from .tasks import validate_csv
        task = validate_csv.delay(dataset.id, job.id)

      elif job_type == 'process_image':
        from .tasks import process_image
        task = process_image.delay(dataset.id, job.id)

      elif job_type == 'generate_statistics':
        from .tasks import generate_statistics
        task = generate_statistics.delay(dataset.id, job.id)

      elif job_type == 'convert_file_format':
        # this job type needs target_format
        if not target_format:
          return Response(
            {"error": "target_format is required for convert_file_format job type."},
            status=status.HTTP_400_BAD_REQUEST
          )  
        from .tasks import convert_file_format
        task = convert_file_format.delay(dataset.id, job.id, target_format)

      # Step 5: Save Celery task ID in job
      job.task_id = task.id
      job.save()
      

      # Step 6: Return job into to user
      response_serializer = JobSerializer(job)
      return Response(response_serializer.data, status=status.HTTP_201_CREATED)


    except Dataset.DoesNotExist:
      return Response(
        {"error": "Dataset with given ID does not exist."},
        status=status.HTTP_404_NOT_FOUND
      )
    except Exception as e:
      logger.error(f"Error creating job: {str(e)}")
      return Response(
        {"error": "An error occurred while creating the job."},
        status=status.HTTP_400_BAD_REQUEST
      )

  @action(detail=True, methods=['get'])
  def status(self, request, pk=None):

    try:
      job = self.get_object()
      serializer = JobSerializer(job)
      return Response(serializer.data)

    except Job.DoesNotExist:
      return Response(
        {"error": "Job with given ID does not exist."},
        status=status.HTTP_404_NOT_FOUND
      )
    
  @action(detail=True, methods=['post'])
  def cancel(self, request, pk=None):
    try:
      job = self.get_object()

      # Only PROCESSING Jobs can be cancelled

      if job.status != 'PROCESSING':
        return Response(
          {"error": "Only PROCESSING jobs can be cancelled."},
          status=status.HTTP_400_BAD_REQUEST
        )

      # Call the cancel job model
      job.cancel_job()

      return Response(
        {"message": "Job cancelled successfully."},
        status=status.HTTP_200_OK
      )
    
    except Job.DoesNotExist:
      return Response(
        {"error": "Job with given ID does not exist."},
        status=status.HTTP_404_NOT_FOUND
      )
    
    except Exception as e:
      logger.error(f"Error cancelling job: {str(e)}")
      return Response(
        {"error": "An error occurred while cancelling the job."},
        status=status.HTTP_400_BAD_REQUEST
      )
    

  @action(detail=True, methods=['get'])
  def results(self, request, pk=None):
    try:
      job = self.get_object()

      if job.status != 'COMPLETED':
        return Response(
          {"error": "Job is not completed yet."},
          status=status.HTTP_400_BAD_REQUEST
        )


      return Response({
        'result_data': job.result_data,
        'id': job.id,
        'status': job.status
      }
      )
    
    except Job.DoesNotExist:
      return Response(
        {"error": "Job with given ID does not exist."},
        status=status.HTTP_404_NOT_FOUND
      )