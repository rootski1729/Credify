from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Customer
from .serializers import (
    CustomerRegistrationSerializer, 
    CustomerRegistrationResponseSerializer)

@api_view(['POST'])
def register_customer(request):

    try:
        serializer = CustomerRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        phone_number = serializer.validated_data['phone_number']
        if Customer.objects.filter(phone_number=phone_number).exists():
            return Response(
                {'error': 'Customer with this phone number already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = Customer.objects.create(**serializer.validated_data)
        
        response_serializer = CustomerRegistrationResponseSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        return Response(
            {'error': 'Customer with this phone number already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )