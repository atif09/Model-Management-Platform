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
  file_path = models.CharField(max_length=512)
  size = models.PositiveIntegerField()
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

  

