from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.urls import reverse
from django.utils.text import slugify

from .models import Post, Category, Tag
from apps.media_library.models import Media


class CategoryModelTest(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
    
    def test_category_creation(self):
        """Test category creation with auto-slug"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
    
    def test_category_str(self):
        """Test string representation"""
        self.assertEqual(str(self.category), 'Test Category')
    
    def test_category_get_absolute_url(self):
        """Test URL generation"""
        url = self.category.get_absolute_url()
        self.assertEqual(url, reverse('posts:category', kwargs={'slug': self.category.slug}))
    
    def test_category_published_post_count(self):
        """Test published post count"""
        self.assertEqual(self.category.published_post_count, 0)


class TagModelTest(TestCase):
    """Test cases for Tag model"""
    
    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag')
    
    def test_tag_creation(self):
        """Test tag creation with auto-slug"""
        self.assertEqual(self.tag.name, 'Test Tag')
        self.assertEqual(self.tag.slug, 'test-tag')
    
    def test_tag_str(self):
        """Test string representation"""
        self.assertEqual(str(self.tag), 'Test Tag')


class PostModelTest(TestCase):
    """Test cases for Post model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.category = Category.objects.create(name='Test Category')
        self.tag = Tag.objects.create(name='Test Tag')
        
        self.post = Post.objects.create(
            title='Test Post',
            content='<p>This is test content.</p>',
            category=self.category,
            author=self.user,
            status='published'
        )
        self.post.tags.add(self.tag)
    
    def test_post_creation(self):
        """Test post creation with auto-slug and auto-excerpt"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.excerpt, 'This is test content....')
        self.assertEqual(self.post.status, 'published')
        self.assertIsNotNone(self.post.published_at)
    
    def test_post_str(self):
        """Test string representation"""
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_post_get_absolute_url(self):
        """Test URL generation"""
        url = self.post.get_absolute_url()
        self.assertEqual(url, reverse('posts:detail', kwargs={'slug': self.post.slug}))
    
    def test_post_reading_time(self):
        """Test reading time calculation"""
        reading_time = self.post.get_reading_time()
        self.assertGreater(reading_time, 0)
    
    def test_post_increment_view_count(self):
        """Test view count increment"""
        initial = self.post.view_count
        self.post.increment_view_count()
        self.assertEqual(self.post.view_count, initial + 1)
    
    def test_published_manager(self):
        """Test published() queryset"""
        published_posts = Post.published()
        self.assertEqual(published_posts.count(), 1)
        
        # Create draft post
        draft = Post.objects.create(
            title='Draft Post',
            content='Draft content',
            status='draft'
        )
        self.assertEqual(Post.published().count(), 1)
    
    def test_is_published_property(self):
        """Test is_published property"""
        self.assertTrue(self.post.is_published)
        
        draft = Post.objects.create(
            title='Draft Post',
            content='Draft content',
            status='draft'
        )
        self.assertFalse(draft.is_published)
    
    def test_get_next_previous_posts(self):
        """Test next/previous post navigation"""
        post1 = Post.objects.create(
            title='Post 1',
            content='Content 1',
            status='published'
        )
        post2 = Post.objects.create(
            title='Post 2',
            content='Content 2',
            status='published'
        )
        
        self.assertEqual(post1.get_next_post(), post2)
        self.assertEqual(post2.get_previous_post(), post1)


class PostViewTest(TestCase):
    """Test cases for post views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            content='<p>Test content</p>',
            category=self.category,
            author=self.user,
            status='published'
        )
    
    def test_post_list_view(self):
        """Test post list page"""
        response = self.client.get(reverse('posts:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_list.html')
        self.assertContains(response, 'Test Post')
    
    def test_post_detail_view(self):
        """Test post detail page"""
        response = self.client.get(
            reverse('posts:detail', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test content')
    
    def test_category_view(self):
        """Test category page"""
        response = self.client.get(
            reverse('posts:category', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/category.html')
        self.assertContains(response, 'Test Category')
        self.assertContains(response, 'Test Post')
    
    def test_tag_view(self):
        """Test tag page"""
        tag = Tag.objects.create(name='Test Tag')
        self.post.tags.add(tag)
        
        response = self.client.get(
            reverse('posts:tag', kwargs={'slug': tag.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/tag.html')
        self.assertContains(response, 'Test Tag')
        self.assertContains(response, 'Test Post')
    
    def test_search_view(self):
        """Test search functionality"""
        response = self.client.get(
            reverse('posts:search') + '?q=Test'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/search.html')
        self.assertContains(response, 'Test Post')
        
        # Search with no results
        response = self.client.get(
            reverse('posts:search') + '?q=nonexistent'
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Post')
    
    def test_archive_view(self):
        """Test archive by year"""
        year = now().year
        response = self.client.get(
            reverse('posts:archive_year', kwargs={'year': year})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/archive.html')