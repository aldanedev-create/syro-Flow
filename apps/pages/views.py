from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse

from .models import Page
from .forms import ContactForm


class PageDetailView(DetailView):
    """Display a single published page"""
    
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Get published pages only"""
        return Page.published().prefetch_related('sections')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        
        context['page_title'] = page.seo_title or page.title
        context['page_description'] = page.seo_description or page.excerpt
        
        return context


class ContactView(FormView):
    """Contact page with real email sending"""
    
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact/'  # Will redirect back with success message
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        context['page_description'] = 'Get in touch with us'
        return context
    
    def form_valid(self, form):
        """Process the contact form and send email"""
        
        # Get form data
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject'] or 'No Subject'
        message = form.cleaned_data['message']
        
        # Build email context
        context = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        # Render email templates
        html_message = render_to_string('emails/contact_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Get recipient email from settings
        recipient_email = getattr(settings, 'CONTACT_EMAIL', None)
        if not recipient_email:
            # Fallback to admin email or default
            recipient_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@syroflow.com')
        
        try:
            # Send email
            send_mail(
                subject=f"Contact Form: {subject}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Send auto-reply to user
            self.send_auto_reply(name, email, message)
            
            # Success message
            messages.success(
                self.request,
                'Thank you for your message! We will get back to you shortly.'
            )
            
        except BadHeaderError:
            messages.error(
                self.request,
                'Invalid header found. Please try again.'
            )
            return self.form_invalid(form)
            
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Contact form email error: {e}")
            
            messages.error(
                self.request,
                'Sorry, there was a problem sending your message. Please try again later.'
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def send_auto_reply(self, name, email, message):
        """Send auto-reply to the person who contacted us"""
        
        context = {
            'name': name,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        html_message = render_to_string('emails/auto_reply.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=f"Thank you for contacting {settings.SITE_NAME}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Don't fail if auto-reply fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Auto-reply email failed: {e}")


class PageListView(ListView):
    """List all published pages (for sitemap or index)"""
    
    model = Page
    template_name = 'pages/page_list.html'
    context_object_name = 'pages'
    
    def get_queryset(self):
        return Page.published().order_by('title')


class PagePreviewView(LoginRequiredMixin, DetailView):
    """Preview any page regardless of status (admin only)"""
    
    model = Page
    template_name = 'pages/page_preview.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Allow viewing drafts for logged-in admins"""
        return Page.objects.all().prefetch_related('sections')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        
        context['page_title'] = f'Preview: {page.title}'
        context['is_preview'] = True
        
        return context