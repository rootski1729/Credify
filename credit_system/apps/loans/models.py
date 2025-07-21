from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.PositiveIntegerField()  # in months
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        indexes = [
            models.Index(fields=['customer', 'start_date']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['loan_id']),
        ]

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"

    @property
    def is_active(self):
        now = datetime.now()
        return self.start_date <= now <= self.end_date

    @property
    def repayments_left(self):
        if not self.is_active:
            return 0
        
        now = datetime.now()
        months_passed = (now.year - self.start_date.year) * 12 + (now.month - self.start_date.month)
        
        if now.day < self.start_date.day:
            months_passed -= 1
            
        remaining = self.tenure - months_passed
        return max(0, remaining)

    @property
    def current_debt(self):
            if not self.is_active:
                return 0
        return self.monthly_payment * self.repayments_left

    def calculate_monthly_payment(self):
        principal = float(self.loan_amount)
        rate = float(self.interest_rate) / (12 * 100) 
        n = self.tenure
        
        if rate == 0:
            return principal / n
        
        emi = principal * rate * (1 + rate) ** n / ((1 + rate) ** n - 1)
        return round(emi, 2)

    def save(self, *args, **kwargs):
        if not self.monthly_payment:
            self.monthly_payment = self.calculate_monthly_payment()
        
        if not self.end_date and self.start_date:
            self.end_date = self.start_date + relativedelta(months=self.tenure)
        
        super().save(*args, **kwargs)