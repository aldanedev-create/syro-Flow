from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import DonationSettings, DonationTransaction, DonationGoal
from .forms import DonationForm


class DonationView(TemplateView):
    """Main donation page"""
    
    template_name = 'donations/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get donation settings
        settings_obj = DonationSettings.get_solo()
        context['settings'] = settings_obj
        
        # Get active goals
        context['goals'] = DonationGoal.objects.filter(
            is_active=True
        ).order_by('-start_date')[:3]
        
        # Get recent donations (for display, with anonymous hidden)
        context['recent_donations'] = DonationTransaction.objects.filter(
            status='completed',
            is_anonymous=False
        ).order_by('-created_at')[:10]
        
        # Get total raised
        total_raised = DonationTransaction.objects.filter(
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        context['total_raised'] = total_raised
        
        # Get donation count
        context['donation_count'] = DonationTransaction.objects.filter(
            status='completed'
        ).count()
        
        context['page_title'] = 'Donations'
        context['page_description'] = 'Support our mission through donations'
        
        return context


class DonationCreateView(View):
    """Handle donation form submission"""
    
    def get(self, request, *args, **kwargs):
        """Display donation form"""
        form = DonationForm()
        settings_obj = DonationSettings.get_solo()
        
        context = {
            'form': form,
            'settings': settings_obj,
        }
        return render(request, 'donations/form.html', context)
    
    def post(self, request, *args, **kwargs):
        """Process donation form"""
        form = DonationForm(request.POST)
        
        if form.is_valid():
            # Create transaction record
            transaction = form.save()
            
            messages.success(
                request,
                f'Thank you for your donation pledge of {transaction.get_amount_display()}. '
                'It will be marked complete after payment is verified.'
            )
            
            return redirect(reverse('donations:thank_you'))
        else:
            # Invalid form
            context = {
                'form': form,
                'settings': DonationSettings.get_solo(),
            }
            return render(request, 'donations/form.html', context)
    
    def send_confirmation_email(self, transaction):
        """Send confirmation only after a verified payment."""
        try:
            subject = 'Thank You for Your Donation'
            message = f"""
            Dear {transaction.donor_name},
            
            Thank you for your generous donation of {transaction.get_amount_display()}!
            
            Your support helps us continue our mission.
            
            Transaction ID: {transaction.transaction_id}
            Date: {transaction.created_at}
            
            God bless you!
            
            - The Syro Flow Team
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [transaction.donor_email]
            
            if transaction.donor_email:
                send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Log email error but don't stop the process
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send donation email: {e}")


class DonationThankYouView(TemplateView):
    """Thank you page after donation"""
    
    template_name = 'donations/thank_you.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Thank You'
        context['page_description'] = 'Thank you for your generous donation'
        return context


class TransactionStatusView(DetailView):
    """View transaction status"""
    
    model = DonationTransaction
    template_name = 'donations/transaction_status.html'
    context_object_name = 'transaction'
    slug_field = 'transaction_id'
    slug_url_kwarg = 'transaction_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()
        context['page_title'] = f'Transaction {transaction.transaction_id}'
        return context


class GoalListView(ListView):
    """List all donation goals"""
    
    model = DonationGoal
    template_name = 'donations/goal_list.html'
    context_object_name = 'goals'
    
    def get_queryset(self):
        return DonationGoal.objects.filter(
            is_active=True
        ).order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Donation Goals'
        context['page_description'] = 'See our current donation goals and campaigns'
        return context


class GoalDetailView(DetailView):
    """View a single donation goal"""
    
    model = DonationGoal
    template_name = 'donations/goal_detail.html'
    context_object_name = 'goal'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goal = self.get_object()
        
        context['page_title'] = goal.title
        context['page_description'] = goal.description[:300]
        context['progress_percentage'] = goal.get_progress_percentage()
        context['remaining'] = goal.get_remaining_amount()
        context['is_completed'] = goal.is_completed()
        
        return context
