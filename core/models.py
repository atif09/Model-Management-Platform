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

  def __str__(self):
    return self.name

  

