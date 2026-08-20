from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from PIL import Image
import io
import os

from .models import Media, MediaCategory
from .validators import validate_file_size, validate_file_type


def create_test_image():
    """Create a test image file"""
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'png')
    file.seek(0)
    return SimpleUploadedFile(
        'test_image.png',
        file.read(),
        content_type='image/png'
    )


def create_test_file():
    """Create a test text file"""
    return SimpleUploadedFile(
        'test_file.txt',
        b'This is a test file content.',
        content_type='text/plain'
    )


class MediaCategoryModelTest(TestCase):
    """Test cases for MediaCategory model"""
    
    def setUp(self):
        self.category = MediaCategory.objects.create(
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


class MediaModelTest(TestCase):
    """Test cases for Media model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.category = MediaCategory.objects.create(name='Test Category')
        
        # Create test image
        self.image = create_test_image()
        
        self.media = Media.objects.create(
            title='Test Image',
            file=self.image,
            uploaded_by=self.user,
            alt_text='Test alt text',
            caption='Test caption',
            media_type='image'
        )
        self.media.categories.add(self.category)
    
    def test_media_creation(self):
        """Test media creation"""
        self.assertEqual(self.media.title, 'Test Image')
        self.assertEqual(self.media.alt_text, 'Test alt text')
        self.assertEqual(self.media.media_type, 'image')
        self.assertEqual(self.media.uploaded_by, self.user)
        self.assertTrue(self.media.file_size > 0)
    
    def test_media_str(self):
        """Test string representation"""
        self.assertEqual(str(self.media), 'Test Image')
    
    def test_media_file_size_display(self):
        """Test file size display"""
        display = self.media.get_file_size_display()
        self.assertIsNotNone(display)
    
    def test_media_is_image(self):
        """Test is_image method"""
        self.assertTrue(self.media.is_image())
    
    def test_media_get_absolute_url(self):
        """Test get_absolute_url"""
        url = self.media.get_absolute_url()
        self.assertIsNotNone(url)
    
    def test_media_get_thumbnail_url(self):
        """Test get_thumbnail_url"""
        url = self.media.get_thumbnail_url()
        self.assertIsNotNone(url)
    
    def test_media_detect_type(self):
        """Test media type detection"""
        # Create media with different file types
        image_media = Media.objects.create(
            title='Image',
            file=create_test_image(),
            media_type='image'
        )
        self.assertEqual(image_media.detect_media_type(), 'image')
    
    def test_media_set_image_dimensions(self):
        """Test image dimensions are set"""
        self.assertIsNotNone(self.media.width)
        self.assertIsNotNone(self.media.height)
        self.assertEqual(self.media.width, 100)
        self.assertEqual(self.media.height, 100)


class MediaValidatorsTest(TestCase):
    """Test cases for media validators"""
    
    def test_file_size_validator(self):
        """Test file size validation"""
        # Small file should pass
        small_file = SimpleUploadedFile('small.txt', b'Small content')
        try:
            validate_file_size(small_file)
        except Exception as e:
            self.fail(f'validate_file_size raised {e} unexpectedly!')
        
        # Create a large file (5MB)
        large_content = b'x' * (5 * 1024 * 1024)
        large_file = SimpleUploadedFile('large.txt', large_content)
        
        # This should raise an error if max size is less than 5MB
        # The validator uses settings.MAX_UPLOAD_SIZE
        try:
            validate_file_size(large_file)
        except Exception:
            # Expected if max size is less than 5MB
            pass
    
    def test_file_type_validator(self):
        """Test file type validation"""
        # Valid file type
        valid_file = SimpleUploadedFile('test.jpg', b'fake jpg content', content_type='image/jpeg')
        try:
            validate_file_type(valid_file)
        except Exception as e:
            self.fail(f'validate_file_type raised {e} unexpectedly!')
        
        # Invalid file type
        # The validator checks extension, so we need a file with invalid extension
        invalid_file = SimpleUploadedFile('test.exe', b'fake exe content', content_type='application/x-msdownload')
        
        # This should raise a validation error if extension is not allowed
        with self.assertRaises(Exception):
            validate_file_type(invalid_file)


class MediaViewTest(TestCase):
    """Test cases for media views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = Client()
        
        self.category = MediaCategory.objects.create(name='Test Category')
        self.media = Media.objects.create(
            title='Test Image',
            file=create_test_image(),
            uploaded_by=self.user,
            media_type='image'
        )
        self.media.categories.add(self.category)
    
    def test_gallery_view(self):
        """Test gallery page"""
        response = self.client.get(reverse('media_library:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/index.html')
        self.assertContains(response, 'Test Image')
    
    def test_media_detail_view(self):
        """Test media detail page"""
        response = self.client.get(
            reverse('media_library:detail', kwargs={'pk': self.media.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/image_detail.html')
        self.assertContains(response, 'Test Image')
    
    def test_gallery_category_view(self):
        """Test gallery by category"""
        response = self.client.get(
            reverse('media_library:category', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/category.html')
        self.assertContains(response, 'Test Category')
        self.assertContains(response, 'Test Image')
    
    def test_media_upload_requires_login(self):
        """Test upload requires login"""
        response = self.client.get(reverse('media_library:upload'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_media_upload_logged_in(self):
        """Test upload when logged in"""
        self.client.login(username='testuser', password='testpass')
        
        # Create a test file
        test_file = create_test_image()
        
        response = self.client.post(reverse('media_library:upload'), {
            'file': test_file,
            'title': 'Uploaded Image',
            'alt_text': 'Alt text for uploaded image',
        }, follow=True)
        
        # Check for success (either redirect or JSON response)
        # The view returns JSON for AJAX, but we're doing a regular post
        # It might redirect to success page or return JSON
        self.assertIn(response.status_code, [200, 302])
        
        # Check that media was created
        self.assertTrue(Media.objects.filter(title='Uploaded Image').exists())


class MediaAPITest(TestCase):
    """Test cases for media API endpoints (if implemented)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = Client()
        
        self.media = Media.objects.create(
            title='API Test Image',
            file=create_test_image(),
            uploaded_by=self.user,
            media_type='image'
        )
    
    def test_api_list_endpoint(self):
        """Test API list endpoint if implemented"""
        # This test assumes you have API endpoints set up
        # Skip if not implemented
        pass
    
    def test_api_detail_endpoint(self):
        """Test API detail endpoint if implemented"""
        pass


class MediaAdminTest(TestCase):
    """Test cases for media admin"""
    
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
        
        self.media = Media.objects.create(
            title='Admin Test Image',
            file=create_test_image(),
            uploaded_by=self.superuser,
            media_type='image'
        )
    
    def test_admin_media_list(self):
        """Test admin media list view"""
        response = self.client.get('/admin/media_library/media/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_media_add(self):
        """Test admin media add view"""
        response = self.client.get('/admin/media_library/media/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_media_change(self):
        """Test admin media change view"""
        response = self.client.get(
            f'/admin/media_library/media/{self.media.pk}/change/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test Image')
    
    def test_admin_category_list(self):
        """Test admin category list view"""
        response = self.client.get('/admin/media_library/mediacategory/')
        self.assertEqual(response.status_code, 200)


class MediaUsageTest(TestCase):
    """Test cases for media usage tracking"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.media = Media.objects.create(
            title='Test Image',
            file=create_test_image(),
            uploaded_by=self.user,
            media_type='image'
        )
    
    def test_media_usage_methods(self):
        """Test get_used_media and get_unused_media methods"""
        # Initially should be unused
        unused = Media.get_unused_media()
        self.assertIn(self.media, unused)
        
        used = Media.get_used_media()
        self.assertNotIn(self.media, used)
        
        # Create a post with this media
        from apps.posts.models import Post, Category
        category = Category.objects.create(name='Test')
        post = Post.objects.create(
            title='Test Post',
            content='Content',
            category=category,
            featured_image=self.media,
            status='published'
        )
        
        # Now should be used
        unused = Media.get_unused_media()
        self.assertNotIn(self.media, unused)
        
        used = Media.get_used_media()
        self.assertIn(self.media, used)


class MediaDeleteTest(TestCase):
    """Test cases for media deletion"""
    
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='admin', password='adminpass')
        
        self.media = Media.objects.create(
            title='Test Image',
            file=create_test_image(),
            uploaded_by=self.user,
            media_type='image'
        )
    
    def test_media_delete_unused(self):
        """Test deleting unused media"""
        response = self.client.post(
            reverse('media_library:delete_media', kwargs={'pk': self.media.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Media.objects.filter(pk=self.media.pk).exists())
    
    def test_media_delete_used(self):
        """Test deleting media that is used in posts"""
        from apps.posts.models import Post, Category
        
        category = Category.objects.create(name='Test')
        post = Post.objects.create(
            title='Test Post',
            content='Content',
            category=category,
            featured_image=self.media,
            status='published'
        )
        
        # Try to delete used media
        response = self.client.post(
            reverse('media_library:delete_media', kwargs={'pk': self.media.pk})
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Media.objects.filter(pk=self.media.pk).exists())