from rest_framework import serializers
from .models import Customer


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']
    
    def validate_phone_number(self, value):
        if len(str(value)) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value
    
    def validate_monthly_income(self, value):
        if value <= 0:
            raise serializers.ValidationError("Monthly income must be positive")
        return value


class CustomerRegistrationResponseSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source='full_name', read_only=True)
    monthly_income = serializers.IntegerField(source='monthly_salary', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']


class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']