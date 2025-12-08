from rest_framework import serializers
from .models import Project, Dataset, Job

class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
  class Meta:
    model = Dataset
    fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields = '__all__'

