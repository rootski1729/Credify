from rest_framework import serializers
from .models import Loan
from apps.customers.serializers import CustomerDetailSerializer


class LoanEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    tenure = serializers.IntegerField(min_value=1, max_value=600)  # max 50 years


class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class LoanCreateRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    tenure = serializers.IntegerField(min_value=1, max_value=600)


class LoanCreateResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class LoanDetailSerializer(serializers.ModelSerializer):
    loan_id = serializers.IntegerField(read_only=True)
    customer = CustomerDetailSerializer(read_only=True)
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    monthly_installment = serializers.DecimalField(
        source='monthly_payment', 
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    tenure = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']


class LoanListSerializer(serializers.ModelSerializer):
    loan_id = serializers.IntegerField(read_only=True)
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    monthly_installment = serializers.DecimalField(
        source='monthly_payment', 
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    repayments_left = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']