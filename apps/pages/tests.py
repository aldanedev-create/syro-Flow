from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

from .models import Page, PageSection


class PageModelTest(TestCase):
    """Test cases for Page model"""
    
    def setUp(self):
        self.page = Page.objects.create(
            title='About Us',
            content='<p>This is the about page content.</p>',
            status='published'
        )
    
    def test_page_creation(self):
        """Test page creation with auto-slug and auto-excerpt"""
        self.assertEqual(self.page.title, 'About Us')
        self.assertEqual(self.page.slug, 'about-us')
        self.assertEqual(self.page.excerpt, 'This is the about page content....')
        self.assertEqual(self.page.status, 'published')
    
    def test_page_str(self):
        """Test string representation"""
        self.assertEqual(str(self.page), 'About Us')
    
    def test_page_get_absolute_url(self):
        """Test URL generation"""
        url = self.page.get_absolute_url()
        self.assertEqual(url, reverse('pages:detail', kwargs={'slug': self.page.slug}))
    
    def test_is_published_property(self):
        """Test is_published property"""
        self.assertTrue(self.page.is_published)
        
        draft = Page.objects.create(
            title='Draft Page',
            content='Draft content',
            status='draft'
        )
        self.assertFalse(draft.is_published)
    
    def test_published_manager(self):
        """Test published() queryset"""
        # Baseline accounts for pages seeded by data migrations (e.g. the
        # About page) in addition to the one created in setUp().
        baseline = Page.published().count()

        # Create draft page
        draft = Page.objects.create(
            title='Draft Page',
            content='Draft content',
            status='draft'
        )
        self.assertEqual(Page.published().count(), baseline)
    
    def test_page_reading_time(self):
        """Test reading time calculation"""
        reading_time = self.page.get_reading_time()
        self.assertGreater(reading_time, 0)
    
    def test_slug_uniqueness(self):
        """Test that slugs are unique"""
        page1 = Page.objects.create(
            title='Test Page',
            content='Content',
            status='published'
        )
        page2 = Page.objects.create(
            title='Test Page',
            content='Different content',
            status='published'
        )
        # Since we're using unique=True, Django should handle this automatically
        # But we should verify slugs are unique
        self.assertNotEqual(page1.slug, page2.slug)
    
    def test_excerpt_auto_generation(self):
        """Test auto-generation of excerpt from content"""
        # Create page without excerpt
        page = Page.objects.create(
            title='Test Page',
            content='<p>This is a test page with some content. It should generate an excerpt automatically.</p>'
        )
        self.assertTrue(page.excerpt)
        self.assertLessEqual(len(page.excerpt), 500)


class PageSectionModelTest(TestCase):
    """Test cases for PageSection model"""
    
    def setUp(self):
        self.page = Page.objects.create(
            title='About Us',
            content='<p>Main content</p>',
            status='published'
        )
        self.section = PageSection.objects.create(
            page=self.page,
            title='Our Mission',
            content='<p>Our mission statement</p>',
            order=1
        )
    
    def test_section_creation(self):
        """Test page section creation"""
        self.assertEqual(self.section.page, self.page)
        self.assertEqual(self.section.title, 'Our Mission')
        self.assertEqual(self.section.order, 1)
    
    def test_section_str(self):
        """Test string representation"""
        self.assertEqual(str(self.section), 'About Us - Our Mission')
    
    def test_section_ordering(self):
        """Test that sections are ordered correctly"""
        section2 = PageSection.objects.create(
            page=self.page,
            title='Our Values',
            content='<p>Our values</p>',
            order=0
        )
        sections = PageSection.objects.filter(page=self.page)
        self.assertEqual(sections[0].order, 0)
        self.assertEqual(sections[1].order, 1)


class PageViewTest(TestCase):
    """Test cases for page views"""
    
    def setUp(self):
        self.page = Page.objects.create(
            title='About Us',
            content='<p>This is the about page content.</p>',
            status='published'
        )
        self.draft_page = Page.objects.create(
            title='Draft Page',
            content='<p>Draft content</p>',
            status='draft'
        )
    
    def test_page_detail_view(self):
        """Test page detail page"""
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': self.page.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/page_detail.html')
        self.assertContains(response, 'About Us')
        self.assertContains(response, 'This is the about page content.')
    
    def test_page_detail_view_draft_not_found(self):
        """Test that draft pages are not accessible to public"""
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': self.draft_page.slug})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_page_detail_view_context(self):
        """Test page detail context variables"""
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': self.page.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('page', response.context)
        self.assertEqual(response.context['page'], self.page)
        self.assertIn('page_title', response.context)
        self.assertIn('page_description', response.context)
    
    def test_page_list_view(self):
        """Test page list view"""
        response = self.client.get(reverse('pages:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/page_list.html')
        self.assertContains(response, 'About Us')
        self.assertNotContains(response, 'Draft Page')
    
    def test_page_with_sections(self):
        """Test page with sections in template"""
        PageSection.objects.create(
            page=self.page,
            title='Mission',
            content='<p>Our mission</p>',
            order=0
        )
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': self.page.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mission')
        self.assertContains(response, 'Our mission')


class PageAdminTest(TestCase):
    """Test cases for Page admin"""
    
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
    
    def test_admin_page_creation(self):
        """Test page creation in admin"""
        response = self.client.post('/admin/pages/page/add/', {
            'title': 'Admin Created Page',
            'content': '<p>Admin content</p>',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after save
        self.assertTrue(Page.objects.filter(title='Admin Created Page').exists())
    
    def test_admin_page_list_view(self):
        """Test admin page list view"""
        response = self.client.get('/admin/pages/page/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_page_bulk_publish(self):
        """Test bulk publish action"""
        page1 = Page.objects.create(title='Test 1', content='Content 1', status='draft')
        page2 = Page.objects.create(title='Test 2', content='Content 2', status='draft')
        
        response = self.client.post('/admin/pages/page/', {
            'action': 'publish_pages',
            '_selected_action': [page1.id, page2.id]
        })
        
        self.assertEqual(response.status_code, 200)
        page1.refresh_from_db()
        page2.refresh_from_db()
        self.assertEqual(page1.status, 'published')
        self.assertEqual(page2.status, 'published')


class PageFormTest(TestCase):
    """Test cases for Page form"""
    
    def test_page_form_valid(self):
        """Test valid form data"""
        from .forms import PageForm
        form = PageForm(data={
            'title': 'New Page',
            'content': '<p>Content</p>',
            'status': 'published'
        })
        self.assertTrue(form.is_valid())
    
    def test_page_form_slug_auto_generation(self):
        """Test automatic slug generation in form"""
        from .forms import PageForm
        form = PageForm(data={
            'title': 'New Page',
            'content': '<p>Content</p>',
            'slug': ''  # Empty slug should auto-generate
        })
        self.assertTrue(form.is_valid())
        # Slug will be generated on model save, not in form validation
    
    def test_page_form_duplicate_slug(self):
        """Test duplicate slug validation"""
        from .forms import PageForm
        Page.objects.create(
            title='Existing Page',
            content='<p>Content</p>',
            slug='existing-page'
        )
        
        # Try to create another page with the same slug
        form = PageForm(data={
            'title': 'Another Page',
            'content': '<p>Content</p>',
            'slug': 'existing-page'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
    
    def test_page_form_section_inline(self):
        """Test page section inline form"""
        from .forms import PageSectionForm
        form = PageSectionForm(data={
            'title': 'Section 1',
            'content': '<p>Section content</p>',
            'order': 0
        })
        self.assertTrue(form.is_valid())


class PageTemplateTest(TestCase):
    """Test cases for page templates"""
    
    def setUp(self):
        self.page = Page.objects.create(
            title='Test Page',
            content='<p>Test content</p>',
            status='published'
        )
    
    def test_page_detail_template_renders(self):
        """Test that page detail template renders properly"""
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': self.page.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/page_detail.html')
        # Check that base template is extended
        self.assertContains(response, 'base.html')
    
    def test_page_list_template_renders(self):
        """Test that page list template renders properly"""
        response = self.client.get(reverse('pages:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/page_list.html')
    
    def test_page_has_meta_tags(self):
        """Test that page includes SEO meta tags"""
        page_with_seo = Page.objects.create(
            title='SEO Page',
            content='<p>SEO content</p>',
            seo_title='SEO Title',
            seo_description='SEO Description',
            status='published'
        )
        response = self.client.get(
            reverse('pages:detail', kwargs={'slug': page_with_seo.slug})
        )
        self.assertEqual(response.status_code, 200)
        # Check for SEO tags in HTML
        self.assertContains(response, 'SEO Title')
        self.assertContains(response, 'SEO Description')