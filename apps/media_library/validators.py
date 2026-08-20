import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from PIL import Image


def validate_file_size(value):
    """Validate that file size does not exceed maximum allowed"""
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)  # Default 10MB
    
    if value.size > max_size:
        raise ValidationError(
            _('File size exceeds maximum allowed size of %(max_size)s MB.'),
            params={
                'max_size': max_size / (1024 * 1024)
            },
            code='file_too_large'
        )


def validate_file_type(value):
    """Validate that file type is allowed"""
    allowed_extensions = getattr(
        settings, 
        'ALLOWED_IMAGE_TYPES', 
        'jpg,jpeg,png,gif,webp,pdf,doc,docx,mp4,mp3'
    ).split(',')
    
    # Get file extension
    ext = os.path.splitext(value.name)[1].lower().lstrip('.')
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _('File type "%(ext)s" is not allowed. Allowed types: %(allowed)s.'),
            params={
                'ext': ext,
                'allowed': ', '.join(allowed_extensions)
            },
            code='invalid_file_type'
        )


def validate_image_dimensions(value):
    """Validate image dimensions (if it's an image)"""
    try:
        # Try to open as image
        img = Image.open(value)
        width, height = img.size
        
        # Check minimum dimensions
        min_width = getattr(settings, 'MIN_IMAGE_WIDTH', 100)
        min_height = getattr(settings, 'MIN_IMAGE_HEIGHT', 100)
        
        if width < min_width or height < min_height:
            raise ValidationError(
                _('Image dimensions too small. Minimum size is %(width)sx%(height)s pixels.'),
                params={
                    'width': min_width,
                    'height': min_height
                },
                code='image_too_small'
            )
        
        # Check maximum dimensions
        max_width = getattr(settings, 'MAX_IMAGE_WIDTH', 4096)
        max_height = getattr(settings, 'MAX_IMAGE_HEIGHT', 4096)
        
        if width > max_width or height > max_height:
            raise ValidationError(
                _('Image dimensions too large. Maximum size is %(width)sx%(height)s pixels.'),
                params={
                    'width': max_width,
                    'height': max_height
                },
                code='image_too_large'
            )
        
    except Exception:
        # Not an image or can't read dimensions
        pass


def validate_image_file(value):
    """Validate that file is a valid image"""
    try:
        Image.open(value)
    except Exception:
        raise ValidationError(
            _('File is not a valid image.'),
            code='invalid_image'
        )


def validate_video_file(value):
    """Validate video file (basic)"""
    allowed_video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in allowed_video_extensions:
        raise ValidationError(
            _('Video format not supported. Supported formats: %(formats)s.'),
            params={'formats': ', '.join(allowed_video_extensions)},
            code='invalid_video_format'
        )


def validate_document_file(value):
    """Validate document file (basic)"""
    allowed_document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in allowed_document_extensions:
        raise ValidationError(
            _('Document format not supported. Supported formats: %(formats)s.'),
            params={'formats': ', '.join(allowed_document_extensions)},
            code='invalid_document_format'
        )


def validate_audio_file(value):
    """Validate audio file (basic)"""
    allowed_audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in allowed_audio_extensions:
        raise ValidationError(
            _('Audio format not supported. Supported formats: %(formats)s.'),
            params={'formats': ', '.join(allowed_audio_extensions)},
            code='invalid_audio_format'
        )


def validate_filename(value):
    """Validate filename for security"""
    import re
    
    filename = value.name
    
    # Check for directory traversal attempts
    if '..' in filename:
        raise ValidationError(
            _('Invalid filename: directory traversal not allowed.'),
            code='invalid_filename'
        )
    
    # Check for special characters
    if re.search(r'[<>:"/\\|?*]', filename):
        raise ValidationError(
            _('Invalid filename: contains restricted characters.'),
            code='invalid_filename'
        )
    
    # Check for null bytes
    if '\x00' in filename:
        raise ValidationError(
            _('Invalid filename: contains null byte.'),
            code='invalid_filename'
        )