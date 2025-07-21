from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'start_date', 'is_active']
    list_filter = ['interest_rate', 'tenure', 'start_date', 'end_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'loan_id']
    raw_id_fields = ['customer']
    ordering = ['-start_date']
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True