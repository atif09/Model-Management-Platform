import hashlib
import uuid
from pathlib import Path
from PIL import Image
import io

# Magic numbers # the first few bytes of common image formats
MAGIC_NUMBERS = {
  'text/csv': [b''],
  'image/png': [b'\x89PNG'],
  'image/jpeg': [b'\xff\xd8\xff'],
  'image/gif': [b'GIF87a', b'GIF89a'],
}

def check_magic_number(file_obj):
  # Read first 4 bytes and check against known magic numbers
  # Returns (is_valid, detected_type)

  file_obj.seek(0)
  magic = file_obj.read(4)
  file_obj.seek(0)

  # PNG check
  if magic.startswith(b'\x89PNG'):
    return True, 'image/png'
  
  # JPEG check
  if magic.startswith(b'\xff\xd8\xff'):
    return True, 'image/jpeg'
  
  # GIF check
  if magic.startswith(b'GIF87a') or magic.startswith(b'GIF89a'):
    return True, 'image/gif'
  
  # CSV: check extension instead (no reliable magic for plain text)
  # This is checked elsewhere in validation logic

  return False, None


def sanitize_filename(filename):
  # Remove directory traversal characters and dangerous chars
  # Keep onl y alphanumerics, dashes, underscores, dots

  # Remove path separators and null bytes
  filename = filename.replace('\\', '').replace('/', '').replace('\0', '')
  # Allow only safe characters
  import re
  filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
  filename = filename.lstrip('.-') # Prevent hidden files
  return filename or 'file'


def generate_file_hash(file_obj):
  # Generate SHA256 of file for duplicate detection
  file_obj.seek(0)
  hash = hashlib.sha256()
  while True:
    chunk = file_obj.read(8192) # Read in 8KB chunks
    if not chunk:
      break
    hash.update(chunk)

  file_obj.seek(0) # reset file pointer to the start
  return hash.hexdigest()


def generate_unique_filename(original_name):
  # Generates a unique filename using UUId to avoid collisions
  # Preserves original extension if possible

  # ext = extension
  ext = Path(original_name).suffix #.suffix extracts the file extension 
  # Example: Path('file.csv').suffix -> '.csv'

  return f"{uuid.uuid4().hex}{ext}"



def extract_image_metadata(file_obj):
  try:
    file_obj.seek(0)
    image = Image.open(file_obj)
    width, height = image.size
    file_obj.seek(0)
    return {
      'width': width,
      'height': height,
      'format': image.format,
    
    
    }
  except Exception:
    file_obj.seek(0)
    return None
  
def mock_virus_scan(file_obj):
  # Place holder for virus scanning logic. Always returns safe
  # In production, integrate ClamAV or similar

  file_obj.seek(0)
  
  # Mock: always return True (file is safe)

  return True


