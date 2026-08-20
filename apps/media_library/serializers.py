from rest_framework import serializers
from .models import Media, MediaCategory


class MediaCategorySerializer(serializers.ModelSerializer):
    """Serializer for MediaCategory model"""
    
    media_count = serializers.IntegerField(source='media_set.count', read_only=True)
    
    class Meta:
        model = MediaCategory
        fields = ('id', 'name', 'slug', 'description', 'media_count', 'created_at')
        read_only_fields = ('created_at',)


class MediaListSerializer(serializers.ModelSerializer):
    """Serializer for media list (summary)"""
    
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Media
        fields = (
            'id', 'title', 'alt_text', 'file_url', 'thumbnail_url',
            'media_type', 'file_size_display', 'file_size',
            'width', 'height',
            'uploaded_by', 'uploaded_by_username',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_file_url(self, obj):
        return obj.get_absolute_url()
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()


class MediaDetailSerializer(serializers.ModelSerializer):
    """Serializer for media detail (full)"""
    
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    categories = MediaCategorySerializer(many=True, read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    uploaded_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = (
            'id', 'title', 'alt_text', 'caption', 'description',
            'file', 'file_url', 'thumbnail_url',
            'file_size', 'file_size_display',
            'width', 'height', 'media_type',
            'categories',
            'uploaded_by', 'uploaded_by_username', 'uploaded_by_full_name',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_file_url(self, obj):
        return obj.get_absolute_url()
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()
    
    def get_uploaded_by_full_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None


class MediaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating media"""
    
    class Meta:
        model = Media
        fields = (
            'id', 'title', 'alt_text', 'caption', 'description',
            'file', 'categories', 'media_type'
        )
    
    def validate_file(self, value):
        """Validate file size and type"""
        from .validators import validate_file_size, validate_file_type
        validate_file_size(value)
        validate_file_type(value)
        return value
    
    def create(self, validated_data):
        """Create media with auto-set uploaded_by"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class MediaUploadSerializer(serializers.Serializer):
    """Serializer for file upload endpoint"""
    
    file = serializers.FileField()
    title = serializers.CharField(max_length=200, required=False)
    alt_text = serializers.CharField(max_length=200, required=False)
    caption = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate_file(self, value):
        """Validate file size and type"""
        from .validators import validate_file_size, validate_file_type
        validate_file_size(value)
        validate_file_type(value)
        return value