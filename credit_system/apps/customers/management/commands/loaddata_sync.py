from django.core.management.base import BaseCommand
from apps.core.tasks import load_customer_data, load_loan_data


class Command(BaseCommand):
    help = 'Load customer and loan data from Excel files synchronously'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading customer data...'))
        customer_result = load_customer_data()
        self.stdout.write(self.style.SUCCESS(f'Customer data result: {customer_result}'))
        
        self.stdout.write(self.style.SUCCESS('Loading loan data...'))
        loan_result = load_loan_data()
        self.stdout.write(self.style.SUCCESS(f'Loan data result: {loan_result}'))
        
        self.stdout.write(self.style.SUCCESS('Data loading completed!'))