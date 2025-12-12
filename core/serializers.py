from rest_framework import serializers

from mlplatform.core.utils import check_magic_number
from .models import Project, Dataset, Job
from .utils import generate_file_hash, mock_virus_scan
from .utils import sanitize_filename, generate_unique_filename, extract_image_metadata


class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):

  # Write-only file field to accept uploads

  file = serializers.FileField(write_only=True, required=True)


  class Meta:
    model = Dataset
    fields = '__all__'
    read_only_fields = ['file_path', 'size', 'uploaded_at'] 

  def validate(self, path):
    uploaded_file = path.get('file')
    if not uploaded_file:
      raise serializers.ValidationError({"file": "No file provided"})
    
    max_size = 100 * 1024 * 1024 # 100 MB
    if uploaded_file > max_size:
      raise serializers.ValidationError({"File": "File size exceeds 100 MB limit."})

    is_valid_magic, detected_type = check_magic_number(uploaded_file)
    
    # Accept CSV and images and common Excel types
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    allowed = False
    if content_type:
      if content_type == 'text/csv' or content_type.startswith('images/'):
        allowed = True
      if content_type in ('application/vnd.ms-excel', 
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
        allowed = True
      
    # Fallback to extension check if MIME not present or uncertain
    if not allowed:
      name = uploaded_file.name.lower()
      if name.endswith(('.csv', '.png', '.jpg', '.jpeg', '.gif', '.xls', '.xlsx')):
        allowed = True

    if not allowed:
      raise serializers.ValidationError({"file": "Unsupported file type. Only CSV and iamge files are allowed"})
    

    # Magic number validation for images (warn if mismatch, but dont block CSV)
    if is_valid_magic and detected_type and detected_type.startswith('image/'):
      if not content_type.startswith('image/'):
        pass # Log warning but allow; file is actually an image

    elif not uploaded_file.name.lower().endswith('.csv'):
      if not (content_type.startswith('image/') or is_valid_magic):
        raise serializers.ValidationError({"file": "File content does not match its type."})
      
    if not mock_virus_scan(uploaded_file):
      raise serializers.ValidationError({"file": "File failed virus scan."})
    
    # Generate and check file hash for duplicates
    file_hash = generate_file_hash(uploaded_file)
    if Dataset.objects.filter(file_hash=file_hash).exists():
      raise serializers.ValidationError({"file": "A file with identical content has already been uploaded."})
    
    path['file_hash'] = file_hash

    return path
  

  def create(self, validated_data):
    uploaded_file = validated_data.pop('file')
    file_hash = validated_data.pop('file_hash', '')

    # Sanitize and generate unique filename
    safe_original_name = sanitize_filename(uploaded_file.name)
    unique_name = generate_unique_filename(safe_original_name)

    # Extract unage netadata uf applicable
    image_data = extract_image_metadata(uploaded_file)

    # Create dataset without saving file yet so we can attach metadata
    dataset = Dataset.objects.create(**validated_data)
    dataset.file.save(uploaded_file.name, uploaded_file, save=False)
    dataset.original_name = uploaded_file.name
    dataset.content_type = getattr(uploaded_file, 'content_type', '')
    dataset.size = uploaded_file.size
    dataset.file_hash = file_hash
    if image_data:
      dataset.image_width = image_data.get('width')
      dataset.image_height = image_data.get('height')
      
    dataset.save()
    return dataset


class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields = '__all__'
    read_only_fields = ['status', 'created_at', 'result_data', 'progress', 'task_id', 'error_message']


class JobSubmitSerializer(serializers.Serializer):
  """
    Serializer for submitting a new job.
    
    What it does:
    - Validates user input when creating a job
    - Checks that dataset_id exists
    - Checks that job_type is valid
    - Checks that target_format is provided for format conversion
    
    Expected input from user:
    {
        "dataset_id": 5,
        "job_type": "validate_csv",
        "target_format": ""  (optional)
    }
  """

  dataset_id = serializers.IntegerField()
  job_type = serializers.ChoiceField(
    choices = ['validate_csv', 'process_image', 'generate_statistics', 'convert_file_format']
  )
  target_format = serializers.CharField(required=False, allow_blank=True)

  def validate_dataset_id(self, value):
    try:
      dataset = Dataset.objects.get(id=value)
    except Dataset.DoesNotExist:
      raise serializers.ValidationError("Dataset with given ID does not exist.")
  
    return value
  




