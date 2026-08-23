from rest_framework import serializers
from .models import DonationSettings, DonationTransaction, DonationGoal


class DonationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for DonationSettings model"""
    
    currency_symbol = serializers.SerializerMethodField()
    formatted_donation_message = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationSettings
        fields = (
            'id', 'bank_name', 'account_name', 'account_number',
            'branch', 'currency', 'currency_symbol',
            'payment_methods', 'mobile_money_number',
            'paypal_email', 'stripe_public_key',
            'donation_message', 'formatted_donation_message',
            'funds_usage', 'impact_stories',
            'is_active', 'cta_text', 'cta_url',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_currency_symbol(self, obj):
        """Get currency symbol"""
        return obj.get_currency_symbol()
    
    def get_formatted_donation_message(self, obj):
        """Get formatted donation message (could include HTML)"""
        return obj.donation_message


class DonationTransactionListSerializer(serializers.ModelSerializer):
    """Serializer for donation transaction list"""
    
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationTransaction
        fields = (
            'id', 'donor_name', 'amount', 'currency',
            'amount_display', 'payment_method',
            'status', 'status_display',
            'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_amount_display(self, obj):
        return obj.get_amount_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class DonationTransactionDetailSerializer(serializers.ModelSerializer):
    """Serializer for donation transaction detail"""
    
    amount_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationTransaction
        fields = (
            'id', 'donor_name', 'donor_email', 'donor_phone',
            'is_anonymous', 'amount', 'currency',
            'amount_display', 'payment_method',
            'transaction_id', 'status', 'status_display',
            'message', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_amount_display(self, obj):
        return obj.get_amount_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class DonationTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating donation transactions"""
    
    class Meta:
        model = DonationTransaction
        fields = (
            'donor_name', 'donor_email', 'donor_phone',
            'is_anonymous', 'amount', 'currency',
            'payment_method', 'message'
        )
    
    def create(self, validated_data):
        """Create transaction with pending status"""
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class DonationTransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating donation transactions"""
    
    class Meta:
        model = DonationTransaction
        fields = (
            'status', 'payment_response'
        )
    
    def update(self, instance, validated_data):
        """Update transaction and handle status changes"""
        old_status = instance.status
        new_status = validated_data.get('status')
        
        instance = super().update(instance, validated_data)
        
        # If transaction is completed, update donation goals
        if old_status != 'completed' and new_status == 'completed':
            from .models import DonationGoal
            goals = DonationGoal.objects.filter(is_active=True)
            for goal in goals:
                goal.add_donation(instance.amount)
        
        return instance


class DonationGoalListSerializer(serializers.ModelSerializer):
    """Serializer for donation goal list"""
    
    progress_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationGoal
        fields = (
            'id', 'title', 'description',
            'target_amount', 'raised_amount',
            'progress_percentage', 'remaining_amount',
            'is_completed', 'is_active',
            'start_date', 'end_date',
            'created_at'
        )
        read_only_fields = ('raised_amount', 'created_at')
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
    
    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()
    
    def get_is_completed(self, obj):
        return obj.is_completed()


class DonationGoalDetailSerializer(serializers.ModelSerializer):
    """Serializer for donation goal detail"""
    
    progress_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationGoal
        fields = (
            'id', 'title', 'description',
            'target_amount', 'raised_amount',
            'progress_percentage', 'remaining_amount',
            'is_completed', 'is_expired',
            'is_active', 'start_date', 'end_date',
            'featured_image', 'created_at', 'updated_at'
        )
        read_only_fields = ('raised_amount', 'created_at', 'updated_at')
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
    
    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()
    
    def get_is_completed(self, obj):
        return obj.is_completed()
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class DonationGoalCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating donation goals"""
    
    class Meta:
        model = DonationGoal
        fields = (
            'title', 'description',
            'target_amount', 'currency',
            'start_date', 'end_date',
            'is_active', 'featured_image'
        )