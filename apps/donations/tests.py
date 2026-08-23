from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from decimal import Decimal

from .models import DonationSettings, DonationTransaction, DonationGoal


class DonationSettingsModelTest(TestCase):
    """Test cases for DonationSettings model"""
    
    def test_settings_creation(self):
        """Test that donation settings can be created"""
        settings = DonationSettings.get_solo()
        self.assertEqual(settings.bank_name, '')
        self.assertEqual(settings.currency, 'USD')
        self.assertTrue(settings.is_active)
    
    def test_settings_singleton(self):
        """Test that only one settings instance exists"""
        settings1 = DonationSettings.get_solo()
        with self.assertRaises(ValueError):
            DonationSettings.objects.create(
                bank_name='Test Bank',
                account_name='Test Account',
                account_number='123456'
            )
    
    def test_settings_update(self):
        """Test that settings can be updated"""
        settings = DonationSettings.get_solo()
        settings.bank_name = 'Test Bank'
        settings.account_name = 'Test Account'
        settings.account_number = '123456'
        settings.save()
        
        updated = DonationSettings.get_solo()
        self.assertEqual(updated.bank_name, 'Test Bank')
        self.assertEqual(updated.account_name, 'Test Account')
    
    def test_currency_symbol(self):
        """Test currency symbol method"""
        settings = DonationSettings.get_solo()
        settings.currency = 'USD'
        self.assertEqual(settings.get_currency_symbol(), '$')
        
        settings.currency = 'EUR'
        self.assertEqual(settings.get_currency_symbol(), '€')
        
        settings.currency = 'NGN'
        self.assertEqual(settings.get_currency_symbol(), '₦')


class DonationTransactionModelTest(TestCase):
    """Test cases for DonationTransaction model"""
    
    def setUp(self):
        self.transaction = DonationTransaction.objects.create(
            donor_name='Test Donor',
            donor_email='test@example.com',
            amount=Decimal('50.00'),
            currency='USD',
            payment_method='bank_transfer',
            status='pending'
        )
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        self.assertEqual(self.transaction.donor_name, 'Test Donor')
        self.assertEqual(self.transaction.amount, Decimal('50.00'))
        self.assertEqual(self.transaction.status, 'pending')
        self.assertIsNotNone(self.transaction.transaction_id)
    
    def test_transaction_str(self):
        """Test string representation"""
        expected = f"Test Donor - 50.00 USD"
        self.assertEqual(str(self.transaction), expected)
    
    def test_transaction_id_generation(self):
        """Test transaction ID auto-generation"""
        transaction = DonationTransaction.objects.create(
            donor_name='Another Donor',
            amount=Decimal('25.00'),
            currency='USD',
            payment_method='paypal'
        )
        self.assertTrue(transaction.transaction_id.startswith('SYRO-'))
        self.assertEqual(len(transaction.transaction_id), 17)  # SYRO- + 12 chars
    
    def test_get_amount_display(self):
        """Test amount display method"""
        display = self.transaction.get_amount_display()
        self.assertEqual(display, 'USD 50.00')
    
    def test_transaction_status_update(self):
        """Test updating transaction status"""
        self.transaction.status = 'completed'
        self.transaction.save()
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'completed')


class DonationGoalModelTest(TestCase):
    """Test cases for DonationGoal model"""
    
    def setUp(self):
        self.goal = DonationGoal.objects.create(
            title='Test Goal',
            description='Test description',
            target_amount=Decimal('1000.00'),
            currency='USD',
            start_date=now().date(),
            is_active=True
        )
    
    def test_goal_creation(self):
        """Test goal creation"""
        self.assertEqual(self.goal.title, 'Test Goal')
        self.assertEqual(self.goal.target_amount, Decimal('1000.00'))
        self.assertEqual(self.goal.raised_amount, Decimal('0.00'))
        self.assertTrue(self.goal.is_active)
    
    def test_goal_str(self):
        """Test string representation"""
        self.assertEqual(str(self.goal), 'Test Goal')
    
    def test_progress_percentage(self):
        """Test progress percentage calculation"""
        self.assertEqual(self.goal.get_progress_percentage(), 0)
        
        self.goal.raised_amount = Decimal('500.00')
        self.goal.save()
        self.assertEqual(self.goal.get_progress_percentage(), 50)
        
        self.goal.raised_amount = Decimal('1000.00')
        self.goal.save()
        self.assertEqual(self.goal.get_progress_percentage(), 100)
        
        self.goal.raised_amount = Decimal('1500.00')
        self.goal.save()
        self.assertEqual(self.goal.get_progress_percentage(), 100)  # Caps at 100
    
    def test_remaining_amount(self):
        """Test remaining amount calculation"""
        self.assertEqual(self.goal.get_remaining_amount(), Decimal('1000.00'))
        
        self.goal.raised_amount = Decimal('300.00')
        self.goal.save()
        self.assertEqual(self.goal.get_remaining_amount(), Decimal('700.00'))
    
    def test_is_completed(self):
        """Test is_completed method"""
        self.assertFalse(self.goal.is_completed())
        
        self.goal.raised_amount = Decimal('1000.00')
        self.goal.save()
        self.assertTrue(self.goal.is_completed())
    
    def test_add_donation(self):
        """Test adding donation to goal"""
        self.goal.add_donation(Decimal('100.00'))
        self.assertEqual(self.goal.raised_amount, Decimal('100.00'))
        
        self.goal.add_donation(Decimal('50.00'))
        self.assertEqual(self.goal.raised_amount, Decimal('150.00'))
    
    def test_is_expired(self):
        """Test is_expired method"""
        from django.utils.timezone import timedelta
        from datetime import timedelta as td
        
        # Set end date in the past
        self.goal.end_date = now().date() - timedelta(days=1)
        self.goal.save()
        self.assertTrue(self.goal.is_expired())
        
        # Set end date in the future
        self.goal.end_date = now().date() + timedelta(days=1)
        self.goal.save()
        self.assertFalse(self.goal.is_expired())


class DonationViewTest(TestCase):
    """Test cases for donation views"""
    
    def setUp(self):
        # Create donation settings
        self.settings = DonationSettings.get_solo()
        self.settings.bank_name = 'Test Bank'
        self.settings.account_name = 'Test Account'
        self.settings.account_number = '123456'
        self.settings.save()
        
        # Create a goal
        self.goal = DonationGoal.objects.create(
            title='Test Goal',
            description='Test description',
            target_amount=Decimal('1000.00'),
            currency='USD',
            start_date=now().date(),
            is_active=True
        )
        
        # Create a completed transaction
        self.transaction = DonationTransaction.objects.create(
            donor_name='Test Donor',
            donor_email='test@example.com',
            amount=Decimal('50.00'),
            currency='USD',
            payment_method='bank_transfer',
            status='completed',
            is_anonymous=False
        )
    
    def test_donation_page(self):
        """Test donation main page"""
        response = self.client.get(reverse('donations:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/index.html')
        self.assertContains(response, 'Test Bank')
        self.assertContains(response, 'Test Account')
        self.assertContains(response, 'Test Goal')
        self.assertContains(response, 'Test Donor')
    
    def test_donation_form_page(self):
        """Test donation form page"""
        response = self.client.get(reverse('donations:donate'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/form.html')
        self.assertContains(response, 'Donation Form')
    
    def test_donation_submission(self):
        """Test donation form submission"""
        response = self.client.post(reverse('donations:donate'), {
            'donor_name': 'New Donor',
            'donor_email': 'new@example.com',
            'amount': '75.00',
            'currency': 'USD',
            'payment_method': 'paypal',
            'is_anonymous': False,
            'message': 'Test message'
        })
        
        # Should redirect to thank you page
        self.assertRedirects(response, reverse('donations:thank_you'))
        
        # Check transaction was created
        transaction = DonationTransaction.objects.filter(
            donor_name='New Donor',
            amount=Decimal('75.00')
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.status, 'completed')
        
        # Check goal was updated
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.raised_amount, Decimal('75.00'))
    
    def test_donation_submission_anonymous(self):
        """Test anonymous donation submission"""
        response = self.client.post(reverse('donations:donate'), {
            'donor_name': 'Anonymous Donor',
            'donor_email': '',
            'amount': '25.00',
            'currency': 'USD',
            'payment_method': 'cash',
            'is_anonymous': True,
            'message': ''
        })
        
        self.assertRedirects(response, reverse('donations:thank_you'))
        
        transaction = DonationTransaction.objects.filter(
            donor_name='Anonymous Donor',
            amount=Decimal('25.00'),
            is_anonymous=True
        ).first()
        self.assertIsNotNone(transaction)
    
    def test_donation_submission_invalid(self):
        """Test donation submission with invalid data"""
        response = self.client.post(reverse('donations:donate'), {
            'donor_name': '',  # Required
            'amount': '0.00',  # Too small
            'currency': 'USD',
            'payment_method': 'paypal'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/form.html')
        self.assertContains(response, 'This field is required')
        self.assertContains(response, 'Ensure this value is greater than or equal to 0.01')
    
    def test_thank_you_page(self):
        """Test thank you page"""
        response = self.client.get(reverse('donations:thank_you'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/thank_you.html')
    
    def test_transaction_status_page(self):
        """Test transaction status page"""
        response = self.client.get(
            reverse('donations:transaction_status', 
                   kwargs={'transaction_id': self.transaction.transaction_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/transaction_status.html')
        self.assertContains(response, self.transaction.transaction_id)
    
    def test_goal_list_page(self):
        """Test goal list page"""
        response = self.client.get(reverse('donations:goals'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/goal_list.html')
        self.assertContains(response, 'Test Goal')
    
    def test_goal_detail_page(self):
        """Test goal detail page"""
        response = self.client.get(
            reverse('donations:goal_detail', kwargs={'pk': self.goal.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/goal_detail.html')
        self.assertContains(response, 'Test Goal')
        self.assertContains(response, '1000.00')


class DonationAdminTest(TestCase):
    """Test cases for donation admin"""
    
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
        
        self.transaction = DonationTransaction.objects.create(
            donor_name='Admin Test',
            amount=Decimal('100.00'),
            currency='USD',
            payment_method='bank_transfer',
            status='pending'
        )
    
    def test_admin_settings_view(self):
        """Test admin settings view"""
        response = self.client.get('/admin/donations/donationsettings/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_transaction_list(self):
        """Test admin transaction list view"""
        response = self.client.get('/admin/donations/donationtransaction/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test')
    
    def test_admin_transaction_change(self):
        """Test admin transaction change view"""
        response = self.client.get(
            f'/admin/donations/donationtransaction/{self.transaction.pk}/change/'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_admin_bulk_publish(self):
        """Test bulk status update action"""
        response = self.client.post('/admin/donations/donationtransaction/', {
            'action': 'mark_as_completed',
            '_selected_action': [self.transaction.pk]
        })
        self.assertEqual(response.status_code, 200)
        
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'completed')
    
    def test_admin_goal_view(self):
        """Test admin goal view"""
        response = self.client.get('/admin/donations/donationgoal/')
        self.assertEqual(response.status_code, 200)


class DonationFormTest(TestCase):
    """Test cases for donation forms"""
    
    def test_donation_form_valid(self):
        """Test valid donation form"""
        from .forms import DonationForm
        form = DonationForm(data={
            'donor_name': 'Test User',
            'donor_email': 'test@example.com',
            'amount': '50.00',
            'currency': 'USD',
            'payment_method': 'paypal',
            'is_anonymous': False,
            'message': 'Test message'
        })
        self.assertTrue(form.is_valid())
    
    def test_donation_form_missing_required(self):
        """Test form with missing required fields"""
        from .forms import DonationForm
        form = DonationForm(data={
            'donor_name': '',
            'amount': '',
            'currency': 'USD',
            'payment_method': 'paypal'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('donor_name', form.errors)
        self.assertIn('amount', form.errors)
    
    def test_donation_form_amount_validation(self):
        """Test amount validation"""
        from .forms import DonationForm
        form = DonationForm(data={
            'donor_name': 'Test',
            'amount': '0.00',
            'currency': 'USD',
            'payment_method': 'paypal'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        
        form = DonationForm(data={
            'donor_name': 'Test',
            'amount': '1000001.00',  # Too high
            'currency': 'USD',
            'payment_method': 'paypal'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_donation_settings_form(self):
        """Test donation settings form"""
        from .forms import DonationSettingsForm
        form = DonationSettingsForm(data={
            'bank_name': 'New Bank',
            'account_name': 'New Account',
            'account_number': '123456',
            'currency': 'USD',
            'is_active': True
        })
        self.assertTrue(form.is_valid())
    
    def test_donation_goal_form_valid(self):
        """Test donation goal form"""
        from .forms import DonationGoalForm
        from django.utils.timezone import timedelta
        from datetime import timedelta as td
        
        start = now().date()
        end = start + timedelta(days=30)
        
        form = DonationGoalForm(data={
            'title': 'New Goal',
            'description': 'Description',
            'target_amount': '500.00',
            'currency': 'USD',
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'is_active': True
        })
        self.assertTrue(form.is_valid())
    
    def test_donation_goal_form_date_validation(self):
        """Test goal form date validation"""
        from .forms import DonationGoalForm
        from django.utils.timezone import timedelta
        from datetime import timedelta as td
        
        start = now().date()
        end = start - timedelta(days=1)  # End date before start date
        
        form = DonationGoalForm(data={
            'title': 'New Goal',
            'description': 'Description',
            'target_amount': '500.00',
            'currency': 'USD',
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'is_active': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)


class DonationIntegrationTest(TestCase):
    """Integration tests for donation workflow"""
    
    def setUp(self):
        self.settings = DonationSettings.get_solo()
        self.settings.bank_name = 'Test Bank'
        self.settings.save()
        
        self.goal = DonationGoal.objects.create(
            title='Integration Test Goal',
            description='Test description',
            target_amount=Decimal('1000.00'),
            currency='USD',
            start_date=now().date(),
            is_active=True
        )
    
    def test_full_donation_flow(self):
        """Test the complete donation workflow"""
        # 1. Visit donation page
        response = self.client.get(reverse('donations:index'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit donation
        response = self.client.post(reverse('donations:donate'), {
            'donor_name': 'Flow Test',
            'donor_email': 'flow@example.com',
            'amount': '100.00',
            'currency': 'USD',
            'payment_method': 'stripe',
            'is_anonymous': False,
            'message': 'Integration test'
        })
        self.assertRedirects(response, reverse('donations:thank_you'))
        
        # 3. Check transaction
        transaction = DonationTransaction.objects.get(
            donor_name='Flow Test',
            amount=Decimal('100.00')
        )
        self.assertEqual(transaction.status, 'completed')
        
        # 4. Check goal updated
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.raised_amount, Decimal('100.00'))
        
        # 5. Check transaction appears on main page
        response = self.client.get(reverse('donations:index'))
        self.assertContains(response, 'Flow Test')
        self.assertContains(response, '100.00')
        
        # 6. Check transaction status page
        response = self.client.get(
            reverse('donations:transaction_status',
                   kwargs={'transaction_id': transaction.transaction_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.transaction_id)
        self.assertContains(response, '100.00')