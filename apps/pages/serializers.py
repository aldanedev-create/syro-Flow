from rest_framework import serializers
from .models import Page, PageSection


class PageSectionSerializer(serializers.ModelSerializer):
    """Serializer for PageSection model"""
    
    class Meta:
        model = PageSection
        fields = ('id', 'title', 'content', 'order')
        read_only_fields = ('id',)


class PageListSerializer(serializers.ModelSerializer):
    """Serializer for page list (summary)"""
    
    class Meta:
        model = Page
        fields = (
            'id', 'title', 'slug', 'excerpt',
            'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class PageDetailSerializer(serializers.ModelSerializer):
    """Serializer for page detail (full content)"""
    
    sections = PageSectionSerializer(many=True, read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Page
        fields = (
            'id', 'title', 'slug', 'content', 'excerpt',
            'sections', 'reading_time',
            'seo_title', 'seo_description',
            'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class PageCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating pages"""
    
    class Meta:
        model = Page
        fields = (
            'id', 'title', 'slug', 'content', 'excerpt',
            'status', 'seo_title', 'seo_description'
        )