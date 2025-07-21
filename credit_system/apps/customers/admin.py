from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit']
    list_filter = ['monthly_salary', 'approved_limit']
    search_fields = ['first_name', 'last_name', 'phone_number']
    ordering = ['customer_id']