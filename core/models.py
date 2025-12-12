from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Project(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name
  
class Dataset(models.Model):
  name = models.CharField(max_length=255)
  file = models.FileField(upload_to='datasets/%Y/%m/%d/')
  original_name = models.CharField(max_length=512, blank=True)
  content_type = models.CharField(max_length=100, blank=True)
  size = models.PositiveBigIntegerField(null=True, blank=True)
  file_hash = models.CharField(max_length=64, unique=True, blank=True)  # SHA-256 hex
  image_width = models.PositiveIntegerField(null=True, blank=True)
  image_height = models.PositiveIntegerField(null=True, blank=True)
  uploaded_at = models.DateTimeField(auto_now_add=True)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)

  def __str__(self):
    return self.name
  

class Job(models.Model):
  STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('PROCESSING', 'Processing'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
  ]
  name = models.CharField(max_length=255)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  result_data = models.JSONField(null=True, blank=True)
  progress = models.IntegerField(default=0)  # percentage from 0 to 100
  task_id = models.CharField(max_length=255, blank=True)
  error_message = models.TextField(blank=True)



  def __str__(self):
    return self.name
  
  def cancel_job(self):

    """
    Cancel a running job by stopping its Celery Task
    What it does:
    
    1. Checks if job has task_id (was submitted to Celery)
    2. Checks if job is still PROCESSING
    3. Gets the celery task using task_id
    4. Kills it immediately with terminate=True
    5. Updates job status to CANCELLED

    Returns: True if  cancelled, False if couldnt cancel
    """

    if self.task_id and self.status == 'PROCESSING':
      from mlplatform.celery import app
      celery_task = app.AsyncResult(self.task_id)
      celery_task.revoke(terminate=True)
      self.status = 'CANCELLED'
      self.save()
      return True
    return False
  
  

  

  

