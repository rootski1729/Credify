from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import Loan
from apps.customers.models import Customer
from apps.core.credit_scoring import CreditScoring
from .serializers import (
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    LoanCreateRequestSerializer,
    LoanCreateResponseSerializer,
    LoanDetailSerializer,
    LoanListSerializer
)


@api_view(['POST'])
def check_loan_eligibility(request):
    """
    Check loan eligibility based on credit score
    POST /check-eligibility
    """
    try:
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Initialize credit scoring system
        credit_scorer = CreditScoring(customer_id)
        eligibility = credit_scorer.check_eligibility(loan_amount, interest_rate, tenure)
        
        response_data = {
            'customer_id': customer_id,
            'approval': eligibility['approved'],
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': float(eligibility['corrected_interest_rate']),
            'tenure': tenure,
            'monthly_installment': round(float(eligibility['monthly_installment']), 2)
        }
        
        response_serializer = LoanEligibilityResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'errors': response_serializer.errors}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_loan(request):
    """
    Process a new loan based on eligibility
    POST /create-loan
    """
    try:
        serializer = LoanCreateRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check eligibility first
        credit_scorer = CreditScoring(customer_id)
        eligibility = credit_scorer.check_eligibility(loan_amount, interest_rate, tenure)
        
        if not eligibility['approved']:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': eligibility.get('reason', 'Loan not approved based on credit score'),
                'monthly_installment': round(float(eligibility['monthly_installment']), 2)
            }
        else:
            # Create the loan
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=eligibility['corrected_interest_rate'],
                start_date=datetime.now(),
                emis_paid_on_time=0
            )
            
            response_data = {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': round(float(loan.monthly_payment), 2)
            }
        
        response_serializer = LoanCreateResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'errors': response_serializer.errors}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_loan_details(request, loan_id):
    """
    View loan details and customer details
    GET /view-loan/<loan_id>
    """
    try:
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all current loan details by customer id
    GET /view-loans/<customer_id>
    """
    try:
        # Check if customer exists
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Get all active loans for the customer
        loans = Loan.objects.filter(customer=customer)
        
        serializer = LoanListSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )