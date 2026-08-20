from rest_framework import serializers
from .models import Post, Category, Tag
from apps.media_library.serializers import MediaSerializer
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    published_post_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 
            'published_post_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'created_at')
        read_only_fields = ('created_at',)


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for User (Author)"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email')
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list (summary)"""
    
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    featured_image = MediaSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'excerpt', 
            'category', 'author', 'featured_image',
            'tags', 'status', 'published_at', 'view_count',
            'reading_time', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'view_count', 'created_at', 'updated_at', 'published_at'
        )


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for post detail (full content)"""
    
    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    featured_image = MediaSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    previous_post = serializers.SerializerMethodField()
    next_post = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'content', 'excerpt',
            'category', 'author', 'featured_image',
            'tags', 'status', 'published_at', 'view_count',
            'reading_time', 'seo_title', 'seo_description',
            'previous_post', 'next_post',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'view_count', 'created_at', 'updated_at', 'published_at'
        )
    
    def get_previous_post(self, obj):
        """Get serialized previous post"""
        previous = obj.get_previous_post()
        if previous:
            return PostListSerializer(previous).data
        return None
    
    def get_next_post(self, obj):
        """Get serialized next post"""
        next_post = obj.get_next_post()
        if next_post:
            return PostListSerializer(next_post).data
        return None


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts"""
    
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'content', 'excerpt',
            'category', 'tags', 'featured_image',
            'status', 'published_at',
            'seo_title', 'seo_description'
        )
    
    def create(self, validated_data):
        """Create post with auto-set author"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)