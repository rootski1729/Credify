from celery import shared_task
import pandas as pd
import os
from datetime import datetime
from django.conf import settings
from apps.customers.models import Customer
from apps.loans.models import Loan


@shared_task
def load_customer_data():
    try:
        file_path = os.path.join(settings.DATA_PATH, 'customer_data.xlsx')
        
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        df = pd.read_excel(file_path)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                customer_data = {
                    'customer_id': row['Customer ID'],
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': row['Phone Number'],
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                }
                
                customer, created = Customer.objects.update_or_create(
                    customer_id=customer_data['customer_id'],
                    defaults=customer_data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing customer row {index}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {'error': f'Failed to load customer data: {str(e)}'}


@shared_task
def load_loan_data():
    try:
        file_path = os.path.join(settings.DATA_PATH, 'loan_data.xlsx')
        
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        df = pd.read_excel(file_path)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                try:
                    customer = Customer.objects.get(customer_id=row['Customer ID'])
                except Customer.DoesNotExist:
                    error_count += 1
                    print(f"Customer {row['Customer ID']} not found for loan {row['Loan ID']}")
                    continue
                
                start_date = pd.to_datetime(row['Date of Approval'])
                end_date = pd.to_datetime(row['End Date'])
                
                loan_data = {
                    'loan_id': row['Loan ID'],
                    'customer': customer,
                    'loan_amount': row['Loan Amount'],
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'monthly_payment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date': start_date,
                    'end_date': end_date,
                }
                
                loan, created = Loan.objects.update_or_create(
                    loan_id=loan_data['loan_id'],
                    defaults=loan_data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing loan row {index}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {'error': f'Failed to load loan data: {str(e)}'}


@shared_task
def load_all_data():
    print("Starting data loading process...")
    
    customer_result = load_customer_data()
    print(f"Customer data loading result: {customer_result}")
    
    loan_result = load_loan_data()
    print(f"Loan data loading result: {loan_result}")
    
    return {
        'customer_data': customer_result,
        'loan_data': loan_result
    }